# DMS Security Recovery

이 문서는 침해된 MySQL 볼륨을 폐기하고 DMS 앱을 안전한 새 데이터베이스로 재구성하는 절차를 정리합니다.

## 1. 즉시 차단

서버에서 먼저 MySQL 외부 노출을 막습니다.

```bash
sudo ufw deny 3306/tcp
```

`ufw`를 사용하지 않는 서버라면 호스팅 방화벽 또는 `iptables`로 3306/TCP를 차단합니다.

## 2. 최소 증거 보존

기존 데이터를 살리지 못하더라도 침해 흔적은 보관합니다.

```bash
mkdir -p ~/incident-dms-$(date +%F)
docker logs dms_mysql > ~/incident-dms-$(date +%F)/dms_mysql.log 2>&1
docker inspect dms_mysql > ~/incident-dms-$(date +%F)/dms_mysql.inspect.json
sudo tar czf ~/incident-dms-$(date +%F)/dms_db_data.tgz -C /var/lib/docker/volumes/dms_db_data/_data .
```

## 3. 자격 증명 교체

서버의 `.env` 값을 모두 새 값으로 바꿉니다.

필수 항목:

```env
DB_ROOT_PASSWORD=<new-long-random-root-password>
DB_USER=dmsapp
DB_PASSWORD=<new-long-random-db-password>
DB_NAME=dmsdb
DB_BIND_IP=127.0.0.1
SECRET_KEY=<new-long-random-secret>
```

원칙:

- `DB_BIND_IP`는 `127.0.0.1` 유지
- 약한 기본값 사용 금지
- 기존 `elvin`, `elvinpass`, `rootpass` 폐기

## 4. 손상된 DB 폐기 후 재생성

주의: 아래 명령은 기존 DMS MySQL 데이터를 제거합니다.

```bash
docker-compose down
docker volume rm dms_db_data
docker-compose up -d dmsdata
```

초기 스키마는 `backend/database/create_schema_prod.sql`이 자동으로 적용됩니다.

## 5. 스키마 검증

```bash
docker exec dms_mysql mysql -u"$DB_USER" -p"$DB_PASSWORD" -D "$DB_NAME" -e "SHOW TABLES;"
```

정상이라면 다음 테이블이 보여야 합니다.

- `UserInfo`
- `wills`
- `recipients`
- `triggers`
- `dispatch_log`

## 6. 앱 복구

```bash
docker-compose up -d dmsback dmsfront
docker-compose ps
docker-compose logs --tail=50 dmsback
```

백엔드가 `DB_HOST=dmsdata`로 연결되고 오류 없이 기동하는지 확인합니다.

## 7. 운영 후 점검

```bash
docker exec dms_backend printenv | grep -E '^DB_|^FLASK_ENV|^SECRET_KEY'
curl -f http://127.0.0.1:5000/api/health
```

점검 항목:

- MySQL 포트가 더 이상 외부에 공개되지 않았는지 확인
- 새 비밀번호가 실제 컨테이너에 반영됐는지 확인
- 백엔드 헬스체크 성공 확인
- 필요 시 샘플 데이터가 아닌 실제 초기 운영 데이터만 다시 적재