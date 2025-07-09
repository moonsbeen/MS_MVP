# SQL 변환 어플리케이션
  
이 프로젝트는 SQL 쿼리를 특정 DBMS에서 다른 DBMS로 변환하고, CSV 파일을 Azure Blob Storage에 업로드하는 Streamlit 애플리케이션입니다.  

## 실행 도메인
user10-webapp-01-hpfve6fcfdhebgge.eastus2-01.azurewebsites.net

## 개요 및 목적
- SQL 쿼리를 입력 받아 SQL 문맥과 구조를 이해하여 다른 문법의 SQL로 변환해 주는 AI Agent  -
  - 이기종 DB간 호환성 확보
  -	AI 기반 쿼리 분석 및 최적화
  -	개발자 생산성 향상
  
## 아키텍처 다이어그램  
- **Azure 서비스**:  
  - Azure Blob Storage: CSV 파일 저장 및 관리  
  - Azure OpenAI: SQL 변환 및 DBMS 감지  
- **프론트엔드**:  
  - Streamlit: 사용자 인터페이스 제공  
- **백엔드**:  
  - Python: SQL 변환 및 데이터 처리 로직  
- **데이터 흐름**:  
  1. 사용자가 SQL 쿼리 입력 → Streamlit 프론트엔드  
  2. DBMS 감지 요청 → Azure OpenAI 호출  
  3. SQL 변환 요청 → Azure OpenAI 호출  
  4. CSV 파일 업로드 → Azure Blob Storage  
  5. SQL 쿼리 실행 → SQLite 데이터베이스에서 처리  
  
## 핵심 기술 포인트  
- **커스텀 프롬프트 엔지니어링**:  
  - SQL 변환을 위한 프롬프트 설계: 사용자의 SQL 쿼리를 다른 DBMS 문법으로 변환하기 위해 고유한 프롬프트를 작성.  
- **Azure OpenAI 사용**:  
  - LLM을 활용하여 SQL 변환 및 DBMS 감지: 고급 자연어 처리 기술을 사용하여 SQL 문법을 이해하고 변환.  
- **데이터 흐름 및 처리**:  
  - CSV 파일을 Blob Storage에서 다운로드하여 SQLite 메모리 내 데이터베이스에서 쿼리 실행.  
- **LangChain 에이전트 설계**:  
  - SQL 변환 및 DBMS 감지 기능을 제공하기 위한 에이전트 설계.  
  
## 라이브 데모  
- **주요 기능 시연**:  
  - SQL 변환 기능 시연: 사용자가 SQL 쿼리를 입력하고 변환 결과를 받는 과정.  
  - CSV 파일 업로드: 파일 선택 후 Azure Blob Storage에 업로드하는 과정 시연.  
  - SQL 테스트: 변환된 SQL 쿼리를 사용하여 데이터베이스에서 쿼리 실행 후 결과를 표시하는 과정.  
  
## 향후 개선 및 확장 계획  
- **추가 기능 개발**:  
  - 다국어 지원: 다양한 언어로 SQL 변환 기능 추가.  
  - Excel 파일 지원: CSV 외의 파일 형식도 지원하는 기능 개발.  
- **성능 최적화**:  
  - LLM 호출 최적화: 성능을 향상시키기 위한 비동기 처리 및 캐싱 메커니즘 적용.  
- **사용자 경험 개선**:  
  - UI/UX 개선: 사용자 피드백을 반영하여 인터페이스 개선.  
- **확장 계획**:  
  - 모바일 애플리케이션 개발 및 기타 플랫폼으로의 배포.  
  
