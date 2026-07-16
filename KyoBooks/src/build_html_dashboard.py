"""
교보문고 실시간 베스트셀러 HTML 웹 대시보드 빌더 스크립트

이 모듈은 KyoBooks/data/bestsellers.csv 도서 데이터를 Pandas로 읽어와
JSON으로 변환한 뒤, HSL 에메랄드 테마와 Chart.js 시각화 로직이 들어있는
HTML 템플릿 코드에 인라인 임베딩하여 로컬 실행이 가능한 dashboard.html 파일을 생성합니다.
"""

import os
import json
import pandas as pd

def build_dashboard():
    # 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    data_path = os.path.join(project_dir, "data", "bestsellers.csv")
    output_path = os.path.join(project_dir, "docs", "dashboard.html")
    
    if not os.path.exists(data_path):
        print(f"데이터 파일이 존재하지 않습니다: {data_path}")
        return
        
    # 1. 데이터 로드 및 수치 전처리
    df = pd.read_csv(data_path, encoding="utf-8-sig")
    df['정가'] = pd.to_numeric(df['정가'], errors='coerce').fillna(0).astype(int)
    df['할인가'] = pd.to_numeric(df['할인가'], errors='coerce').fillna(0).astype(int)
    df['할인율'] = pd.to_numeric(df['할인율'], errors='coerce').fillna(0).astype(int)
    df['리뷰건수'] = pd.to_numeric(df['리뷰건수'], errors='coerce').fillna(0).astype(int)
    df['평점'] = pd.to_numeric(df['평점'], errors='coerce').fillna(0.0)
    
    # 2. JSON 문자열 변환
    books_json = df.to_json(orient="records", force_ascii=False)
    
    # 3. HTML / CSS / JS 올인원 템플릿 정의
    html_template = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>교보문고 베스트셀러 종합 대시보드</title>
  <!-- Google Fonts 연동 -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
  <!-- Chart.js CDN 연동 -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  
  <style>
    :root {
      /* HSL Tailored Color Palette */
      --bg-primary: hsl(140, 15%, 96%);      /* 연하고 소프트한 그린 그레이 */
      --color-primary: hsl(156, 100%, 15%);  /* 교보 포레스트 딥 그린 (#004F2F) */
      --color-primary-light: hsl(156, 35%, 28%);
      --color-primary-soft: hsl(140, 30%, 93%);
      --color-accent: hsl(30, 35%, 65%);     /* 브론즈 골드 포인트 */
      --color-accent-hover: hsl(30, 35%, 55%);
      --text-dark: hsl(140, 20%, 12%);       /* 짙은 차콜 */
      --text-muted: hsl(140, 10%, 45%);
      --card-bg: rgba(255, 255, 255, 0.85);  /* 반투명 글래스모피즘 카드 */
      --card-border: rgba(255, 255, 255, 0.6);
      
      /* Visual Effects */
      --glass-shadow: 0 10px 30px 0 rgba(0, 79, 47, 0.06);
      --backdrop-blur: blur(16px);
      --border-radius: 18px;
      --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Outfit', 'Inter', 'Noto Sans KR', sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-dark);
      line-height: 1.6;
      padding: 2rem 1.5rem;
      background-image: radial-gradient(circle at 10% 20%, rgba(0, 79, 47, 0.03) 0%, transparent 40%),
                        radial-gradient(circle at 90% 80%, rgba(191, 163, 138, 0.05) 0%, transparent 40%);
      background-attachment: fixed;
    }

    .container {
      max-width: 1400px;
      margin: 0 auto;
    }

    /* Glassmorphism Card Style Base */
    .glass-card {
      background: var(--card-bg);
      backdrop-filter: var(--backdrop-blur);
      -webkit-backdrop-filter: var(--backdrop-blur);
      border: 1px solid var(--card-border);
      border-radius: var(--border-radius);
      box-shadow: var(--glass-shadow);
      padding: 1.8rem;
      transition: var(--transition-smooth);
    }
    
    .glass-card:hover {
      transform: translateY(-3px);
      box-shadow: 0 12px 40px 0 rgba(0, 79, 47, 0.1);
    }

    /* Header */
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
      padding: 1.5rem 2rem;
      background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
      color: white;
      border-radius: var(--border-radius);
      box-shadow: 0 10px 25px rgba(0, 79, 47, 0.15);
    }

    header h1 {
      font-family: 'Outfit', sans-serif;
      font-size: 1.8rem;
      font-weight: 700;
      letter-spacing: -0.5px;
      display: flex;
      align-items: center;
      gap: 0.8rem;
    }

    header h1 span {
      background: var(--color-accent);
      color: var(--color-primary);
      padding: 0.2rem 0.6rem;
      border-radius: 6px;
      font-size: 0.9rem;
      font-weight: 800;
      letter-spacing: 0.5px;
    }

    header .meta-info {
      font-size: 0.9rem;
      opacity: 0.9;
      text-align: right;
    }

    /* KPI Summary Grid */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    .kpi-card {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      border-left: 5px solid var(--color-primary);
    }

    .kpi-card:nth-child(4) {
      border-left-color: var(--color-accent);
    }

    .kpi-title {
      font-size: 0.9rem;
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 0.5rem;
    }

    .kpi-value {
      font-size: 2rem;
      font-weight: 700;
      color: var(--color-primary);
      font-family: 'Outfit', sans-serif;
      margin-bottom: 0.2rem;
    }

    .kpi-desc {
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    /* Control Panel (Search & Filter) */
    .control-panel {
      margin-bottom: 2rem;
      display: flex;
      flex-direction: column;
      gap: 1.2rem;
    }

    .search-row {
      display: flex;
      gap: 1rem;
    }

    .search-input-wrapper {
      position: relative;
      flex-grow: 1;
    }

    .search-input {
      width: 100%;
      padding: 0.9rem 1.2rem;
      border: 1px solid rgba(0, 79, 47, 0.15);
      border-radius: 12px;
      background: white;
      color: var(--text-dark);
      font-size: 0.95rem;
      font-family: inherit;
      outline: none;
      transition: var(--transition-smooth);
    }

    .search-input:focus {
      border-color: var(--color-primary);
      box-shadow: 0 0 0 3px rgba(0, 79, 47, 0.1);
    }

    .tag-container {
      display: flex;
      flex-wrap: wrap;
      gap: 0.6rem;
      align-items: center;
    }

    .tag-label {
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--color-primary);
      margin-right: 0.5rem;
    }

    .tag-btn {
      padding: 0.4rem 0.9rem;
      border-radius: 20px;
      border: 1px solid rgba(0, 79, 47, 0.1);
      background: white;
      font-size: 0.8rem;
      font-weight: 500;
      cursor: pointer;
      color: var(--text-dark);
      transition: var(--transition-smooth);
    }

    .tag-btn:hover {
      background: var(--color-primary-soft);
      border-color: var(--color-primary);
    }

    .tag-btn.active {
      background: var(--color-primary);
      color: white;
      border-color: var(--color-primary);
      box-shadow: 0 4px 10px rgba(0, 79, 47, 0.15);
    }

    /* Charts Section Grid */
    .charts-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    @media (max-width: 768px) {
      .charts-grid {
        grid-template-columns: 1fr;
      }
    }

    .chart-container {
      position: relative;
      height: 320px;
      width: 100%;
      margin-top: 1rem;
    }

    .chart-card-title {
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--color-primary);
      border-bottom: 1px solid rgba(0, 79, 47, 0.08);
      padding-bottom: 0.6rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    /* Data Table Section */
    .table-section {
      overflow: hidden;
    }

    .table-header-wrapper {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }

    .table-container {
      width: 100%;
      overflow-x: auto;
      border-radius: 12px;
      border: 1px solid rgba(0, 79, 47, 0.08);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.9rem;
      background: white;
    }

    th {
      background-color: var(--color-primary);
      color: white;
      font-weight: 600;
      padding: 1rem;
      cursor: pointer;
      user-select: none;
      transition: var(--transition-smooth);
    }

    th:hover {
      background-color: var(--color-primary-light);
    }

    th.sort-active::after {
      content: ' ▾';
      font-size: 0.8rem;
    }
    
    th.sort-active.asc::after {
      content: ' ▴';
    }

    td {
      padding: 0.9rem 1rem;
      border-bottom: 1px solid rgba(0, 79, 47, 0.05);
      color: var(--text-dark);
      transition: var(--transition-smooth);
    }

    tr {
      cursor: pointer;
    }

    tr:hover td {
      background-color: rgba(0, 79, 47, 0.03);
    }

    tr:nth-child(even) td {
      background-color: rgba(240, 245, 241, 0.25);
    }

    .text-center {
      text-align: center;
    }
    
    .rating-badge {
      background: hsl(45, 100%, 94%);
      color: hsl(45, 100%, 30%);
      padding: 0.2rem 0.5rem;
      border-radius: 6px;
      font-weight: 700;
      font-size: 0.8rem;
    }

    /* Pagination */
    .pagination {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 0.5rem;
      margin-top: 1.5rem;
    }

    .page-btn {
      padding: 0.4rem 0.8rem;
      border-radius: 8px;
      border: 1px solid rgba(0, 79, 47, 0.1);
      background: white;
      color: var(--text-dark);
      cursor: pointer;
      font-size: 0.85rem;
      transition: var(--transition-smooth);
    }

    .page-btn:hover:not(:disabled) {
      background: var(--color-primary);
      color: white;
      border-color: var(--color-primary);
    }

    .page-btn:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }

    .page-info {
      font-size: 0.85rem;
      color: var(--text-muted);
      margin: 0 0.5rem;
    }

    /* Modal Styling */
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 40, 24, 0.4);
      backdrop-filter: blur(8px);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 1000;
      opacity: 0;
      pointer-events: none;
      transition: var(--transition-smooth);
    }

    .modal-overlay.active {
      opacity: 1;
      pointer-events: auto;
    }

    .modal-card {
      background: white;
      border-radius: var(--border-radius);
      box-shadow: 0 20px 50px rgba(0, 40, 24, 0.2);
      width: 90%;
      max-width: 600px;
      overflow: hidden;
      transform: translateY(20px);
      transition: var(--transition-smooth);
      border: 1px solid rgba(255, 255, 255, 0.8);
    }

    .modal-overlay.active .modal-card {
      transform: translateY(0);
    }

    .modal-header {
      background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
      color: white;
      padding: 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .modal-header h3 {
      font-size: 1.2rem;
      font-weight: 700;
    }

    .close-btn {
      background: none;
      border: none;
      color: white;
      font-size: 1.5rem;
      cursor: pointer;
      opacity: 0.8;
      transition: var(--transition-smooth);
    }

    .close-btn:hover {
      opacity: 1;
      transform: rotate(90deg);
    }

    .modal-body {
      padding: 1.8rem;
      display: flex;
      gap: 1.5rem;
    }

    @media (max-width: 576px) {
      .modal-body {
        flex-direction: column;
        align-items: center;
      }
    }

    .modal-img-wrapper {
      width: 150px;
      flex-shrink: 0;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
      border: 1px solid rgba(0, 79, 47, 0.08);
      height: fit-content;
    }

    .modal-img-wrapper img {
      width: 100%;
      display: block;
    }

    .modal-details {
      flex-grow: 1;
      display: flex;
      flex-direction: column;
      gap: 0.8rem;
    }

    .modal-book-title {
      font-size: 1.3rem;
      font-weight: 700;
      color: var(--color-primary);
      line-height: 1.3;
    }

    .modal-meta-row {
      display: grid;
      grid-template-columns: 80px 1fr;
      font-size: 0.9rem;
      border-bottom: 1px solid rgba(0, 0, 0, 0.05);
      padding-bottom: 0.4rem;
    }

    .modal-meta-label {
      color: var(--text-muted);
      font-weight: 600;
    }

    .modal-meta-val {
      color: var(--text-dark);
    }

    .modal-book-desc {
      font-size: 0.85rem;
      color: var(--text-muted);
      line-height: 1.5;
      background: var(--bg-primary);
      padding: 0.8rem;
      border-radius: 8px;
      max-height: 150px;
      overflow-y: auto;
      margin-top: 0.5rem;
    }
  </style>
</head>
<body>

  <div class="container">
    
    <!-- Header -->
    <header>
      <div>
        <h1>📚 교보문고 실시간 베스트셀러 <span>99종 대시보드</span></h1>
      </div>
      <div class="meta-info">
        <div>데이터 범위: 1위 ~ 99위 전체 도서</div>
        <div id="update-time">최종 갱신: 2026-07-16</div>
      </div>
    </header>

    <!-- KPI summary cards -->
    <section class="kpi-grid">
      <div class="glass-card kpi-card">
        <div>
          <div class="kpi-title">총 수집 도서 수</div>
          <div class="kpi-value" id="kpi-total">0</div>
        </div>
        <div class="kpi-desc">중복 제거 및 순위 정제 완료</div>
      </div>
      <div class="glass-card kpi-card">
        <div>
          <div class="kpi-title">평균 도서 정가</div>
          <div class="kpi-value" id="kpi-price">0원</div>
        </div>
        <div class="kpi-desc">소비자 기준 단가 평균</div>
      </div>
      <div class="glass-card kpi-card">
        <div>
          <div class="kpi-title">평균 할인율</div>
          <div class="kpi-value" id="kpi-discount">0%</div>
        </div>
        <div class="kpi-desc">도서정가제 할인 포함</div>
      </div>
      <div class="glass-card kpi-card">
        <div>
          <div class="kpi-title">누적 총 리뷰 수</div>
          <div class="kpi-value" id="kpi-reviews">0</div>
        </div>
        <div class="kpi-desc">독자 피드백 반응 총계</div>
      </div>
    </section>

    <!-- Control Panel -->
    <section class="glass-card control-panel">
      <div class="search-row">
        <div class="search-input-wrapper">
          <input type="text" id="search-bar" class="search-input" placeholder="도서명, 저자, 출판사 키워드로 실시간 검색...">
        </div>
      </div>
      <div class="tag-container">
        <span class="tag-label">장르별 필터:</span>
        <button class="tag-btn active" data-genre="ALL">전체 보기</button>
        <!-- JS를 통해 동적 카테고리 버튼 추가 -->
        <div id="dynamic-tags" style="display: inline-flex; flex-wrap: wrap; gap: 0.6rem;"></div>
      </div>
    </section>

    <!-- Chart Grid -->
    <section class="charts-grid">
      <!-- Chart 1: 출판사 점유율 -->
      <div class="glass-card">
        <div class="chart-card-title">🏭 상위 10개 출판사 점유율</div>
        <div class="chart-container">
          <canvas id="chart-publishers"></canvas>
        </div>
      </div>
      
      <!-- Chart 2: 가격대 분포 -->
      <div class="glass-card">
        <div class="chart-card-title">💸 베스트셀러 도서 가격대 분포</div>
        <div class="chart-container">
          <canvas id="chart-prices"></canvas>
        </div>
      </div>

      <!-- Chart 3: 장르별 비중 -->
      <div class="glass-card">
        <div class="chart-card-title">🧩 분야(장르)별 도서 점유 비중</div>
        <div class="chart-container">
          <canvas id="chart-genres"></canvas>
        </div>
      </div>

      <!-- Chart 4: 평점 vs 리뷰수 -->
      <div class="glass-card">
        <div class="chart-card-title">📈 독자 평점과 누적 리뷰 수 상관관계</div>
        <div class="chart-container">
          <canvas id="chart-correlation"></canvas>
        </div>
      </div>
    </section>

    <!-- Data Table Grid -->
    <section class="glass-card table-section">
      <div class="table-header-wrapper">
        <h2 style="font-size: 1.2rem; color: var(--color-primary); font-weight: 700;">📋 상세 도서 목록 데이터</h2>
        <div style="font-size: 0.85rem; color: var(--text-muted);" id="row-count-info">총 99건 중 99건 표시</div>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th id="th-순위" onclick="sortTable('순위')" class="sort-active asc" style="width: 70px;">순위</th>
              <th id="th-도서명" onclick="sortTable('도서명')">도서명</th>
              <th id="th-저자" onclick="sortTable('저자')">저자</th>
              <th id="th-출판사" onclick="sortTable('출판사')">출판사</th>
              <th id="th-할인가" onclick="sortTable('할인가')" class="text-center" style="width: 110px;">할인가</th>
              <th id="th-평점" onclick="sortTable('평점')" class="text-center" style="width: 90px;">평점</th>
              <th id="th-리뷰건수" onclick="sortTable('리뷰건수')" class="text-center" style="width: 100px;">리뷰수</th>
            </tr>
          </thead>
          <tbody id="table-body">
            <!-- JS 동적 렌더링 -->
          </tbody>
        </table>
      </div>
      
      <!-- Pagination -->
      <div class="pagination">
        <button class="page-btn" id="btn-prev" onclick="changePage(-1)">이전</button>
        <span class="page-info" id="page-info">1 / 10 페이지</span>
        <button class="page-btn" id="btn-next" onclick="changePage(1)">다음</button>
      </div>
    </section>

  </div>

  <!-- Detail Viewer Modal -->
  <div class="modal-overlay" id="detail-modal" onclick="closeModal(event)">
    <div class="modal-card" onclick="event.stopPropagation()">
      <div class="modal-header">
        <h3 id="modal-title">도서 상세 정보</h3>
        <button class="close-btn" onclick="toggleModal(false)">&times;</button>
      </div>
      <div class="modal-body">
        <div class="modal-img-wrapper">
          <img id="modal-img" src="" alt="도서 표지">
        </div>
        <div class="modal-details">
          <div class="modal-book-title" id="modal-book-name">도서명 영역</div>
          
          <div class="modal-meta-row" style="margin-top: 0.5rem;">
            <div class="modal-meta-label">저자</div>
            <div class="modal-meta-val" id="modal-author">-</div>
          </div>
          <div class="modal-meta-row">
            <div class="modal-meta-label">출판사</div>
            <div class="modal-meta-val" id="modal-publisher">-</div>
          </div>
          <div class="modal-meta-row">
            <div class="modal-meta-label">출판일</div>
            <div class="modal-meta-val" id="modal-date">-</div>
          </div>
          <div class="modal-meta-row">
            <div class="modal-meta-label">소비자 정가</div>
            <div class="modal-meta-val" id="modal-price">-</div>
          </div>
          <div class="modal-meta-row">
            <div class="modal-meta-label">실판매가</div>
            <div class="modal-meta-val" id="modal-sale-price">-</div>
          </div>
          <div class="modal-meta-row">
            <div class="modal-meta-label">평점/리뷰</div>
            <div class="modal-meta-val" id="modal-satisfaction">-</div>
          </div>
          
          <div class="modal-book-desc" id="modal-desc">
            도서 요약 소개 영역...
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 데이터 인라인 주입 -->
  <script>
    const BESTSELLERS_DATA = /*{{BOOK_DATA_JSON}}*/;
    
    // 글로벌 상태 변수
    let filteredData = [...BESTSELLERS_DATA];
    let selectedGenre = "ALL";
    let searchKeyword = "";
    let currentPage = 1;
    const itemsPerPage = 10;
    let sortConfig = { key: '순위', asc: true };
    
    // Chart 인스턴스 보관용
    let chartPublishers = null;
    let chartPrices = null;
    let chartGenres = null;
    let chartCorrelation = null;

    // 초기화 함수
    window.addEventListener('DOMContentLoaded', () => {
      // 1. 현재 날짜 표기
      const today = new Date();
      document.getElementById('update-time').innerText = `최종 갱신: ${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
      
      // 2. 동적 장르(태그) 목록 추출 및 렌더링
      initGenreButtons();
      
      // 3. 실시간 필터 및 검색 연동 리스너
      document.getElementById('search-bar').addEventListener('input', (e) => {
        searchKeyword = e.target.value.toLowerCase().trim();
        currentPage = 1;
        applyFilters();
      });
      
      // 4. 최초 렌더링
      applyFilters();
    });

    // 장르 목록 추출 및 버튼 렌더링
    function initGenreButtons() {
      const allGenres = [];
      BESTSELLERS_DATA.forEach(book => {
        if (book.태그) {
          const tags = book.태그.split(',').map(t => t.trim());
          tags.forEach(tag => {
            if (tag && !allGenres.includes(tag)) {
              allGenres.push(tag);
            }
          });
        }
      });
      
      // 상위 8개 카테고리만 드롭다운 바깥으로 꺼내기
      const container = document.getElementById('dynamic-tags');
      allGenres.slice(0, 8).forEach(genre => {
        const btn = document.createElement('button');
        btn.className = 'tag-btn';
        btn.innerText = genre;
        btn.setAttribute('data-genre', genre);
        btn.addEventListener('click', () => selectGenre(genre, btn));
        container.appendChild(btn);
      });
      
      // 태그 기본 전체보기 활성화
      document.querySelector('.tag-btn[data-genre="ALL"]').addEventListener('click', function() {
        selectGenre("ALL", this);
      });
    }

    // 장르 선택 변경
    function selectGenre(genre, element) {
      selectedGenre = genre;
      currentPage = 1;
      
      // 버튼 클래스 토글
      document.querySelectorAll('.tag-btn').forEach(btn => btn.classList.remove('active'));
      element.classList.add('active');
      
      applyFilters();
    }

    // 데이터 필터링 결합
    function applyFilters() {
      filteredData = BESTSELLERS_DATA.filter(book => {
        // 검색어 필터링
        const matchesSearch = searchKeyword === "" || 
          book.도서명.toLowerCase().includes(searchKeyword) ||
          book.저자.toLowerCase().includes(searchKeyword) ||
          book.출판사.toLowerCase().includes(searchKeyword);
          
        // 장르 필터링
        const matchesGenre = selectedGenre === "ALL" || 
          (book.태그 && book.태그.includes(selectedGenre));
          
        return matchesSearch && matchesGenre;
      });
      
      // 필터 상태 유지 정렬
      performSort();
      
      // UI 전면 업데이트
      updateKPIs();
      updateCharts();
      renderTable();
    }

    // KPI 카드 수치 업데이트
    function updateKPIs() {
      document.getElementById('kpi-total').innerText = `${filteredData.length}권`;
      
      if (filteredData.length === 0) {
        document.getElementById('kpi-price').innerText = '0원';
        document.getElementById('kpi-discount').innerText = '0%';
        document.getElementById('kpi-reviews').innerText = '0';
        return;
      }
      
      const totalPrice = filteredData.reduce((sum, item) => sum + item.정가, 0);
      const totalSale = filteredData.reduce((sum, item) => sum + item.할인가, 0);
      const avgPrice = Math.round(totalPrice / filteredData.length);
      const avgDiscount = Math.round(((totalPrice - totalSale) / totalPrice) * 100);
      const totalReviews = filteredData.reduce((sum, item) => sum + item.리뷰건수, 0);
      
      document.getElementById('kpi-price').innerText = `${avgPrice.toLocaleString()}원`;
      document.getElementById('kpi-discount').innerText = `${isNaN(avgDiscount) ? 0 : avgDiscount}%`;
      document.getElementById('kpi-reviews').innerText = `${totalReviews.toLocaleString()}건`;
    }

    // 차트 재생성 및 업데이트
    function updateCharts() {
      // 1. 출판사 차트 데이터
      const pubMap = {};
      filteredData.forEach(item => {
        pubMap[item.출판사] = (pubMap[item.출판사] || 0) + 1;
      });
      const topPubs = Object.entries(pubMap)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
      
      renderPublishersChart(topPubs.map(x => x[0]), topPubs.map(x => x[1]));

      // 2. 가격대 분포 데이터 (5,000원 구간)
      const priceBins = { "1만 미만": 0, "1.5만 미만": 0, "2만 미만": 0, "2.5만 미만": 0, "3만 미만": 0, "3만 이상": 0 };
      filteredData.forEach(item => {
        const pr = item.정가;
        if (pr < 10000) priceBins["1만 미만"]++;
        else if (pr < 15000) priceBins["1.5만 미만"]++;
        else if (pr < 20000) priceBins["2만 미만"]++;
        else if (pr < 25000) priceBins["2.5만 미만"]++;
        else if (pr < 30000) priceBins["3만 미만"]++;
        else priceBins["3만 이상"]++;
      });
      renderPricesChart(Object.keys(priceBins), Object.values(priceBins));

      // 3. 장르별 비중 데이터
      const genreMap = {};
      filteredData.forEach(item => {
        if (item.태그) {
          const tags = item.태그.split(',').map(t => t.trim());
          tags.forEach(tag => {
            if (tag) genreMap[tag] = (genreMap[tag] || 0) + 1;
          });
        }
      });
      const sortedGenres = Object.entries(genreMap)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
      
      const genreLabels = sortedGenres.map(x => x[0]);
      const genreData = sortedGenres.map(x => x[1]);
      const otherSum = Object.entries(genreMap)
        .sort((a, b) => b[1] - a[1])
        .slice(5)
        .reduce((sum, current) => sum + current[1], 0);
      
      if (otherSum > 0) {
        genreLabels.push("기타 장르");
        genreData.push(otherSum);
      }
      renderGenresChart(genreLabels, genreData);

      // 4. 상관관계 데이터 (평점 vs 리뷰)
      const scatterPoints = filteredData.map(item => ({
        x: item.평점,
        y: item.리뷰건수,
        title: item.도서명
      }));
      renderCorrelationChart(scatterPoints);
    }

    // Chart.js 1: 출판사 점유율 수평막대
    function renderPublishersChart(labels, data) {
      if (chartPublishers) chartPublishers.destroy();
      const ctx = document.getElementById('chart-publishers').getContext('2d');
      chartPublishers = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: '도서 등록 수 (권)',
            data: data,
            backgroundColor: 'rgba(0, 79, 47, 0.7)',
            borderColor: 'rgba(0, 79, 47, 1)',
            borderWidth: 1.5,
            borderRadius: 6
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: { grid: { display: false } },
            y: { grid: { display: false } }
          }
        }
      });
    }

    // Chart.js 2: 가격대 분포 곡선 영역
    function renderPricesChart(labels, data) {
      if (chartPrices) chartPrices.destroy();
      const ctx = document.getElementById('chart-prices').getContext('2d');
      chartPrices = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: '도서 수 (권)',
            data: data,
            fill: true,
            backgroundColor: 'rgba(191, 163, 138, 0.3)',
            borderColor: 'rgba(191, 163, 138, 1)',
            borderWidth: 2,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { display: false } },
            y: { grid: { display: true, color: 'rgba(0, 0, 0, 0.05)' } }
          }
        }
      });
    }

    // Chart.js 3: 장르 비중 도넛
    function renderGenresChart(labels, data) {
      if (chartGenres) chartGenres.destroy();
      const ctx = document.getElementById('chart-genres').getContext('2d');
      chartGenres = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            data: data,
            backgroundColor: [
              '#004F2F',
              '#1b6844',
              '#37825b',
              '#BF9E7B',
              '#DFCEBA',
              '#888888'
            ],
            borderWidth: 2,
            borderColor: '#ffffff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right',
              labels: { boxWidth: 12, font: { size: 10 } }
            }
          }
        }
      });
    }

    // Chart.js 4: 상관관계 분포도
    function renderCorrelationChart(points) {
      if (chartCorrelation) chartCorrelation.destroy();
      const ctx = document.getElementById('chart-correlation').getContext('2d');
      chartCorrelation = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [{
            label: '도서 개체 분포',
            data: points,
            backgroundColor: 'rgba(0, 79, 47, 0.6)',
            borderColor: 'rgba(0, 79, 47, 0.8)',
            borderWidth: 1,
            pointRadius: 6,
            pointHoverRadius: 8
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const pt = context.raw;
                  return `${pt.title} (평점: ${pt.x}점, 리뷰: ${pt.y}건)`;
                }
              }
            }
          },
          scales: {
            x: {
              title: { display: true, text: '독자 만족도 평점 (점)', font: { size: 10 } },
              min: 0,
              max: 10,
              grid: { display: false }
            },
            y: {
              title: { display: true, text: '리뷰 수 (건)', font: { size: 10 } },
              grid: { color: 'rgba(0, 0, 0, 0.05)' }
            }
          }
        }
      });
    }

    // 테이블 렌더링
    function renderTable() {
      const tbody = document.getElementById('table-body');
      tbody.innerHTML = '';
      
      const totalRows = filteredData.length;
      document.getElementById('row-count-info').innerText = `총 99건 중 ${totalRows}건 표시`;
      
      if (totalRows === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center" style="padding: 3rem; color: var(--text-muted);">검색 및 필터 조건에 부합하는 도서가 없습니다.</td></tr>`;
        document.getElementById('page-info').innerText = '0 / 0 페이지';
        document.getElementById('btn-prev').disabled = true;
        document.getElementById('btn-next').disabled = true;
        return;
      }
      
      const totalPages = Math.ceil(totalRows / itemsPerPage);
      if (currentPage > totalPages) currentPage = totalPages;
      
      const startIdx = (currentPage - 1) * itemsPerPage;
      const endIdx = Math.min(startIdx + itemsPerPage, totalRows);
      
      const pageData = filteredData.slice(startIdx, endIdx);
      
      pageData.forEach(book => {
        const tr = document.createElement('tr');
        tr.addEventListener('click', () => openModal(book));
        
        tr.innerHTML = `
          <td class="text-center" style="font-weight: 700; color: var(--color-primary);">${book.순위}</td>
          <td style="font-weight: 600; text-align: left; max-width: 400px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${book.도서명}</td>
          <td style="color: #555555;">${book.저자 || '-'}</td>
          <td style="color: #666666;">${book.출판사 || '-'}</td>
          <td class="text-center" style="font-family: 'Outfit', sans-serif; font-weight: 600;">${book.할인가.toLocaleString()}원</td>
          <td class="text-center"><span class="rating-badge">★ ${book.평점.toFixed(2)}</span></td>
          <td class="text-center" style="font-family: 'Outfit', sans-serif; color: var(--text-muted);">${book.리뷰건수.toLocaleString()}건</td>
        `;
        tbody.appendChild(tr);
      });
      
      // 페이징 라벨 및 버튼 상태
      document.getElementById('page-info').innerText = `${currentPage} / ${totalPages} 페이지`;
      document.getElementById('btn-prev').disabled = (currentPage === 1);
      document.getElementById('btn-next').disabled = (currentPage === totalPages);
    }

    // 테이블 헤더 정렬
    function sortTable(key) {
      if (sortConfig.key === key) {
        sortConfig.asc = !sortConfig.asc;
      } else {
        sortConfig.key = key;
        sortConfig.asc = true;
      }
      
      // 헤더 활성 표시 클래스 설정
      document.querySelectorAll('th').forEach(th => th.classList.remove('sort-active', 'asc'));
      const activeTh = document.getElementById(`th-${key}`);
      if (activeTh) {
        activeTh.classList.add('sort-active');
        if (sortConfig.asc) activeTh.classList.add('asc');
      }
      
      currentPage = 1;
      performSort();
      renderTable();
    }

    // 실제 정렬 동작
    function performSort() {
      filteredData.sort((a, b) => {
        let valA = a[sortConfig.key];
        let valB = b[sortConfig.key];
        
        // 수치형 변수 비교
        if (typeof valA === 'number' && typeof valB === 'number') {
          return sortConfig.asc ? valA - valB : valB - valA;
        }
        
        // 문자열 비교
        return sortConfig.asc ? 
          String(valA).localeCompare(String(valB)) : 
          String(valB).localeCompare(String(valA));
      });
    }

    // 페이지 변경
    function changePage(direction) {
      currentPage += direction;
      renderTable();
    }

    // 상세 보기 모달 제어
    function openModal(book) {
      document.getElementById('modal-book-name').innerText = book.도서명;
      document.getElementById('modal-author').innerText = book.저자 || '미상';
      document.getElementById('modal-publisher').innerText = book.출판사 || '미상';
      document.getElementById('modal-date').innerText = book.출판일 || '-';
      document.getElementById('modal-price').innerText = `${book.정가.toLocaleString()}원`;
      document.getElementById('modal-sale-price').innerText = `${book.할인가.toLocaleString()}원 (할인율: ${book.할인율}%)`;
      document.getElementById('modal-satisfaction').innerText = `★ ${book.평점.toFixed(2)}점 / 누적 리뷰 ${book.리뷰건수.toLocaleString()}건`;
      document.getElementById('modal-desc').innerText = book.부제목 || '도서 세부 요약 소개 정보가 제공되지 않습니다.';
      
      const img = document.getElementById('modal-img');
      img.src = book.이미지URL || 'https://contents.kyobobook.co.kr/resources/images/common/no_image.gif';
      
      toggleModal(true);
    }

    function toggleModal(show) {
      const modal = document.getElementById('detail-modal');
      if (show) {
        modal.classList.add('active');
      } else {
        modal.classList.remove('active');
      }
    }

    function closeModal(event) {
      // 오버레이 클릭 시만 닫기
      if (event.target.id === 'detail-modal') {
        toggleModal(false);
      }
    }
  </script>
</body>
</html>"""
    
    # 4. JSON 치환 주입 및 빌드 저장
    final_html = html_template.replace("/*{{BOOK_DATA_JSON}}*/", books_json)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html)
        
    print(f"\n[빌드 완료] 인터랙티브 대시보드 웹앱이 {output_path} 경로에 작성되었습니다!")

if __name__ == "__main__":
    build_dashboard()
