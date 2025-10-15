#!/bin/bash

# DMS 배포 스크립트 for Cafe24 Linux Server
# 사용법: ./deploy.sh [dev|prod]

set -e  # 에러 발생 시 스크립트 중단

ENVIRONMENT=${1:-dev}

echo "🚀 DMS 배포 시작 - 환경: $ENVIRONMENT"

# 환경 변수 파일 확인
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다. .env.example을 복사하여 .env를 생성하고 설정을 수정하세요."
    cp .env.example .env
    echo "📝 .env 파일을 수정한 후 다시 실행하세요."
    exit 1
fi

# Docker와 Docker Compose 설치 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다."
    echo "설치 방법: https://docs.docker.com/engine/install/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose가 설치되지 않았습니다."
    echo "설치 방법: https://docs.docker.com/compose/install/"
    exit 1
fi

# 기존 컨테이너 중지 및 제거
echo "🔄 기존 컨테이너 중지 중..."
docker-compose down --remove-orphans

# 이미지 빌드
echo "🏗️  Docker 이미지 빌드 중..."
if [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose --profile production build --no-cache
else
    docker-compose build --no-cache
fi

# 컨테이너 실행
echo "▶️  컨테이너 실행 중..."
if [ "$ENVIRONMENT" = "prod" ]; then
    docker-compose --profile production up -d
else
    docker-compose up -d
fi

# 헬스체크
echo "🔍 서비스 상태 확인 중..."
sleep 10

# 데이터베이스 헬스체크
if docker-compose exec -T db mysqladmin ping -h localhost --silent; then
    echo "✅ 데이터베이스 연결 성공"
else
    echo "❌ 데이터베이스 연결 실패"
fi

# 백엔드 헬스체크
if curl -f http://localhost:5000/api/health &> /dev/null; then
    echo "✅ 백엔드 API 서비스 정상"
else
    echo "❌ 백엔드 API 서비스 오류"
fi

# 프론트엔드 헬스체크
if curl -f http://localhost:3000 &> /dev/null; then
    echo "✅ 프론트엔드 서비스 정상"
else
    echo "❌ 프론트엔드 서비스 오류"
fi

echo ""
echo "🎉 배포 완료!"
echo "📍 서비스 접근 URL:"
echo "   - 프론트엔드: http://localhost:3000"
echo "   - 백엔드 API: http://localhost:5000"
if [ "$ENVIRONMENT" = "prod" ]; then
    echo "   - Nginx: http://localhost:80"
fi
echo ""
echo "📊 컨테이너 상태 확인:"
docker-compose ps
echo ""
echo "📝 로그 확인: docker-compose logs -f [service_name]"
echo "🛑 서비스 중지: docker-compose down"