# DMS API Documentation v2.0

## 🏗️ **시스템 아키텍처**

**Dead Man's Switch (DMS)** - 디지털 메시지 서비스  
자동 메시지 발송 시스템으로 사용자 비활성 상태 감지 시 지정된 수신자에게 메시지를 전송합니다.

---

## 📡 **API 엔드포인트 목록**

### 🏠 **Home & System**
- `GET /` - API 홈페이지
- `GET /api/health` - 시스템 상태 확인
- `GET /api/docs` - API 문서 페이지

### 🔐 **Authentication**
- `POST /api/auth/register` - 사용자 회원가입
- `POST /api/auth/login` - 사용자 로그인
- `GET /api/auth/verify` - 토큰 검증

### 👥 **Users (UserInfo)**
- `GET /api/users` - 모든 사용자 조회
- `GET /api/users/{id}` - 특정 사용자 조회
- `POST /api/users` - 새 사용자 생성
- `PUT /api/users/{id}` - 사용자 정보 수정
- `DELETE /api/users/{id}` - 사용자 삭제

### 📜 **Wills**
- `GET /api/wills` - 모든 유언장 조회
- `GET /api/wills/{id}` - 특정 유언장 조회
- `GET /api/wills/user/{user_id}` - 사용자별 유언장 조회
- `POST /api/wills` - 새 유언장 생성
- `PUT /api/wills/{id}` - 유언장 수정
- `DELETE /api/wills/{id}` - 유언장 삭제

### 📧 **Recipients**
- `GET /api/recipients` - 모든 수신자 조회
- `GET /api/recipients/{id}` - 특정 수신자 조회
- `GET /api/recipients/will/{will_id}` - 유언장별 수신자 조회
- `POST /api/recipients` - 새 수신자 추가
- `PUT /api/recipients/{id}` - 수신자 정보 수정
- `DELETE /api/recipients/{id}` - 수신자 삭제

### ⚡ **Triggers**
- `GET /api/triggers` - 모든 트리거 조회
- `GET /api/triggers/{id}` - 특정 트리거 조회
- `GET /api/triggers/user/{user_id}` - 사용자별 트리거 조회
- `GET /api/triggers/user/{user_id}/pending` - 사용자 대기 중 트리거 조회
- `POST /api/triggers` - 새 트리거 생성
- `PUT /api/triggers/{id}` - 트리거 수정
- `DELETE /api/triggers/{id}` - 트리거 삭제

### 📨 **Dispatch Logs**
- `GET /api/dispatch-logs` - 모든 발송 로그 조회
- `GET /api/dispatch-logs/{id}` - 특정 발송 로그 조회
- `GET /api/dispatch-logs/will/{will_id}` - 유언장별 발송 로그 조회
- `POST /api/dispatch-logs` - 새 발송 로그 생성
- `PUT /api/dispatch-logs/{id}` - 발송 로그 수정
- `DELETE /api/dispatch-logs/{id}` - 발송 로그 삭제

### 🛠️ **System & Testing**
- `GET /api/system/info` - 시스템 정보 조회
- `GET /api/test/health` - 테스트 헬스체크
- `POST /api/logs/frontend` - 프론트엔드 로그 수신

---

## 📊 **데이터 모델**

### UserInfo
```json
{
  "id": 1,
  "user_id": "bluespak",
  "FirstName": "Elvin",
  "LastName": "Kang",
  "Email": "bluespak@gmail.com",
  "DOB": "1975-02-02",
  "Grade": "Standard",
  "created_at": "2025-10-14T12:44:29"
}
```

### Will
```json
{
  "id": 1,
  "user_id": "bluespak",
  "title": "My Digital Will",
  "content": "Important message content...",
  "created_at": "2025-10-14T15:30:00",
  "updated_at": "2025-10-14T15:30:00"
}
```

### Recipients
```json
{
  "id": 1,
  "will_id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2025-10-14T15:30:00"
}
```

### Triggers
```json
{
  "id": 1,
  "user_id": "bluespak",
  "trigger_type": "inactivity",
  "trigger_value": 30,
  "trigger_date": "2025-11-13T15:30:00",
  "status": "active",
  "created_at": "2025-10-14T15:30:00"
}
```

### DispatchLog
```json
{
  "id": 1,
  "will_id": 1,
  "recipient_id": 1,
  "status": "sent",
  "sent_at": "2025-10-14T15:30:00",
  "created_at": "2025-10-14T15:30:00"
}
```

---

## 🔍 **API 사용 예제**

### 1. 사용자 생성
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "FirstName": "John",
    "LastName": "Doe",
    "Email": "john@example.com",
    "DOB": "1990-01-01",
    "Grade": "Standard"
  }'
```

### 2. 유언장 생성
```bash
curl -X POST http://localhost:5000/api/wills \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "john.doe",
    "title": "My Last Will",
    "content": "Important final message..."
  }'
```

### 3. 트리거 생성
```bash
curl -X POST http://localhost:5000/api/triggers \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "john.doe",
    "trigger_type": "inactivity",
    "trigger_value": 30
  }'
```

---

## 🏷️ **상태 코드**

- `200 OK` - 성공
- `201 Created` - 리소스 생성 성공
- `400 Bad Request` - 잘못된 요청
- `404 Not Found` - 리소스 없음
- `500 Internal Server Error` - 서버 오류

---

## 🔧 **개발 환경 설정**

```bash
# 서버 시작
cd backend
python app/app.py

# 기본 URL
http://localhost:5000
```

**업데이트 날짜**: 2025-10-14  
**API 버전**: v2.0  
**문서 버전**: 2.0.0