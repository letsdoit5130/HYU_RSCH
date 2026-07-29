# 완도 전복 글로벌 15개국 825개사 파트너 DB 수집 및 24대 컬럼 엄격 실측 검증 Implementation Plan

## 1. 개요 (Overview)
완도 전복의 글로벌 15대 유망국가(홍콩, 싱가포르, 베트남, 마카오, 대만, 말레이시아, 태국, 미국, 캐나다, 호주, 일본, 프랑스, 네덜란드, 독일, 영국)를 대상으로 수산물 수입상, 아시안 마트 체인, HORECA 벤더, 미슐랭 식자재상 825개사의 24대 표준 스키마 데이터를 정밀 수집하고, 2단계 실측 통신/팩트 검증 파이프라인을 통하여 100% 신뢰할 수 있는 파트너 데이터베이스 및 5대 산출물을 자동 구축합니다.

---

## 2. 24대 표준 스키마 및 증빙/검증 규격

| 순번 | 컬럼명 | 설명 및 검증 기준 |
|:---:|:---|:---|
| 1 | 데이터 수집일 | 데이터 수집 연월일 (YYYY-MM-DD) |
| 2 | 데이터 검증일 | 2단계 실측 검증 완료 연월일 (YYYY-MM-DD) |
| 3 | 취급 품목 | @BIZ-Jeonbok/BIZ-JB-Gathered.csv 지정 HS코드 및 제품군 |
| 4 | 회사명 (사명만) | 순수 기업명 (국가명 접두사 및 '#' 기호 100% 제거) |
| 5 | Prf_CName | 사명 수집 출처 웹사이트 링크 (공식 수산 무역 디렉토리 URL) |
| 6 | Ver_CName | 100% 팩트 확인된 실체 기업만 `O` 할당 (검색 URL 등은 무효화 및 공란) |
| 7 | 웹사이트 | 공식 웹사이트 URL (미존재 시 공란) |
| 8 | Prf_CWeb | 웹사이트 출처 링크 |
| 9 | Ver_CWeb | 실제 HTTP `200/301/302` 커넥션 성공 시 `O` 할당 (접속불능 시 공란) |
| 10 | 컨택 이메일 | 공식 컨택 이메일 주소 (미존재 시 공란) |
| 11 | Prf_Email | 이메일 수집 출처 웹사이트 링크 |
| 12 | Ver_Email | 이메일 유효성 확인 시 `O` 할당 (미검증 시 공란) |
| 13 | 회사 위치한 도시 | 기업 본사/물류센터 소재 도시 |
| 14 | 회사 위치한 지방 | 기업 소재 주/지방 (Province/State) |
| 15 | 회사 위치한 국가 | 15대 타겟 국가명 |
| 16 | Messanger | WhatsApp, LINE, Zalo, WeChat 메신저 정보 |
| 17 | Prf_Msg | 메신저 수집 증빙 출처 링크 |
| 18 | Ver_Msg | 메신저 실존 및 유효 번호/채널 확인 시 `O` 할당 |
| 19 | SNS | LinkedIn, Facebook, Instagram 소셜 프로필 |
| 20 | Prf_SNS | SNS 수집 증빙 출처 링크 |
| 21 | Ver_SNS | SNS 프로필 실제 접속 확인 시 `O` 할당 |
| 22 | 회사 소개 | 현지 업태 및 비즈니스 특징 상세 설명 |
| 23 | 추천 수출물품 및 수출가 | 타겟 추천 수출 품목 및 CIF 단가 |
| 24 | Verified_CINFO | 구글 지도(Google Maps) 실시간 오프라인 위치 확인 링크 |

---

## 3. 서브에이전트 계층 구조 (Two-Stage Subagent Architecture)

### 1단계: 수집 서브에이전트 (Subagents 1~6)
* **Subagent 1**: 중화권 (홍콩, 마카오, 대만) 수산물/건재상 바이어 수집
* **Subagent 2**: 동남아 (싱가포르, 베트남, 말레이시아, 태국) 수산 유통상 수집
* **Subagent 3**: 북미 (미국, 캐나다) 아시안 리테일 & HORECA 벤더 수집
* **Subagent 4**: 오세아니아 (호주, 뉴질랜드) 수산 임포터 및 델리 수집
* **Subagent 5**: 동아시아 (일본 도쿄 토요스, 오사카 시장) 횟감 전복 벤더 수집
* **Subagent 6**: 서유럽 (프랑스, 네덜란드, 독일, 영국) 미슐랭 & 럭셔리 델리 수집

### 2단계: 엄격 검증 서브에이전트 (Verification Subagents 1~4)
* **Verification Subagent 1**: HTTP GET 핑 통신을 통한 웹사이트 도메인 실존성 실측 (`verify_real_web.py`)
* **Verification Subagent 2**: 컨택 이메일 및 B2B 문의 폼 유효성 실측
* **Verification Subagent 3**: 메신저 및 SNS 공식 프로필 실존성 실측
* **Verification Subagent 4**: 사명 100% 매칭 및 오탐(`google.com/search`) 무효화 엄격 클리닝 (`verify_buyers.py`)

---

## 4. 파이프라인 프로세스 (Pipeline Execution Flow)

```
crawler_buyer.py (825개사 24대 컬럼 파트너 DB 생성)
       ↓
verify_real_web.py (HTTP GET 커넥션 실측 및 접속불능 사이트 공란 정제)
       ↓
verify_buyers.py (사명 100% 매칭 및 Ver_* 'O' 배지 엄격 부여)
       ↓
make_xlsx_data.py (openpyxl 기반 24대 컬럼 Excel 데이터북 생성)
       ↓
make_html_dashboard.py (24대 컬럼 및 📍 구글지도 위치확인 대시보드 생성)
       ↓
make_full_docx_report.py & make_pptx_deck.py (통합 보고서 및 발표자료 동기화)
```

---

## 5. 정제 및 품질 보장 규칙 (Data Quality Rules)
1. **사명 기호 제거**: 사명 뒤 `#` 번호표시 100% 전면 삭제.
2. **부재 데이터 공란 처리**: `N/A` 표기를 전면 제거하고 완전 공란(`""`)으로 일관성 유지.
3. **구글 검색 URL 무효화**: `google.com/search` 패턴 주소를 증빙에서 차단하고, 100% 팩트 확인된 실체 기업만 `O` 할당.
4. **오프라인 지리 검증**: 맨 오른쪽 `Verified_CINFO` 컬럼으로 구글 지도 오프라인 매장/사무실 조회를 바로 지원.
