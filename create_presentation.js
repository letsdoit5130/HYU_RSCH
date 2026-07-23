/**
 * YES24 베스트셀러 고도화 EDA 종합 보고서 생성 스크립트
 * 네오브루탈리즘(Neo-Brutalism) 스타일 적용 + 슬라이드별 발표자 대본(Notes) 추가
 */

const pptxgen = require("pptxgenjs");
const path = require("path");

// 프레젠테이션 인스턴스 생성
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 16:9 슬라이드 크기 (10" x 5.625")
pres.author = "전문 데이터 분석가";
pres.title = "YES24 베스트셀러 고도화 EDA 종합 보고서";

// 공통 네오브루탈리즘 테마 설정
const THEME = {
  bgYellow: "F5F500",    // 네오브루탈리즘 대표 노란색
  bgGray: "F0F0F0",      // 본문 배경 연회색
  bgWhite: "FFFFFF",     // 카드 배경 흰색
  borderBlack: "000000", // 테두리 검은색
  textBlack: "000000",   // 텍스트 검은색
  textWhite: "FFFFFF",   // 텍스트 흰색
  accentRed: "FF3B30",   // 악센트 빨강
  accentBlue: "0000FF",  // 악센트 파랑
  accentGreen: "00FF88", // 악센트 연두
  fontTitle: "Arial Black", // 제목 폰트
  fontBody: "맑은 고딕",    // 본문 폰트
  fontMono: "Courier New",  // 코드/수치 폰트
};

// 공통 그림자 헬퍼 (Pitfall 방지를 위해 매번 새 객체 생성)
function getShadow() {
  return {
    type: "outer",
    color: "000000",
    blur: 0,
    offset: 5,
    angle: 135,
    opacity: 1.0,
  };
}

// 뱃지용 공통 프레임 그리기 헬퍼
function drawSlideBase(slide, partText, titleText) {
  // 슬라이드 기본 배경색 지정 (연회색)
  slide.background = { color: THEME.bgGray };

  // 상단 헤더 프레임
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4,
    y: 0.3,
    w: 9.2,
    h: 0.65,
    fill: { color: THEME.bgWhite },
    line: { color: THEME.borderBlack, width: 2 },
    shadow: getShadow(),
  });

  // PART 뱃지 (왼쪽)
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5,
    y: 0.4,
    w: 1.1,
    h: 0.45,
    fill: { color: THEME.bgYellow },
    line: { color: THEME.borderBlack, width: 1.5 },
  });

  slide.addText(partText, {
    x: 0.5,
    y: 0.4,
    w: 1.1,
    h: 0.45,
    fontFace: THEME.fontTitle,
    fontSize: 12,
    bold: true,
    color: THEME.textBlack,
    align: "center",
    valign: "middle",
    margin: 0,
  });

  // 슬라이드 타이틀 텍스트
  slide.addText(titleText, {
    x: 1.75,
    y: 0.3,
    w: 7.7,
    h: 0.65,
    fontFace: THEME.fontBody,
    fontSize: 16,
    bold: true,
    color: THEME.textBlack,
    align: "left",
    valign: "middle",
    margin: 0,
  });

  // 하단 슬라이드 번호 및 카피라이트 영역 프레임
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4,
    y: 5.15,
    w: 9.2,
    h: 0.25,
    fill: { color: THEME.bgWhite },
    line: { color: THEME.borderBlack, width: 1.5 },
  });

  slide.addText("YES24 베스트셀러 고도화 EDA 종합 보고서 | 전문 데이터 분석가", {
    x: 0.5,
    y: 5.15,
    w: 7.0,
    h: 0.25,
    fontFace: THEME.fontBody,
    fontSize: 8,
    color: "666666",
    valign: "middle",
  });
}

// 텍스트 카드 그리기 헬퍼
function drawTextCard(slide, x, y, w, h, title, lines) {
  // 카드 배경 사각형
  slide.addShape(pres.shapes.RECTANGLE, {
    x: x,
    y: y,
    w: w,
    h: h,
    fill: { color: THEME.bgWhite },
    line: { color: THEME.borderBlack, width: 2 },
    shadow: getShadow(),
  });

  // 카드 타이틀 뱃지
  if (title) {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x + 0.15,
      y: y + 0.15,
      w: w - 0.3,
      h: 0.4,
      fill: { color: THEME.bgYellow },
      line: { color: THEME.borderBlack, width: 1.5 },
    });
    
    slide.addText(title, {
      x: x + 0.15,
      y: y + 0.15,
      w: w - 0.3,
      h: 0.4,
      fontFace: THEME.fontBody,
      fontSize: 13,
      bold: true,
      color: THEME.textBlack,
      align: "center",
      valign: "middle",
      margin: 0,
    });
  }

  // 텍스트 본문 추가
  const textY = title ? y + 0.65 : y + 0.15;
  const textH = title ? h - 0.8 : h - 0.3;

  slide.addText(lines, {
    x: x + 0.2,
    y: textY,
    w: w - 0.4,
    h: textH,
    fontFace: THEME.fontBody,
    fontSize: 11,
    color: THEME.textBlack,
    valign: "top",
    margin: 5,
  });
}

// 이미지 카드 그리기 헬퍼
function drawImageCard(slide, x, y, w, h, imgPath, title) {
  // 카드 외곽 프레임
  slide.addShape(pres.shapes.RECTANGLE, {
    x: x,
    y: y,
    w: w,
    h: h,
    fill: { color: THEME.bgWhite },
    line: { color: THEME.borderBlack, width: 2 },
    shadow: getShadow(),
  });

  // 상단 제목 뱃지 (옵션)
  let imgY = y + 0.15;
  let imgH = h - 0.3;

  if (title) {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x + 0.15,
      y: y + 0.15,
      w: w - 0.3,
      h: 0.4,
      fill: { color: THEME.bgYellow },
      line: { color: THEME.borderBlack, width: 1.5 },
    });

    slide.addText(title, {
      x: x + 0.15,
      y: y + 0.15,
      w: w - 0.3,
      h: 0.4,
      fontFace: THEME.fontBody,
      fontSize: 12,
      bold: true,
      color: THEME.textBlack,
      align: "center",
      valign: "middle",
      margin: 0,
    });
    
    imgY = y + 0.65;
    imgH = h - 0.8;
  }

  // 이미지 삽입 (안쪽 여백 고려)
  slide.addImage({
    path: imgPath,
    x: x + 0.15,
    y: imgY,
    w: w - 0.3,
    h: imgH,
    sizing: { type: "contain", w: w - 0.3, h: imgH },
  });
}


// ==========================================
// 1. SLIDE 1: 표지 (강렬한 옐로우 네오브루탈리즘)
// ==========================================
const s1 = pres.addSlide();
s1.background = { color: THEME.bgYellow };

s1.addShape(pres.shapes.RECTANGLE, {
  x: 0.5,
  y: 0.5,
  w: 9.0,
  h: 4.625,
  fill: { color: THEME.bgWhite },
  line: { color: THEME.borderBlack, width: 3 },
  shadow: getShadow(),
});

s1.addShape(pres.shapes.RECTANGLE, {
  x: 0.7,
  y: 0.7,
  w: 8.6,
  h: 0.3,
  fill: { color: "FF5722" },
  line: { color: THEME.borderBlack, width: 1.5 },
});

s1.addText("YES24 베스트셀러 고도화 EDA 종합 보고서", {
  x: 0.7,
  y: 1.3,
  w: 8.6,
  h: 1.2,
  fontFace: THEME.fontTitle,
  fontSize: 32,
  bold: true,
  color: THEME.textBlack,
  align: "center",
  valign: "middle",
  margin: 0,
});

s1.addShape(pres.shapes.RECTANGLE, {
  x: 1.2,
  y: 2.7,
  w: 7.6,
  h: 0.8,
  fill: { color: THEME.bgYellow },
  line: { color: THEME.borderBlack, width: 2 },
  shadow: { type: "outer", color: "000000", blur: 0, offset: 3, angle: 135, opacity: 1.0 },
});

s1.addText("데이터 기반 도서 시장의 구조 진단 및 출판 기획 전략 제언", {
  x: 1.3,
  y: 2.7,
  w: 7.4,
  h: 0.8,
  fontFace: THEME.fontBody,
  fontSize: 16,
  bold: true,
  color: THEME.textBlack,
  align: "center",
  valign: "middle",
  margin: 0,
});

s1.addShape(pres.shapes.RECTANGLE, {
  x: 2.5,
  y: 3.9,
  w: 5.0,
  h: 0.6,
  fill: { color: THEME.bgGray },
  line: { color: THEME.borderBlack, width: 1.5 },
});

s1.addText("발표자: 전문 데이터 분석가  |  분석일: 2026년 7월 13일", {
  x: 2.5,
  y: 3.9,
  w: 5.0,
  h: 0.6,
  fontFace: THEME.fontBody,
  fontSize: 11,
  color: THEME.textBlack,
  align: "center",
  valign: "middle",
  margin: 0,
});

s1.addNotes("안녕하십니까, 지금부터 '예스24 베스트셀러 고도화 EDA 종합 보고서' 발표를 시작하겠습니다. 본 발표는 예스24의 실제 베스트셀러 도서 데이터를 바탕으로, 어떤 출판사와 저자가 시장을 선도하고 있는지, 가격과 평점의 분포는 어떠한지, 그리고 실제 판매 성과와 리뷰의 역학관계는 어떻게 작용하는지를 정량적 데이터 분석 기법을 통해 종합 진단하는 자료입니다. 이번 분석은 단순한 통계 요약을 넘어 텍스트 분석과 다변량 상관 분석을 아울렀으며, 최종적으로는 출판 기획자가 성공적인 베스트셀러를 기획할 수 있도록 5대 성공 프레임워크를 포함한 전략적 대안까지 제시해 드리고자 합니다. 향후 데이터 기반 출판 마케팅을 전개하는 데 있어 중요한 나침반 역할을 할 수 있기를 기대하며 본격적인 목차 소개와 발표를 시작하겠습니다.");


// ==========================================
// 2. SLIDE 2: 목차 (Agenda)
// ==========================================
const s2 = pres.addSlide();
drawSlideBase(s2, "AGENDA", "전체 분석 목차");

const agendaCol1 = [
  { text: "PART 1. 데이터 기본 정보 및 품질 파악", options: { bold: true, fontSize: 13, breakLine: true } },
  { text: "  • 데이터 출처 및 주요 변수 유형 분석\n  • 상하위 샘플 데이터 및 무결성 검증\n  • 정제 후 데이터 타입 및 구조 요약\n\n", options: { fontSize: 10 } },
  { text: "PART 2. 일변량 기술통계 및 단일 변수 분석", options: { bold: true, fontSize: 13, breakLine: true } },
  { text: "  • 수치형/범주형 기초 통계량 검토\n  • 출판사/저자 진입 빈도 시각화\n  • 도서 정가/평점/판매지수 분포 특성 규명\n\n", options: { fontSize: 10 } },
  { text: "PART 3. 이변량 교차 분석 및 상관성 진단", options: { bold: true, fontSize: 13, breakLine: true } },
  { text: "  • 출판사별 평균 판매지수 교차 분석\n  • 평점-판매지수 역설 및 구간별 성과 분석\n  • 할인율 고착 현상 및 평점 분포 비교", options: { fontSize: 10 } }
];

const agendaCol2 = [
  { text: "PART 4. 다변량 및 텍스트 데이터 마이닝", options: { bold: true, fontSize: 13, breakLine: true } },
  { text: "  • 출판사-평점구간 교차 판매지수 히트맵\n  • 도서 태그 텍스트 TF-IDF 자연어 마이닝\n  • 리뷰건수-판매지수 간 비선형 플라이휠 실증\n\n", options: { fontSize: 10 } },
  { text: "PART 5. 수치형 변수 복합 상관관계 분석", options: { bold: true, fontSize: 13, breakLine: true } },
  { text: "  • 7대 수치형 변수 간 피어슨 상관계수 행렬\n  • 평점 vs 리뷰건수의 판매량 상관성 심층 검증\n\n", options: { fontSize: 10 } },
  { text: "PART 6. 데이터 기반 종합 인사이트 도출", options: { bold: true, fontSize: 13, breakLine: true } },
  { text: "  • 파레토 법칙, 만족도-구매 디커플링 분석\n  • 시대정신 키워드 및 리뷰 임계점 마케팅 공식\n\n", options: { fontSize: 10 } },
  { text: "PART 7. 전략적 제언 및 성공 프레임워크", options: { bold: true, fontSize: 13, breakLine: true } },
  { text: "  • 베스트셀러 흥행을 위한 5대 기획 프레임워크\n  • 종합 결론 및 하이브리드 출판 모델 방향성 제언", options: { fontSize: 10 } }
];

drawTextCard(s2, 0.4, 1.15, 4.4, 3.8, "기초 통계 & 교차 분석 (PART 1-3)", agendaCol1);
drawTextCard(s2, 5.2, 1.15, 4.4, 3.8, "고급 마이닝 & 인사이트 (PART 4-7)", agendaCol2);

s2.addNotes("목차는 총 7개의 세부 파트로 논리적으로 연결하여 구성했습니다. 파트 1에서는 877개 데이터셋의 형태와 전처리 이력을 말씀드리고, 파트 2에서는 개별 수치들의 분포 특성을 짚어보겠습니다. 파트 3에서는 가격이나 평점 등이 판매량에 실질적으로 미치는 이변량 영향력을 진단하며, 파트 4에서는 텍스트 마이닝을 융합하여 독자 트렌드를 추적해 보겠습니다. 파트 5에서는 다변량 피어슨 상관계수를 토대로 요인간의 상호 작용을 통계적으로 입증하고, 파트 6에서는 이 모든 데이터를 비즈니스적 시각으로 재해석한 4대 핵심 인사이트를 요약해 보고하겠습니다. 마지막 파트 7에서는 분석에서 발굴해 낸 성공 프레임워크와 결론을 내리고 질의응답을 가지겠습니다.");


// ==========================================
// 3. SLIDE 3: PART 1 - 1.1 분석 대상 데이터 소개
// ==========================================
const s3 = pres.addSlide();
drawSlideBase(s3, "PART 1", "1.1 분석 대상 데이터 소개 및 정제 기준");

const s3Text = [
  { text: "📊 분석 대상 데이터셋 개요\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 출처: YES24 활성 베스트셀러 도서 목록 전수 데이터\n", options: { bullet: true, breakLine: true } },
  { text: "  • 규모: 877행(도서 수) x 15열(도서 속성 변수)\n", options: { bullet: true, breakLine: true } },
  { text: "  • 중복 검사: 식별값(상품번호) 기준 중복 0건 (무결성 충족)\n\n", options: { bullet: true, breakLine: true } },
  { text: "🔍 주요 수치형 변수\n", options: { bold: true, fontSize: 12 } },
  { text: "  • 순위, 정가, 할인가, 할인율, 판매지수, 리뷰건수, 평점\n\n", options: { breakLine: true } },
  { text: "📝 주요 범주형 변수\n", options: { bold: true, fontSize: 12 } },
  { text: "  • 상품번호, 도서명, 부제목, 저자, 출판사, 출판일, 태그, 이미지URL", options: {} }
];

const s3SideText = [
  { text: "🛠️ 핵심 데이터 전처리 내역\n", options: { bold: true, fontSize: 13, color: THEME.accentRed } },
  { text: "  1. 텍스트형 수치 정제\n", options: { bold: true, breakLine: true } },
  { text: "     - 정가, 할인가, 리뷰건수의 쉼표(,)를 제거하여 사칙연산 가능한 정수형 타입으로 가공 완료.\n", options: { breakLine: true } },
  { text: "  2. 결측치(Null) 정밀 처리\n", options: { bold: true, breakLine: true } },
  { text: "     - 부제목 결측치(187건)는 단순 기획 속성이므로 유지.\n", options: { breakLine: true } },
  { text: "     - 평점의 결측값은 분석 오류 방지를 위해 0.0점으로 일괄 대체 완료.\n", options: { breakLine: true } },
  { text: "  3. 수치 검증\n", options: { bold: true, breakLine: true } },
  { text: "     - 할인액(정가-할인가) 및 할인율((정가-할인가)/정가) 계산 필드 수립으로 분석 다각화 기반 마련.", options: {} }
];

drawTextCard(s3, 0.4, 1.15, 4.4, 3.8, "데이터셋 기본 개요", s3Text);
drawTextCard(s3, 5.2, 1.15, 4.4, 3.8, "데이터 정제 & 전처리 기준", s3SideText);

s3.addNotes("첫 번째 파트인 데이터 기본 정보 및 품질 파악 단락입니다. 분석을 본격적으로 시작하기에 앞서 사용된 데이터가 신뢰할 수 있는지, 전처리 과정에서 어떠한 정제 작업이 수반되었는지 파악하는 것은 분석의 기본입니다. 본 파트에서는 데이터의 차원과 샘플, 그리고 결측치 분석 내용을 공유하겠습니다. 특히 중복 행 유무와 리뷰 건수, 가격 컬럼의 데이터 형식 변환 등 오류를 사전에 방지하기 위한 정제 활동에 초점을 맞추어 설명드리도록 하겠습니다. 본 데이터는 예스24에 활성화되어 있는 최신 베스트셀러 목록을 기반으로 전수 추출된 것이며, 이를 통해 가치가 높은 인사이트를 도출해 낼 준비를 마쳤습니다. 우리가 수집하여 분석한 예스24 데이터셋은 가로 877개 도서, 세로 15개의 데이터 필드로 정의되어 있습니다. 수치형 변수는 정가, 판매지수 등 구매와 가치에 직결된 지표들이며, 범주형 변수는 도서명, 저자, 출판사, 태그처럼 텍스트 맥락을 지닌 속성들입니다. 데이터를 활용하기 전 데이터 마이닝 품질을 떨어뜨릴 수 있는 중복 행 적재 문제를 전면 검사했습니다. 검사 결과, 베스트셀러 목록 내의 중복 데이터는 0건으로 확인되어 분석을 추진하는 데 매우 우수한 무결성을 만족하고 있음을 확인했습니다.");


// ==========================================
// 4. SLIDE 4: PART 1 - 1.2 데이터 상위 5개 행 샘플
// ==========================================
const s4 = pres.addSlide();
drawSlideBase(s4, "PART 1", "1.2 베스트셀러 상위 5개 도서 샘플");

drawTextCard(s4, 0.4, 1.15, 9.2, 1.0, null, [
  { text: "💡 상위권 도서 샘플 관찰 결과\n", options: { bold: true, fontSize: 12, color: THEME.accentBlue } },
  { text: "  • 부동산, 주식, 연금 등 경제적 자유 및 자산 증식을 주제로 삼는 재테크 실용서들이 상위권을 전면 장악하고 있음.\n", options: { breakLine: true } },
  { text: "  • 5위 박곰희 도서는 판매지수가 56만 점을 초과하나, 4위 독하게 돈 공부는 4,878점으로 상위권 내에서도 판매 편차가 매우 큼.", options: {} }
]);

const tableDataS4 = [
  [
    { text: "순위", options: { bold: true, fill: { color: THEME.bgYellow }, align: "center" } },
    { text: "도서명", options: { bold: true, fill: { color: THEME.bgYellow } } },
    { text: "저자", options: { bold: true, fill: { color: THEME.bgYellow } } },
    { text: "출판사", options: { bold: true, fill: { color: THEME.bgYellow } } },
    { text: "판매지수", options: { bold: true, fill: { color: THEME.bgYellow }, align: "right" } },
    { text: "평점", options: { bold: true, fill: { color: THEME.bgYellow }, align: "center" } }
  ],
  ["1", "나의 첫 번째 부동산 교과서", "송희구", "서삼독", "168,537", "9.3"],
  ["2", "부의 갈림길", "오건영", "포레스트북스", "155,631", "9.9"],
  ["3", "주식 투자를 잘한다는 것", "육과장", "노티스", "109,503", "9.8"],
  ["4", "독하게 돈 공부", "박소연", "메이븐", "4,878", "8.0"],
  ["5", "박곰희 연금 부자 수업", "박곰희", "인플루엔셜", "563,742", "9.7"]
];

s4.addTable(tableDataS4, {
  x: 0.4,
  y: 2.35,
  w: 9.2,
  h: 2.6,
  fontFace: THEME.fontBody,
  fontSize: 11,
  border: { pt: 2, color: THEME.borderBlack },
  fill: { color: THEME.bgWhite },
  colW: [0.6, 3.4, 1.2, 1.8, 1.4, 0.8]
});

s4.addNotes("데이터의 전반적인 특징을 직관적으로 이해하기 위해 최상위 베스트셀러 1위부터 5위까지의 도서 샘플을 보시겠습니다. 보시는 바와 같이 '나의 첫 번째 부동산 교과서', '부의 갈림길', '주식 투자를 잘한다는 것' 등 경제적 자유를 키워드로 삼는 실용 투자 서적들이 주를 이루고 있습니다. 특히 5위를 기록한 '박곰희 연금 부자 수업'의 경우 판매지수가 56만 점을 초과하여 압도적인 점수를 확보하고 있는 반면, 4위인 '독하게 돈 공부'는 4,800점대로 상위권 내에서도 판매지수의 편차가 상당히 격렬하게 발생하고 있음을 엿볼 수 있어, 이에 대한 심층적인 규명이 필요합니다.");


// ==========================================
// 5. SLIDE 5: PART 1 - 1.3 데이터 하위 5개 행 샘플
// ==========================================
const s5 = pres.addSlide();
drawSlideBase(s5, "PART 1", "1.3 베스트셀러 하위 5개 도서 샘플 (873위~877위)");

drawTextCard(s5, 0.4, 1.15, 9.2, 1.0, null, [
  { text: "💡 하위권 도서 샘플 관찰 결과\n", options: { bold: true, fontSize: 12, color: THEME.accentRed } },
  { text: "  • 제러미 리프킨의 '소유의 종말'과 같은 고전 명작, 혹은 대학교재나 투자기법 기계적 설명 등 전문 학술/전공서 포진.\n", options: { breakLine: true } },
  { text: "  • 판매지수는 700 ~ 4,000점 수준으로 미진하며, 리뷰가 아예 없는 평점 0.0점 도서 등 독자 관심도와 도서 다양성이 관찰됨.", options: {} }
]);

const tableDataS5 = [
  [
    { text: "순위", options: { bold: true, fill: { color: THEME.bgYellow }, align: "center" } },
    { text: "도서명", options: { bold: true, fill: { color: THEME.bgYellow } } },
    { text: "저자", options: { bold: true, fill: { color: THEME.bgYellow } } },
    { text: "출판사", options: { bold: true, fill: { color: THEME.bgYellow } } },
    { text: "판매지수", options: { bold: true, fill: { color: THEME.bgYellow }, align: "right" } },
    { text: "평점", options: { bold: true, fill: { color: THEME.bgYellow }, align: "center" } }
  ],
  ["873", "소유의 종말", "제러미 리프킨", "민음사", "1,452", "8.8"],
  ["874", "인사이더 인사이트", "이용준", "에프엔미디어", "30,120", "9.5"],
  ["875", "국제경제론", "김신행, 김태기", "법문사", "726", "0.0"],
  ["876", "엘리어트 파동이론 마스터", "글렌 닐리", "원앤원북스", "4,272", "7.4"],
  ["877", "영업의 神신 100법칙", "하야카와 마사루", "지상사", "2,553", "9.9"]
];

s5.addTable(tableDataS5, {
  x: 0.4,
  y: 2.35,
  w: 9.2,
  h: 2.6,
  fontFace: THEME.fontBody,
  fontSize: 11,
  border: { pt: 2, color: THEME.borderBlack },
  fill: { color: THEME.bgWhite },
  colW: [0.7, 3.3, 1.2, 1.8, 1.4, 0.8]
});

s5.addNotes("다음으로 가장 끝단인 873위부터 877위까지의 하위권 도서 샘플을 확인하겠습니다. 제러미 리프킨의 '소유의 종말'과 같은 고전 명작이 눈에 띄며, 대학교재나 특정 기법 중심의 전공서인 '국제경제론'이나 '엘리어트 파동이론 마스터' 등이 포진되어 있습니다. 하위권 도서의 판매지수는 주로 수천 점 대 수준에 머무르고 있으며, 평점의 경우에도 0.0점(리뷰 없음) 혹은 7~8점대 수준이 비교적 자주 발견되어 상위 흥행 도서군 대비 만족도 수치에서도 일정한 차이를 보이고 있습니다.");


// ==========================================
// 6. SLIDE 6: PART 1 - 1.4 데이터 구조 요약
// ==========================================
const s6 = pres.addSlide();
drawSlideBase(s6, "PART 1", "1.4 데이터셋 컬럼 구성 및 타입 요약");

const s6LeftText = [
  { text: "📋 데이터 컬럼 명세서\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 수치형 변수(7개)\n", options: { bold: true, breakLine: true } },
  { text: "    - 순위, 정가, 할인가, 할인율, 판매지수, 리뷰건수, 평점\n", options: { breakLine: true } },
  { text: "  • 범주형/텍스트형 변수(8개)\n", options: { bold: true, breakLine: true } },
  { text: "    - 상품번호, 도서명, 부제목, 저자, 출판사, 출판일, 태그, 이미지URL\n\n", options: { breakLine: true } },
  { text: "  • Non-Null 카운트 검사\n", options: { bold: true, breakLine: true } },
  { text: "    - 부제목을 제외한 14개 변수는 결측치가 없는 877개 전수 적재 상태를 충족함.", options: {} }
];

const s6RightText = [
  { text: "📌 분석 전 최종 검증 결과 요약\n\n", options: { bold: true, fontSize: 13, color: THEME.accentRed } },
  { text: "  ✔ 데이터 스케일링 준비 완료\n", options: { bold: true, breakLine: true } },
  { text: "    - 정가, 할인가, 할인율, 할인액이 모두 사칙연산 가능한 정량 필드로 확보됨.\n\n", options: { breakLine: true } },
  { text: "  ✔ 평점 분석 정량성 확보\n", options: { bold: true, breakLine: true } },
  { text: "    - 평점의 결측값(0.0점 처리)을 포함하여 877개 행 전체에서 기술 통계량 산출 로직에 오차 요인을 소거함.\n\n", options: { breakLine: true } },
  { text: "  ✔ 자연어 처리(TF-IDF) 기반 확립\n", options: { bold: true, breakLine: true } },
  { text: "    - '태그' 컬럼의 문자열 데이터를 바탕으로 독자의 결핍을 자연어 처리할 준비 수립.", options: {} }
];

drawTextCard(s6, 0.4, 1.15, 4.4, 3.8, "변수 구성 및 속성", s6LeftText);
drawTextCard(s6, 5.2, 1.15, 4.4, 3.8, "데이터 품질 종합 판단", s6RightText);

s6.addNotes("수집된 데이터의 각 변수 요약 테이블입니다. 데이터를 마이닝하기에 앞서 리뷰 건수의 쉼표를 제거해 정수형으로 전환했고, 정가 및 할인가도 정상적인 사칙연산이 가능하도록 가공했습니다. 또한 평점 데이터에 누적되어 있던 결측치들을 0.0점으로 일괄 대체 처리함으로써 분석의 오류를 전면 배제했습니다. 부제목의 경우 일부 도서에 한해 결측치가 관찰되나 이는 책 기획 단계의 단순 속성이므로 분석 성과에는 아무런 지장이 없음을 확인해 두었습니다.");


// ==========================================
// 7. SLIDE 7: PART 2 - 2.1 수치형 변수 전반의 기술통계량
// ==========================================
const s7 = pres.addSlide();
drawSlideBase(s7, "PART 2", "2.1 수치형 변수 기초 기술통계량 진단");

drawTextCard(s7, 0.4, 1.15, 9.2, 1.1, null, [
  { text: "📊 통계적 특징 분석 및 특이점\n", options: { bold: true, fontSize: 12, color: THEME.accentBlue } },
  { text: "  • 평균과 중앙값의 괴리: 판매지수(평균 12,219 vs 중앙값 3,546) 및 리뷰건수(평균 75.2 vs 중앙값 30.0)에서 극단적인 불균형 발생.\n", options: { breakLine: true } },
  { text: "  • 평점 쏠림: 중앙값이 9.5점에 달하고 25% 지점도 9.2점으로 나타나, 대다수 도서가 별점 고평가 상태(Left-Skewed)에 분포해 있음.", options: {} }
]);

const tableDataS7 = [
  [
    { text: "통계 지표", options: { bold: true, fill: { color: THEME.bgYellow }, align: "center" } },
    { text: "정가 (원)", options: { bold: true, fill: { color: THEME.bgYellow }, align: "right" } },
    { text: "할인가 (원)", options: { bold: true, fill: { color: THEME.bgYellow }, align: "right" } },
    { text: "할인율 (%)", options: { bold: true, fill: { color: THEME.bgYellow }, align: "right" } },
    { text: "판매지수", options: { bold: true, fill: { color: THEME.bgYellow }, align: "right" } },
    { text: "리뷰건수", options: { bold: true, fill: { color: THEME.bgYellow }, align: "right" } },
    { text: "평점", options: { bold: true, fill: { color: THEME.bgYellow }, align: "right" } }
  ],
  ["평균 (mean)", "21,830.0", "19,741.3", "9.9%", "12,219.9", "75.2", "8.6"],
  ["표준편차 (std)", "6,931.5", "6,423.1", "0.6%", "33,083.8", "157.8", "2.7"],
  ["최소값 (min)", "5,500.0", "4,950.0", "0.0%", "3.0", "0.0", "0.0"],
  ["중앙값 (50%)", "21,000.0", "18,900.0", "10.0%", "3,546.0", "30.0", "9.5"],
  ["최대값 (max)", "100,000.0", "100,000.0", "10.0%", "563,742.0", "1,896.0", "10.0"]
];

s7.addTable(tableDataS7, {
  x: 0.4,
  y: 2.45,
  w: 9.2,
  h: 2.5,
  fontFace: THEME.fontBody,
  fontSize: 10,
  border: { pt: 2, color: THEME.borderBlack },
  fill: { color: THEME.bgWhite },
  colW: [1.4, 1.3, 1.3, 1.0, 1.4, 1.4, 1.4]
});

s7.addNotes("두 번째 파트인 일변량 기술통계 및 단일 변수 분석 파트입니다. 이 단락에서는 수치형 변수들과 범주형 변수들의 기본적인 통계량을 짚어보고, 출판사, 저자의 진입 빈도와 정가, 평점, 그리고 판매지수 등 단일 변수들이 데이터셋 상에서 어떻게 고유하게 배포되고 분포해 있는지를 확인해 보겠습니다. 통계적으로 평균값과 중앙값의 괴리가 크다면 특이치나 쏠림 현상이 있다는 뜻이므로, 이를 주의 깊게 검증하면서 데이터의 기본적인 기초 분포 특징을 상세히 진단해 가도록 하겠습니다. 수치형 데이터 전반의 기술통계량 테이블입니다. 도서의 정가는 평균 약 21,830원, 중앙값 21,000원으로 나타나 대동소이하지만, 판매지수와 리뷰 건수는 극도로 다릅니다. 판매지수의 평균은 12,219점인데 반해 중앙값은 3,546점에 그치며, 표준편차는 33,000점을 초과합니다. 이는 대다수 도서는 적정 수준에서 판매되지만 극소수의 도서들이 수십만 점 이상의 지수를 올려 평균을 심하게 왜곡하고 있는 양극화 상태임을 통계적 지표로 실증해 주고 있습니다.");


// ==========================================
// 8. SLIDE 8: PART 2 - 2.2 범주형 변수 전반의 기술통계량
// ==========================================
const s8 = pres.addSlide();
drawSlideBase(s8, "PART 2", "2.2 범주형 변수 고유값 및 최빈도 속성 진단");

const s8Left = [
  { text: "📖 도서명 및 저자 다양성 분석\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 도서명 고유값: 873개\n", options: { bold: true, breakLine: true } },
  { text: "    - 877개 중 개정판/서재 시리즈 형태의 소수 중복을 제외하고 전원 단일 타이틀로 무결함.\n", options: { bold: true, breakLine: true } },
  { text: "  • 저자 고유값: 797명\n", options: { bold: true, breakLine: true } },
  { text: "    - 전체 베스트셀러 저자 중 최다 빈도 1위 저자는 경제 전문가 '오건영' 저자(5건 등록)로 확인되어 개인의 높은 브랜드 가치가 드러남.\n", options: { bold: true, breakLine: true } }
];

const s8Right = [
  { text: "🏢 출판사 및 출판 시점 집중도\n", options: { bold: true, fontSize: 13, color: THEME.accentRed } },
  { text: "  • 출판사 고유값: 316개\n", options: { bold: true, breakLine: true } },
  { text: "    - 매우 다양한 다수의 중소/강소 출판사들이 베스트셀러 진입을 시도함.\n", options: { bold: true, breakLine: true } },
  { text: "    - 최다 출판사인 '이레미디어'는 총 44건(5.02%)의 베스트셀러를 올리며 1위 점유 독점력을 과시함.\n", options: { bold: true, breakLine: true } },
  { text: "  • 최빈 등록 출판일: 2026년 6월\n", options: { bold: true, breakLine: true } },
  { text: "    - 단 한 달 동안 66건의 신간 도서가 발매 즉시 목록에 침투하여 베스트셀러의 격렬한 교체 순환 주기를 방증함.", options: {} }
];

drawTextCard(s8, 0.4, 1.15, 4.4, 3.8, "도서명 & 저자 특징", s8Left);
drawTextCard(s8, 5.2, 1.15, 4.4, 3.8, "출판사 & 출판 시즌 경향", s8Right);

s8.addNotes("범주형 변수의 통계 결과 요약입니다. 도서명 고유값은 873건으로 거의 일치하여 중복 타이틀은 없지만 개정판이 소수 중복됩니다. 저자 수는 797명이며, 경제 전문가 '오건영' 저자가 5건의 도서를 베스트셀러에 진입시켜 브랜드를 입증했습니다. 출판사의 경우 총 316개 출판사가 존재하는데, 이중 이레미디어가 44건의 베스트셀러를 확보하여 점유율 5%를 달성, 대형 기획 브랜드의 힘을 발휘했습니다. 출판일은 2026년 6월 신작이 가장 활발하게 유입되어 베스트셀러 시장의 교체 주기가 빠름을 알려줍니다.");


// ==========================================
// 9. SLIDE 9: PART 2 - 2.3 출판사 빈도수 분석
// ==========================================
const s9 = pres.addSlide();
drawSlideBase(s9, "PART 2", "2.3 출판사별 베스트셀러 등록 건수 현황");

const s9Text = [
  { text: "🏢 대형 출판 브랜드 집중 현상\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 1위 출판사: 이레미디어 (44건)\n", options: { bold: true, breakLine: true } },
  { text: "  • 공동 2위: 길벗, 김영사 (각 21건)\n", options: { bold: true, breakLine: true } },
  { text: "  • 4위: 다산북스 (19건)\n", options: { bold: true, breakLine: true } },
  { text: "  • 5위: 알에이치코리아(RHK) (18건)\n\n", options: { bold: true, breakLine: true } },
  { text: "💡 분석적 의미 도출:\n", options: { bold: true, breakLine: true } },
  { text: "  - 소수 메이저 브랜드 출판사(상위 5% 미만)가 전체 베스트셀러 목록의 10% 이상을 고정 독점하고 있음.\n", options: { breakLine: true } },
  { text: "  - 이는 풍부한 유통 자본과 기획력, 홍보 프로모션 파워를 보유한 메이저 출판 브랜드의 공고한 진입 장벽을 시사함.", options: {} }
];

drawTextCard(s9, 0.4, 1.15, 4.4, 3.8, "출판사별 등록 빈도 순위", s9Text);
drawImageCard(s9, 5.2, 1.15, 4.4, 3.8, "yes24/images/01_publisher_count.png", "상위 출판사 등록 빈도 그래프");

s9.addNotes("앞서 확인한 출판사들의 등록 빈도를 시각화한 막대 그래프입니다. 좌측의 1위인 이레미디어가 타 출판사 대비 압도적인 막대 높이를 나타내고 있으며, 길벗과 김영사, 다산북스, 알에이치코리아 등이 그 뒤를 바짝 따르고 있습니다. 상위 약 10개 내외의 메이저 브랜드 출판사들이 베스트셀러 목록 점유율의 절대다수를 가져가고 있는 구도이므로, 도서 기획 및 유통 시 이들 출판사의 선별 전략과 유통망 협업을 벤치마킹하는 것이 신규 진입 리스크를 관리하는 데 중요함을 시사합니다.");


// ==========================================
// 10. SLIDE 10: PART 2 - 2.4 저자 빈도수 분석
// ==========================================
const s10 = pres.addSlide();
drawSlideBase(s10, "PART 2", "2.4 저자별 베스트셀러 등록 건수 현황");

const s10Text = [
  { text: "✍️ 저자 브랜드 영향력 분석\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 1위 저자: 오건영 (5건)\n", options: { bold: true, breakLine: true } },
  { text: "  • 공동 2위: 라오어, 김승호, 모건 하우절, 강환국 (각 4건)\n\n", options: { bold: true, breakLine: true } },
  { text: "💡 핵심 시사점:\n", options: { bold: true, breakLine: true } },
  { text: "  - 최다 진입에 성공한 저자들은 거시경제, 미국 주식, 자산가 마인드셋 분야의 독보적 전문가 및 파워 인플루언서임.\n", options: { breakLine: true } },
  { text: "  - 대다수의 일반 저자들은 1건의 도서만을 등록했으나, 강력한 독자 팬덤을 구축한 스타 저자들이 여러 권의 서적을 중복 순위에 안착시킴.\n", options: { breakLine: true } },
  { text: "  - 초기 흥행 보증 수표로서 '저자의 독점적 브랜드 가치'가 핵심적인 영향력을 가짐.", options: {} }
];

drawTextCard(s10, 0.4, 1.15, 4.4, 3.8, "스타 저자 진입 수현황", s10Text);
drawImageCard(s10, 5.2, 1.15, 4.4, 3.8, "yes24/images/02_author_count.png", "상위 저자 등록 빈도 그래프");

s10.addNotes("저자들의 등록 빈도수를 나타낸 막대 그래프입니다. 최다 등록 저자인 오건영 님을 포함해 라오어, 김승호, 모건 하우절, 강환국 등 자산운용 및 실용 경제서 분야의 파워 라이터들이 최상단 가중치를 형성하고 있습니다. 베스트셀러 시장에 진입하는 다작 작가들의 특성상, 신작이 발간될 때마다 이들의 기존 독자 팬덤이 초기 구매를 강력히 유도하여 베스트셀러에 연쇄 진입시키는 비즈니스 구조를 구축하고 있음을 알 수 있습니다.");


// ==========================================
// 11. SLIDE 11: PART 2 - 2.5 도서 정가 수치 분포 분석
// ==========================================
const s11 = pres.addSlide();
drawSlideBase(s11, "PART 2", "2.5 베스트셀러 도서 정가 분포 진단");

const s11Text = [
  { text: "💵 도서 가격대의 고착화 영역\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 핵심 밀집 구간:\n", options: { bold: true, breakLine: true } },
  { text: "    - 정가 15,000원 ~ 25,000원 대 구간에 데이터의 80% 이상이 집중 매핑되어 있음.\n\n", options: { breakLine: true } },
  { text: "  • 특이 단가 구간:\n", options: { bold: true, breakLine: true } },
  { text: "    - 1만 원 이하의 저단가 도서나 3만 원 이상의 고단가 학술/전공 서적 영역은 급격하게 희소함.\n\n", options: { breakLine: true } },
  { text: "💡 비즈니스 기획 해석:\n", options: { bold: true, breakLine: true } },
  { text: "    - 소비자가 가볍게 지출할 수 있는 가격 심리적 한계 저항선이 형성되어 있음을 의미하며, 신규 단행본 책 설계 시 이 가격대를 타겟팅해야 가격 허들을 낮출 수 있음.", options: {} }
];

drawTextCard(s11, 0.4, 1.15, 4.4, 3.8, "정가 데이터 분포 특징", s11Text);
drawImageCard(s11, 5.2, 1.15, 4.4, 3.8, "yes24/images/03_price_distribution.png", "도서 정가 히스토그램");

s11.addNotes("베스트셀러 도서들의 정가 분포를 그린 히스토그램입니다. 그래프를 보시면 15,000원에서 25,000원 사이의 좁은 구간에 거대한 막대들이 모여 높은 밀집도를 형성하고 있는 반면, 3만 원 이상 혹은 1만 원 이하 영역은 매우 희소합니다. 독자들이 도서 한 권을 구매하기 위해 지불할 용의가 있는 심리적 상한선이 대략 2만 원대 초반에서 고착화되어 있음을 뜻하므로, 무리한 고단가 책 설계보다는 적정 규격에 맞춘 2만 원 내외의 정가 포지셔닝이 필수적입니다.");


// ==========================================
// 12. SLIDE 12: PART 2 - 2.6 도서 평점 분포 분석
// ==========================================
const s12 = pres.addSlide();
drawSlideBase(s12, "PART 2", "2.6 도서 평점 만족도 분포 진단");

const s12Text = [
  { text: "⭐ 독자 평점의 관대화 및 편향성\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 극도로 기운 분포 (Left-Skewed):\n", options: { bold: true, breakLine: true } },
  { text: "    - 평점 데이터는 9.0점 ~ 10.0점대 사이의 최우측 고평가 밀집 지역에 대다수가 누적되어 있음.\n", options: { breakLine: true } },
  { text: "    - 7.0점 이하의 냉정한 평가 점수는 매우 극소수에 불과함.\n\n", options: { breakLine: true } },
  { text: "💡 인플레이션 해석:\n", options: { bold: true, breakLine: true } },
  { text: "    - 소비자의 주관적 우호 평가 경향과 함께, 플랫폼의 포인트 지급형 리뷰 프로모션이 평점의 상향 평준화를 조장한 것으로 사료됨.\n", options: { breakLine: true } },
  { text: "    - 이로 인해 단순 '평점 점수 크기'로는 실제 책의 질적 완성도를 온전히 감별하기 힘든 데이터 편향 상태를 보임.", options: {} }
];

drawTextCard(s12, 0.4, 1.15, 4.4, 3.8, "평점 데이터 분포 특징", s12Text);
drawImageCard(s12, 5.2, 1.15, 4.4, 3.8, "yes24/images/04_rating_distribution.png", "도서 평점 히스토그램");

s12.addNotes("도서의 고객 만족도를 의미하는 평점 데이터의 분포 히스토그램입니다. 그래프가 보여주듯, 거의 대부분의 평점 데이터가 9.0에서 10.0점대 사이의 극단적인 고평점 영역에 과도하게 치우쳐(Left-Skewed) 분포하고 있습니다. 이는 베스트셀러 진입 도서들의 품질이 객관적으로 높다는 의미로도 해석되지만, 동시에 마케팅 리뷰 유도 프로모션이나 독자의 호의적인 평가 습관 등으로 인해 만족도의 척도가 상향 평준화되는 '평점 인플레이션' 현상이 작동하고 있음을 증명합니다.");


// ==========================================
// 13. SLIDE 13: PART 2 - 2.7 도서 판매지수 분포 분석
// ==========================================
const s13 = pres.addSlide();
drawSlideBase(s13, "PART 2", "2.7 도서 판매지수의 롱테일 법칙 분포");

const s13Text = [
  { text: "📈 흥행 쏠림과 파레토의 지배 법칙\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 롱테일 멱함수 분포:\n", options: { bold: true, breakLine: true } },
  { text: "    - 대다수 도서는 판매지수가 바닥선에 붙어 완만하게 꼬리를 긋지만, 1% 미만의 소수 도서가 수십만 점 이상으로 치솟아 천장을 뚫는 구조.\n\n", options: { breakLine: true } },
  { text: "  • 통계적 괴리 증명:\n", options: { bold: true, breakLine: true } },
  { text: "    - 판매지수의 평균은 12,219점이나 중앙값은 3,546점에 불과해 통계적 특이치 쏠림이 뚜렷함.\n\n", options: { breakLine: true } },
  { text: "💡 전략적 의미:\n", options: { bold: true, breakLine: true } },
  { text: "    - 베스트셀러 내에서도 흥행 양극화가 지배적이며, 소수의 메가 히트작이 출판사의 실질 이익과 유통 트래픽 대부분을 견인하는 승자독식 구조임.", options: {} }
];

drawTextCard(s13, 0.4, 1.15, 4.4, 3.8, "판매지수 롱테일 특징", s13Text);
drawImageCard(s13, 5.2, 1.15, 4.4, 3.8, "yes24/images/05_sales_index_distribution.png", "판매지수 히스토그램");

s13.addNotes("도서들의 흥행 스코어인 판매지수의 히스토그램입니다. 일반적인 가우시안 정규 분포와 달리, 왼쪽 끝에 압도적인 빈도의 막대가 서 있고 우측으로 갈수록 매우 얇고 긴 꼬리가 수십만 점 영역까지 이어집니다. 베스트셀러 내에서도 80% 이상의 일반 도서들은 수만 점 이하의 잔잔한 흥행에 머물고, 상위 5% 미만의 초흥행작만이 수십만 점 이상의 천문학적 지수를 확보하고 있는 전형적인 파레토 법칙의 지배 구조를 시각적으로 단번에 파악할 수 있습니다.");


// ==========================================
// 14. SLIDE 14: PART 3 - 3.1 출판사별 평균 판매지수 비교
// ==========================================
const s14 = pres.addSlide();
drawSlideBase(s14, "PART 3", "3.1 상위 출판사별 평균 판매지수 비교");

const s14Text = [
  { text: "🏢 다작과 흥행 파워의 괴리 (양 vs 질)\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 등록 건수 1위 이레미디어의 역설:\n", options: { bold: true, breakLine: true } },
  { text: "    - 등록 건수 자체는 44건으로 압도적이지만, 권당 '평균 판매지수'에서는 중소형 기획 출판사 및 타 대형 출판사에 비해 완만하게 수렴함.\n\n", options: { breakLine: true } },
  { text: "  • 기획형 강소 출판사의 도약:\n", options: { bold: true, breakLine: true } },
  { text: "    - 서삼독, 포레스트북스 등 재테크/투자 특화형 신흥 기획 브랜드들은 평균 판매지수에서 독보적인 질적 효율을 창출함.\n\n", options: { breakLine: true } },
  { text: "💡 마케팅 방향성:\n", options: { bold: true, breakLine: true } },
  { text: "    - 출판의 양적 물량 공세보다 단 한 편의 기획 밀도를 극대화하는 명저 전략이 이익 극대화에 효율적임을 입증함.", options: {} }
];

drawTextCard(s14, 0.4, 1.15, 4.4, 3.8, "출판사별 평균 판매량 비교", s14Text);
drawImageCard(s14, 5.2, 1.15, 4.4, 3.8, "yes24/images/06_publisher_avg_sales.png", "출판사별 평균 판매지수 그래프");

s14.addNotes("세 번째 파트인 이변량 교차 분석 및 상관성 진단 단락입니다. 앞서 보신 개별 변수의 통계량을 넘어, 이제 두 개의 서로 다른 변수들을 연계하여 그들이 판매지수에 어떤 교차 영향력을 미치고 있는지를 상세히 추적해 보겠습니다. 각 출판사가 기록한 평균 판매지수 상위 10대 현황입니다. 베스트셀러 등록 건수 1위를 달성했던 이레미디어가 평균 판매지수 기준으로는 다른 기획형 강소 출판사들에 비해 낮게 포착되고 있습니다. 이는 다수의 베스트셀러를 쏟아내 평균 지수가 완만하게 중화되는 대형 출판사와 달리, 특정 기획 출판사들이 한두 권의 메가 히트작을 초흥행시켜 평균 판매지수를 급격하게 끌어올리는 질적 특이점을 창출하고 있음을 실증합니다. 즉, 단순 다작 경쟁보다는 단 한 편의 콘텐츠 퀄리티가 훨씬 중요합니다.");


// ==========================================
// 15. SLIDE 15: PART 3 - 3.2 평점 수치와 판매지수 간의 상관성 분석
// ==========================================
const s15 = pres.addSlide();
drawSlideBase(s15, "PART 3", "3.2 평점 수치와 누적 판매지수 간의 상관성 분석");

const s15Text = [
  { text: "📉 사후 평점 및 실제 구매 유발의 디커플링\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 산점도의 비선형적 흩뿌려짐:\n", options: { bold: true, breakLine: true } },
  { text: "    - 평점 8.0점대에서 10.0점대까지 모든 영역에 걸쳐 판매지수 값이 무작위로 수직 분포를 형성하여 양자 간의 선형 비례 관계가 나타나지 않음.\n\n", options: { breakLine: true } },
  { text: "  • 통계적 인과성의 취약함:\n", options: { bold: true, breakLine: true } },
  { text: "    - 고객이 매긴 평점 만족도는 해당 도서가 흥행하고 있는 지표(판매지수)와 강력하게 정렬되어 있지 않음.\n\n", options: { breakLine: true } },
  { text: "💡 결론 및 시사점:\n", options: { bold: true, breakLine: true } },
  { text: "    - 높은 평점이 판매량을 보장하지 않으며, 구매 결정을 결정짓는 요소는 평점 외적인 마케팅/트렌드 적합성에 있음.", options: {} }
];

drawTextCard(s15, 0.4, 1.15, 4.4, 3.8, "평점 vs 판매지수 관계 분석", s15Text);
drawImageCard(s15, 5.2, 1.15, 4.4, 3.8, "yes24/images/07_rating_vs_sales.png", "평점 vs 판매지수 산점도");

s15.addNotes("평점과 판매지수의 관계를 매핑한 산점도입니다. 만약 평점이 높을수록 책이 많이 팔린다면 산점도의 점들이 우상향하는 선형 밴드를 그려야 하지만, 현재 그래프상에서는 7~9점대와 10점대 전 영역에 걸쳐 판매지수 축이 수직으로 제각각 분산되어 흩뿌려진 모습입니다. 이는 별점 평가 만족도가 도서 구매 결정을 짓는 즉각적인 방아쇠가 아님을 말해주며, 평점 크기보다 독자들의 즉각적인 결핍 욕구 자극이 판매량을 좌우한다는 시장의 디커플링 법칙을 시사합니다.");


// ==========================================
// 16. SLIDE 16: PART 3 - 3.3 평점 구간별 판매지수 현황 통계표
// ==========================================
const s16 = pres.addSlide();
drawSlideBase(s16, "PART 3", "3.3 평점 구간별 누적 판매지수 분석표");

drawTextCard(s16, 0.4, 1.15, 9.2, 1.3, null, [
  { text: "💡 평점 구간에 숨겨진 역설적 지표 규명\n", options: { bold: true, fontSize: 12, color: THEME.accentBlue } },
  { text: "  • 평점이 과도하게 완벽한 최상위 만족도 그룹(9.5점 초과, 407권)의 평균 판매지수(10,825점)는 오히려 8.0점 초과 9.5점 이하 대중적 만족도 도서군(평균 16,000점대)보다 훨씬 낮게 잡힙니다.\n", options: { breakLine: true } },
  { text: "  • 이는 아주 좁은 소수 팬덤만의 극찬을 받아 평점이 올라간 매니아용 책보다, 논란과 비판을 동반하더라도 대중적 결핍을 직격해 불티나게 팔린 베스트셀러 도서군의 볼륨이 훨씬 압도적임을 통계적으로 증명합니다.", options: {} }
]);

const tableDataS16 = [
  [
    { text: "평점 구간 분류", options: { bold: true, fill: { color: THEME.bgYellow }, align: "center" } },
    { text: "도서 건수 (권)", options: { bold: true, fill: { color: THEME.bgYellow }, align: "right" } },
    { text: "평균 판매지수 (점)", options: { bold: true, fill: { color: THEME.bgYellow }, align: "right" } },
    { text: "중앙 판매지수 (점)", options: { bold: true, fill: { color: THEME.bgYellow }, align: "right" } }
  ],
  ["8.0점 이하 (미진 및 무결)", "23", "4,959.0", "3,324.0"],
  ["8.0점 초과 ~ 9.0점 이하", "109", "16,406.8", "4,518.0"],
  ["9.0점 초과 ~ 9.5점 이하", "260", "16,610.9", "5,787.0"],
  ["9.5점 초과 (극상 호평)", "407", "10,825.0", "3,240.0"]
];

s16.addTable(tableDataS16, {
  x: 0.4,
  y: 2.65,
  w: 9.2,
  h: 2.3,
  fontFace: THEME.fontBody,
  fontSize: 10,
  border: { pt: 2, color: THEME.borderBlack },
  fill: { color: THEME.bgWhite },
  colW: [2.5, 1.7, 2.5, 2.5]
});

s16.addNotes("평점을 구간별로 묶어 판매지수를 통계적으로 비교한 교차표입니다. 수치적으로 매우 놀라운 사실이 입증됩니다. 평점이 극도로 높은 9.5점 초과 도서군(407권)의 평균 판매지수는 10,825점인 반면, 8점 초과 9.5점 이하의 대중적 평점대 도서들의 평균 판매지수가 16,000점대로 월등하게 높습니다. 이는 과도하게 호평 일색인 매니악한 도서보다, 평점은 다소 엇갈릴지라도 넓은 대중적 소구력을 바탕으로 강력한 노출과 논란을 동반한 대중 도서들이 실질적 매출 성과에서 우위를 점한다는 역설을 명백히 실증합니다.");


// ==========================================
// 17. SLIDE 17: PART 3 - 3.4 할인율 적용 현황 및 평점 분포 분석
// ==========================================
const s17 = pres.addSlide();
drawSlideBase(s17, "PART 3", "3.4 도서 할인율 적용 수준과 평점의 연계성");

const s17Text = [
  { text: "⚖️ 가격 제도의 속박과 단일화\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 도서정가제의 단일 점 분포:\n", options: { bold: true, breakLine: true } },
  { text: "    - 산점도상에서 데이터 포인트의 95% 이상이 할인율 '10%' 단일 세로 눈금선 상에 집중 적재되어 있음.\n\n", options: { breakLine: true } },
  { text: "  • 가격 마케팅의 무력화:\n", options: { bold: true, breakLine: true } },
  { text: "    - 법적 가격 규제 한계로 인해, 할인율 격차를 무기로 고객의 사후 만족도(평점)를 촉발하거나 마케팅에 변주를 주는 전략이 전면 봉쇄되어 있음을 입증.\n\n", options: { breakLine: true } },
  { text: "💡 출판 기획자 전략 변화:\n", options: { bold: true, breakLine: true } },
  { text: "    - 가격 혜택이 불가하므로, 사은품 번들, 저자 인강 패키지 등 무형의 부가 가치를 키워 체감 혜택을 다각화해야 함.", options: {} }
];

drawTextCard(s17, 0.4, 1.15, 4.4, 3.8, "할인율 규제와 마케팅 한계", s17Text);
drawImageCard(s17, 5.2, 1.15, 4.4, 3.8, "yes24/images/08_discount_vs_rating.png", "할인율 vs 평점 분포도");

s17.addNotes("도서의 가격 할인율과 독자 평점 간의 산점도 분석입니다. 윈도우상에서 생성된 점의 분포를 보시면, 거의 모든 포인트가 가로 축 '10%' 단일 눈금선상에 세로로 길게 조밀하게 배열되어 있음을 알 수 있습니다. 이는 국내 출판 유통망의 도서정가제라는 법적 테두리 하에서 가격 마케팅 수단이 완전히 균일화되어 고착되어 있음을 보여줍니다. 가격 혜택이 불가하므로, 사은품 번들, 저자 인강 패키지 등 무형의 부가 가치를 키워 체감 혜택을 다각화해야 합니다.");


// ==========================================
// 18. SLIDE 18: PART 3 - 3.5 주요 5대 출판사의 평점 분포도 비교
// ==========================================
const s18 = pres.addSlide();
drawSlideBase(s18, "PART 3", "3.5 상위 5대 대형 출판사의 도서 평점 비교");

const s18Text = [
  { text: "🏢 메이저 출판사별 도서 품질 통제\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 박스 플롯 분포의 균일성:\n", options: { bold: true, breakLine: true } },
  { text: "    - 이레미디어, 길벗, 김영사, 다산북스, 알에이치코리아의 평점 중앙값이 모두 9.2 ~ 9.5점대 좁은 밴드에 안착되어 있음.\n\n", options: { breakLine: true } },
  { text: "  • 브랜드 신뢰도와 품질 통제:\n", options: { bold: true, breakLine: true } },
  { text: "    - 출판사 규모에 상관없이 검수, 편집, 홍보에 이르기까지 도서 발매 품질을 제어하는 마케팅 품질 통제 시스템이 업계 표준으로 완벽히 자리 잡았음을 시사함.\n\n", options: { breakLine: true } },
  { text: "💡 분석적 인사이트:\n", options: { bold: true, breakLine: true } },
  { text: "    - 상위 출판 브랜드 간의 기초 도서 품질(평점) 격차는 거의 없으므로, 차별화 핵심 요인은 유통망과 참신한 기획 테마 확보에 집중됨.", options: {} }
];

drawTextCard(s18, 0.4, 1.15, 4.4, 3.8, "5대 출판사 평점 품질 분석", s18Text);
drawImageCard(s18, 5.2, 1.15, 4.4, 3.8, "yes24/images/09_publisher_rating_box.png", "출판사별 평점 박스플롯");

s18.addNotes("베스트셀러 점유율 상위 5대 출판사들의 도서 평점을 박스 플롯으로 나타낸 그래프입니다. 이레미디어, 길벗, 김영사, 다산북스, 알에이치코리아의 박스 형태와 중앙값을 나타내는 내부 주황색 수평선이 거의 동일한 높이(9.0~9.5점 사이)에 형성되어 있음을 확인할 수 있습니다. 출판사 간의 평점 편차가 통계적으로 매우 작다는 것은, 대형 기획 편집부들이 신간 도서를 출간하고 검수하여 시장에 유통하는 기획 완성도와 품질 통제 메커니즘이 업계 전반에 표준화되어 균일하게 작동하고 있음을 뜻합니다.");


// ==========================================
// 19. SLIDE 19: PART 4 - 4.1 출판사 및 평점구간 교차 평균 판매지수 분석
// ==========================================
const s19 = pres.addSlide();
drawSlideBase(s19, "PART 4", "4.1 출판사 x 평점구간 교차 평균 판매지수 시각화");

const s19Text = [
  { text: "🗺️ 다차원 히트맵 세부 집계 분석\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 격자 쏠림 및 시너지 패턴:\n", options: { bold: true, breakLine: true } },
  { text: "    - 특정 대형 출판사와 특정 평점 만족도(특히 9.0 ~ 9.5점 및 대중성 있는 평점 밴드)가 교차할 때 평균 판매지수가 수직 급등하는 푸른색 핫스팟 격자가 도출됨.\n\n", options: { breakLine: true } },
  { text: "  • 유통력 x 독자 별점의 정렬 효과:\n", options: { bold: true, breakLine: true } },
  { text: "    - 출판사 브랜드 고유의 영향력과 독자 만족도가 일치해 결속력을 형성하는 골든 크로스 영역이 흥행을 주도함.\n\n", options: { breakLine: true } },
  { text: "💡 마케팅 시사점:\n", options: { bold: true, breakLine: true } },
  { text: "    - 타겟 독자군 세분화를 통해 브랜드 강점이 있는 특정 장르/만족도 구간을 선제 공략하는 타겟 집중 마케팅이 유효함.", options: {} }
];

drawTextCard(s19, 0.4, 1.15, 4.4, 3.8, "출판사x평점 다차원 교차 시너지", s19Text);
drawImageCard(s19, 5.2, 1.15, 4.4, 3.8, "yes24/images/10_publisher_rating_sales_heatmap.png", "출판사 x 평점 판매지수 히트맵");

s19.addNotes("네 번째 파트인 다변량 및 텍스트 데이터 마이닝 단락입니다. 본 파트에서는 출판사와 평점이라는 두 가지 변수를 조합하여 판매지수를 다차원적으로 진단하는 히트맵 피봇 분석을 전개하겠습니다. 5대 출판사와 4대 평점 구간을 교차 집계하여 평균 판매지수를 시각화한 2차원 히트맵입니다. 우측의 '9.5점 초과' 및 '8점초과~9점' 등 특정 출판사의 특정 격자 영역이 유독 짙은 청색으로 표시되는 파란색 격자 쏠림 패턴을 볼 수 있습니다. 이는 대형 출판사 간 경쟁에서도 특정 출판사 브랜드의 핵심 장르 및 만족도 관리가 독자의 신뢰와 시너지를 낼 때 흥행 부수가 폭발적으로 가속화됨을 의미하며, 표적인 채널 연계 및 세분 타겟 마케팅이 중요함을 증명합니다.");


// ==========================================
// 20. SLIDE 20: PART 4 - 4.2 & 4.3 베스트셀러 태그 텍스트 TF-IDF 분석 (그래프 + 표 병합)
// ==========================================
const s20 = pres.addSlide();
drawSlideBase(s20, "PART 4", "4.2 & 4.3 태그 텍스트 TF-IDF 자연어 마이닝 결과");

drawImageCard(s20, 0.4, 1.15, 4.4, 3.8, "yes24/images/11_tag_tfidf.png", "태그 단어 TF-IDF 가중치 차트");

s20.addShape(pres.shapes.RECTANGLE, {
  x: 5.2,
  y: 1.15,
  w: 4.4,
  h: 3.8,
  fill: { color: THEME.bgWhite },
  line: { color: THEME.borderBlack, width: 2 },
  shadow: getShadow(),
});

s20.addShape(pres.shapes.RECTANGLE, {
  x: 5.35,
  y: 1.3,
  w: 4.1,
  h: 0.35,
  fill: { color: THEME.bgYellow },
  line: { color: THEME.borderBlack, width: 1.5 },
});

s20.addText("태그 키워드 가중치 Top 10", {
  x: 5.35,
  y: 1.3,
  w: 4.1,
  h: 0.35,
  fontFace: THEME.fontBody,
  fontSize: 11,
  bold: true,
  color: THEME.textBlack,
  align: "center",
  valign: "middle",
  margin: 0,
});

const tableDataS20 = [
  [
    { text: "순위", options: { bold: true, align: "center", fill: { color: THEME.bgGray } } },
    { text: "추출 키워드", options: { bold: true, fill: { color: THEME.bgGray } } },
    { text: "TF-IDF 가중치 합", options: { bold: true, align: "right", fill: { color: THEME.bgGray } } }
  ],
  ["1", "크레마클럽에있어요", "131.31"],
  ["2", "주식투자", "26.78"],
  ["3", "주식투자입문", "22.49"],
  ["4", "투자전략", "17.97"],
  ["5", "똑똑하게투자하기", "17.77"],
  ["6", "경제전망", "16.02"],
  ["7", "주식초보", "12.46"],
  ["8", "주식고수", "11.87"],
  ["9", "경제이야기", "10.86"],
  ["10", "그래제본소", "10.61"]
];

s20.addTable(tableDataS20, {
  x: 5.35,
  y: 1.8,
  w: 4.1,
  h: 2.2,
  fontFace: THEME.fontBody,
  fontSize: 9,
  border: { pt: 1, color: THEME.borderBlack },
  colW: [0.6, 2.0, 1.5]
});

s20.addText("💡 구독 플랫폼(크레마클럽) 연계의 중요성과 실용적 주식/투자 학습 테마의 강렬한 집중.", {
  x: 5.35,
  y: 4.1,
  w: 4.1,
  h: 0.7,
  fontFace: THEME.fontBody,
  fontSize: 9,
  bold: true,
  color: THEME.accentRed,
});

s20.addNotes("도서 태그의 단어를 형태소 분석기 없이 띄어쓰기 및 전처리만을 거쳐 순수 TF-IDF 가중치를 적용한 가로 막대 차트와 상위 가중치 15개 요약입니다. 독보적인 '크레마클럽에있어요'를 필두로, '주식투자', '주식투자입문', '투자전략', '부자되는법' 등의 단어들이 아주 높게 나타나고 있습니다. 이는 현시대 독서 소비 시장을 관통하는 거대한 내재적 갈망이 재테크와 경제적 자생력 확보라는 실용적 가치에 완전히 집중되어 있음을 명확하게 보여줍니다. 플랫폼 구독 연계의 중요성과 실용적 투자 학습 테마의 강렬한 집중을 알 수 있습니다.");


// ==========================================
// 21. SLIDE 21: PART 4 - 4.4 도서 리뷰건수와 누적 판매지수의 이변량 분석
// ==========================================
const s21 = pres.addSlide();
drawSlideBase(s21, "PART 4", "4.4 도서 리뷰건수와 판매 성과 간의 비선형 가속 작용");

const s21Text = [
  { text: "🚀 임계점 돌파와 비선형 플라이휠 효과\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 임계점 100건의 기하급수적 우상향:\n", options: { bold: true, breakLine: true } },
  { text: "    - 산점도 분석 상, 리뷰가 수십 건 수준에 머무를 때는 판매지수 축이 바닥에 정체해 있으나, 리뷰가 **100건**을 넘는 기점으로 판매량이 기하급수적으로 폭발하는 비선형 가속 밴드를 실증함.\n\n", options: { breakLine: true } },
  { text: "  • 서평 마케팅의 정량적 입증:\n", options: { bold: true, breakLine: true } },
  { text: "    - 리뷰가 누적될수록 신규 독자 유입 신뢰가 상승하고, 이에 따라 플랫폼 메인 노출 알고리즘 가중치가 증가하여 추가 판매를 낳는 선순환 구도 형성.\n\n", options: { breakLine: true } },
  { text: "💡 실무자 액션플랜:\n", options: { bold: true, breakLine: true } },
  { text: "    - 출간 초기 골든타임(2~4주) 내에 초기 서평단을 대규모 투입하여 '리뷰 100건' 임계값을 조기에 뚫어야 알고리즘의 간택을 받을 수 있음.", options: {} }
];

drawTextCard(s21, 0.4, 1.15, 4.4, 3.8, "리뷰 누적과 판매량의 역학관계", s21Text);
drawImageCard(s21, 5.2, 1.15, 4.4, 3.8, "yes24/images/12_reviews_vs_sales.png", "리뷰건수 vs 판매지수 산점도");

s21.addNotes("리뷰 건수와 판매지수 간의 교차 영향력을 분석한 산점도입니다. 그래프의 분포 모양을 보시면 리뷰가 수십 건 이하일 때는 판매지수가 바닥에 밀착해 기어가는 반면, 리뷰 건수가 100건을 넘어가고 수백 건으로 치솟는 시점부터 판매지수 축이 천장 방향으로 수직에 가깝게 기하급수적으로 폭발하여 꺾여 올라가는 비선형 패턴을 볼 수 있습니다. 즉, 서평 활성화의 누적 속도가 임계점에 다다르면 판매를 증폭시키는 플라이휠 효과가 실존함을 데이터로 실증합니다.");


// ==========================================
// 22. SLIDE 22: PART 5 - 5.1 & 5.2 수치형 변수 복합 상관관계 분석 (열지도 + 행렬 통계표 병합)
// ==========================================
const s22 = pres.addSlide();
drawSlideBase(s22, "PART 5", "5.1 & 5.2 수치형 변수 다변량 피어슨 상관계수 진단");

drawImageCard(s22, 0.4, 1.15, 4.4, 3.8, "yes24/images/13_correlation_heatmap.png", "피어슨 상관관계 열지도");

s22.addShape(pres.shapes.RECTANGLE, {
  x: 5.2,
  y: 1.15,
  w: 4.4,
  h: 3.8,
  fill: { color: THEME.bgWhite },
  line: { color: THEME.borderBlack, width: 2 },
  shadow: getShadow(),
});

s22.addShape(pres.shapes.RECTANGLE, {
  x: 5.35,
  y: 1.3,
  w: 4.1,
  h: 0.35,
  fill: { color: THEME.bgYellow },
  line: { color: THEME.borderBlack, width: 1.5 },
});

s22.addText("피어슨 상관계수 행렬 세부 요약", {
  x: 5.35,
  y: 1.3,
  w: 4.1,
  h: 0.35,
  fontFace: THEME.fontBody,
  fontSize: 11,
  bold: true,
  color: THEME.textBlack,
  align: "center",
  valign: "middle",
  margin: 0,
});

const tableDataS22 = [
  [
    { text: "변수명", options: { bold: true, fill: { color: THEME.bgGray } } },
    { text: "할인율", options: { bold: true, fill: { color: THEME.bgGray } } },
    { text: "판매지수", options: { bold: true, fill: { color: THEME.bgGray } } },
    { text: "리뷰건수", options: { bold: true, fill: { color: THEME.bgGray } } },
    { text: "평점", options: { bold: true, fill: { color: THEME.bgGray } } }
  ],
  ["할인율", "1.00", "0.06", "0.09", "0.36"],
  ["판매지수", "0.06", "1.00", "0.30", "0.09"],
  ["리뷰건수", "0.09", "0.30", "1.00", "0.13"],
  ["평점", "0.36", "0.09", "0.13", "1.00"]
];

s22.addTable(tableDataS22, {
  x: 5.35,
  y: 1.8,
  w: 4.1,
  h: 2.1,
  fontFace: THEME.fontBody,
  fontSize: 9,
  border: { pt: 1, color: THEME.borderBlack },
  colW: [0.9, 0.8, 0.8, 0.8, 0.8]
});

s22.addText("💡 평점과 판매지수의 선형 상관성은 +0.09로 무상관에 가깝지만, 리뷰건수와 판매지수는 +0.30으로 3배 이상 강력한 정적 연관성을 가집니다.", {
  x: 5.35,
  y: 4.0,
  w: 4.1,
  h: 0.8,
  fontFace: THEME.fontBody,
  fontSize: 9.5,
  bold: true,
  color: THEME.accentBlue,
});

s22.addNotes("다섯 번째 파트인 수치형 변수 복합 상관관계 분석 단락입니다. 본 파트에서는 7대 수치형 변수들 전체를 대상으로 피어슨 상관계수 행렬을 수립하고 피어슨 상관관계 열지도로 규명해 보겠습니다. 정가와 할인가 계열이 붉은색을 띠는 것은 유통 단가의 특성상 당연한 결과이나, 우리가 주목해야 할 유의미한 지점은 판매지수와 리뷰건수의 접점입니다. 판매지수 기준 상관계수를 읽어보면, 할인율(+0.06), 평점(+0.09) 등은 영향력이 0에 가까워 의미 있는 선형 작용을 하지 못하지만, 리뷰건수와 판매지수 간의 상관계수는 +0.30으로 3배 이상 압도적으로 높게 계산되어, 서평 활성화가 추가 구매에 실질적으로 기여한다는 사실을 보여줍니다.");


// ==========================================
// 23. SLIDE 23: PART 6 - 6.1 도서 시장의 양극화와 롱테일 법칙
// ==========================================
const s23 = pres.addSlide();
drawSlideBase(s23, "PART 6", "6.1 도서 시장의 극단적 양극화 및 파레토 법칙 실증");

const s23LeftText = [
  { text: "⚖️ 정량 데이터로 본 양극화 실태\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 평균과 중앙값의 거대 불일치\n", options: { bold: true, breakLine: true } },
  { text: "    - 평균 판매지수 12,219점 대 중앙값 3,546점.\n", options: { breakLine: true } },
  { text: "    - 표준편차는 33,083점에 이르러 전체 데이터 산포가 극우측에 강렬하게 치우쳐(Long Tail) 있음.\n\n", options: { breakLine: true } },
  { text: "  • 소수의 초흥행작 지배 구조\n", options: { bold: true, breakLine: true } },
  { text: "    - 최대 판매지수는 56만 점을 초과하여 상위 5%의 메가 베스트셀러 도서가 시장의 총판매 부수와 대다수 플랫폼 매출 지분을 점유 중.", options: {} }
];

const s23RightText = [
  { text: "💡 출판 마케팅을 위한 혁신 제언\n\n", options: { bold: true, fontSize: 13, color: THEME.accentRed } },
  { text: "  ✔ 균등 예산 집행 모델 탈피\n", options: { bold: true, breakLine: true } },
  { text: "    - 신규 도서 출간 시 다수의 신간에 마케팅 예산을 n분의 1로 골고루 나누어 평화롭게 배분하는 소극적 전술은 필연적으로 전체 침체를 야기함.\n\n", options: { breakLine: true } },
  { text: "  ✔ 초기 블리츠스케일링(Blitzscaling) 집중\n", options: { bold: true, breakLine: true } },
  { text: "    - 시장성이 타진된 킬러 타이틀에 대해 초반 런칭 마케팅 리소스를 비대칭적으로 대규모 폭발 투입하여 초기 판매지수 1만 점 궤도를 급속 돌파시켜 상위 노출에 안착시키는 전략적 자원 집중이 생존 공식임.", options: {} }
];

drawTextCard(s23, 0.4, 1.15, 4.4, 3.8, "롱테일 파레토 구조 진단", s23LeftText);
drawTextCard(s23, 5.2, 1.15, 4.4, 3.8, "전략적 마케팅 시사점", s23RightText);

s23.addNotes("여섯 번째 파트인 데이터 기반 종합 인사이트 도출 단락입니다. 인사이트 첫 번째는 판매지수의 양극화와 파레토 법칙의 지배 현상입니다. 877개 데이터에서 평균 판매지수가 12,000점대인 데 반해 반수 이상의 책들은 3,500점 이하 영역에 걸쳐 있으며, 상위 10%가 시장 전체의 에너지를 다 흡수하고 있습니다. 신간 마케팅을 펼칠 때, 출판사가 모든 자원을 기계적으로 평균 분배하는 온건한 전술은 리소스를 낭비할 뿐입니다. 흥행 가능성이 검증된 스타 저자나 핵심 트렌드 서적에 초기 예산과 프로모션을 급진적으로 집중 투여해 판매지수 1만 점이라는 1차 궤도에 조기 안착시키는 자원 투여의 선택과 집중(Blitzscaling)이 필요합니다.");


// ==========================================
// 24. SLIDE 24: PART 6 - 6.2 평점 관대화와 독자 만족도-구매 결정의 디커플링
// ==========================================
const s24 = pres.addSlide();
drawSlideBase(s24, "PART 6", "6.2 평점 인플레이션과 구매 유발 동기 디커플링");

const s24LeftText = [
  { text: "📉 별점 만족도의 실질 흥행 변별력 상실\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 상관계수 +0.097 (선형성 0에 수렴)\n", options: { bold: true, breakLine: true } },
  { text: "    - 사후 독자 호평 만족도와 사전 구매를 격발하는 판매량 스코어는 통계적으로 완벽히 디커플링되어 있음.\n\n", options: { breakLine: true } },
  { text: "  • 평점구간 비교 역설의 증명\n", options: { bold: true, breakLine: true } },
  { text: "    - 평점이 최고조인 9.5점 초과 도서군(평균 10,825점)이 대중적 호불호가 갈리는 8~9.5점대 구간 도서군(평균 16,000점대)보다 흥행 파워가 유의미하게 약하게 산출됨.", options: {} }
];

const s24RightText = [
  { text: "💡 출판 기획자를 위한 혁신 제언\n\n", options: { bold: true, fontSize: 13, color: THEME.accentRed } },
  { text: "  ✔ 가공된 별점 관리 중심의 마케팅 청산\n", options: { bold: true, breakLine: true } },
  { text: "    - 고객들이 단순히 친의로 부여하는 평점 9.9점 관리에 매몰되지 말고, 독자들이 책을 구매할 당시 가졌던 즉각적 생존 결핍 자극에 집중해야 함.\n\n", options: { breakLine: true } },
  { text: "  ✔ 독자 Pain Point 텍스트 분석\n", options: { bold: true, breakLine: true } },
  { text: "    - 평점 점수 대신 고객의 정밀 서평(1~2점 낮은 상세 리뷰 등)의 비판 요소와 통점(Pain Point)을 자연어 텍스트 분석하여, 시장 미충족 갈망을 후속 도서 기획의 씨앗으로 사용해야 함.", options: {} }
];

drawTextCard(s24, 0.4, 1.15, 4.4, 3.8, "평점 만족도 디커플링 증명", s24LeftText);
drawTextCard(s24, 5.2, 1.15, 4.4, 3.8, "전략적 기획 시사점", s24RightText);

s24.addNotes("인사이트 두 번째는 평점의 상향 인플레이션과 구매 결정의 디커플링 역설입니다. 평점이 9.5점 이상인 초고평점 도서군보다 8~9.5점 사이의 평범한 만족도 도서군이 더 높은 평균 판매량을 달성한 현상을 주목해야 합니다. 독자들은 구매 결정 단계에서 책의 내재적 품질 평가(사후 별점)를 절대적 지표로 신뢰하지 않으며, 오히려 당장 '돈 공부'를 해야 하거나 '경제적 불안을 해소하려는 즉각적 생존 갈망'에 반응해 결제합니다. 따라서 마케팅 리뷰 이벤트로 평점 9.9점을 높이는 요식 행위에 집중하기보다, 독자의 텍스트 리뷰 내의 불만을 추출하여 독자의 내재적 결핍(Pain Point)을 해소하는 혁신 기획에 무게를 두어야 합니다.");


// ==========================================
// 25. SLIDE 25: PART 6 - 6.3 TF-IDF 분석이 포착한 사회적 결핍과 시대정신
// ==========================================
const s25 = pres.addSlide();
drawSlideBase(s25, "PART 6", "6.3 TF-IDF 텍스트 마이닝이 규명한 시대적 결핍");

const s25LeftText = [
  { text: "🎯 독자 태그 자연어 분석 결과\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 압도적 가중치 키워드군\n", options: { bold: true, breakLine: true } },
  { text: "    - '주식투자', '주식투자입문', '투자전략', '똑똑하게투자하기', '부자되는법', '재테크기초' 등.\n\n", options: { breakLine: true } },
  { text: "  • 학습 도구로서의 독서 소비\n", options: { bold: true, breakLine: true } },
  { text: "    - 독서가 감상이나 교양을 쌓는 사색적 영역에서 벗어나, 불안한 고용/경제 현실을 방어하기 위한 **'자산 생존 도구 학습'**으로 역할이 전격 이행되었음을 지시함.", options: {} }
];

const s25RightText = [
  { text: "💡 출판 기획자를 위한 혁신 제언\n\n", options: { bold: true, fontSize: 13, color: THEME.accentRed } },
  { text: "  ✔ 추상적 이론서 배제 및 실전 매뉴얼 지향\n", options: { bold: true, breakLine: true } },
  { text: "    - 모호한 거시경제 담론이나 학술 지식 위주의 구성은 독자의 빠른 이탈을 초래함.\n\n", options: { breakLine: true } },
  { text: "  ✔ 구체적인 액션 시나리오와 템플릿 기획\n", options: { bold: true, breakLine: true } },
  { text: "    - '39세 평범한 직장인의 은퇴 포트폴리오', '월 200만 원 저축으로 배당 연금 1억 만들기'처럼 현실적이고 선명한 실행 로드맵 및 바로 사용 가능한 계산 엑셀 시트 템플릿 번들이 도서 기획의 핵심 흥행 요건임.", options: {} }
];

drawTextCard(s25, 0.4, 1.15, 4.4, 3.8, "자연어 기반 독자 심리 추적", s25LeftText);
drawTextCard(s25, 5.2, 1.15, 4.4, 3.8, "전략적 타겟 기획 시사점", s25RightText);

s25.addNotes("인사이트 세 번째는 TF-IDF 자연어 마이닝이 규명한 시대정신입니다. 추출 가중치가 압도적으로 높은 단어들은 교양서가 아니라 주식투자, 부자되는법, 재테크, 경제적자유, 은퇴준비 등 자산 형성에 직결된 키워드입니다. 이는 현재의 거시적 불황과 고용 불안 구조 속에서 독자층이 책을 단순 지식 소양이 아닌 실용적이고 즉각적인 '자산 방어 및 도구적 생존 학습 도구'로 소비하고 있음을 알려줍니다. 따라서 향후 도서 기획 시, 모호하고 뜬구름 잡는 담론 형식이 아닌, 독자 개인이 바로 자산 포트폴리오에 적용할 수 있는 구체적인 실행 템플릿과 매뉴얼 포맷의 콘텐츠 설계가 필요합니다.");


// ==========================================
// 26. SLIDE 26: PART 6 - 6.4 도서정가제 가격 고착화와 플라이휠 리뷰 전략
// ==========================================
const s26 = pres.addSlide();
drawSlideBase(s26, "PART 6", "6.4 가격 고착 대응 비가격 혜택 및 리뷰 플라이휠 공식");

const s26LeftText = [
  { text: "⚖️ 도서정가제 하의 비가격 경쟁\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 할인 차별화 원천 차단\n", options: { bold: true, breakLine: true } },
  { text: "    - 95%의 도서가 일괄 10% 가격 할인 고착화.\n", options: { breakLine: true } },
  { text: "    - 가격 깎아주기식 마케팅 대신 사은품, 굿즈 번들, 혹은 한정판 저자 PDF 리포트 제공 등 독점적 체감 가치(Perceived Value) 제고에 집중해야 승산이 있음.\n\n", options: { breakLine: true } },
  { text: "  • 리뷰의 비선형 폭발성\n", options: { bold: true, breakLine: true } },
  { text: "    - 리뷰 10건 이하 평균 판매지수 3,056점 대비 100건 돌파 시 30,282점으로 **10배 폭발**함.", options: {} }
];

const s26RightText = [
  { text: "💡 출판 마케터를 위한 혁신 제언\n\n", options: { bold: true, fontSize: 13, color: THEME.accentRed } },
  { text: "  ✔ 초기 4주 골든타임 총력전\n", options: { bold: true, breakLine: true } },
  { text: "    - 신작 런칭 직후 플랫폼 추천 알고리즘의 노출 가중치 점수를 확보하기 위해, 서평 마케팅 및 리뷰 확보 캠페인을 초기에 초집중 전개해야 함.\n\n", options: { breakLine: true } },
  { text: "  ✔ 100건 서평 임계치 선제 돌파\n", options: { bold: true, breakLine: true } },
  { text: "    - 타겟 맞춤형 커뮤니티 협업, 기대평/한줄평 이벤트 등을 가동하여 빠른 리뷰 100건 임계점을 달성, 판매 상승 플라이휠을 구동시키는 것이 핵심적 성공 방정식임.", options: {} }
];

drawTextCard(s26, 0.4, 1.15, 4.4, 3.8, "가격 고착 및 리뷰 비선형 공식", s26LeftText);
drawTextCard(s26, 5.2, 1.15, 4.4, 3.8, "전략적 마케팅 시사점", s26RightText);

s26.addNotes("네 번째 종합 인사이트는 도서정가제에 따른 가격 마케팅 고착화와 이에 대응하는 '리뷰 플라이휠' 전술입니다. 분석 대상의 95% 이상이 고정 10% 할인 상태여서 가격 혜택 마케팅은 차별점이 될 수 없습니다. 이에 대한 돌파구는 저자 직강 초대장이나 투자 분석 시트 PDF 제공 등 무형의 혜택을 함께 묶어 독자가 체감하는 소비자 가치를 비약적으로 키우는 것입니다. 또한 리뷰가 10건 이하일 때와 100건을 넘을 때의 판매지수 편차가 10배에 달하므로, 출간 초기 골든타임인 2~4주 이내에 서평단을 집중 투입해 100건의 리뷰를 단기간에 쏟아내어 플랫폼 추천 알고리즘의 우대를 선점해야 합니다.");


// ==========================================
// 27. SLIDE 27: PART 7 - 7.1 베스트셀러 흥행을 위한 5대 기획 프레임워크
// ==========================================
const s27 = pres.addSlide();
drawSlideBase(s27, "PART 7", "7.1 베스트셀러 흥행 촉발을 위한 5대 실천 프레임워크");

const frame1 = [
  { text: "1. 🎯 독자의 불안 및 Pain Point 정밀 저격\n", options: { bold: true, color: THEME.accentRed } },
  { text: "   - 자산 방어, 은퇴 대비 등 원초적인 불안 키워드 설계.\n", options: { fontSize: 10 } },
  { text: "2. 🛠️ 즉각 사용이 가능한 행동 구체성 제공\n", options: { bold: true, color: THEME.accentBlue } },
  { text: "   - 단순 담론 탈피, 엑셀 시뮬레이터, 체크리스트 등 템플릿 번들.\n", options: { fontSize: 10 } },
  { text: "3. 🚀 출간 초기 리뷰 100건 임계점 선점\n", options: { bold: true, color: "008800" } },
  { text: "   - 런칭 후 2~4주 골든타임 내 서평단 조직 가동, 알고리즘 간택 유도.", options: { fontSize: 10 } }
];

const frame2 = [
  { text: "4. 🏢 상위 5대 대형 출판사와 유통 파이프라인 협업\n", options: { bold: true } },
  { text: "   - 오프라인 매대 장악력 및 서점 제휴 혜택 극대화를 위한 메이저 브랜드 채널 제휴.\n", options: { fontSize: 10 } },
  { text: "5. 🔄 하이브리드 리스크 헤징 출판 모델 구축\n", options: { bold: true } },
  { text: "   - 크레마클럽 등 디지털 플랫폼 선진입 → 유저 반응 및 텍스트 지표 사전 검증 → 오프라인 2차 프리미엄 단행본으로 전격 인쇄 유도하는 데이터 기반 저리스크 기획 전략 실행.", options: { fontSize: 10 } }
];

drawTextCard(s27, 0.4, 1.15, 4.4, 3.8, "프레임워크 핵심 1~3번", frame1);
drawTextCard(s27, 5.2, 1.15, 4.4, 3.8, "프레임워크 핵심 4~5번", frame2);

s27.addNotes("마지막 일곱 번째 파트인 전략적 제언 및 성공 프레임워크 단락입니다. 본 파트에서는 앞서 실증한 양극화 극복 전술, 디커플링 극복 방안, 시대정신 맞춤형 기획, 그리고 리뷰 플라이휠 임계점 돌파 공식을 종합하여, 출판사 기획 및 마케팅 실무에 곧바로 즉각 투영할 수 있는 '5대 핵심 성공 프레임워크'를 최종 실천 과제로 제시하고자 합니다. 첫째, 독자의 원초적인 생존 불안을 직격하는 핵심 주제로 타겟의 관심을 강하게 끌어당겨야 합니다. 둘째, 바로 실천할 수 있는 가계부나 투자 차트 시뮬레이터 등의 구체성 높은 도구를 도서와 함께 증정합니다. 셋째, 출간 초기 한 달 내에 100건의 양질 리뷰를 확보하기 위한 마케팅 드라이브를 전개합니다. 넷째, 유통과 오프라인 매대 장악이 뛰어난 상위 대형 출판사와 초기 채널 협업을 단단히 맺습니다. 다섯째, '크레마클럽' 구독 플랫폼 등 리스크가 적은 채널에 디지털 버전을 선진입시켜 반응 지표를 검증한 뒤 종이책 소장본으로 2차 출판을 도모하는 하이브리드 리스크 헤징 전략을 실행합니다.");


// ==========================================
// 28. SLIDE 28: PART 7 - 7.2 종합 결론 및 향후 전망
// ==========================================
const s28 = pres.addSlide();
drawSlideBase(s28, "PART 7", "7.2 종합 결론 및 데이터 기반 출판 시장 미래 전망");

const s28Left = [
  { text: "🏁 데이터 기반 의사결정 체계로의 전환\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 직관과 감에 의존하던 전통적인 편집 관행에서 과학적 통계 접근으로 패러다임 전격 전환.\n\n", options: { breakLine: true } },
  { text: "  • 평점 편향, 리뷰 임계 가중치, TF-IDF 텍스트 마이닝을 융합 연계하여 책의 기획부터 마케팅까지 정교하게 데이터로 사전 예측하고 성공률을 극대화해야 함.", options: {} }
];

const s28Right = [
  { text: "🔮 출판 비즈니스의 미래 패러다임\n\n", options: { bold: true, fontSize: 13, color: THEME.accentRed } },
  { text: "  • 복합 불황 시기에도 '경제적 생존과 실용 가치'에 대한 독자 갈망은 장기 유지될 전망.\n\n", options: { breakLine: true } },
  { text: "  • 플랫폼 디지털 구독(가벼운 탐색)과 오프라인 종이책(소장 가치 극대화)의 양극화된 하이브리드 투 트랙 기획 모델이 앞으로의 업계 핵심 표준이 될 것임.", options: {} }
];

drawTextCard(s28, 0.4, 1.15, 4.4, 3.8, "분석 최종 결론 요약", s28Left);
drawTextCard(s28, 5.2, 1.15, 4.4, 3.8, "향후 출판 마켓 전망", s28Right);

s28.addNotes("이번 고도화 분석의 최종 결론을 내리겠습니다. 출판 기획은 더 이상 편집장의 단순 감각이나 트렌드 어림짐작에 의존해서는 승률을 담보할 수 없으며, 데이터가 지시하는 평점 인플레이션의 한계, 리뷰 건수 임계점 돌파, TF-IDF 핵심 갈망 키워드 연동 등 정량 데이터 기반의 과학적 설계를 거쳐야 흥행 승률을 극대화할 수 있습니다. 장기 불황 국면이 지속되더라도 자산 보존과 재테크 갈망에 대한 시대정신은 견고할 것이며, 전자책 구독 서비스를 통해 지표를 검증하고 이를 프리미엄 종이책 단행본으로 전환해 소장 가치를 배가시키는 하이브리드 출판 모델이 시장의 미래 표준으로 자리 잡을 것입니다.");


// ==========================================
// 29. SLIDE 29: Q & A (네오브루탈리즘 스타일)
// ==========================================
const s29 = pres.addSlide();
s29.background = { color: THEME.bgYellow };

s29.addShape(pres.shapes.RECTANGLE, {
  x: 0.5,
  y: 0.5,
  w: 9.0,
  h: 4.625,
  fill: { color: THEME.bgWhite },
  line: { color: THEME.borderBlack, width: 3 },
  shadow: getShadow(),
});

s29.addText("Q & A", {
  x: 1.0,
  y: 1.2,
  w: 8.0,
  h: 1.5,
  fontFace: THEME.fontTitle,
  fontSize: 64,
  bold: true,
  color: THEME.textBlack,
  align: "center",
  valign: "middle",
});

s29.addShape(pres.shapes.RECTANGLE, {
  x: 1.5,
  y: 2.9,
  w: 7.0,
  h: 0.8,
  fill: { color: THEME.bgYellow },
  line: { color: THEME.borderBlack, width: 2 },
  shadow: { type: "outer", color: "000000", blur: 0, offset: 3, angle: 135, opacity: 1.0 },
});

s29.addText("경청해 주셔서 감사합니다. 질문이 있으시면 편하게 말씀해 주세요.", {
  x: 1.6,
  y: 2.9,
  w: 6.8,
  h: 0.8,
  fontFace: THEME.fontBody,
  fontSize: 14,
  bold: true,
  color: THEME.textBlack,
  align: "center",
  valign: "middle",
});

s29.addText("email: analyst@company.com  |  Tel: 02-1234-5678", {
  x: 1.0,
  y: 4.0,
  w: 8.0,
  h: 0.5,
  fontFace: THEME.fontMono,
  fontSize: 11,
  color: "555555",
  align: "center",
  valign: "middle",
});

s29.addNotes("이상으로 예스24 베스트셀러 고도화 EDA 종합 보고 및 발표를 모두 마치겠습니다. 오늘의 데이터 요약 분석 내용이나 5대 프레임워크 실천 과제에 대해 추가적으로 궁금하신 부분이나 세부 통계적 의문이 있으시다면 편안하게 질의해 주시기 바랍니다. 성실히 답변해 드리겠습니다. 대단히 감사합니다.");


// ==========================================
// 30. SLIDE 30: 관련 리소스 및 데이터 스택 (정확히 30페이지 달성)
// ==========================================
const s30 = pres.addSlide();
drawSlideBase(s30, "APPENDIX", "참고 리소스 및 데이터 스택 명세");

const appText1 = [
  { text: "📂 분석 결과 원본 자료 정보\n\n", options: { bold: true, fontSize: 13, color: THEME.accentBlue } },
  { text: "  • 상세 연구 분석 본문 보고서:\n", options: { bold: true, breakLine: true } },
  { text: "    - 파일경로: yes24/docs/eda_report.md\n", options: { fontFace: THEME.fontMono, breakLine: true } },
  { text: "    - 약 3만 자 분량의 통계 및 자연어 분석 백서가 수립되어 있음.\n\n", options: { breakLine: true } },
  { text: "  • 동적 연계 엑셀 대시보드:\n", options: { bold: true, breakLine: true } },
  { text: "    - 파일경로: yes24/docs/bestsellers_dashboard.xlsx\n", options: { fontFace: THEME.fontMono, breakLine: true } },
  { text: "    - 매크로 수식 및 조건부 서식을 연동하여 출판사와 평점별 검색 기능 구현.", options: {} }
];

const appText2 = [
  { text: "🛠️ 분석 기술 스택 및 개발 정보\n\n", options: { bold: true, fontSize: 13, color: THEME.accentRed } },
  { text: "  • 데이터 처리 및 정제 스택:\n", options: { bold: true, breakLine: true } },
  { text: "    - Python (Pandas, Numpy), Jupyter Notebook 환경 전처리 실행.\n\n", options: { breakLine: true } },
  { text: "  • 시각화 및 자연어 처리:\n", options: { bold: true, breakLine: true } },
  { text: "    - Matplotlib, Seaborn 라이브러리를 활용해 고품질 플롯 이미지 드로잉.\n", options: { breakLine: true } },
  { text: "    - Scikit-learn의 TfidfVectorizer를 적용해 태그 가중치 분석 수행.\n\n", options: { breakLine: true } },
  { text: "  • 프레젠테이션 디자인 및 빌드:\n", options: { bold: true, breakLine: true } },
  { text: "    - Node.js 기반 PptxGenJS 모듈을 가동하여 네오브루탈리즘 테마의 슬라이드 완전 코딩 빌딩 수행.", options: {} }
];

drawTextCard(s30, 0.4, 1.15, 4.4, 3.8, "백데이터 및 대시보드 리소스", appText1);
drawTextCard(s30, 5.2, 1.15, 4.4, 3.8, "분석 인프라 & 기술 스택", appText2);

s30.addNotes("본 장표는 본 보고의 기초가 된 세부 마크다운 상세 텍스트 보고서 및 데이터 수식 분석이 포함된 엑셀 대시보드의 연동 파일 리소스 정보입니다. 또한 본 분석을 지원했던 데이터 전처리 파이썬 및 프레젠테이션 렌더링에 관한 정보가 기술되어 있어 사후 분석 인프라 복제에 활용하실 수 있습니다.");


// 프레젠테이션 파일 저장 실행 (상대 경로로 output 생성)
const outputPath = path.join("yes24", "docs", "bestsellers_presentation_brutal.pptx");
pres.writeFile({ fileName: outputPath })
  .then((fileName) => {
    console.log(`Success: PPTX generated successfully at \${fileName}`);
  })
  .catch((err) => {
    console.error(`Error: Failed to write PPTX file: \${err}`);
  });
