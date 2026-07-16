# 데이터 수집에 꼭 필요한 핵심 정보

## 네트워크 메뉴를 통해 실제 데이터를 가져오는 URL

```
https://store.kyobobook.co.kr/api/gw/best/best-seller/realtime?page=1&per=50
```

## 해당 Request에 대한 Header 정보

```json
{
  "sec-ch-ua-platform": "\"Windows\"",
  "referer": "https://store.kyobobook.co.kr/bestseller/realtime?page=1&per=50",
  "sec-ch-ua": "\"HeadlessChrome\";v=\"149\", \"Chromium\";v=\"149\", \"Not)A;Brand\";v=\"24\"",
  "sec-ch-ua-mobile": "?0",
  "x-api-gw-key": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..46i-NsIUjJggOjej.GukKPz3OyKam4iWzXeBoLGQDKlA7thzNqM2WBclON-AUoUi_7K2DUeOp4l8HrgdbhQqRIkPAZ8J0S626Dp4Matl5OZoESE8x_nnBGDTXHRf9AC5zzfI2WvYgFLjMIpw82k6x9rYt.wzusaQ0rM7PIHvpOZAciYA",
  "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/149.0.7827.55 Safari/537.36",
  "content-type": "application/json",
  "sec-ch-ua-platform-version": "\"19.0.0\""
}
```

HTTP 요청 정보 중 보안 통과를 위해 가장 중요한 정보는 `x-api-gw-key` 헤더입니다. 이 헤더가 없을 경우 `401 Unauthorized` 에러를 반환합니다.

## Payload

- GET 요청 방식을 사용하므로 POST Payload는 존재하지 않고 Query String 파라미터를 그대로 사용합니다.

## 응답 예시 (JSON 데이터의 일부 정보)

데이터를 수집(크롤링 또는 API 호출)할 때마다 실제 요청 정보(URL, Header, Payload)와 응답 구조를 기반으로 파이썬 스크래핑 코드를 안전하게 작성합니다.
