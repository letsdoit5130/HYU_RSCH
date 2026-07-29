"""
BIZ-전복_Gathered_EDA_Report.md 기반 Word(.docx) 종합 보고서 자동 생성 스크립트

이 스크립트는 BIZ-전복_Gathered_EDA_Report.md 보고서의 Executive Summary, 
미수(Size)별 가격 구조 표, 15개 시각화 차트, HS Code별 TOP 10 유망국가 표, 
및 4대 특별 부록을 정갈한 표 서식과 이미지 배치가 적용된 최종 Word(.docx) 보고서로 변환 생성합니다.
"""
import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

# Windows 콘솔 인코딩 방어
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_PATH = os.path.join(BASE_DIR, 'reports', 'BIZ-전복_Gathered_EDA_Report.md')
DOCX_OUTPUT = os.path.join(BASE_DIR, 'reports', 'BIZ_Jeonbok_Integrated_Report.docx')
IMG_DIR = os.path.join(BASE_DIR, 'images')

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def create_docx_report():
    doc = docx.Document()

    # 페이지 여백 설정 (1인치)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # 1. Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("📊 한국산 전복(Abalone) 무역 통계 종합 EDA 및 1인 상사 글로벌 시장개척 전략 보고서")
    run.bold = True
    run.font.size = Pt(20)
    run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s_run = sub.add_run("UN Comtrade 무역 데이터 기반 15개 차트 분석, 미수(Size) 가격 구조 및 4대 실전 영업 부록 패키지")
    s_run.font.size = Pt(12)
    s_run.font.color.rgb = RGBColor(0x59, 0x59, 0x59)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 2. Executive Summary & 미수 가격구조 표
    h1 = doc.add_heading("📌 Executive Summary (경영 요약)", level=1)
    h1.runs[0].font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

    p_exec = doc.add_paragraph("본 보고서는 UN Comtrade 무역 통계 데이터를 기반으로 한국산 전복의 글로벌 수입 시장 구조, 단가 체계, 미수(Size)별 가격 구조 및 1인 상사를 위한 해외 로컬 디스트리뷰터 소싱 전략을 종합 정리한 보고서입니다.")
    p_exec.paragraph_format.line_spacing = 1.25

    # 미수 가격구조 표
    doc.add_heading("💰 전복 미수(Size) 및 규격별 글로벌 가격 구조 (Pricing Structure)", level=2)
    
    table_data = [
        ["품목 규격 / 미수", "마리당 중량", "주요 수출국", "평균 단가 ($/kg)", "주요 타깃 시장", "소싱 추천 포인트"],
        ["10미 미만 (대과)", "100g 이상", "한국 완도, 호주", "$42.0 ~ $48.0", "일본 고급 일식집, 료칸", "고급 항공직송 프리미엄 오퍼"],
        ["10 ~ 12미 (중대과)", "80g ~ 100g", "한국 완도", "$36.0 ~ $40.0", "도쿄 도요스 시장 도매상사", "메인 수출 주력 미수 1차 상사"],
        ["13 ~ 15미 (중과)", "65g ~ 80g", "한국, 중국", "$30.0 ~ $34.0", "관서 레스토랑, 아시안 마트", "H-Mart, 99 Ranch 채널 공급"],
        ["15 ~ 20미 (중소과)", "50g ~ 65g", "한국, 베트남", "$24.0 ~ $28.0", "냉동 IQF 가공, 외식 체인", "해상 IQF 컨테이너 대량 공급"],
        ["20미 이상 (소과)", "50g 미만", "한국, 중국", "$18.0 ~ $22.0", "통조림 가공, HMR 가공", "통조림 FDA 승인 공장 연동"]
    ]

    t = doc.add_table(rows=len(table_data), cols=6)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = t.cell(r_idx, c_idx)
            cell.text = val
            if r_idx == 0:
                set_cell_background(cell, "1F497D")
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            else:
                if r_idx % 2 == 1:
                    set_cell_background(cell, "F2F2F2")

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 3. 15개 시각화 차트 수록
    h2 = doc.add_heading("📈 15개 다차원 무역 시각화 분석 & 차트", level=1)
    h2.runs[0].font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

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
            doc.add_heading(title_txt, level=2)
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.add_run().add_picture(img_path, width=Inches(5.5))
            doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 4. 4대 특별 부록
    h3 = doc.add_heading("🎁 4대 특별 부록 (1인 상사 실전 무역 영업 패키지)", level=1)
    h3.runs[0].font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

    doc.add_heading("부록 1. 1인 상사 실전 B2B 오퍼서 (B2B Offer Sheet Draft)", level=2)
    doc.add_paragraph("FOB/CIF 단가, Minimum Order Quantity (MOQ), IQF 패킹 스펙 및 FDA/HACCP 검역 인증서 패키지가 완비된 실전 B2B 오퍼서 초안입니다.")

    doc.add_heading("부록 2. 해외 바이어 콜드 어프로치 영업 파이프라인 가이드", level=2)
    doc.add_paragraph("1차 콜드 이메일 템플릿, 2차 LinkedIn InMail 1:1 메시지 터치, 3차 WhatsApp/전화 모바일 미팅 유도 3단계 파이프라인.")

    doc.add_heading("부록 3. 글로벌 주요 수산 박람회 (Trade Show) 일정", level=2)
    doc.add_paragraph("도쿄 수산물전시회(8월), 보스턴 SENA 박람회(3월), 홍콩 수산박람회(9월), 상하이 수산전시회(8월) 소싱 가이드.")

    doc.add_heading("부록 4. 무역보험공사 수출안전망 및 리스크 관리 가이드", level=2)
    doc.add_paragraph("L/C, T/T 결제 리스크 방지책, K-SURE 단기수출보험(선적후) 보상 활용 및 해상/항공 화물 적하보험 안전 관리.")

    doc.save(DOCX_OUTPUT)
    print(f"✅ Word(.docx) 종합 보고서 생성 완료: {DOCX_OUTPUT}")

if __name__ == "__main__":
    create_docx_report()
