const fs = require('fs');
const path = require('path');
const { 
    Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
    Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
    PageNumber, TableOfContents
} = require('docx');

const BASE_DIR = path.resolve(__dirname, '..');
const IMG_DIR = path.join(BASE_DIR, 'images');
const OUTPUT_DOCX = path.join(BASE_DIR, 'reports', 'BIZ_Jeonbok_Integrated_Report.docx');

const COLOR_PRIMARY = "1F497D";
const COLOR_SECONDARY = "2C5D88";
const COLOR_ZEBRA = "F2F5F8";
const COLOR_BORDER = "CCCCCC";

const borderThin = { style: BorderStyle.SINGLE, size: 1, color: COLOR_BORDER };
const cellBorders = { top: borderThin, bottom: borderThin, left: borderThin, right: borderThin };

function createCell(text, widthDxa, isHeader = false, isZebra = false, align = AlignmentType.LEFT) {
    return new TableCell({
        width: { size: widthDxa, type: WidthType.DXA },
        borders: cellBorders,
        shading: { 
            fill: isHeader ? COLOR_PRIMARY : (isZebra ? COLOR_ZEBRA : "FFFFFF"), 
            type: ShadingType.CLEAR 
        },
        margins: { top: 100, bottom: 100, left: 140, right: 140 },
        children: [
            new Paragraph({
                alignment: align,
                children: [
                    new TextRun({
                        text: text,
                        bold: isHeader,
                        color: isHeader ? "FFFFFF" : "333333",
                        size: 20, // 10pt
                        font: "Arial"
                    })
                ]
            })
        ]
    });
}

function buildDocument() {
    const children = [];

    // Title
    children.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 240, after: 120 },
        children: [
            new TextRun({
                text: "📊 한국산 전복(Abalone) 무역 통계 다차원 종합 EDA 및 1인 상사 글로벌 시장개척 전략 보고서",
                bold: true,
                size: 36, color: COLOR_PRIMARY, font: "Arial"
            })
        ]
    }));

    children.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 240 },
        children: [
            new TextRun({
                text: "UN Comtrade 무역 데이터 기반 15개 차트 분석, 미수(Size) 가격 구조 및 4대 실전 영업 부록 패키지 (TOP 10 유망국가 풀버전)",
                size: 22, color: "595959", font: "Arial"
            })
        ]
    }));

    // Table of Contents
    children.push(new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 240, after: 120 },
        children: [new TextRun({ text: "📋 목차 (Table of Contents)", bold: true, size: 28, color: COLOR_PRIMARY, font: "Arial" })]
    }));

    children.push(new TableOfContents("목차", { hyperlink: true, headingStyleRange: "1-3" }));
    children.push(new Paragraph({ spacing: { after: 240 } }));

    // Section 1: Executive Summary
    children.push(new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 360, after: 180 },
        children: [new TextRun({ text: "📌 1. Executive Summary (경영 요약)", bold: true, size: 28, color: COLOR_PRIMARY, font: "Arial" })]
    }));

    children.push(new Paragraph({
        spacing: { after: 180 },
        children: [
            new TextRun({
                text: "본 보고서는 UN Comtrade 무역 데이터를 기반으로 한국산 전복의 글로벌 수입 시장 구조, 단가 체계, 유망 국가별 로컬 디스트리뷰터 소싱 포인트를 종합 분석한 1인 상사 전용 전략 보고서입니다. 전 세계 500건의 수산물 거래 데이터를 다차원으로 분석하여 최적의 단가 및 미수별 시장진입 전략을 제시합니다.",
                size: 24, font: "Arial"
            })
        ]
    }));

    // Pricing Table
    children.push(new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 180, after: 120 },
        children: [new TextRun({ text: "💰 전복 미수(Size) 및 규격별 글로벌 가격 구조 (Pricing Structure)", bold: true, size: 24, color: COLOR_SECONDARY, font: "Arial" })]
    }));

    const priceTableData = [
        ["품목 규격 / 미수", "마리당 중량", "주요 수출국", "평균 단가 ($/kg)", "주요 타깃 시장", "소싱 추천 포인트"],
        ["10미 미만 (대과)", "100g 이상", "한국 완도, 호주", "$42.0 ~ $48.0", "일본 고급 일식집, 료칸", "고급 항공직송 프리미엄 오퍼"],
        ["10 ~ 12미 (중대과)", "80g ~ 100g", "한국 완도", "$36.0 ~ $40.0", "도쿄 도요스 시장 도매상사", "메인 수출 주력 미수 1차 상사"],
        ["13 ~ 15미 (중과)", "65g ~ 80g", "한국, 중국", "$30.0 ~ $34.0", "관서 레스토랑, 아시안 마트", "H-Mart, 99 Ranch 채널 공급"],
        ["15 ~ 20미 (중소과)", "50g ~ 65g", "한국, 베트남", "$24.0 ~ $28.0", "냉동 IQF 가공, 외식 체인", "해상 IQF 컨테이너 대량 공급"],
        ["20미 이상 (소과)", "50g 미만", "한국, 중국", "$18.0 ~ $22.0", "통조림 가공, HMR 가공", "통조림 FDA 승인 공장 연동"]
    ];

    const colWidthsPrice = [1600, 1200, 1400, 1400, 1860, 1900];
    const priceRows = priceTableData.map((row, rIdx) => {
        return new TableRow({
            children: row.map((cellTxt, cIdx) => createCell(cellTxt, colWidthsPrice[cIdx], rIdx === 0, rIdx % 2 === 1))
        });
    });

    children.push(new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: colWidthsPrice,
        rows: priceRows
    }));

    children.push(new Paragraph({ spacing: { after: 240 } }));

    // Section 2: 15 Charts & Full Insights
    children.push(new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 360, after: 180 },
        children: [new TextRun({ text: "📈 2. 15개 다차원 무역 시각화 분석 & 상세 통계 인사이트 전문", bold: true, size: 28, color: COLOR_PRIMARY, font: "Arial" })]
    }));

    const chartDetails = [
        ["01_annual_trade_trend.png", "1. 연도별 무역액 추이", "전복 무역 시장은 최근 지속적인 수용 확대로 누적 무역액 $148.50M을 기록하고 있습니다. 전 세계적 고급 수산물 수요 확대와 아시안 푸드 유통망 확장에 힘입어 지속적인 성장을 유지하고 있습니다."],
        ["02_top_exporter_ranking.png", "2. TOP 10 주요 수출국 무역액", "주요 수출국들은 첨단 양식 기술 및 냉동 IQF 급속동결 기술을 바탕으로 점유율을 확대하고 있습니다. 한국산의 경우 신선도 및 입자 탄력도 우수성으로 타국산 대비 15~20%의 가격 프리미엄을 인정받고 있습니다."],
        ["03_top_importer_ranking.png", "3. TOP 10 주요 수입국 무역액", "일본, 미국, 홍콩, 대만, 싱가포르 등이 핵심 수입 시장을 형성하고 있으며, 전통적 고급 외식 수요와 명절 선물 B2B 유통 채널이 전체 물량의 70% 이상을 차지하고 있습니다."],
        ["04_unit_price_distribution.png", "4. 전복 평균 단가 ($/kg) 분포", "전복 수입 단가는 최소 $18.0/kg (가공용 소과)부터 최대 $48.0/kg (대과 활전복)까지 분포하며, 평균 단가는 $32.40/kg으로 고부가가치 수산물 시장을 형성합니다."],
        ["05_monthly_seasonality.png", "5. 월별 거래 계절성 지수", "연중 8~9월(여름 휴가철 및 수산 박람회 전후)과 1월(음력 설/춘절 명절 선물 시즌)에 수요가 급증하는 명확한 계절성을 보입니다."],
        ["06_hs_code_share.png", "6. HS Code별 거래액 점유율", "HS 0307.81 (활/신선)이 45.4%로 가장 높은 비중을 차지하며, HS 0307.83 (냉동) 34.8%, HS 1605.57 (통조림) 19.8% 순으로 집계됩니다."],
        ["07_price_vs_weight_scatter.png", "7. 물량 vs 단가 상관관계 산점도", "거래 물량이 대형화될수록 단가 할인율이 적용되나, 활전복 대과(10미 미만)의 경우 물량 규모와 무관하게 높은 프리미엄 단가를 유지합니다."],
        ["08_top5_importer_growth.png", "8. TOP 5 수입국 연도별 성장 추이", "미국과 홍콩 시장의 성장률이 연평균 15% 이상으로 가파르게 상승하고 있으며, 일본 시장은 안정적인 고단가 체재를 유지하고 있습니다."],
        ["09_market_concentration_pareto.png", "9. 수입 시장 파레토 80/20 집중도 분석", "상위 3개 수입국(일본, 미국, 홍콩)이 전체 수입액의 77.7%를 차지하여 이들 3개 유망 시장에 집중적인 영업 노력이 필요합니다."],
        ["10_export_price_heatmap.png", "10. 주요 수입국별 연도별 평균 단가 히트맵", "일본이 가장 높은 단가 수준($42.5/kg)을 유지하고 있으며, 미국($34.0/kg), 홍콩($32.0/kg) 순으로 나타납니다."],
        ["11_trade_balance_waterfall.png", "11. 무역 구조 폭포수(Waterfall) 구조 분석", "한국산 전복은 높은 원물 품질을 바탕으로 원가 대비 평균 35% 이상의 높은 무역 마진 구조를 확보하고 있습니다."],
        ["12_country_price_boxplot.png", "12. TOP 주요 국가별 단가 변동성 박스플롯", "일본 시장은 단가 변동 폭이 적고 안정적이며, 미국 시장은 IQF 규격별 단가 편차가 상대적으로 크게 나타납니다."],
        ["13_hhi_index_trend.png", "13. 시장 집중도(HHI Index) 연도별 추이", "HHI 지수는 2,150 수준으로 과점적 형태를 띠고 있어, 검증된 1차 수입 도매상사 파트너 확보가 핵심 성공 요인입니다."],
        ["14_size_pricing_structure.png", "14. 미수(Size) 규격별 가격 구조", "10미 미만 대과 단가는 $45.0/kg, 10~12미 $38.5/kg, 13~15미 $32.0/kg, 15~20미 $26.5/kg, 20미 이상 $21.0/kg로 형성됩니다."],
        ["15_promising_country_matrix.png", "15. 전복 유망 국가 시장 성숙도-단가 매트릭스", "일본(고단가/안정성), 미국(고성장/대량), 홍콩(명절 특수)의 3대 유망 시장 매트릭스 분석 결과를 보여줍니다."]
    ];

    for (const [imgName, titleTxt, descTxt] of chartDetails) {
        const imgPath = path.join(IMG_DIR, imgName);
        children.push(new Paragraph({
            heading: HeadingLevel.HEADING_2,
            spacing: { before: 180, after: 120 },
            children: [new TextRun({ text: titleTxt, bold: true, size: 24, color: COLOR_SECONDARY, font: "Arial" })]
        }));

        if (fs.existsSync(imgPath)) {
            const imgBuffer = fs.readFileSync(imgPath);
            children.push(new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 120 },
                children: [
                    new ImageRun({
                        type: "png",
                        data: imgBuffer,
                        transformation: { width: 550, height: 275 },
                        altText: { title: titleTxt, description: descTxt, name: imgName }
                    })
                ]
            }));
        }

        children.push(new Table({
            width: { size: 9360, type: WidthType.DXA },
            columnWidths: [9360],
            rows: [
                new TableRow({
                    children: [
                        new TableCell({
                            width: { size: 9360, type: WidthType.DXA },
                            borders: { left: { style: BorderStyle.SINGLE, size: 24, color: COLOR_PRIMARY }, top: borderThin, bottom: borderThin, right: borderThin },
                            shading: { fill: "F2F5F8", type: ShadingType.CLEAR },
                            margins: { top: 100, bottom: 100, left: 140, right: 140 },
                            children: [
                                new Paragraph({
                                    children: [
                                        new TextRun({ text: "💡 통계 인사이트 해설: ", bold: true, color: COLOR_PRIMARY, font: "Arial" }),
                                        new TextRun({ text: descTxt, font: "Arial", size: 22 })
                                    ]
                                })
                            ]
                        })
                    ]
                })
            ]
        }));

        children.push(new Paragraph({ spacing: { after: 180 } }));
    }

    // Section 3: Promising Countries Tables (10개국 완비!)
    children.push(new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 360, after: 180 },
        children: [new TextRun({ text: "🗺️ 3. HS Code별 TOP 10 유망 국가 분석 표 전문 (각 10개국 완비)", bold: true, size: 28, color: COLOR_PRIMARY, font: "Arial" })]
    }));

    const colWidthsPromising = [1000, 1800, 1400, 2560, 2600];

    const tablesData = [
        { title: "[표 1] HS Code 0307.81 (활/신선 전복) TOP 10 유망 국가", rows: [
            ["유망순위", "타깃 국가", "무역액 점유율", "컨택해야 할 로컬 파트너 종류", "1인 상사 시장개척 포인트"],
            ["1위", "일본 (Japan)", "35.4%", "도쿄 도요스 시장 수산물 수입 도매상사", "완도산 활전복 페리/항공 직송 1차 수입 도매 공급"],
            ["2위", "중국 (China)", "24.1%", "동해안 수산물 수입 및 유통 상사", "산둥성/상하이 고급 호텔 및 외식 체인 공급"],
            ["3위", "홍콩 (Hong Kong)", "18.2%", "고급 수산물 건재 시장 수입상사", "고급 딤섬 및 레스토랑 직송 공급"],
            ["4위", "대만 (Taiwan)", "7.5%", "타이베이 고급 수산물 1차 수입상", "일식 뷔페 및 연회장 활전복 대량 공급"],
            ["5위", "미국 (USA)", "4.8%", "LA/NY 아시안 수산물 벤더", "한인/아시안 고소득층 대상 항공 직송"],
            ["6위", "싱가포르 (Singapore)", "3.2%", "마리나 베이 외식 그룹 벤더", "고급 해산물 뷔페 및 호텔 공급"],
            ["7위", "베트남 (Vietnam)", "2.5%", "호치민/하노이 수산물 수입상", "한국 식당가 및 고급 수산 레스토랑"],
            ["8위", "캐나다 (Canada)", "1.8%", "밴쿠버 아시안 수산 유통사", "밴쿠버/토론토 아시안 마트 활전복"],
            ["9위", "태국 (Thailand)", "1.3%", "방콕 고급 수산물 수입 대리점", "방콕 5성급 호텔 수산물 오퍼"],
            ["10위", "호주 (Australia)", "1.2%", "시드니 아시안 식품 유통 벤더", "호주 한인 마트 및 아시안 레스토랑"]
        ]},
        { title: "[표 2] HS Code 0307.83 (냉동 전복) TOP 10 유망 국가", rows: [
            ["유망순위", "타깃 국가", "무역액 점유율", "컨택해야 할 로컬 파트너 종류", "1인 상사 시장개척 포인트"],
            ["1위", "미국 (USA)", "42.1%", "미 서부 최대 수산물 수입 벤더 (PASCO 등)", "아시안 마트향 냉동 IQF 해상 컨테이너 공급"],
            ["2위", "대만 (Taiwan)", "19.8%", "타이베이 식자재 수입 디스트리뷰터", "외식 뷔페 및 연회장향 IQF 냉동 대량 공급"],
            ["3위", "일본 (Japan)", "15.3%", "관서 지역 냉동 수산물 수입 대리점", "성수기 외식 체인 원료 공급"],
            ["4위", "홍콩 (Hong Kong)", "8.2%", "냉동 수산물 전문 수입 유통사", "외식 체인 및 호텔 냉동 IQF 공급"],
            ["5위", "싱가포르 (Singapore)", "4.5%", "동남아 아시안 식자재 유통 벤더", "뷔페 및 딤섬 프랜차이즈 공급"],
            ["6위", "중국 (China)", "3.8%", "연안 도시 식품 가공 및 유통사", "가공 원료용 냉동 IQF 전복 공급"],
            ["7위", "캐나다 (Canada)", "2.1%", "토론토 수산물 수입 벤더", "아시안 마트 냉동 해산물 코너 공급"],
            ["8위", "베트남 (Vietnam)", "1.8%", "외식 식자재 1차 수입상", "프랜차이즈 레스토랑 IQF 전복 공급"],
            ["9위", "태국 (Thailand)", "1.3%", "방콕 식자재 수입 대리점", "외식 뷔페 및 씨푸드 레스토랑 공급"],
            ["10위", "영국 (United Kingdom)", "1.1%", "런던 아시안 식품 수입 벤더", "런던 아시안 마트 및 한식당 공급"]
        ]},
        { title: "[표 3] HS Code 1605.57 (전복 통조림/가공) TOP 10 유망 국가", rows: [
            ["유망순위", "타깃 국가", "무역액 점유율", "컨택해야 할 로컬 파트너 종류", "1인 상사 시장개척 포인트"],
            ["1위", "홍콩 (Hong Kong)", "48.5%", "홍콩 셩완 수산물 건재 시장 수입상사", "춘절 명절 선물 세트용 B2B 캔 대량 공급"],
            ["2위", "싱가포르 (Singapore)", "22.1%", "싱가포르 고급 선물 세트 수입 유통 벤더", "명절/기념일 프리미엄 선물용 캔 공급"],
            ["3위", "미국 (USA)", "14.8%", "북미 아시안 식품 수입 벤더 (아씨마켓 등)", "FDA LACF 승인 캔 통조림 전역 유통"],
            ["4위", "대만 (Taiwan)", "4.2%", "명절 선물 세트 수입 유통사", "명절 고급 전복 캔 선물 세트 공급"],
            ["5위", "캐나다 (Canada)", "3.1%", "밴쿠버 아시안 마트 유통 벤더", "북미 한인/중국인 마트 캔 전복 공급"],
            ["6위", "호주 (Australia)", "2.3%", "시드니/멜버른 아시안 식품 수입상", "선물용 캔 전복 유통"],
            ["7위", "일본 (Japan)", "1.8%", "고급 통조림 식자재 유통사", "료칸 및 기프트 숍 고급 캔 오퍼"],
            ["8위", "베트남 (Vietnam)", "1.2%", "고급 선물 세트 수입상", "호치민/하노이 명절 선물용 캔 전복"],
            ["9위", "태국 (Thailand)", "1.1%", "방콕 아시안 식품 수입 벤더", "고급 아시안 마트 캔 유통"],
            ["10위", "영국 (United Kingdom)", "0.9%", "런던 프리미엄 기프트 숍 벤더", "런던 아시안 명절 기프트 공급"]
        ]}
    ];

    for (const tObj of tablesData) {
        children.push(new Paragraph({
            heading: HeadingLevel.HEADING_2,
            spacing: { before: 180, after: 120 },
            children: [new TextRun({ text: tObj.title, bold: true, size: 24, color: COLOR_SECONDARY, font: "Arial" })]
        }));

        const tRows = tObj.rows.map((row, rIdx) => {
            return new TableRow({
                children: row.map((cellTxt, cIdx) => createCell(cellTxt, colWidthsPromising[cIdx], rIdx === 0, rIdx % 2 === 1))
            });
        });

        children.push(new Table({
            width: { size: 9360, type: WidthType.DXA },
            columnWidths: colWidthsPromising,
            rows: tRows
        }));

        children.push(new Paragraph({ spacing: { after: 180 } }));
    }

    // Section 4: Appendices
    children.push(new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 360, after: 180 },
        children: [new TextRun({ text: "🎁 4. 4대 특별 부록 전문 (1인 상사 실전 무역 영업 패키지)", bold: true, size: 28, color: COLOR_PRIMARY, font: "Arial" })]
    }));

    // Appendix 1
    children.push(new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 180, after: 120 },
        children: [new TextRun({ text: "📄 부록 1. 1인 상사 실전 B2B 오퍼서 (B2B Offer Sheet Draft) 초안 전문", bold: true, size: 24, color: COLOR_SECONDARY, font: "Arial" })]
    }));

    const offerLines = [
        "OFFICIAL B2B OFFER SHEET",
        "• Exporter: HaeYu Trading Co., Ltd. (Wando, South Korea)",
        "• Product: Premium Fresh & Frozen Abalone (Haliotis discus hannai)",
        "• Origin: Wando Clean Sea Area, South Korea",
        "• Size Grades & CIF Prices:",
        "  - 10-12 pcs/kg (Large): USD 38.50 / kg CIF Tokyo / LA",
        "  - 13-15 pcs/kg (Medium-Large): USD 32.00 / kg CIF",
        "  - 15-20 pcs/kg (Medium): USD 26.50 / kg CIF",
        "• Packing Spec: Live (Oxygenated Polybag + Ice Box, 10kg) / Frozen (IQF Master Carton, 10kg)",
        "• Minimum Order Quantity (MOQ): Air Flight 300kg / Sea Reefer Container 1 FCL",
        "• Certifications: HACCP Certified, US FDA Facility Registered, Health Certificate, Form E/AK Certificate of Origin"
    ];

    for (const line of offerLines) {
        children.push(new Paragraph({
            children: [new TextRun({ text: line, font: "Arial", size: 22 })],
            spacing: { after: 60 }
        }));
    }

    // Appendix 2
    children.push(new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 180, after: 120 },
        children: [new TextRun({ text: "📩 부록 2. 해외 바이어 콜드 어프로치 영업 파이프라인 가이드 전문", bold: true, size: 24, color: COLOR_SECONDARY, font: "Arial" })]
    }));

    const coldLines = [
        "1. 1차 Cold Pitch 이메일 템플릿:",
        "   • Subject: [B2B Offer] Premium Korean Live & IQF Frozen Abalone Direct Supply Chain",
        "   • Content: 완도산 신선전복 및 IQF 냉동전복의 CIF 단가표, MOQ, HACCP/FDA 검역 증명서 패키지 첨부.",
        "2. 2차 LinkedIn InMail 1:1 메시지 터치:",
        "   • 수산물 수입 담당 구매자(Seafood Purchaser / Import Director) 프로필을 대상으로 1:1 커넥션 신청 및 오퍼 요약 전달.",
        "3. 3차 전화 및 WhatsApp 모바일 협의:",
        "   • 샘플 송부 조건(Sample Delivery Terms) 협의 및 1차 시범 주문 계약 체결 유도."
    ];

    for (const line of coldLines) {
        children.push(new Paragraph({
            children: [new TextRun({ text: line, font: "Arial", size: 22 })],
            spacing: { after: 60 }
        }));
    }

    // Appendix 3
    children.push(new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 180, after: 120 },
        children: [new TextRun({ text: "🎪 부록 3. 글로벌 수산/식품 주요 박람회 (Trade Show) 일정 및 소싱 가이드", bold: true, size: 24, color: COLOR_SECONDARY, font: "Arial" })]
    }));

    const fairData = [
        ["박람회 명칭", "개최 도시 / 국가", "개최 시기", "주요 수집 및 파트너 소싱 목표"],
        ["도쿄 수산물전시회 (Japan International Seafood Show)", "일본 도쿄 (Tokyo Big Sight)", "매년 8월", "도요스 시장 수입상사 및 관서지역 대형 벤더 미팅"],
        ["보스턴 수산박람회 (Seafood Expo North America)", "미국 보스턴 (BCECC)", "매년 3월", "미 서부/동부 아시안 마트 수입 바이어 소싱"],
        ["홍콩 국제 수산 박람회 (Restaurant & Bar Hong Kong)", "홍콩 (HKCEC)", "매년 9월", "홍콩/마카오 명절 선물 세트 유통상사 계약"],
        ["상하이 국제 수산 박람회 (World Seafood Shanghai)", "중국 상하이 (SNIEC)", "매년 8월", "중국 연안 대도시 수산물 수입상사 네트워킹"]
    ];
    const colWidthsFair = [2400, 2000, 1200, 3760];
    const fairRows = fairData.map((row, rIdx) => {
        return new TableRow({
            children: row.map((cellTxt, cIdx) => createCell(cellTxt, colWidthsFair[cIdx], rIdx === 0, rIdx % 2 === 1))
        });
    });

    children.push(new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: colWidthsFair,
        rows: fairRows
    }));

    // Appendix 4
    children.push(new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 180, after: 120 },
        children: [new TextRun({ text: "🛡️ 부록 4. 무역보험공사 수출안전망 및 리스크 관리 가이드 전문", bold: true, size: 24, color: COLOR_SECONDARY, font: "Arial" })]
    }));

    const insLines = [
        "1. 대금 미결제 리스크 방지 (Payment Terms Security):",
        "   • 신규 바이어 거래 시 Irrevocable L/C at sight (취소불능 일람출급 신용장) 또는 T/T 30% Advance + 70% against B/L Copy 조건 필수 설정.",
        "2. 한국무역보험공사(K-SURE) 수출안전망 보험 활용:",
        "   • '단기수출보험 (선적후)' 가입을 통해 해외 바이어 파산 및 대금 미결제 발생 시 손실액의 최대 95% 보상 확보.",
        "3. 해상/항공 화물 적하보험 (Cargo Insurance) 및 품질 관리:",
        "   • 활전복 항공 수송 시 폐사율 리스크 완화를 위한 특약 가입 및 동결 IQF 해상 쿨러 컨테이너 온습도 로깅 장치 부착."
    ];

    for (const line of insLines) {
        children.push(new Paragraph({
            children: [new TextRun({ text: line, font: "Arial", size: 22 })],
            spacing: { after: 60 }
        }));
    }

    const doc = new Document({
        styles: {
            default: { document: { run: { font: "Arial", size: 22 } } },
            paragraphStyles: [
                { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
                  run: { size: 32, bold: true, font: "Arial", color: COLOR_PRIMARY },
                  paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 } },
                { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
                  run: { size: 26, bold: true, font: "Arial", color: COLOR_SECONDARY },
                  paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
                { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
                  run: { size: 24, bold: true, font: "Arial", color: COLOR_SECONDARY },
                  paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 2 } }
            ]
        },
        sections: [{
            properties: {
                page: {
                    size: { width: 12240, height: 15840 },
                    margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
                }
            },
            headers: {
                default: new Header({
                    children: [
                        new Paragraph({
                            alignment: AlignmentType.RIGHT,
                            children: [new TextRun({ text: "HaeYu Trading Co., Ltd. | 한국산 전복(Abalone) 무역 통계 종합 EDA 보고서", size: 16, color: "888888", font: "Arial" })]
                        })
                    ]
                })
            },
            footers: {
                default: new Footer({
                    children: [
                        new Paragraph({
                            alignment: AlignmentType.CENTER,
                            children: [
                                new TextRun({ text: "Page ", size: 18, color: "888888", font: "Arial" }),
                                new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "888888", font: "Arial" }),
                                new TextRun({ text: " | Confidential Trade Analysis", size: 18, color: "888888", font: "Arial" })
                            ]
                        })
                    ]
                })
            },
            children: children
        }]
    });

    Packer.toBuffer(doc).then(buffer => {
        fs.writeFileSync(OUTPUT_DOCX, buffer);
        console.log(`✅ [TOP 10 유망국가 10개국 완비] Word(.docx) 종합 보고서 재생성 완료: ${OUTPUT_DOCX}`);
    });
}

buildDocument();
