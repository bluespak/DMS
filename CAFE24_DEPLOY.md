# Cafe24 서버 배포 가이드

## 1. 서버 환경 준비

### Docker 설치 (CentOS/RHEL)
```bash
# Docker 설치
sudo yum update -y
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# Docker 서비스 시작
sudo systemctl start docker
sudo systemctl enable docker

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER
```

### Docker Compose 설치
```bash
# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 2. 프로젝트 배포

### 코드 다운로드
```bash
# Git 클론
git clone https://github.com/bluespak/DMS.git
cd DMS
```

### 환경 설정
```bash
# 환경 변수 파일 생성
cp .env.example .env

# .env 파일 편집 (Cafe24 환경에 맞게 수정)
nano .env
```

### Cafe24 특화 .env 설정 예시
```env
# Database Configuration
DB_ROOT_PASSWORD=cafe24_secure_root_pass
DB_NAME=dmsdb
DB_USER=dmsuser
DB_PASSWORD=cafe24_secure_db_pass
DB_PORT=3306

# Backend Configuration (Cafe24 허용 포트)
BACKEND_PORT=8080
FLASK_ENV=production
SECRET_KEY=cafe24-production-secret-key

# Frontend Configuration
FRONTEND_PORT=8081
REACT_APP_API_URL=http://your-cafe24-domain.com:8080

# Nginx Configuration
NGINX_PORT=80
```

### 방화벽 설정 (필요한 경우)
```bash
# 필요한 포트 열기
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=8081/tcp
sudo firewall-cmd --reload
```

## 3. 배포 실행

### 개발 환경 배포
```bash
chmod +x deploy.sh
./deploy.sh dev
```

### 프로덕션 환경 배포
```bash
./deploy.sh prod
```

## 4. 서비스 관리 명령어

### 서비스 상태 확인
```bash
docker-compose ps
docker-compose logs -f
```

### 서비스 재시작
```bash
docker-compose restart
```

### 서비스 중지
```bash
docker-compose down
```

### 완전 초기화 (데이터 포함)
```bash
docker-compose down -v
docker system prune -a
```

## 5. 모니터링 및 유지보수

### 로그 모니터링
```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### 리소스 사용량 확인
```bash
docker stats
```

### 백업 (데이터베이스)
```bash
# 데이터베이스 백업
docker-compose exec db mysqldump -u root -p dmsdb > backup_$(date +%Y%m%d_%H%M%S).sql
```

## 6. 트러블슈팅

### 포트 충돌 해결
```bash
# 포트 사용 확인
netstat -tulpn | grep :포트번호

# 포트 변경: .env 파일에서 포트 수정 후 재배포
```

### 권한 문제
```bash
# Docker 권한 문제
sudo chown -R $USER:$USER /path/to/DMS
```

### 메모리/디스크 부족
```bash
# 사용하지 않는 컨테이너/이미지 정리
docker system prune -a
```

## 7. SSL/HTTPS 설정 (선택사항)

### Let's Encrypt 인증서 적용
```bash
# Certbot 설치
sudo yum install -y certbot

# 인증서 발급
sudo certbot certonly --standalone -d your-domain.com

# 인증서를 nginx 볼륨에 복사
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./nginx/ssl/key.pem
```