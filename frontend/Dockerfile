# Frontend Dockerfile - Multi-stage build
# Stage 1: Build React app
FROM node:18-alpine as build

WORKDIR /app

# package.json과 package-lock.json 복사
COPY package*.json ./

# 의존성 설치 (package-lock.json 동기화 문제 해결)
RUN npm install

# 소스 코드 복사
COPY . .

# 빌드 인수
ARG REACT_APP_API_URL=http://localhost:5000
ENV REACT_APP_API_URL=$REACT_APP_API_URL

# React 앱 빌드
RUN npm run build

# Stage 2: Nginx로 정적 파일 서빙
FROM nginx:alpine

# 빌드된 파일을 nginx 디렉토리로 복사
COPY --from=build /app/build /usr/share/nginx/html

# 커스텀 nginx 설정
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 포트 노출
EXPOSE 80

# nginx 실행
CMD ["nginx", "-g", "daemon off;"]