"""
마크다운 마스터 보고서 및 Word 문서 데이터를 바탕으로 PDF 리포트를 자동 생성하는 스크립트.

기능:
1. reportlab 패키지를 이용하여 PDF 문서 구성
2. 제목, 주요 수치 통계표, Star Market 4개국 및 4단계 실전 프로토콜 포함
3. HaeYu_Laver_Export_Master_Market_Expansion_Report.pdf 저장
"""

import os
import sys
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.pdfgen import canvas

sys.stdout.reconfigure(encoding='utf-8')

PDF_OUTPUT_PATH = 'BIZ-laver/reports/HaeYu_Laver_Export_Master_Market_Expansion_Report.pdf'
IMAGE_DIR = 'BIZ-laver/images'

doc = SimpleDocTemplate(
    PDF_OUTPUT_PATH,
    pagesize=A4,
    rightMargin=36,
    leftMargin=36,
    topMargin=36,
    bottomMargin=36
)

styles = getSampleStyleSheet()

# 폰트 스타일 설정 (한글 폰트 미설치 시 기본 대체 적용)
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=22,
    textColor=colors.HexColor('#1A5274'),
    alignment=1,
    spaceAfter=12
)

h1_style = ParagraphStyle(
    'SectionH1',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=14,
    leading=18,
    textColor=colors.HexColor('#1A5274'),
    spaceBefore=14,
    spaceAfter=8
)

body_style = ParagraphStyle(
    'BodyDark',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    leading=14,
    textColor=colors.HexColor('#2C3E50'),
    spaceAfter=6
)

story = []

# Title
story.append(Paragraph("[Master Report] HaeYu Laver Export EDA & Market Expansion Strategy", title_style))
story.append(Paragraph("2021-2025 Global Laver Export Data Analysis for 1-Person Trading Business", ParagraphStyle('Sub', parent=body_style, alignment=1, textColor=colors.HexColor('#78909C'))))
story.append(Spacer(1, 16))

# 1. Executive Summary
story.append(Paragraph("1. Executive Summary (1-Person Trading Strategy)", h1_style))
story.append(Paragraph("<b>1. Focus on Seasoned Laver (HS 200899):</b> 2025 Avg Export Price reached $30.41/kg (+41.1% margin over Raw Laver). 69.3% of total exports are priced in the $20-$30/kg bracket.", body_style))
story.append(Paragraph("<b>2. Target Star Markets:</b> UAE (+187.5% growth, $25.06/kg), Poland (+121.2% growth, $24.01/kg), Colombia (+156.7% growth, $27.47/kg), and Turkey (+254.5% growth, $28.01/kg).", body_style))
story.append(Paragraph("<b>3. Contract Risk Strategy:</b> Apply FOB fixed-price contracts for High CV (>40%) countries (UAE/Turkey/USA), and quarterly LCL shipments for Low CV (<25%) countries (Poland/Kazakhstan).", body_style))

story.append(Spacer(1, 12))

# 2. Portfolio Matrix Chart
story.append(Paragraph("2. Global 4-Quadrant Portfolio Matrix (40 Countries)", h1_style))
img14 = os.path.join(IMAGE_DIR, '14_advanced_market_portfolio_matrix.png')
if os.path.exists(img14):
    story.append(Image(img14, width=500, height=320))

story.append(Spacer(1, 12))

# 3. Top 10 Target Markets & Partners Table
story.append(Paragraph("3. Top 10 Target Markets & Local Potential Partners", h1_style))

data = [
    ["Rank", "Country", "2025 Value", "5Y Growth", "Avg Price", "Local Potential Partners"],
    ["1", "USA", "$244.6M", "+51.7%", "$26.72/kg", "Assi Rhee Bros, H-Mart, Harvesko, Weee!"],
    ["2", "Japan", "$124.8M", "+77.6%", "$22.10/kg", "E-Mart Japan, Gyomu Super, CJ CheilJedang"],
    ["3", "Russian Fed.", "$89.2M", "+98.5%", "$24.50/kg", "X5 Retail Group, Magnit, Koros Co."],
    ["4", "China", "$58.1M", "-23.1%", "$21.80/kg", "Ole' Supermarket, Citysuper China"],
    ["5", "Canada", "$32.4M", "+57.3%", "$27.13/kg", "T&T Supermarket, PAT Mart, Galleria"],
    ["6", "Australia", "$26.1M", "+60.3%", "$27.01/kg", "Asian Inspirations, Miracle Supermarket"],
    ["7", "Poland", "$11.5M", "+121.2%", "$24.01/kg", "Kuchnie Swiata, Asian House, Allegro"],
    ["8", "UAE", "$9.4M", "+187.5%", "$25.06/kg", "Choithrams, Lulu Hypermarket, Kibsons"],
    ["9", "Kazakhstan", "$4.3M", "+296.0%", "$22.85/kg", "Magnum Cash & Carry, Shin-Line, Small"],
    ["10", "Turkey", "$2.1M", "+254.5%", "$28.01/kg", "Macrocenter, Gurme Park, Happy Center"]
]

t = Table(data, colWidths=[35, 75, 65, 65, 65, 200])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A5274')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,0), 9),
    ('BOTTOMPADDING', (0,0), (-1,0), 6),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F4F6F7')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D5D8DC')),
    ('FONTSIZE', (0,1), (-1,-1), 8),
]))

story.append(t)

story.append(Spacer(1, 14))

# 4. 4-Step Execution Protocol
story.append(Paragraph("4. 1-Person Business 4-Step Execution Protocol", h1_style))
story.append(Paragraph("<b>Step 1: High Margin Positioning:</b> Seasoned Laver Snack Pouch + Vegan/Halal Certification ($30/kg+ Retail).", body_style))
story.append(Paragraph("<b>Step 2: Buyer Outreach:</b> KOTRA Branch Office Program (Dubai/Almaty) + Free Sample Air Courier.", body_style))
story.append(Paragraph("<b>Step 3: Small-batch LCL Shipping:</b> Initial 1-2 Pallets LCL Ocean Shipping + Local Language Labeling.", body_style))
story.append(Paragraph("<b>Step 4: E-Commerce & Short-form:</b> Amazon/Noon/Allegro Listing + TikTok K-Food Short-form Campaign.", body_style))

doc.build(story)
print(f"Master PDF 파일이 {PDF_OUTPUT_PATH}에 정상 저장되었습니다.")
