import streamlit as st
import pandas as pd
import json
import os
import sqlite3
import chardet  
from io import StringIO  
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI  
from langchain.schema import SystemMessage, HumanMessage
from langchain_community.chat_models import AzureChatOpenAI
from azure.storage.blob import BlobServiceClient

# 환경 변수 로드 (.env 읽어서 메모리에 load)
load_dotenv() 
api_key = os.getenv("OPENAI_API_KEY")  
api_azure_endpoint = os.getenv("OPENAI_ENDPOINT")  
api_type = os.getenv("OPENAI_API_TYPE")  
api_version = os.getenv("OPENAI_API_VERSION")  
chat_deployment_name = os.getenv("CHAT_DEPLOYMENT_NAME") 
azure_blob = os.getenv("AZURE_STOREGE_CONNECTION_STRING") 
azure_container = os.getenv("AZURE_STORAGE_CONTAINER") 

# 초기 세션 정의
if "query" not in st.session_state:
  st.session_state.query = ""
if "converted_sql" not in st.session_state:
  st.session_state.converted_sql = None
if "csv_uploaded" not in st.session_state:
  st.session_state.csv_uploaded = False
if "upload_file" not in st.session_state:
  st.session_state.upload_file = None 

# SQL 변환 함수 (Langchain, Azure OpenAI)
def convert_sql(query: str, source : str, target: str):
  llm = AzureChatOpenAI (
      openai_api_key=api_key,
      azure_endpoint=api_azure_endpoint,
      deployment_name=chat_deployment_name,
      openai_api_version=api_version,
      openai_api_type=api_type,
      temperature=0
  ) 
  
  prompt = f"""
    당신은 SQL 변환 전문가 입니다.
    아래 SQL 쿼리는 {source} DBMS 용입니다.
    이를 {target} DBMS 문법에 맞게 정확히 변환해 주세요.

    결과는 반드시 **아래 JSON 형식**을 따르세요.
    다른 말이나 설명 없이 JSON만 출력하세요.
    예시 형식:
    {{
      "source_dbms": "{source}",
      "target_dbms": "{target}",
      "conversion_notes": "<한국어로 어떤 문법을 왜 바꿨는지 간단히 요약, SQL문에대한 간단한 해석 등>",
      "converted_sql": "<변환된 SQL 쿼리 내용>"
    }}

    원본 sql 쿼리: {query}
  """

  messages = [
    SystemMessage(content="당신은 전문 sql 변환기입니다."),
    HumanMessage(content=prompt)
  ]

  return llm(messages).content.strip()

def detect_source_db(query: str) -> str:
  llm = AzureChatOpenAI(   
    openai_api_key=api_key,
    azure_endpoint=api_azure_endpoint,
    deployment_name=chat_deployment_name,
    openai_api_version=api_version,
    openai_api_type=api_type,
    temperature=0
  )

  messages = [
    SystemMessage(content="당신은 SQL 분석 전문가 입니다."),
    HumanMessage(content=f"""
      다음 SQL은 어떤 DBMS의 문법입니까?
      sql
      {query}
      )
      반드시 다음 중 한 단어로만 반환하세요: Oracle, Mysql, Mssql, Postgersql, Teradata, Nosql
      """)
  ] 

  result = llm(messages).content.strip().split()[0].capitalize()
  if result not in ["Oracle", "Mysql", "Mssql", "Postgersql"]:
    return "Unknown"
  return result

def upload_to_blob(file, filename):    
  try:   
    # BlobServiceClient 생성  
    blob_service_client = BlobServiceClient.from_connection_string(azure_blob)           
    # BlobClient 생성  
    blob_client = blob_service_client.get_blob_client(container=azure_container, blob=filename)     
    # 파일 업로드  
    blob_client.upload_blob(file.getvalue(), overwrite=True)  # overwrite=True로 덮어쓰기 가능            
    #st.success(f"File {file.name} uploaded to Blob Storage successfully!")  

    # 실제 URL 생성  
    blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{azure_container}/{filename}"  
    return blob_url  # 실제 URL 반환  
  except Exception as e:  
    st.error(f"Error uploading file: {e}")  
    return None  # 오류 발생 시 None 반환  

def load_and_join_csv_from_blob(connection_string, container_name, join_query):  
  # 1. BlobServiceClient 생성  
  blob_service_client = BlobServiceClient.from_connection_string(connection_string)  

  # 2. 컨테이너 클라이언트 생성  
  container_client = blob_service_client.get_container_client(container_name)  
  
  # 3. Blob 목록 가져오기  
  blobs = container_client.list_blobs()  
  
  dataframes = {}  
  for blob in blobs:  
    if blob.name.endswith('.csv'):  # CSV 파일 필터링  
      # Blob 다운로드  
      blob_client = container_client.get_blob_client(blob)  
      stream = blob_client.download_blob()  
      csv_data = stream.content_as_bytes()  # 바이트 형태로 다운로드  
  
      # 인코딩 감지  
      result = chardet.detect(csv_data)  
      encoding = result['encoding']  
  
      # CSV 데이터를 DataFrame으로 변환  
      df = pd.read_csv(StringIO(csv_data.decode(encoding)), encoding=encoding)  
  
      # 파일 이름을 테이블 이름으로 사용 (확장자 제거)  
      table_name = blob.name.split('.')[0]  
      dataframes[table_name] = df  
  
  # 5. SQLite 데이터베이스 연결 (메모리 내 데이터베이스 사용)  
  conn = sqlite3.connect(':memory:')  
  
  # 6. DataFrame을 SQLite 데이터베이스에 저장  
  for table_name, df in dataframes.items():  
    df.to_sql(table_name, conn, index=False, if_exists='replace')  
  
  # 7. SQL 조인 쿼리 실행  
  result = pd.read_sql_query(join_query, conn)  
   
  conn.close()  
  return result  
  

# 페이지 설정  
st.set_page_config(page_title="SQL 변환기", layout="wide")  
st.title("🧸 AI 기반 SQL 변환 및 실행기")  
  
# 초기화 버튼  
if st.button("🔁 초기화"):  
  st.session_state.query = ""  
  st.session_state.converted_sql = None
  st.session_state.csv_uploaded = False  
  st.session_state.upload_file = None 
  
dbms_options = ["Oracle", "Mysql", "Postgresql", "Mssql", "Teradata", "Nosql"]    
target_db = st.selectbox("✍ 변환할 DBMS 선택", dbms_options, index=dbms_options.index(st.session_state.get("target_db", dbms_options[0])))  
  
# SQL 쿼리 입력 
st.session_state.query = st.text_area("변환할 SQL 쿼리를 입력하세요.", st.session_state.get("query", ""), height=200)  
  
if st.button("SQL 변환하기"):  
  if not st.session_state.query.strip():  
      st.warning("SQL 쿼리를 입력하세요.")  
  else:  
    with st.spinner("원본 DBMS 감지 중..."):  
      detected_source_db = detect_source_db(st.session_state.query)  # DBMS 감지 함수 호출  
  
    if detected_source_db == "Unknown":  
      st.error("원본 DBMS를 감지할 수 없습니다.")  
    else:  
      #st.success(f"감지된 DBMS: `{detected_source_db}`   변환할 DBMS: `{target_db}`")  
      # DBMS가 동일한지 확인  
      if detected_source_db == target_db:  
        st.warning("🚫원본과 대상 DBMS가 동일합니다.🚫")  
      else:  
        with st.spinner(f"GPT를 통해 변환중..."):  
          json_output = convert_sql(st.session_state.query, detected_source_db, target_db)
          parsed = json.loads(json_output)
          st.session_state.converted_sql = parsed["converted_sql"]
          #st.session_state.converted_sql = convert_sql(st.session_state.query, st.session_state.source_db, target_db)  # SQL 변환 함수 호출  
          st.success("변환 완료!")  

    # 변환된 SQL 표시  
    if st.session_state.converted_sql:  
      st.markdown("---")
      st.markdown("### 📃 변환 정보")
      st.markdown(f"- **원본 DBMS**: `{parsed['source_dbms']}`")
      st.markdown(f"- **대상 DBMS**: `{parsed['target_dbms']}`")
      st.markdown(f"- **변환 요약**: `{parsed['conversion_notes']}`")

      st.markdown("---") 
      st.markdown("### 📃 변환된 SQL")
      st.code(parsed["converted_sql"], language="sql") 

st.markdown("---") 
st.header("📁 CSV 파일 업로드")
st.session_state.upload_file = st.file_uploader("CSV 파일을 선택하세요", type=["csv"])
if st.session_state.upload_file is not None:
  st.write(f"선택된 파일: `{st.session_state.upload_file.name}`")
  if st.button("csv파일 업로드"):
    blob_url = upload_to_blob(st.session_state.upload_file, st.session_state.upload_file.name)
    if blob_url is not None:
      st.success(f"blob에 업로드 완료")
      st.session_state.csv_uploaded = True
    else: 
      st.write(f"파일 업로드 실패")
else:
  if st.session_state.csv_uploaded:  
    st.write(f"이미 업로드된 파일: `{st.session_state.upload_file}`")  
  else:  
    st.info("먼저 CSV 파일을 선택하세요.")

if st.session_state.converted_sql:
  st.markdown("---")
  st.header("📊 SQL 테스트 하기")
  if st.button("SQL 테스트"):
    with st.spinner("SQL 수행 중..."):
      try:  
        # 쿼리 실행  
        result_df = load_and_join_csv_from_blob(azure_blob, azure_container, st.session_state.converted_sql)  
        # 결과 출력  
        st.dataframe(result_df)  # Streamlit의 데이터프레임 표시  
      except sqlite3.Error as e:  
        st.error(f"SQL Error: {e}")  # SQL 오류 메시지 출력  
      except Exception as e:  
        st.error(f"Error: {e}")  # 일반 오류 메시지 출력
  
