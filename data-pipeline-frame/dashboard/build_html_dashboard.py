"""
HTML/JS 인라인 매핑 1페이저 웹 대시보드 자동 빌더 (build_html_dashboard.py)

이 프로그램은 수집된 CSV 데이터를 JSON으로 직렬화하고
CORS 우회 인라인 매핑 방식으로 HTML 1페이저 프리미엄 대시보드(docs/dashboard.html)를 자동 생성하는 모듈입니다.

작성일: 2026-07-23
"""

import os
import pandas as pd

def build_html_dashboard(csv_path: str = "data/raw_data.csv", output_html: str = "docs/dashboard.html"):
    print(f"[HTML-BUILDER] 웹 대시보드 빌드 시작 -> {output_html}")
    if not os.path.exists(csv_path):
        print(f"[HTML-BUILDER ERROR] 데이터 없음: {csv_path}")
        return
        
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    json_data = df.to_json(orient="records", force_ascii=False)
    
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>비즈니스 수집 데이터 웹 대시보드</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #f8fafc; padding: 20px; }}
        .card {{ background: #1e293b; padding: 20px; border-radius: 12px; margin-bottom: 20px; }}
        h1 {{ color: #38bdf8; }}
    </style>
</head>
<body>
    <h1>📊 비즈니스 데이터 실시간 탐색 대시보드</h1>
    <div class="card">
        <h3>수집 데이터 건수: {len(df)}건</h3>
    </div>
    <script>
        const RAW_DATA = {json_data};
        console.log("Loaded Data:", RAW_DATA);
    </script>
</body>
</html>
"""
    os.makedirs(os.path.dirname(output_html), exist_ok=True)
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[HTML-BUILDER COMPLETED] 웹 대시보드 빌드 완수: {output_html}")

if __name__ == "__main__":
    build_html_dashboard()
