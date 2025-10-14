"""
Frontend Log Routes
프론트엔드에서 전송되는 로그를 처리하는 API 엔드포인트
"""
from flask import Blueprint, request, jsonify, current_app
import os
import json
import shutil
from datetime import datetime
import threading
from utils.logging_config import get_dms_logger

def init_frontend_log_routes(app):
    """Frontend 로그 라우트 초기화"""
    
    # DMS 로깅 시스템 사용
    dms_logger = get_dms_logger()
    logger = dms_logger.get_logger()
    logger.info("Frontend 로그 라우트 초기화 시작...")
    
    # 프론트엔드 로그를 백엔드 로그 디렉토리에 저장
    frontend_logs_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'logs', 'frontend'
    )
    logger.info(f"Frontend 로그 디렉토리: {frontend_logs_dir}")
    
    # 로그 설정 (환경변수 기반)
    max_file_size_mb = int(os.getenv('FRONTEND_LOG_MAX_SIZE_MB', '20'))  # 기본 20MB
    archive_hours = int(os.getenv('FRONTEND_LOG_ARCHIVE_HOURS', '72'))   # 기본 72시간 (3일)
    
    def ensure_log_directories():
        """로그 디렉토리 생성 (archive 포함)"""
        categories = ['system', 'data', 'server', 'error']
        for category in categories:
            category_dir = os.path.join(frontend_logs_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            
            # 아카이브 디렉토리도 생성
            archive_dir = os.path.join(frontend_logs_dir, 'archive', category)
            os.makedirs(archive_dir, exist_ok=True)
    
    def auto_archive_old_logs():
        """설정된 시간 이상 된 로그 파일을 자동으로 archive 폴더로 이동"""
        try:
            import shutil
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(hours=archive_hours)
            moved_count = 0
            
            categories = ['system', 'data', 'server', 'error']
            for category in categories:
                category_dir = os.path.join(frontend_logs_dir, category)
                archive_dir = os.path.join(frontend_logs_dir, 'archive', category)
                
                if not os.path.exists(category_dir):
                    continue
                
                for log_file in os.listdir(category_dir):
                    if log_file.endswith('.log'):
                        file_path = os.path.join(category_dir, log_file)
                        try:
                            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                            
                            if file_time < cutoff_date:
                                archive_file = os.path.join(archive_dir, log_file)
                                shutil.move(file_path, archive_file)
                                moved_count += 1
                        except Exception:
                            continue
            
            if moved_count > 0:
                hours_text = f"{archive_hours}시간"
                if archive_hours >= 24:
                    days = archive_hours // 24
                    remaining_hours = archive_hours % 24
                    if remaining_hours == 0:
                        hours_text = f"{days}일"
                    else:
                        hours_text = f"{days}일 {remaining_hours}시간"
                logger.info(f"Frontend 로그 자동 아카이브 완료: {moved_count}개 파일 이동 ({hours_text} 이상 된 로그)")
                
        except Exception as e:
            logger.error(f"Frontend 로그 아카이브 실패: {str(e)}")
    
    def check_file_size_and_rotate(file_path):
        """파일 크기 확인 및 로테이션"""
        try:
            if os.path.exists(file_path):
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                if file_size_mb > max_file_size_mb:
                    # 파일을 아카이브로 이동
                    archive_category = os.path.basename(os.path.dirname(file_path))
                    archive_dir = os.path.join(frontend_logs_dir, 'archive', archive_category)
                    archive_file = os.path.join(archive_dir, f"archived_{os.path.basename(file_path)}")
                    
                    import shutil
                    shutil.move(file_path, archive_file)
                    logger.info(f"Frontend 로그 파일 크기 제한으로 아카이브: {file_path} -> {archive_file}")
                    return True
        except Exception as e:
            logger.error(f"Frontend 로그 파일 크기 확인 실패: {str(e)}")
        return False
    
    ensure_log_directories()
    auto_archive_old_logs()  # 초기화 시 자동 아카이브 실행
    
    # 로그 큐 및 처리
    log_queue = []
    processing_lock = threading.Lock()
    
def get_log_filename(category):
    """날짜 기반 로그 파일명 생성 (하루 단위)"""
    today = datetime.now().strftime('%Y%m%d')
    return f"dms_frontend_{category}_{today}.log"

def get_rotated_filename(category, sequence):
    """로테이션된 파일명 생성 (크기 초과 시)"""
    today = datetime.now().strftime('%Y%m%d')
    timestamp = datetime.now().strftime('%H%M%S')
    return f"dms_frontend_{category}_{today}_{timestamp}_part{sequence:03d}.log"
    
    def write_logs_to_file(logs_by_category):
        """로그를 파일에 비동기로 저장 (요구사항 적용: 날짜별 파일, 크기 제한)"""
        try:
            for category, logs in logs_by_category.items():
                if not logs:
                    continue
                
                # 날짜 기반 파일명 (하루 단위)
                file_name = get_log_filename(category)
                file_path = os.path.join(frontend_logs_dir, category, file_name)
                
                # 로그 내용 준비
                log_lines = []
                for log in logs:
                    timestamp = log.get('timestamp', datetime.now().isoformat())
                    level = log.get('level', 'info').upper()
                    message = log.get('message', '')
                    session_id = log.get('sessionId', '')
                    user_agent = log.get('userAgent', '')
                    url = log.get('url', '')
                    data = log.get('data', {})
                    
                    # 백엔드와 동일한 포맷 적용: 밀리초 포함
                    try:
                        if timestamp.endswith('Z'):
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        else:
                            dt = datetime.fromisoformat(timestamp)
                        formatted_timestamp = dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 밀리초까지
                    except:
                        formatted_timestamp = timestamp
                    
                    # 세션 ID에서 마지막 8자리만 추출
                    short_session_id = session_id.split('_')[-1][:8] if session_id else 'unknown'
                    
                    data_str = f" | Data: {json.dumps(data, ensure_ascii=False, separators=(',', ':'))}" if data else ""
                    url_str = f" | URL: {url}" if url else ""
                    agent_str = f" | Agent: {user_agent[:50]}..." if user_agent else ""
                    
                    # 백엔드와 동일한 로그 포맷
                    log_line = f"{formatted_timestamp} | FRONTEND | SID:{short_session_id} | {level.ljust(8)} | DMS.frontend.{category} | {message}{data_str}{url_str}{agent_str}"
                    log_lines.append(log_line)
                
                # 새로 추가될 로그 내용
                new_content = '\n'.join(log_lines) + '\n'
                
                # 파일 크기 체크 및 로테이션 처리
                if os.path.exists(file_path):
                    current_size = os.path.getsize(file_path)
                    new_content_size = len(new_content.encode('utf-8'))
                    max_size_bytes = max_file_size_mb * 1024 * 1024
                    
                    # 파일 크기가 제한을 초과할 경우 로테이션
                    if current_size + new_content_size > max_size_bytes:
                        # 로테이션 파일명 생성 (순서 번호 포함)
                        sequence = 1
                        while True:
                            rotated_filename = get_rotated_filename(category, sequence)
                            rotated_path = os.path.join(frontend_logs_dir, 'archive', category, rotated_filename)
                            if not os.path.exists(rotated_path):
                                break
                            sequence += 1
                        
                        # 현재 파일을 아카이브로 이동
                        shutil.move(file_path, rotated_path)
                        logger.info(f"Frontend 로그 파일 크기 제한으로 로테이션: {file_name} -> archive/{category}/{rotated_filename}")
                
                # 로그 파일에 저장
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(new_content)
                
                logger.info(f"Frontend 로그 {len(logs)}개를 {category}/{file_name} 파일에 저장 완료")
                
        except Exception as e:
            logger.error(f"Frontend 로그 파일 저장 실패: {str(e)}")
    
    def process_log_queue():
        """큐에 있는 로그들을 처리"""
        with processing_lock:
            if not log_queue:
                return
            
            # 카테고리별로 로그 그룹화
            logs_by_category = {}
            
            while log_queue:
                log = log_queue.pop(0)
                category = log.get('category', 'system')
                
                if category not in logs_by_category:
                    logs_by_category[category] = []
                
                logs_by_category[category].append(log)
            
            # 별도 스레드에서 파일 저장
            if logs_by_category:
                thread = threading.Thread(target=write_logs_to_file, args=(logs_by_category,))
                thread.daemon = True
                thread.start()
    
    @app.route('/api/logs/frontend', methods=['POST'])
    def receive_frontend_logs():
        """프론트엔드에서 전송된 로그를 받아서 파일에 저장"""
        logger.info("Frontend 로그 요청 수신됨")
        try:
            data = request.get_json()
            
            if not data or 'logs' not in data:
                return jsonify({
                    'success': False,
                    'error': '로그 데이터가 없습니다.'
                }), 400
            
            logs = data['logs']
            source = data.get('source', 'unknown')
            
            if not isinstance(logs, list):
                return jsonify({
                    'success': False,
                    'error': '로그는 배열 형태여야 합니다.'
                }), 400
            
            # 로그를 큐에 추가
            with processing_lock:
                log_queue.extend(logs)
            
            # 비동기로 로그 처리
            thread = threading.Thread(target=process_log_queue)
            thread.daemon = True
            thread.start()
            
            # 백엔드 로그에도 기록
            logger.info(f"Frontend에서 {len(logs)}개 로그 수신 (source: {source})")
            
            return jsonify({
                'success': True,
                'message': f'{len(logs)}개 로그 수신 완료',
                'processed': len(logs)
            })
            
        except Exception as e:
            logger.error(f"Frontend 로그 처리 실패: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'로그 처리 중 오류 발생: {str(e)}'
            }), 500
    
    @app.route('/api/logs/frontend/stats', methods=['GET'])
    def get_frontend_log_stats():
        """프론트엔드 로그 파일 통계 (아카이브 포함)"""
        try:
            stats = {
                'totalFiles': 0,
                'totalArchivedFiles': 0,
                'categories': {},
                'archiveCategories': {},
                'sizes': {},
                'archiveSizes': {},
                'latestFiles': {},
                'archiveInfo': {
                    'archiveHours': archive_hours,
                    'maxFileSizeMB': max_file_size_mb
                }
            }
            
            categories = ['system', 'data', 'server', 'error']
            
            for category in categories:
                # 현재 로그 파일들
                category_dir = os.path.join(frontend_logs_dir, category)
                
                if os.path.exists(category_dir):
                    files = [f for f in os.listdir(category_dir) if f.endswith('.log')]
                    stats['categories'][category] = len(files)
                    stats['totalFiles'] += len(files)
                    
                    total_size = 0
                    latest_file = None
                    latest_time = 0
                    
                    for file in files:
                        file_path = os.path.join(category_dir, file)
                        file_size = os.path.getsize(file_path)
                        file_mtime = os.path.getmtime(file_path)
                        
                        total_size += file_size
                        
                        if file_mtime > latest_time:
                            latest_time = file_mtime
                            latest_file = file
                    
                    stats['sizes'][category] = total_size
                    stats['latestFiles'][category] = {
                        'filename': latest_file,
                        'modified': datetime.fromtimestamp(latest_time).isoformat() if latest_file else None,
                        'sizeBytes': os.path.getsize(os.path.join(category_dir, latest_file)) if latest_file else 0
                    } if latest_file else None
                else:
                    stats['categories'][category] = 0
                    stats['sizes'][category] = 0
                
                # 아카이브 로그 파일들
                archive_dir = os.path.join(frontend_logs_dir, 'archive', category)
                
                if os.path.exists(archive_dir):
                    archive_files = [f for f in os.listdir(archive_dir) if f.endswith('.log')]
                    stats['archiveCategories'][category] = len(archive_files)
                    stats['totalArchivedFiles'] += len(archive_files)
                    
                    archive_total_size = 0
                    for file in archive_files:
                        file_path = os.path.join(archive_dir, file)
                        archive_total_size += os.path.getsize(file_path)
                    
                    stats['archiveSizes'][category] = archive_total_size
                else:
                    stats['archiveCategories'][category] = 0
                    stats['archiveSizes'][category] = 0
            
            return jsonify({
                'success': True,
                'stats': stats
            })
            
        except Exception as e:
            logger.error(f"Frontend 로그 통계 조회 실패: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'통계 조회 중 오류 발생: {str(e)}'
            }), 500
    
    @app.route('/api/logs/frontend/archive', methods=['POST'])
    def manual_archive_logs():
        """프론트엔드 로그 수동 아카이브"""
        try:
            auto_archive_old_logs()
            return jsonify({
                'success': True,
                'message': '로그 아카이브가 완료되었습니다.'
            })
        except Exception as e:
            logger.error(f"Frontend 로그 수동 아카이브 실패: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'아카이브 중 오류 발생: {str(e)}'
            }), 500
    
    logger.info("Frontend 로그 라우트 초기화 완료")
    logger.info(f"Frontend 로그 설정 - 최대 파일 크기: {max_file_size_mb}MB, 아카이브 기간: {archive_hours}시간")