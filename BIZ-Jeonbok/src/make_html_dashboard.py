"""
BIZ-전복_Gathered_EDA_Report.md 기반 반응형 HTML5 대시보드 자동 생성 스크립트

이 스크립트는 BIZ-전복_Gathered_EDA_Report.md 보고서의 무역 분석 수치, 
미수(Size) 가격 구조 표, 15개 차트 갤러리 및 로컬 디스트리뷰터 수집 데이터를 
Chart.js 시각화 차트와 반응형 CSS Grid 그리드가 적용된 웹 대시보드 HTML 파일로 변환 생성합니다.
"""
import os
import sys

# Windows 콘솔 인코딩 방어
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_OUTPUT = os.path.join(BASE_DIR, 'reports', 'BIZ_Jeonbok_Dashboard.html')
IMG_DIR = os.path.join(BASE_DIR, 'images')

def create_html_dashboard():
    html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 한국산 전복(Abalone) 무역 통계 종합 EDA 대시보드</title>
    <!-- Google Fonts & Chart.js -->
    <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary: #1F497D;
            --accent: #D62728;
            --bg: #F8FAFC;
            --card-bg: #FFFFFF;
            --text: #1E293B;
            --text-sub: #64748B;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Pretendard', sans-serif; background-color: var(--bg); color: var(--text); padding: 30px; }
        
        .header { background: linear-gradient(135deg, #1F497D 0%, #0F2B48 100%); color: white; padding: 35px; border-radius: 16px; margin-bottom: 30px; box-shadow: 0 10px 25px rgba(31, 73, 125, 0.2); }
        .header h1 { font-size: 2rem; font-weight: 700; margin-bottom: 10px; }
        .header p { font-size: 1.05rem; opacity: 0.9; }

        .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .kpi-card { background: var(--card-bg); padding: 22px; border-radius: 14px; border: 1px solid #E2E8F0; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
        .kpi-card h3 { font-size: 0.9rem; color: var(--text-sub); margin-bottom: 8px; text-transform: uppercase; }
        .kpi-card .val { font-size: 1.8rem; font-weight: 700; color: var(--primary); }

        .section-title { font-size: 1.4rem; font-weight: 700; color: var(--primary); margin: 40px 0 20px 0; border-left: 5px solid var(--primary); padding-left: 12px; }

        .table-card { background: var(--card-bg); border-radius: 14px; border: 1px solid #E2E8F0; overflow: hidden; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        th { background: var(--primary); color: white; font-weight: 600; padding: 14px 18px; font-size: 0.95rem; }
        td { padding: 14px 18px; border-bottom: 1px solid #E2E8F0; font-size: 0.92rem; }
        tr:nth-child(even) { background-color: #F8FAFC; }
        tr:hover { background-color: #F1F5F9; }

        .chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 25px; margin-bottom: 30px; }
        .chart-card { background: var(--card-bg); padding: 20px; border-radius: 14px; border: 1px solid #E2E8F0; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
        .chart-card h4 { font-size: 1.1rem; color: var(--primary); margin-bottom: 15px; font-weight: 600; }
        .chart-card img { width: 100%; height: auto; border-radius: 8px; }

        .footer { text-align: center; color: var(--text-sub); font-size: 0.9rem; margin-top: 50px; padding-top: 20px; border-top: 1px solid #E2E8F0; }
    </style>
</head>
<body>

    <div class="header">
        <h1>📊 한국산 전복(Abalone) 무역 통계 종합 EDA 대시보드</h1>
        <p>UN Comtrade 무역 분석 데이터, 미수(Size) 가격 구조 및 글로벌 로컬 디스트리뷰터 소싱 통합 대시보드</p>
    </div>

    <!-- KPI Section -->
    <div class="kpi-grid">
        <div class="kpi-card">
            <h3>분석 레코드 수</h3>
            <div class="val">500 건</div>
        </div>
        <div class="kpi-card">
            <h3>누적 무역 시장 규모</h3>
            <div class="val">$148.50 M</div>
        </div>
        <div class="kpi-card">
            <h3>평균 수출입 단가</h3>
            <div class="val">$32.40 / kg</div>
        </div>
        <div class="kpi-card">
            <h3>최대 수입국 (일본)</h3>
            <div class="val">35.4 %</div>
        </div>
    </div>

    <!-- Pricing Structure Table -->
    <div class="section-title">💰 전복 미수(Size) 및 규격별 글로벌 가격 구조 ($/kg)</div>
    <div class="table-card">
        <table>
            <thead>
                <tr>
                    <th>품목 규격 / 미수</th>
                    <th>마리당 중량</th>
                    <th>주요 수출국</th>
                    <th>평균 단가 ($/kg)</th>
                    <th>주요 타깃 시장</th>
                    <th>1인 상사 소싱 추천 포인트</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>10미 미만 (대과)</strong></td>
                    <td>100g 이상</td>
                    <td>한국 완도, 호주</td>
                    <td><span style="color:#D62728; font-weight:bold;">$42.0 ~ $48.0</span></td>
                    <td>일본 고급 일식집, 스시야, 료칸</td>
                    <td>고급 항공직송 프리미엄 오퍼</td>
                </tr>
                <tr>
                    <td><strong>10 ~ 12미 (중대과)</strong></td>
                    <td>80g ~ 100g</td>
                    <td>한국 완도</td>
                    <td><span style="color:#D62728; font-weight:bold;">$36.0 ~ $40.0</span></td>
                    <td>도쿄 도요스 시장 도매상사</td>
                    <td>메인 수출 주력 미수 1차 상사</td>
                </tr>
                <tr>
                    <td><strong>13 ~ 15미 (중과)</strong></td>
                    <td>65g ~ 80g</td>
                    <td>한국, 중국</td>
                    <td>$30.0 ~ $34.0</td>
                    <td>관서 레스토랑, 아시안 마트</td>
                    <td>H-Mart, 99 Ranch 채널 공급</td>
                </tr>
                <tr>
                    <td><strong>15 ~ 20미 (중소과)</strong></td>
                    <td>50g ~ 65g</td>
                    <td>한국, 베트남</td>
                    <td>$24.0 ~ $28.0</td>
                    <td>냉동 IQF 가공, 외식 프랜차이즈</td>
                    <td>해상 IQF 컨테이너 대량 공급</td>
                </tr>
                <tr>
                    <td><strong>20미 이상 (소과)</strong></td>
                    <td>50g 미만</td>
                    <td>한국, 중국</td>
                    <td>$18.0 ~ $22.0</td>
                    <td>통조림 가공, HMR 파우치 가공</td>
                    <td>통조림 FDA 승인 공장 연동</td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- 15 Charts Gallery -->
    <div class="section-title">📈 15개 다차원 무역 시각화 분석 차트 갤러리</div>
    <div class="chart-grid">
        <div class="chart-card">
            <h4>1. 연도별 무역액 추이</h4>
            <img src="../images/01_annual_trade_trend.png" alt="1. 연도별 무역액 추이">
        </div>
        <div class="chart-card">
            <h4>2. TOP 10 주요 수출국 무역액</h4>
            <img src="../images/02_top_exporter_ranking.png" alt="2. TOP 10 주요 수출국">
        </div>
        <div class="chart-card">
            <h4>3. TOP 10 주요 수입국 무역액</h4>
            <img src="../images/03_top_importer_ranking.png" alt="3. TOP 10 주요 수입국">
        </div>
        <div class="chart-card">
            <h4>4. 전복 평균 단가 ($/kg) 분포</h4>
            <img src="../images/04_unit_price_distribution.png" alt="4. 단가 분포">
        </div>
        <div class="chart-card">
            <h4>5. 월별 거래 계절성 지수</h4>
            <img src="../images/05_monthly_seasonality.png" alt="5. 계절성 지수">
        </div>
        <div class="chart-card">
            <h4>6. HS Code별 거래액 점유율</h4>
            <img src="../images/06_hs_code_share.png" alt="6. HS Code 점유율">
        </div>
        <div class="chart-card">
            <h4>7. 물량 vs 단가 상관관계 산점도</h4>
            <img src="../images/07_price_vs_weight_scatter.png" alt="7. 산점도">
        </div>
        <div class="chart-card">
            <h4>8. TOP 5 수입국 연도별 성장 추이</h4>
            <img src="../images/08_top5_importer_growth.png" alt="8. 성장 추이">
        </div>
        <div class="chart-card">
            <h4>9. 수입 시장 파레토 80/20 집중도</h4>
            <img src="../images/09_market_concentration_pareto.png" alt="9. 파레토 분석">
        </div>
        <div class="chart-card">
            <h4>10. 주요 수입국 연도별 단가 히트맵</h4>
            <img src="../images/10_export_price_heatmap.png" alt="10. 히트맵">
        </div>
        <div class="chart-card">
            <h4>11. 무역 구조 폭포수 분석</h4>
            <img src="../images/11_trade_balance_waterfall.png" alt="11. 폭포수 차트">
        </div>
        <div class="chart-card">
            <h4>12. 주요 국가별 단가 박스플롯</h4>
            <img src="../images/12_country_price_boxplot.png" alt="12. 박스플롯">
        </div>
        <div class="chart-card">
            <h4>13. 시장 집중도(HHI Index) 추이</h4>
            <img src="../images/13_hhi_index_trend.png" alt="13. HHI 추이">
        </div>
        <div class="chart-card">
            <h4>14. 미수(Size) 규격별 가격 구조</h4>
            <img src="../images/14_size_pricing_structure.png" alt="14. 미수 가격구조">
        </div>
        <div class="chart-card">
            <h4>15. 유망 국가 시장 성숙도-단가 매트릭스</h4>
            <img src="../images/15_promising_country_matrix.png" alt="15. 유망국가 매트릭스">
        </div>
    </div>

    <div class="footer">
        <p>© 2026 HaeYu Trading Co., Ltd. All Rights Reserved. Generated by Antigravity Trade EDA Pipeline.</p>
    </div>

</body>
</html>
"""

    with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML 대시보드 생성 완료: {HTML_OUTPUT}")

if __name__ == "__main__":
    create_html_dashboard()
