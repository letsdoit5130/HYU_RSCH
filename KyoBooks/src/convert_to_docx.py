"""
교보문고 베스트셀러 보고서 워드 변환기

이 모듈은 수집된 KyoBooks/data/bestsellers.csv 도서 데이터를 바탕으로
종합 분석 보고서 마크다운 파일(eda_report.md)을 자동으로 작성하고,
이를 서식이 완비된 MS Word 보고서(eda_report.docx)로 변환합니다.

주요 기능:
1. Pandas를 활용하여 평균 가격, 점유율 상위 출판사, 최고/최저가 등 핵심 지표 요약
2. 동적 마크다운 보고서(eda_report.md) 생성 및 차트 이미지 임베딩 연동
3. 마크다운 마크업(헤더, 본문, 코드, 이미지, 표)을 docx 문서 객체 스타일로 정밀 매핑
4. 교보문고 시그니처 컬러(#004F2F)를 표 헤더 음영 등에 적용하여 브랜딩 구축
5. A4 표준 규격 문서 설정 및 한글 전용 폰트(맑은 고딕) 적용
"""

import os
import re
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, hex_color):
    """셀의 배경색을 지정된 16진수 색상 코드로 설정합니다."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """셀 내부 여백(패딩)을 DXA 단위로 설정합니다."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table):
    """테이블 전체 테두리를 연한 회색 실선으로 설정합니다."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        f'  <w:left w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>'
        f'  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def parse_markdown_table_row(line):
    """마크다운 테이블 행 텍스트를 파싱하여 셀 목록을 반환합니다."""
    stripped = line.strip().strip('|')
    if not stripped:
        return []
    parts = stripped.split('|')
    return [p.strip() for p in parts]

def generate_report_markdown(data_path, md_path):
    """csv 데이터를 읽고 동적으로 분석 리포트 마크다운 파일을 생성합니다."""
    df = pd.read_csv(data_path, encoding="utf-8-sig")
    
    # 지표 산출
    total_books = len(df)
    mean_price = int(df['정가'].mean())
    mean_sapr = int(df['할인가'].mean())
    mean_discount = df['할인율'].mean()
    mean_rating = df['평점'].mean()
    total_reviews = int(df['리뷰건수'].sum())
    
    top_pub = df['출판사'].value_counts().head(3)
    pub_rank_str = ", ".join([f"{pub}({count}권)" for pub, count in top_pub.items()])
    
    max_price_book = df.loc[df['정가'].idxmax()]
    min_price_book = df.loc[df['정가'].idxmin()]
    
    # 마크다운 템플릿 작성
    md_content = f"""# 교보문고 실시간 베스트셀러 종합 분석 보고서

본 보고서는 교보문고 실시간 베스트셀러 순위 데이터를 기반으로 가격대 분포, 점유율 상위 출판사, 할인율 경향 및 고객 만족도(평점 및 리뷰 수) 등을 분석한 비즈니스 요약 보고서입니다.

---

## 1. 종합 요약 지표
수집된 실시간 베스트셀러 총 {total_books}권의 요약 통계는 다음과 같습니다.

- **총 분석 도서 수**: {total_books}권
- **평균 도서 정가**: {mean_price:,}원
- **평균 도서 판매가**: {mean_sapr:,}원 (평균 할인율: {mean_discount:.1f}%)
- **평균 평점**: {mean_rating:.2f}점 / 10점 만점
- **총 고객 리뷰 수**: {total_reviews:,}건
- **상위 점유율 출판사**: {pub_rank_str}
- **최고가 도서**: {max_price_book['도서명']} ({max_price_book['정가']:,}원)
- **최저가 도서**: {min_price_book['도서명']} ({min_price_book['정가']:,}원)

---

## 2. 출판사 점유율 분석
실시간 베스트셀러에 가장 많은 도서를 등록한 출판사들의 순위와 분포 분석입니다. 상위 출판사들이 베스트셀러 목록에서 차지하는 비율이 높게 나타납니다.

![출판사 점유율 분포](../images/top_publishers.png)

### 점유율 상위 5개 출판사 실적 요약
| 순위 | 출판사명 | 도서 수 (권) | 평균 평점 |
|:---:|:---|:---:|:---:|
"""
    # 상위 5개 출판사 테이블 채우기
    top_5_pubs = df['출판사'].value_counts().head(5)
    for rank, (pub, count) in enumerate(top_5_pubs.items(), 1):
        pub_df = df[df['출판사'] == pub]
        avg_rating = pub_df['평점'].mean()
        md_content += f"| {rank} | {pub} | {count} | {avg_rating:.2f} |\n"
        
    md_content += f"""
---

## 3. 가격 분포 및 할인율 경향
도서 정가와 실제 구매가(할인가)의 비교를 통해 베스트셀러의 가격 저항선과 할인 혜택 경향을 분석합니다.

![도서 가격 분포](../images/price_distribution.png)

대부분의 베스트셀러 도서는 15,000원 ~ 20,000원 대 가격 구간에 집중되어 분포하고 있으며, 일반 도서정가제 정책의 영향으로 대부분 10%의 도서 할인이 일관되게 적용되고 있습니다. 잡지 등 특수 품목의 경우 예외 할인율이 적용되는 것을 볼 수 있습니다.

![할인율 분포](../images/discount_rates.png)

---

## 4. 도서 분야(카테고리) 및 만족도 상관관계
베스트셀러로 선정된 도서 중 어떤 장르 및 카테고리가 높은 점유율을 차지하고 있는지 워드클라우드 기반 분석 결과와, 도서 평점/리뷰 수 등 주요 지표 간의 상관관계를 탐색합니다.

![도서 분야 워드클라우드](../images/tag_wordcloud.png)

![주요 지표 상관관계 열지도](../images/correlation_heatmap.png)

상관관계 분석 결과, 가격과 할인율은 평점 및 리뷰 수와 뚜렷한 양/음의 선형적 상관관계를 보이지 않습니다. 이는 도서 구매 결정에 있어 절대적 가격이나 평점 자체보다는, 도서 고유의 인지도와 내용적 선호도가 더욱 결정적인 역할을 하고 있음을 시사합니다.
"""
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"보고서 마크다운 작성 완료: {md_path}")

def convert_md_to_docx(md_path, docx_path, image_base_dir):
    if not os.path.exists(md_path):
        print(f"오류: 마크다운 파일이 존재하지 않습니다: {md_path}")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    doc = Document()

    # 페이지 설정 (A4 표준 규격)
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

    # 본문 기본 글꼴 스타일
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Malgun Gothic'
    font.size = Pt(10)
    font.color.rgb = RGBColor(51, 51, 51)
    style.paragraph_format.line_spacing = 1.3
    style.paragraph_format.space_after = Pt(6)

    in_table = False
    table_data = []

    i = 0
    while i < len(lines):
        line = lines[i]
        line_stripped = line.strip()

        # A. 제목 파싱 (H1, H2, H3)
        if line_stripped.startswith("#"):
            # 테이블 빌드 마감 처리
            if in_table and table_data:
                build_docx_table(doc, table_data)
                in_table = False
                table_data = []

            h_match = re.match(r'^(#{1,3})\s+(.*)$', line_stripped)
            if h_match:
                level = len(h_match.group(1))
                text = h_match.group(2)
                p = doc.add_heading(level=level)
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.keep_with_next = True
                
                run = p.add_run(text)
                run.font.name = 'Malgun Gothic'
                # 제목 크기 및 컬러 매핑
                if level == 1:
                    run.font.size = Pt(18)
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(0, 79, 47) # 교보 초록
                elif level == 2:
                    run.font.size = Pt(14)
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(50, 90, 70)
                else:
                    run.font.size = Pt(11)
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(100, 100, 100)
            i += 1
            continue

        # B. 구분선 (---) 처리
        if line_stripped == "---":
            if in_table and table_data:
                build_docx_table(doc, table_data)
                in_table = False
                table_data = []
            
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run("❖   ❖   ❖")
            run.font.size = Pt(8)
            run.font.color.rgb = RGBColor(180, 180, 180)
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(12)
            i += 1
            continue

        # C. 이미지 파싱 (![라벨](경로))
        img_match = re.match(r'^!\[(.*?)\]\((.*?)\)$', line_stripped)
        if img_match:
            if in_table and table_data:
                build_docx_table(doc, table_data)
                in_table = False
                table_data = []

            img_rel_path = img_match.group(2)
            # 상대 경로를 실경로로 치환
            # ../images/top_publishers.png -> KyoBooks/images/top_publishers.png
            img_filename = os.path.basename(img_rel_path)
            img_path = os.path.join(image_base_dir, img_filename)
            
            if os.path.exists(img_path):
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(10)
                
                # 이미지 추가 (가로 폭 5.5인치 설정)
                p.add_run().add_picture(img_path, width=Inches(5.5))
                
                # 이미지 캡션 추가
                cap_p = doc.add_paragraph()
                cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                cap_run = cap_p.add_run(f"[그림] {img_match.group(1)}")
                cap_run.font.name = 'Malgun Gothic'
                cap_run.font.size = Pt(8.5)
                cap_run.font.color.rgb = RGBColor(120, 120, 120)
                cap_p.paragraph_format.space_after = Pt(12)
            else:
                print(f"경고: 이미지를 찾을 수 없어 삽입을 건너뜁니다: {img_path}")
            i += 1
            continue

        # D. 테이블 파싱
        if line_stripped.startswith("|"):
            if re.match(r'^\|[\s:-|]*\|$', line_stripped):
                i += 1
                continue
            in_table = True
            row_cells = parse_markdown_table_row(line)
            if row_cells:
                table_data.append(row_cells)
            i += 1
            continue
        else:
            if in_table:
                build_docx_table(doc, table_data)
                in_table = False
                table_data = []

        # E. 리스트 아이템 처리 (- 내용 또는 * 내용)
        list_match = re.match(r'^[-*]\s+(.*)$', line_stripped)
        if list_match:
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(3)
            # 굵은 글씨 (**) 처리 지원
            text_content = list_match.group(1)
            parse_inline_formatting(p, text_content)
            i += 1
            continue

        # F. 일반 문단
        if line_stripped:
            p = doc.add_paragraph()
            parse_inline_formatting(p, line_stripped)
        
        i += 1

    # 파일 미종료 테이블 안전 종료
    if in_table and table_data:
        build_docx_table(doc, table_data)

    doc.save(docx_path)
    print(f"MS Word 보고서 변환 및 저장 완료: {docx_path}")

def parse_inline_formatting(paragraph, text):
    """**텍스트** 같은 굵은 글씨 스타일을 인라인으로 파싱하여 문단에 추가합니다."""
    parts = re.split(r'(\*\*.*?\*\*)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        else:
            run = paragraph.add_run(part)
        run.font.name = 'Malgun Gothic'

def build_docx_table(doc, table_data):
    """수집된 테이블 2차원 리스트 데이터를 Word 표 객체로 재구성합니다."""
    if not table_data:
        return
    
    num_rows = len(table_data)
    num_cols = len(table_data[0])
    
    table = doc.add_table(rows=num_rows, cols=num_cols)
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_table_borders(table)
    
    for r_idx, row_list in enumerate(table_data):
        # 행 개수 보정
        if r_idx >= len(table.rows):
            break
        row = table.rows[r_idx]
        
        # 헤더 여부 확인
        is_header = (r_idx == 0)
        
        for c_idx, text in enumerate(row_list):
            if c_idx >= len(row.cells):
                break
            cell = row.cells[c_idx]
            cell.text = "" # 기본텍스트 초기화
            
            p = cell.paragraphs[0]
            # 헤더 가운데 정렬, 본문은 첫 열 왼쪽, 나머지 가운데 정렬
            if is_header:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 1 else WD_ALIGN_PARAGRAPH.CENTER
                
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            
            run = p.add_run(text)
            run.font.name = 'Malgun Gothic'
            run.font.size = Pt(9.5)
            
            if is_header:
                run.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                set_cell_background(cell, "004F2F") # 교보 초록색 헤더
            else:
                # 홀수 행에 가벼운 배경 음영
                if r_idx % 2 == 1:
                    set_cell_background(cell, "F9FBF9")
                    
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    data_path = os.path.join(project_dir, "data", "bestsellers.csv")
    md_path = os.path.join(project_dir, "docs", "eda_report.md")
    docx_path = os.path.join(project_dir, "docs", "eda_report.docx")
    image_base_dir = os.path.join(project_dir, "images")
    
    # 1. 마크다운 보고서 자동 생성
    generate_report_markdown(data_path, md_path)
    
    # 2. 워드 파일 변환
    convert_md_to_docx(md_path, docx_path, image_base_dir)

if __name__ == "__main__":
    main()
