"""
BIZ-전복_Gathered_EDA_Report.md 기반 PPT(.pptx) 발표용 덱 자동 생성 스크립트

이 스크립트는 BIZ-전복_Gathered_EDA_Report.md 보고서의 15개 시각화 차트, 
미수(Size)별 가격 구조, 3대 HS Code 유망국가 표 및 4대 특별 부록을 현대적인 16:9 와이드 슬라이드 포맷의 
PPT Presentation (.pptx) 파일로 변환 생성합니다.
"""
import os
import sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Windows 콘솔 인코딩 방어
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PPTX_OUTPUT = os.path.join(BASE_DIR, 'reports', 'BIZ_Jeonbok_Market_Entry_Deck.pptx')
IMG_DIR = os.path.join(BASE_DIR, 'images')

def create_pptx_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333) # 16:9 와이드 스크린
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Style Colors
    COLOR_PRIMARY = RGBColor(0x1F, 0x49, 0x7D) # Navy
    COLOR_ACCENT = RGBColor(0xD6, 0x27, 0x28)  # Red
    COLOR_TEXT = RGBColor(0x33, 0x33, 0x33)

    # 1. 표지 슬라이드
    slide1 = prs.slides.add_slide(blank_layout)
    bg = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_PRIMARY
    bg.line.fill.background()

    txBox = slide1.shapes.add_textbox(Inches(1), Inches(2.2), Inches(11.333), Inches(3.5))
    tf = txBox.text_frame
    tf.word_wrap = True
    
    p1 = tf.paragraphs[0]
    p1.text = "🦪 한국산 전복(Abalone) 글로벌 시장개척 전략 덱"
    p1.font.bold = True
    p1.font.size = Pt(36)
    p1.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p1.alignment = PP_ALIGN.LEFT

    p2 = tf.add_paragraph()
    p2.text = "UN Comtrade 무역 분석, 15개 차트, 미수 가격 구조 및 로컬 파트너 소싱 전략"
    p2.font.size = Pt(20)
    p2.font.color.rgb = RGBColor(0xD0, 0xE0, 0xF0)
    p2.alignment = PP_ALIGN.LEFT

    # 2. Executive Summary 슬라이드
    slide2 = prs.slides.add_slide(blank_layout)
    headerBox = slide2.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.0))
    tf = headerBox.text_frame
    p = tf.paragraphs[0]
    p.text = "📌 Executive Summary: 미수(Size)별 가격 구조"
    p.font.bold = True
    p.font.size = Pt(24)
    p.font.color.rgb = COLOR_PRIMARY

    # 표 삽입 (6열 6행)
    rows, cols = 6, 6
    left, top, width, height = Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8)
    table_shape = slide2.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table

    table_data = [
        ["품목 규격 / 미수", "마리당 중량", "주요 수출국", "평균 단가", "주요 타깃 시장", "소싱 추천 포인트"],
        ["10미 미만 (대과)", "100g 이상", "한국 완도, 호주", "$42.0 ~ $48.0", "일본 고급 일식집, 료칸", "고급 항공직송 프리미엄 오퍼"],
        ["10 ~ 12미 (중대과)", "80g ~ 100g", "한국 완도", "$36.0 ~ $40.0", "도쿄 도요스 시장 도매상사", "메인 수출 주력 미수 1차 상사"],
        ["13 ~ 15미 (중과)", "65g ~ 80g", "한국, 중국", "$30.0 ~ $34.0", "관서 레스토랑, 아시안 마트", "H-Mart, 99 Ranch 채널 공급"],
        ["15 ~ 20미 (중소과)", "50g ~ 65g", "한국, 베트남", "$24.0 ~ $28.0", "냉동 IQF 가공, 외식 체인", "해상 IQF 컨테이너 대량 공급"],
        ["20미 이상 (소과)", "50g 미만", "한국, 중국", "$18.0 ~ $22.0", "통조림 가공, HMR 가공", "통조림 FDA 승인 공장 연동"]
    ]

    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(12)
            if r_idx == 0:
                p.font.bold = True
                p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_PRIMARY
            else:
                p.font.color.rgb = COLOR_TEXT

    # 3. 15개 시각화 차트 슬라이드 15장 자동 생성
    chart_files = [
        ("01_annual_trade_trend.png", "1. 연도별 무역액 추이"),
        ("02_top_exporter_ranking.png", "2. TOP 10 주요 수출국 무역액"),
        ("03_top_importer_ranking.png", "3. TOP 10 주요 수입국 무역액"),
        ("04_unit_price_distribution.png", "4. 전복 평균 단가 ($/kg) 분포"),
        ("05_monthly_seasonality.png", "5. 월별 거래 계절성 지수"),
        ("06_hs_code_share.png", "6. HS Code별 거래액 점유율"),
        ("07_price_vs_weight_scatter.png", "7. 물량 vs 단가 상관관계 산점도"),
        ("08_top5_importer_growth.png", "8. TOP 5 수입국 연도별 성장 추이"),
        ("09_market_concentration_pareto.png", "9. 수입 시장 파레토 집중도 분석"),
        ("10_export_price_heatmap.png", "10. 주요 수입국별 연도별 평균 단가 히트맵"),
        ("11_trade_balance_waterfall.png", "11. 무역 구조 폭포수 분석"),
        ("12_country_price_boxplot.png", "12. TOP 주요 국가별 단가 변동성 박스플롯"),
        ("13_hhi_index_trend.png", "13. 시장 집중도(HHI Index) 추이"),
        ("14_size_pricing_structure.png", "14. 미수(Size) 규격별 가격 구조"),
        ("15_promising_country_matrix.png", "15. 전복 유망 국가 시장 성숙도-단가 매트릭스")
    ]

    for img_name, title_txt in chart_files:
        img_path = os.path.join(IMG_DIR, img_name)
        if os.path.exists(img_path):
            slide = prs.slides.add_slide(blank_layout)
            hb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.8))
            tf = hb.text_frame
            p = tf.paragraphs[0]
            p.text = f"📊 {title_txt}"
            p.font.bold = True
            p.font.size = Pt(24)
            p.font.color.rgb = COLOR_PRIMARY

            slide.shapes.add_picture(img_path, Inches(1.5), Inches(1.4), width=Inches(10.333))

    # 4. 4대 특별 부록 슬라이드
    slide_app = prs.slides.add_slide(blank_layout)
    hb = slide_app.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.8))
    tf = hb.text_frame
    p = tf.paragraphs[0]
    p.text = "🎁 4대 특별 부록 (1인 상사 실전 무역 영업 패키지)"
    p.font.bold = True
    p.font.size = Pt(24)
    p.font.color.rgb = COLOR_PRIMARY

    tb_app = slide_app.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
    tf_app = tb_app.text_frame
    tf_app.word_wrap = True

    appendices = [
        "1. 1인 상사 실전 B2B 오퍼서: FOB/CIF 단가, MOQ, IQF/포장 규격 스펙, HACCP/FDA 검역 승인 패키지 제공",
        "2. 해외 바이어 콜드 어프로치: 1차 Cold Pitch 이메일 ➔ 2차 LinkedIn InMail ➔ 3차 모바일/전화 협의 3단계 파이프라인",
        "3. 글로벌 수산/식품 주요 박람회: 도쿄 수산전시회(8월), 보스턴 SENA 박람회(3월), 홍콩/상하이 수산전시회 소싱 가이드",
        "4. 무역보험공사 수출안전망: L/C, T/T 결제 조건 안전책, K-SURE 단기수출보험 가입 및 화물 적하보험 온도 로깅 장치 부착"
    ]

    for item in appendices:
        p = tf_app.add_paragraph()
        p.text = item
        p.font.size = Pt(16)
        p.font.color.rgb = COLOR_TEXT
        p.space_after = Pt(18)

    prs.save(PPTX_OUTPUT)
    print(f"✅ PPT(.pptx) 슬라이드 덱 생성 완료: {PPTX_OUTPUT}")

if __name__ == "__main__":
    create_pptx_deck()
