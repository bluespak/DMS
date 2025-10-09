import os
from dotenv import load_dotenv
import pymysql

print("=== .env 파일 디버깅 ===")

# 현재 작업 디렉토리 확인
current_dir = os.getcwd()
print(f"현재 작업 디렉토리: {current_dir}")

# .env 파일 경로 확인
env_file_path = os.path.join(current_dir, '.env')
print(f".env 파일 경로: {env_file_path}")
print(f".env 파일 존재 여부: {os.path.exists(env_file_path)}")

# .env 파일 내용 직접 읽기
try:
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"\n.env 파일 내용:")
        print(content)
except FileNotFoundError:
    print("❌ .env 파일을 찾을 수 없습니다!")
except Exception as e:
    print(f"❌ .env 파일 읽기 오류: {e}")

print("\n=== dotenv 로드 테스트 ===")

# .env 파일 로드 (명시적 경로 지정)
load_result = load_dotenv('.env', verbose=True)
print(f"load_dotenv() 결과: {load_result}")

# 환경 변수 확인
print("\n=== 환경 변수 확인 ===")
env_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'DATABASE_URL', 'FLASK_ENV', 'SECRET_KEY']

for var in env_vars:
    value = os.getenv(var)
    if value:
        if 'PASSWORD' in var or 'SECRET' in var:
            print(f"{var}: {'*' * len(value)}")
        else:
            print(f"{var}: {value}")
    else:
        print(f"{var}: ❌ 없음")

print("\n=== 모든 환경 변수 ===")
all_env = dict(os.environ)
dms_related = {k: v for k, v in all_env.items() if any(keyword in k.upper() for keyword in ['DB', 'DATABASE', 'FLASK', 'SECRET', 'DMS'])}
for k, v in dms_related.items():
    if any(keyword in k.upper() for keyword in ['PASSWORD', 'SECRET', 'KEY']):
        print(f"{k}: {'*' * len(v)}")
    else:
        print(f"{k}: {v}")

# 데이터베이스 연결 정보
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

print(f"\n=== 최종 연결 정보 ===")
print(f"Host: {DB_HOST}")
print(f"User: {DB_USER}")
print(f"Password: {'설정됨' if DB_PASSWORD else '❌ 없음'}")
print(f"Database: {DB_NAME}")

if all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
    print("✅ 모든 연결 정보가 설정되었습니다.")
else:
    print("❌ 일부 연결 정보가 누락되었습니다.")