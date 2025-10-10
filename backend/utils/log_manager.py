#!/usr/bin/env python3
"""
DMS 로그 관리 유틸리티
로그 파일 아카이브, 정리, 분석 기능 제공
"""

import os
import sys
import shutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging_config import get_system_logger

def archive_old_logs(hours_old=None):
    """오래된 로그 파일들을 archive 폴더로 이동"""
    system_logger = get_system_logger()
    logger = system_logger.get_logger()
    
    # 환경변수에서 기본값 가져오기 (기본값: 72시간)
    if hours_old is None:
        hours_old = int(os.getenv('LOG_ARCHIVE_HOURS', '72'))
    
    # 로그 디렉토리 경로
    backend_dir = Path(__file__).parent.parent
    logs_dir = backend_dir / 'logs'
    archive_dir = logs_dir / 'archive'
    
    # archive 디렉토리 생성
    archive_dir.mkdir(exist_ok=True)
    
    cutoff_date = datetime.now() - timedelta(hours=hours_old)
    moved_count = 0
    
    # 시간 표시 계산
    hours_text = f"{hours_old}시간"
    if hours_old >= 24:
        days = hours_old // 24
        remaining_hours = hours_old % 24
        if remaining_hours == 0:
            hours_text = f"{days}일"
        else:
            hours_text = f"{days}일 {remaining_hours}시간"
    
    logger.info(f"로그 아카이브 시작 - {hours_text} 이전 파일들을 이동")
    
    # 각 서브 디렉토리 확인
    for subdir in ['server', 'data', 'system']:
        subdir_path = logs_dir / subdir
        if not subdir_path.exists():
            continue
            
        # 해당 서브디렉토리의 아카이브 폴더 생성
        archive_subdir = archive_dir / subdir
        archive_subdir.mkdir(exist_ok=True)
        
        # 로그 파일들 확인
        for log_file in subdir_path.glob('*.log'):
            # 파일 수정 시간 확인
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            if file_time < cutoff_date:
                # 아카이브로 이동
                archive_file = archive_subdir / log_file.name
                shutil.move(str(log_file), str(archive_file))
                moved_count += 1
                logger.info(f"아카이브 이동: {log_file.name} -> archive/{subdir}/")
    
    logger.info(f"로그 아카이브 완료 - {moved_count}개 파일 이동")
    return moved_count

def clean_logs():
    """모든 로그 파일 삭제 (개발/테스트 용도)"""
    system_logger = get_system_logger()
    logger = system_logger.get_logger()
    
    backend_dir = Path(__file__).parent.parent
    logs_dir = backend_dir / 'logs'
    
    deleted_count = 0
    
    logger.warning("로그 파일 전체 삭제 시작")
    
    # 각 서브 디렉토리의 로그 파일들 삭제
    for subdir in ['server', 'data', 'system']:
        subdir_path = logs_dir / subdir
        if not subdir_path.exists():
            continue
            
        for log_file in subdir_path.glob('*.log'):
            log_file.unlink()
            deleted_count += 1
            logger.info(f"삭제: {log_file.name}")
    
    logger.warning(f"로그 파일 삭제 완료 - {deleted_count}개 파일 삭제")
    return deleted_count

def show_log_stats():
    """로그 파일 통계 정보 표시"""
    system_logger = get_system_logger()
    logger = system_logger.get_logger()
    
    backend_dir = Path(__file__).parent.parent
    logs_dir = backend_dir / 'logs'
    
    stats = {
        'server': {'count': 0, 'size': 0},
        'data': {'count': 0, 'size': 0},
        'system': {'count': 0, 'size': 0},
        'archive': {'count': 0, 'size': 0}
    }
    
    # 각 디렉토리 통계 수집
    for category in stats.keys():
        dir_path = logs_dir / category
        if dir_path.exists():
            for log_file in dir_path.rglob('*.log'):
                stats[category]['count'] += 1
                stats[category]['size'] += log_file.stat().st_size
    
    logger.info("로그 파일 통계 정보 조회")
    
    print("\n" + "="*60)
    print("📊 DMS 로그 파일 통계")
    print("="*60)
    
    for category, data in stats.items():
        size_mb = data['size'] / (1024 * 1024)
        print(f"{category.upper():>8}: {data['count']:>3}개 파일, {size_mb:>6.1f} MB")
    
    total_count = sum(data['count'] for data in stats.values())
    total_size = sum(data['size'] for data in stats.values()) / (1024 * 1024)
    
    print("-" * 60)
    print(f"{'총합':>8}: {total_count:>3}개 파일, {total_size:>6.1f} MB")
    print("="*60)

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='DMS 로그 관리 유틸리티')
    parser.add_argument('action', choices=['archive', 'clean', 'stats'], 
                       help='수행할 작업: archive(아카이브), clean(정리), stats(통계)')
    parser.add_argument('--hours', type=int, 
                       help='아카이브할 로그 파일의 시간 (기본: 환경변수 LOG_ARCHIVE_HOURS 또는 72시간)')
    parser.add_argument('--days', type=int, 
                       help='아카이브할 로그 파일의 일수 (시간으로 변환, --hours 우선)')
    
    args = parser.parse_args()
    
    print("🔧 DMS 로그 관리 유틸리티")
    print(f"📅 작업: {args.action}")
    
    if args.action == 'archive':
        # 시간 계산 (--hours 우선, 그 다음 --days, 마지막으로 환경변수)
        hours_old = None
        if args.hours:
            hours_old = args.hours
        elif args.days:
            hours_old = args.days * 24
        
        moved_count = archive_old_logs(hours_old)
        print(f"✅ {moved_count}개 파일을 아카이브로 이동했습니다.")
        
    elif args.action == 'clean':
        confirm = input("⚠️  모든 로그 파일을 삭제하시겠습니까? (y/N): ")
        if confirm.lower() == 'y':
            deleted_count = clean_logs()
            print(f"✅ {deleted_count}개 파일을 삭제했습니다.")
        else:
            print("❌ 작업이 취소되었습니다.")
            
    elif args.action == 'stats':
        show_log_stats()

if __name__ == '__main__':
    main()