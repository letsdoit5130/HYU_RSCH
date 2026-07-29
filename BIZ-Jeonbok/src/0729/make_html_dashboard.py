"""
완도 전복 글로벌 무역 15대 유망국가 825개사 실존 파트너 대시보드 HTML 생성 스크립트

사용자 요청 반영:
1. 메신저 및 SNS 증빙/검증 컬럼(Prf_Msg, Ver_Msg, Prf_SNS, Ver_SNS) 추가 반영.
2. 24대 필수 표준 스키마 렌더링.
3. 실제 접속 가능한 100% 매칭 항목만 'O' 배지 표시.
"""

import os
import pandas as pd
import json

def build_html_dashboard():
    output_dir = os.path.join("BIZ-Jeonbok", "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    csv_path = os.path.join("BIZ-Jeonbok", "data", "abalone_buyers_db_cleaned.csv")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, dtype=str).fillna("")
        data_json = df.to_json(orient="records", force_ascii=False)
    else:
        data_json = "[]"
        
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>완도 전복 글로벌 15개국 24대 컬럼 실존 바이어 대시보드</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #f8fafc; font-family: 'Pretendard', sans-serif; color: #1e293b; }}
        .header-bg {{ background: linear-gradient(135deg, #0f172a 0%, #0284c7 100%); color: white; padding: 2.5rem 0; margin-bottom: 2rem; border-radius: 0 0 1rem 1rem; }}
        .card-custom {{ border: none; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 1.5rem; background: white; }}
        .table-responsive {{ max-height: 750px; overflow-y: auto; }}
        th {{ background-color: #f1f5f9 !important; color: #334155; font-size: 11px; position: sticky; top: 0; z-index: 10; white-space: nowrap; }}
        td {{ font-size: 11px; vertical-align: middle; white-space: nowrap; }}
        .badge-country {{ background-color: #e0f2fe; color: #0369a1; font-weight: 600; padding: 3px 6px; border-radius: 4px; }}
        .badge-item {{ background-color: #f0fdf4; color: #166534; font-weight: 600; padding: 3px 6px; border-radius: 4px; }}
        .badge-ok {{ background-color: #dcfce7; color: #15803d; font-weight: 700; padding: 2px 6px; border-radius: 4px; display: inline-block; }}
        .btn-gmaps {{ background-color: #2563eb; color: white; font-weight: 600; font-size: 10px; padding: 3px 6px; border-radius: 4px; text-decoration: none; display: inline-block; }}
        .btn-gmaps:hover {{ background-color: #1d4ed8; color: white; }}
    </style>
</head>
<body>
    <div class="header-bg text-center">
        <h1 class="fw-bold">완도 전복 글로벌 15개국 24대 컬럼 실존 바이어 대시보드</h1>
        <p class="lead mb-0">사명·웹·이메일·메신저·SNS 5대 영역 증빙링크(Prf) 및 엄격 실존검증(Ver = O) 100% 반영</p>
    </div>

    <div class="container-fluid px-4">
        <div class="card card-custom p-4">
            <div class="row g-3 align-items-center mb-3">
                <div class="col-md-3">
                    <label class="form-label fw-bold">국가 선택</label>
                    <select id="countryFilter" class="form-select" onchange="filterData()">
                        <option value="ALL">전체 15개국 (825개사)</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label fw-bold">품목 선택</label>
                    <select id="itemFilter" class="form-select" onchange="filterData()">
                        <option value="ALL">전체 품목</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label fw-bold">통합 검색</label>
                    <input type="text" id="searchInput" class="form-control" placeholder="사명, 도시, 증빙링크 검색..." onkeyup="filterData()">
                </div>
                <div class="col-md-2 text-end">
                    <span id="recordCount" class="badge bg-primary fs-6">총 0개 바이어</span>
                </div>
            </div>

            <div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead>
                        <tr>
                            <th>수집일</th>
                            <th>검증일</th>
                            <th>취급 품목</th>
                            <th>회사명 (사명만)</th>
                            <th>Prf_CName</th>
                            <th>Ver_CName</th>
                            <th>웹사이트</th>
                            <th>Prf_CWeb</th>
                            <th>Ver_CWeb</th>
                            <th>컨택 이메일</th>
                            <th>Prf_Email</th>
                            <th>Ver_Email</th>
                            <th>도시</th>
                            <th>지방</th>
                            <th>국가</th>
                            <th>Messanger</th>
                            <th>Prf_Msg</th>
                            <th>Ver_Msg</th>
                            <th>SNS</th>
                            <th>Prf_SNS</th>
                            <th>Ver_SNS</th>
                            <th>회사 소개</th>
                            <th>추천 수출물품 및 수출가</th>
                            <th>Verified_CINFO</th>
                        </tr>
                    </thead>
                    <tbody id="buyerTableBody">
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const rawData = {data_json};
        
        function initFilters() {{
            const countrySet = new Set();
            const itemSet = new Set();
            
            rawData.forEach(r => {{
                if (r["회사 위치한 국가"]) countrySet.add(r["회사 위치한 국가"]);
                if (r["취급 품목"]) itemSet.add(r["취급 품목"]);
            }});
            
            const countrySelect = document.getElementById("countryFilter");
            countrySet.forEach(c => {{
                const opt = document.createElement("option");
                opt.value = c; opt.innerText = c;
                countrySelect.appendChild(opt);
            }});
            
            const itemSelect = document.getElementById("itemFilter");
            itemSet.forEach(i => {{
                const opt = document.createElement("option");
                opt.value = i; opt.innerText = i;
                itemSelect.appendChild(opt);
            }});
            
            filterData();
        }}

        function filterData() {{
            const countryVal = document.getElementById("countryFilter").value;
            const itemVal = document.getElementById("itemFilter").value;
            const searchVal = document.getElementById("searchInput").value.toLowerCase();
            
            const filtered = rawData.filter(r => {{
                const matchCountry = (countryVal === "ALL" || r["회사 위치한 국가"] === countryVal);
                const matchItem = (itemVal === "ALL" || r["취급 품목"] === itemVal);
                const matchSearch = !searchVal || 
                    (r["회사명 (사명만)"] && r["회사명 (사명만)"].toLowerCase().includes(searchVal)) ||
                    (r["회사 위치한 도시"] && r["회사 위치한 도시"].toLowerCase().includes(searchVal)) ||
                    (r["Prf_CName"] && r["Prf_CName"].toLowerCase().includes(searchVal));
                return matchCountry && matchItem && matchSearch;
            }});
            
            renderTable(filtered);
        }}

        function renderTable(data) {{
            const tbody = document.getElementById("buyerTableBody");
            tbody.innerHTML = "";
            document.getElementById("recordCount").innerText = `총 ${{data.length}}개 바이어`;
            
            data.forEach(r => {{
                const tr = document.createElement("tr");
                
                const prfCNameLink = r["Prf_CName"] 
                    ? `<a href="${{r["Prf_CName"]}}" target="_blank" class="text-decoration-none" style="color:#0284c7;">🔗 사명증빙</a>` : '';
                const prfCWebLink = r["Prf_CWeb"] 
                    ? `<a href="${{r["Prf_CWeb"]}}" target="_blank" class="text-decoration-none" style="color:#0284c7;">🔗 웹증빙</a>` : '';
                const prfEmailLink = r["Prf_Email"] 
                    ? `<a href="${{r["Prf_Email"]}}" target="_blank" class="text-decoration-none" style="color:#0284c7;">🔗 이메일증빙</a>` : '';
                const prfMsgLink = r["Prf_Msg"] 
                    ? `<a href="${{r["Prf_Msg"]}}" target="_blank" class="text-decoration-none" style="color:#0284c7;">🔗 메신저증빙</a>` : '';
                const prfSnsLink = r["Prf_SNS"] 
                    ? `<a href="${{r["Prf_SNS"]}}" target="_blank" class="text-decoration-none" style="color:#0284c7;">🔗 SNS증빙</a>` : '';
                    
                const verCNameBadge = r["Ver_CName"] === "O" ? '<span class="badge-ok">O</span>' : '';
                const verCWebBadge = r["Ver_CWeb"] === "O" ? '<span class="badge-ok">O</span>' : '';
                const verEmailBadge = r["Ver_Email"] === "O" ? '<span class="badge-ok">O</span>' : '';
                const verMsgBadge = r["Ver_Msg"] === "O" ? '<span class="badge-ok">O</span>' : '';
                const verSnsBadge = r["Ver_SNS"] === "O" ? '<span class="badge-ok">O</span>' : '';
                
                const webVal = r["웹사이트"] 
                    ? `<a href="${{r["웹사이트"]}}" target="_blank" class="text-decoration-none fw-bold" style="color:#0369a1;">${{r["웹사이트"]}}</a>` : '';
                const emailVal = r["컨택 이메일"] 
                    ? `<a href="mailto:${{r["컨택 이메일"]}}" class="text-decoration-none" style="color:#334155;">${{r["컨택 이메일"]}}</a>` : '';
                const cinfoVal = r["Verified_CINFO"] 
                    ? `<a href="${{r["Verified_CINFO"]}}" target="_blank" class="btn-gmaps">📍 구글지도 위치확인</a>` : '';

                tr.innerHTML = `
                    <td>${{r["데이터 수집일"] || ""}}</td>
                    <td><span class="badge bg-success">${{r["데이터 검증일"] || ""}}</span></td>
                    <td><span class="badge-item">${{r["취급 품목"] || ""}}</span></td>
                    <td><strong>${{r["회사명 (사명만)"] || ""}}</strong></td>
                    <td>${{prfCNameLink}}</td>
                    <td>${{verCNameBadge}}</td>
                    <td>${{webVal}}</td>
                    <td>${{prfCWebLink}}</td>
                    <td>${{verCWebBadge}}</td>
                    <td>${{emailVal}}</td>
                    <td>${{prfEmailLink}}</td>
                    <td>${{verEmailBadge}}</td>
                    <td>${{r["회사 위치한 도시"] || ""}}</td>
                    <td>${{r["회사 위치한 지방"] || ""}}</td>
                    <td><span class="badge-country">${{r["회사 위치한 국가"] || ""}}</span></td>
                    <td>${{r["Messanger (WhatsApp, Line, Zalo and etc)"] || ""}}</td>
                    <td>${{prfMsgLink}}</td>
                    <td>${{verMsgBadge}}</td>
                    <td>${{r["SNS (Linkedin, Instagram, Facebook etc)"] || ""}}</td>
                    <td>${{prfSnsLink}}</td>
                    <td>${{verSnsBadge}}</td>
                    <td style="color:#475569;">${{r["회사 소개"] || ""}}</td>
                    <td style="color:#0369a1; font-weight:600;">${{r["추천 수출물품 및 수출가"] || ""}}</td>
                    <td>${{cinfoVal}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        window.onload = initFilters;
    </script>
</body>
</html>"""

    html_file = os.path.join(output_dir, "Wando_Abalone_Dashboard.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"--- UPDATED HTML DASHBOARD WITH 24 COLS GENERATED SUCCESSFULLY: {html_file} ---")

if __name__ == "__main__":
    build_html_dashboard()
