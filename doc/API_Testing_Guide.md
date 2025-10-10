# DMS API 테스트 컬렉션 사용 가이드

이 폴더에는 DMS API를 테스트할 수 있는 다양한 도구용 컬렉션 파일들이 포함되어 있습니다.

## 📁 파일 목록

### 1. `DMS_API_Hoppscotch_Collection.json`
- **용도**: [Hoppscotch](https://hoppscotch.io/) 에서 사용
- **특징**: 웹 기반 API 테스트 도구, 실시간 테스트 가능
- **사용법**:
  1. https://hoppscotch.io/ 접속
  2. "Collections" → "Import" 클릭
  3. `DMS_API_Hoppscotch_Collection.json` 파일 업로드
  4. 환경 변수 "DMS Local Development" 선택
  5. 각 API 엔드포인트 테스트 실행

### 2. `DMS_API_Postman_Collection.json`
- **용도**: [Postman](https://www.postman.com/) 에서 사용
- **특징**: 전문적인 API 개발 도구, 자동화 테스트 지원
- **사용법**:
  1. Postman 애플리케이션 실행
  2. "Import" 버튼 클릭
  3. `DMS_API_Postman_Collection.json` 파일 선택
  4. Collection Variables에서 `base_url` 확인 (http://127.0.0.1:5000)
  5. 순서대로 API 테스트 실행

### 3. `api-documentation.html`
- **용도**: DMS API 전체 문서
- **특징**: 모든 엔드포인트의 상세 설명, 예제 포함
- **사용법**: 웹 브라우저로 열어서 확인

## 🚀 테스트 시나리오

### 기본 테스트 순서
1. **System API**: Health Check로 서버 상태 확인
2. **UserInfo API**: 사용자 생성 → 조회 → 수정 → 삭제
3. **Will API**: 유언장 생성 → 조회 → 수정 → 삭제
4. **Recipients API**: 수신자 생성 → 조회 → 수정 → 삭제
5. **Triggers API**: 트리거 생성 → 조회 → 수정 → 삭제
6. **DispatchLog API**: 발송 로그 생성 → 조회 → 수정 → 삭제

### 환경 변수
컬렉션에는 다음 환경 변수들이 포함되어 있습니다:
- `base_url`: http://127.0.0.1:5000 (로컬 개발 서버)
- `created_user_id`: 생성된 사용자 ID (자동 설정)
- `created_will_id`: 생성된 유언장 ID (자동 설정)
- `created_recipient_id`: 생성된 수신자 ID (자동 설정)
- `created_trigger_id`: 생성된 트리거 ID (자동 설정)
- `created_log_id`: 생성된 로그 ID (자동 설정)

## 📊 API 엔드포인트 개요

### UserInfo API (사용자 관리)
- `GET /api/users` - 모든 사용자 조회
- `GET /api/users/{id}` - 특정 사용자 조회
- `POST /api/users` - 사용자 생성
- `PUT /api/users/{id}` - 사용자 수정
- `DELETE /api/users/{id}` - 사용자 삭제

### Will API (유언장 관리)
- `GET /api/wills` - 모든 유언장 조회
- `GET /api/wills/{id}` - 특정 유언장 조회
- `GET /api/wills/user/{user_id}` - 특정 사용자의 유언장들 조회
- `POST /api/wills` - 유언장 생성 (user_id, subject, body 필수)
- `PUT /api/wills/{id}` - 유언장 수정 (subject, body, user_id 선택)
- `DELETE /api/wills/{id}` - 유언장 삭제

### Recipients API (수신자 관리)
- `GET /api/recipients` - 모든 수신자 조회
- `GET /api/recipients/will/{will_id}` - 특정 유언장의 수신자들 조회
- `GET /api/recipients/{id}` - 특정 수신자 조회
- `POST /api/recipients` - 수신자 생성
- `PUT /api/recipients/{id}` - 수신자 수정
- `DELETE /api/recipients/{id}` - 수신자 삭제

### Triggers API (트리거 관리)
- `GET /api/triggers` - 모든 트리거 조회
- `GET /api/triggers/user/{user_id}` - 특정 사용자의 트리거들 조회
- `GET /api/triggers/{id}` - 특정 트리거 조회
- `POST /api/triggers` - 트리거 생성
- `PUT /api/triggers/{id}` - 트리거 수정
- `DELETE /api/triggers/{id}` - 트리거 삭제

### DispatchLog API (발송 로그 관리)
- `GET /api/dispatch-logs` - 모든 발송 로그 조회
- `GET /api/dispatch-logs/will/{will_id}` - 특정 유언장의 발송 로그들 조회
- `GET /api/dispatch-logs/recipient/{recipient_id}` - 특정 수신자의 발송 로그들 조회
- `POST /api/dispatch-logs` - 발송 로그 생성
- `PUT /api/dispatch-logs/{id}` - 발송 로그 수정
- `DELETE /api/dispatch-logs/{id}` - 발송 로그 삭제

### System API (시스템)
- `GET /api/health` - 서버 상태 확인
- `GET /api/docs` - API 문서 조회

## 🔧 사전 준비사항

1. **DMS 서버 실행**: Flask 앱이 http://127.0.0.1:5000 에서 실행 중이어야 함
2. **데이터베이스**: MySQL 데이터베이스가 정상적으로 연결되어 있어야 함
3. **환경 설정**: .env 파일이 올바르게 설정되어 있어야 함

## 💡 추천 워크플로우

### Hoppscotch 사용 시
1. Collection 임포트 후 Environment 선택
2. System API의 Health Check로 서버 상태 확인
3. UserInfo API부터 순차적으로 테스트
4. 각 단계에서 생성된 ID들이 자동으로 다음 테스트에 사용됨

### Postman 사용 시
1. Collection 임포트 후 Collection Variables 확인
2. Runner 기능으로 전체 테스트 일괄 실행 가능
3. Test Scripts에서 자동 검증 및 변수 설정
4. Newman으로 CI/CD 파이프라인에 통합 가능

## ⚠️ 주의사항

- 테스트 실행 시 실제 데이터베이스에 데이터가 생성/수정/삭제됩니다
- 테스트용 데이터베이스를 사용하는 것을 권장합니다
- ID 값들은 테스트 실행 순서에 따라 자동으로 설정됩니다
- 일부 테스트는 이전 테스트의 결과에 의존할 수 있습니다

---

📝 **마지막 업데이트**: 2025-10-10  
🔗 **관련 링크**: [DMS GitHub Repository](https://github.com/bluespak/DMS)