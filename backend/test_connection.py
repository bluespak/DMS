import os
from dotenv import load_dotenv
import pymysql

# .env 파일 로드
load_dotenv()

# 환경 변수에서 데이터베이스 정보 가져오기
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

print("데이터베이스 연결 정보:")
print(f"Host: {DB_HOST}")
print(f"User: {DB_USER}")
print(f"Password: {'*' * len(DB_PASSWORD) if DB_PASSWORD else 'None'}")
print(f"Database: {DB_NAME}")
print()

# SQLAlchemy 연결 문자열 형식
sqlalchemy_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
print(f"SQLAlchemy 연결 문자열:")
print(f"mysql+pymysql://{DB_USER}:{'*' * len(DB_PASSWORD)}@{DB_HOST}/{DB_NAME}")
print()

# PyMySQL로 직접 연결 테스트
try:
    print("MySQL 연결 테스트 중...")
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4',
        port=3306
    )
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ 연결 성공! MySQL 버전: {version[0]}")
        
        # 데이터베이스 목록 확인
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        print(f"사용 가능한 데이터베이스: {[db[0] for db in databases]}")
        
        # 현재 데이터베이스의 테이블 확인
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"'{DB_NAME}' 데이터베이스의 테이블: {[table[0] for table in tables]}")
        
except Exception as e:
    print(f"❌ 연결 실패: {e}")
    print("\n가능한 해결책:")
    print("1. MySQL 서버가 실행 중인지 확인")
    print("2. 호스트 주소와 포트 확인")
    print("3. 사용자명과 비밀번호 확인")
    print("4. 데이터베이스 이름 확인")
    print("5. 방화벽 설정 확인")
    
finally:
    if 'connection' in locals():
        connection.close()
        print("연결이 종료되었습니다.")