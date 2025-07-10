# 🔧 SQL 변환 어플리케이션  
  
이 프로젝트는 SQL 쿼리를 특정 DBMS에서 다른 DBMS로 변환하고, CSV 파일을 Azure Blob Storage에 업로드하여 테스트 해볼수 있는 Streamlit 애플리케이션입니다.  
  
## 🌐 실행 도메인  
[http://user10-webapp-01-hpfve6fcfdhebgge.eastus2-01.azurewebsites.net](http://user10-webapp-01-hpfve6fcfdhebgge.eastus2-01.azurewebsites.net)  
  
## 📚 개요 및 목적  
- **SQL 쿼리를 입력 받아 SQL 문맥과 구조를 이해하여 다른 문법의 SQL로 변환해 주는 AI Agent**  
- 이기종 DB 간 호환성 확보  
- 개발자 생산성 향상  
  
## 📊 아키텍처 다이어그램  
- **Azure 서비스**:
  - **Azure OpenAI**: 입력받은 SQL 변환 및 DBMS 판단
  - **Azure Blob Storage**: CSV 파일 저장 및 관리  
- **프론트엔드**:  
  - **Streamlit**: 사용자 인터페이스 제공  
- **데이터 흐름**:  
  1. Streamlit 기반 화면 → 사용자가 SQL 변환할 쿼리 입력  
  2. Azure OpenAI 호출 → DBMS 판단 요청
  3. Azure OpenAI 호출 → SQL 변환 요청  
  4. CSV 파일 업로드 → Azure Blob Storage  
  5. SQL 쿼리 실행 → SQLite 데이터베이스에서 Azure Blob Storage에 업로드된 데이터 기반 처리  
  
## 🔑 핵심 기술 포인트  
- **커스텀 프롬프트 엔지니어링**:  
  - SQL 변환을 위한 프롬프트 설계: 사용자의 SQL 쿼리를 다른 DBMS 문법으로 변환하기 위해 프롬프트를 작성.  
- **Azure OpenAI 사용**:  
  - LLM을 활용하여 SQL 변환 및 DBMS 감지: SQL 문법을 이해하고 변환.  
- **데이터 흐름 및 처리**:  
  - CSV 파일을 Blob Storage에서 다운로드 및 업로드하여 SQLite 메모리 내 데이터베이스에서 쿼리 실행.  
- **LangChain 에이전트 설계**:  
  - SQL 변환 및 DBMS 감지 기능을 제공하기 위한 에이전트 설계.  
  
## 🚀 라이브 데모  
- **주요 기능 시연**:  
  - SQL 변환 기능 시연: 사용자가 SQL 쿼리를 입력하고 변환 결과를 받는 과정.  
  - CSV 파일 업로드: 파일 선택 후 Azure Blob Storage에 업로드하는 과정 시연.  
  - SQL 테스트: 변환된 SQL 쿼리를 사용하여 업로드한 파일 대상으로 쿼리 실행 후 결과를 표시하는 과정.  
  
## 🔄 향후 개선 및 확장 계획  
- CSV 외의 파일 형식도 지원하는 기능 개발  
- 데이터베이스 연동  
