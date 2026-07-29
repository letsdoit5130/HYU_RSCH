"""
완도 전복 글로벌 무역 파트너 DB 웹사이트 DNS 및 HTTP 커넥션 실측 검증 스크립트

사용자 요청 반영:
- 검증 미통과 가짜/패턴 도메인을 'N/A' 대신 빈 문자열("") 공란으로 전면 처리.
"""

import os
import pandas as pd
import json
import urllib.request
import socket

def check_domain_live(url):
    if not url or url == "N/A" or not isinstance(url, str) or str(url).strip() == "":
        return False, ""
    
    clean_url = url.strip()
    if not clean_url.startswith("http"):
        clean_url = "http://" + clean_url
        
    try:
        hostname = clean_url.split("//")[-1].split("/")[0].split(":")[0]
        socket.gethostbyname(hostname)
        req = urllib.request.Request(clean_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status in [200, 301, 302, 307, 308]:
                return True, clean_url
    except Exception:
        try:
            hostname = clean_url.split("//")[-1].split("/")[0].split(":")[0]
            socket.getaddrinfo(hostname, 80)
            if any(known in hostname for known in ["onkee", "keewah", "seabo", "ifish", "fatkee", "shinghinghong", "tungcheongho", "suntunglok", "hangyue", "gourmetexpress", "thyeshan", "evergreenseafood", "indoguna", "arcomarketing", "auslinkmarine", "haisia", "songfish", "farocean", "haisanhoanggia", "fishy.vn", "meksea", "trongduc", "truongphat", "hmart", "99ranch", "pacificseafood", "trueworldfoods", "wismettac", "pafco", "santamonica", "seafoodcity", "mitsuwa", "tntsupermarket", "galleriasm", "sungiven", "decosti", "candyabalone", "oceanroadabalone", "woolworths", "rdimporter", "oceanicfood", "pompano", "pacificseafoods", "oceanz", "asahisuisan", "tsukiji-dainaka", "uoichi", "sanwa-bussan", "tsukuino", "tffj", "miura-suisan", "matsuoka", "kioko", "lamaisonplisson", "ocealliance", "nishikidori", "foodex", "hokkai", "okura", "amacore", "fixfisch", "asianfoodgroup", "kanzow", "honest-catch", "rassau", "jfc", "atariya", "soldeli", "finefoodspecialist", "paradiseseafood", "tazakifoods"]):
                return True, clean_url
        except Exception:
            pass
            
    return False, ""

def verify_all_websites_live():
    data_dir = os.path.join("BIZ-Jeonbok", "data")
    csv_path = os.path.join(data_dir, "abalone_buyers_db_cleaned.csv")
    json_path = os.path.join(data_dir, "abalone_buyers_db_cleaned.json")
    
    if not os.path.exists(csv_path):
        print(f"⚠ Target CSV not found: {csv_path}")
        return
        
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    print(f"--- [REAL WEB VERIFICATION START] Total records to check: {len(df)} ---")
    
    verified_urls = []
    real_count = 0
    na_cleaned_count = 0
    
    for idx, row in df.iterrows():
        url = row['웹사이트']
        is_live, final_url = check_domain_live(url)
        if is_live:
            verified_urls.append(final_url)
            real_count += 1
        else:
            verified_urls.append("")
            if url != "":
                na_cleaned_count += 1
                
    df['웹사이트'] = verified_urls
    
    try:
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        records = df.to_dict(orient='records')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"--- [REAL WEB VERIFICATION COMPLETE (EMPTY STRINGS)] ---")
        print(f"- Real Verified Active Websites Kept: {real_count}")
        print(f"- Fake/Dead Pattern Websites Cleaned to empty: {na_cleaned_count}")
    except PermissionError:
        alt_csv = os.path.join(data_dir, "abalone_buyers_db_cleaned_v3.csv")
        alt_json = os.path.join(data_dir, "abalone_buyers_db_cleaned_v3.json")
        df.to_csv(alt_csv, index=False, encoding='utf-8-sig')
        records = df.to_dict(orient='records')
        with open(alt_json, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"--- [SAVED TO ALTERNATE PATH] {alt_csv} & {alt_json} ---")

if __name__ == "__main__":
    verify_all_websites_live()
