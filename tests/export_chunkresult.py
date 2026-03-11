import sqlite3
import csv
import os
from datetime import datetime
from src.database import Repository
from src.logger import get_logger

logger = get_logger(__name__)

def export_runs_to_csv(db_path: str = "data/main.db", output_dir: str = "data/export"):
    """
    DB에 적재된 변환 결과(Runs & Chunks)를 엑셀에서 보기 좋게 CSV로 추출합니다.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 파일명에 날짜와 시간을 붙여 중복 방지 (한글 깨짐 방지를 위해 utf-8-sig 사용)
    timestamp = datetime.now().strftime('%m%d_%H%M')
    file_path = os.path.join(output_dir, f"transformation_report_{timestamp}.csv")

    query = """
        SELECT 
            r.transformer_name as '트랜스포머명',
            c.run_id as '실행ID',
            c.source as '파일명',
            c.hierarchy as '계층구조',
            c.char_count as '글자수',
            c.content as '청크본문',
            r.created_at as '실행일시',
            r.finished_at as '종료일시'
        FROM wiki_chunk c
        JOIN transformation_run r ON c.run_id = r.run_id
        ORDER BY r.created_at DESC, c.id ASC
    """

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query)
            rows = cursor.fetchall()

            if not rows:
                print("⚠️ DB에 추출할 데이터가 없습니다. 먼저 Transformer를 실행해 주세요.")
                return

            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows([dict(row) for row in rows])

        print(f"✅ CSV 추출 완료!")
        print(f"📍 경로: {os.path.abspath(file_path)}")
        print(f"📊 총 {len(rows)}개의 청크가 내보내졌습니다.")

    except Exception as e:
        logger.error(f"CSV 추출 중 오류 발생: {e}")
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    # 별도로 실행할 때 호출
    export_runs_to_csv()