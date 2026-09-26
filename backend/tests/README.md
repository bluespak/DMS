# DMS API 테스트 가이드

## 📋 개요

DMS (Digital Message Service) API의 유닛 테스트 모음입니다. 모든 API 엔드포인트에 대한 포괄적인 테스트를 제공합니다.

## 🏗️ 테스트 구조

```
backend/tests/
├── __init__.py                 # 패키지 초기화
├── test_config.py              # 테스트 설정 및 기본 클래스
├── test_userinfo_api.py        # UserInfo API 테스트
├── test_will_api.py            # Will API 테스트
├── test_recipients_api.py      # Recipients API 테스트
├── test_triggers_api.py        # Triggers API 테스트
├── test_dispatchlog_api.py     # DispatchLog API 테스트
├── run_tests.py                # 테스트 실행 스크립트
└── README.md                   # 이 파일
```

## 🚀 테스트 실행 방법

### 1. 모든 테스트 실행

```bash
# backend/tests 디렉토리에서
python run_tests.py
```

### 2. 특정 테스트 모듈 실행

```bash
# UserInfo API 테스트만 실행
python run_tests.py test_userinfo_api

# Will API 테스트만 실행
python run_tests.py test_will_api

# Recipients API 테스트만 실행
python run_tests.py test_recipients_api

# Triggers API 테스트만 실행
python run_tests.py test_triggers_api

# DispatchLog API 테스트만 실행
python run_tests.py test_dispatchlog_api
```

### 3. 개별 테스트 파일 직접 실행

```bash
python test_userinfo_api.py
python test_will_api.py
python test_recipients_api.py
python test_triggers_api.py
python test_dispatchlog_api.py
```

### 4. unittest 명령어 사용

```bash
# 모든 테스트 실행
python -m unittest discover -s . -p "test_*.py" -v

# 특정 테스트 클래스 실행
python -m unittest test_userinfo_api.TestUserInfoAPI -v

# 특정 테스트 메서드 실행
python -m unittest test_userinfo_api.TestUserInfoAPI.test_create_user_success -v
```

## 🧪 테스트 범위

### UserInfo API 테스트
- ✅ 빈 사용자 목록 조회
- ✅ 사용자 생성 (성공/실패 케이스)
- ✅ 사용자 조회 (ID별, 존재하지 않는 경우)
- ✅ 사용자 정보 수정
- ✅ 사용자 삭제
- ✅ 날짜 형식 검증
- ✅ 데이터 유효성 검증

### Will API 테스트
- ✅ 빈 유언장 목록 조회
- ✅ 유언장 생성 (성공/실패 케이스)
- ✅ 유언장 조회 (ID별, 존재하지 않는 경우)
- ✅ 유언장 수정 (전체/부분 수정)
- ✅ 유언장 삭제
- ✅ 필수 필드 검증

### Recipients API 테스트
- ✅ 빈 수신자 목록 조회
- ✅ 수신자 생성 (성공/실패 케이스)
- ✅ 수신자 조회 (ID별, 유언장별)
- ✅ 수신자 정보 수정
- ✅ 수신자 삭제
- ✅ 관계 코드 처리

### Triggers API 테스트
- ✅ 빈 트리거 목록 조회
- ✅ 트리거 생성 (성공/실패 케이스)
- ✅ 트리거 조회 (ID별, 사용자별)
- ✅ 트리거 수정
- ✅ 트리거 삭제
- ✅ 트리거 타입 검증 (inactivity, date, manual)

### DispatchLog API 테스트
- ✅ 빈 발송 로그 목록 조회
- ✅ 발송 로그 생성 (성공/실패 케이스)
- ✅ 발송 로그 조회 (ID별, 유언장별, 수신자별)
- ✅ 발송 로그 수정
- ✅ 발송 로그 삭제
- ✅ 상태 코드 검증 (pending, sent, failed)
- ✅ 날짜 처리

## 🔧 테스트 설정

### 테스트 데이터베이스
- 기본값은 테스트 전용 SQLite 파일 DB 사용
- `TEST_DATABASE_URI` 또는 `TEST_DB_*` 환경변수로 MySQL 테스트 DB 사용 가능
- 테스트 후 자동 정리

예시:

```bash
export TEST_DATABASE_URI="mysql+pymysql://user:password@dmsdata:3306/dmsdb_test"
python -m unittest discover -s . -p "test_*.py" -v
```

### 테스트 환경 설정
- Flask 테스트 클라이언트 사용
- 실제 HTTP 요청/응답 시뮬레이션
- JSON 데이터 검증
- 상태 코드 검증

## 📊 테스트 결과 예시

```
🧪 DMS API 테스트 시작
==================================================
✅ test_userinfo_api 테스트 로드 완료
✅ test_will_api 테스트 로드 완료
✅ test_recipients_api 테스트 로드 완료
✅ test_triggers_api 테스트 로드 완료
✅ test_dispatchlog_api 테스트 로드 완료

test_create_user_success (test_userinfo_api.TestUserInfoAPI) ... ok
test_create_will_success (test_will_api.TestWillAPI) ... ok
...

==================================================
테스트 결과 요약
==================================================
실행된 테스트: 45
실패: 0
에러: 0

🎉 모든 테스트가 성공했습니다!
```

## 🛠️ 테스트 추가하기

새로운 테스트를 추가하려면:

1. `test_config.py`의 `BaseTestCase`를 상속
2. `setUp()` 메서드에서 필요한 테스트 데이터 준비
3. `test_`로 시작하는 메서드 작성
4. `self.assertEqual()`, `self.assertTrue()` 등으로 검증
5. `run_tests.py`의 `test_modules` 리스트에 추가

### 예시:
```python
class TestNewAPI(BaseTestCase):
    def test_new_feature(self):
        response = self.client.get('/api/new-endpoint')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
```

## 🚨 주의사항

1. **테스트 데이터 격리**: 각 테스트는 독립적으로 실행되어야 합니다
2. **실제 데이터베이스 사용 금지**: 테스트는 항상 인메모리 DB 사용
3. **외부 의존성 최소화**: 모킹이나 스텁 사용 권장
4. **테스트 이름 명확화**: 테스트 목적이 명확히 드러나는 이름 사용

## 📚 추가 정보

- 테스트는 CI/CD 파이프라인에서 자동 실행
- 코드 커버리지 목표: 90% 이상
- 모든 API 엔드포인트는 최소 성공/실패 케이스 테스트 필요