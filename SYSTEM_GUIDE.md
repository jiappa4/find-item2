# 🚀 가격 비교 시스템 - 전체 가이드

## 📋 시스템 구조

```
find-item2/
├── backend/                 # 백엔드 시스템
│   ├── scraper.py          # 웹 스크래핑 배치
│   ├── api_server.py       # Flask API 서버
│   ├── prices.db           # SQLite 데이터베이스
│   ├── requirements.txt    # Python 패키지
│   ├── setup.bat          # 환경 설정
│   ├── run_scraper.bat    # 배치 실행
│   └── run_api.bat        # API 서버 실행
└── index.html             # 프론트엔드 (웹 UI)
```

## 🎯 작동 방식

### 1단계: 배치로 가격 수집
```
scraper.py 실행
    ↓
네이버쇼핑, 쿠팡, G마켓에서 가격 크롤링
    ↓
SQLite DB에 저장 (prices.db)
    ↓
JSON 파일 생성 (백업용)
```

### 2단계: API 서버 제공
```
api_server.py 실행
    ↓
http://localhost:5000/api
    ↓
DB에서 데이터 조회
    ↓
JSON 형식으로 반환
```

### 3단계: 웹 UI에서 검색
```
index.html 열기
    ↓
검색어 입력
    ↓
API 호출
    ↓
결과 표시 (최저가 순 정렬)
```

## 🔧 설치 및 실행

### Step 1: 백엔드 환경 설정

```cmd
cd C:\Users\netwo\Documents\find-item2\backend
setup.bat
```

이 명령어가 자동으로:
- Python 가상환경 생성
- 필요한 패키지 설치 (Selenium, Flask 등)
- Chrome 드라이버 설정

### Step 2: 가격 수집 배치 실행

```cmd
cd C:\Users\netwo\Documents\find-item2\backend
run_scraper.bat
```

**수집 대상 설정:**
`scraper.py` 파일 하단 수정:
```python
search_queries = [
    "신일 팬히터 1200",
    "다이슨 청소기",
    "삼성 갤럭시 버즈"
]
```

### Step 3: API 서버 실행

```cmd
cd C:\Users\netwo\Documents\find-item2\backend
run_api.bat
```

서버 주소: `http://localhost:5000`

### Step 4: 웹 UI 열기

**방법 1: 직접 열기**
```
C:\Users\netwo\Documents\find-item2\index.html 더블클릭
```

**방법 2: 로컬 서버 (권장)**
```cmd
cd C:\Users\netwo\Documents\find-item2
python -m http.server 8000
# 브라우저: http://localhost:8000
```

## 📊 API 엔드포인트

### 1. 상품 검색
```
GET /api/search?q=검색어

응답:
{
  "query": "신일 팬히터 1200",
  "count": 15,
  "summary": {
    "totalCount": 15,
    "lowestPrice": 38900,
    "avgPrice": 42500,
    "freeShippingRate": 40
  },
  "products": [...]
}
```

### 2. 전체 상품 목록
```
GET /api/products

응답:
{
  "queries": [
    {
      "query": "신일 팬히터 1200",
      "count": 15,
      "lastUpdated": "2025-11-07 10:30:00"
    }
  ]
}
```

### 3. 통계 정보
```
GET /api/stats

응답:
{
  "totalProducts": 45,
  "totalQueries": 3,
  "shopStats": [...],
  "lastUpdate": "2025-11-07 10:30:00"
}
```

### 4. 헬스 체크
```
GET /api/health

응답:
{
  "status": "healthy",
  "timestamp": "2025-11-07T10:30:00"
}
```

## 🔄 정기 배치 실행

### Windows 작업 스케줄러 설정

1. **작업 스케줄러 열기**
   - Win + R → `taskschd.msc`

2. **작업 만들기**
   - 이름: "가격 수집 배치"
   - 트리거: 매일 오전 9시
   - 동작: `C:\Users\netwo\Documents\find-item2\backend\run_scraper.bat`

3. **완료**
   - 매일 자동으로 최신 가격 수집

## 🎨 커스터마이징

### 검색 대상 추가
`backend/scraper.py`:
```python
search_queries = [
    "신일 팬히터 1200",
    "추가할 상품명 1",
    "추가할 상품명 2"
]
```

### 쇼핑몰 추가
`backend/scraper.py`에 새 메서드 추가:
```python
def scrape_11st(self, query):
    # 11번가 스크래핑 로직
    pass
```

### UI 테마 변경
`index.html` CSS 부분:
```html
<style>
    /* 색상 테마 변경 */
    .bg-gradient-to-br {
        background: linear-gradient(135deg, #your-color-1, #your-color-2);
    }
</style>
```

## 📦 데이터베이스 구조

### products 테이블
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    search_query TEXT,      -- 검색어
    shop TEXT,              -- 쇼핑몰명
    name TEXT,              -- 상품명
    option_name TEXT,       -- 옵션
    original_price INTEGER, -- 정가
    discount_price INTEGER, -- 할인가
    shipping_fee INTEGER,   -- 배송비
    final_price INTEGER,    -- 최저실현가
    link TEXT,              -- 상품 링크
    image_url TEXT,         -- 이미지 URL
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## 🐛 문제 해결

### 1. API 서버 연결 안 됨
**증상:** "API 서버가 실행되지 않았습니다"
**해결:**
```cmd
cd backend
run_api.bat
```

### 2. 스크래핑 실패
**증상:** "수집된 상품이 없습니다"
**해결:**
- Chrome 브라우저 업데이트
- 인터넷 연결 확인
- `scraper.py`의 CSS 선택자 확인 (쇼핑몰 구조 변경 시)

### 3. 검색 결과 없음
**증상:** "검색 결과가 없습니다"
**해결:**
- 배치 먼저 실행: `run_scraper.bat`
- DB 파일 확인: `backend/prices.db`

### 4. CORS 오류
**증상:** "CORS policy blocked"
**해결:**
- API 서버에 CORS 설정 확인
- 로컬 서버로 웹 실행 (파일:// 대신 http://)

## 📈 성능 최적화

### 스크래핑 속도 개선
```python
# scraper.py에서 병렬 처리
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(self.scrape_naver_shopping, query),
        executor.submit(self.scrape_coupang, query),
        executor.submit(self.scrape_gmarket, query)
    ]
```

### DB 인덱스 최적화
```sql
CREATE INDEX idx_search_query ON products(search_query);
CREATE INDEX idx_final_price ON products(final_price);
CREATE INDEX idx_updated_at ON products(updated_at);
```

## 🚀 프로덕션 배포

### 옵션 1: GitHub Pages (프론트엔드만)
- 정적 페이지 호스팅
- API는 별도 서버 필요

### 옵션 2: Heroku (전체 스택)
```bash
# Procfile 생성
web: cd backend && python api_server.py
worker: cd backend && python scraper.py
```

### 옵션 3: AWS/Azure (추천)
- EC2/VM에 백엔드 배포
- S3/Blob Storage에 프론트엔드 호스팅
- RDS/SQL Database로 DB 마이그레이션

## 📝 향후 개선 사항

- [ ] 더 많은 쇼핑몰 지원 (11번가, 옥션, 인터파크)
- [ ] 가격 히스토리 추적
- [ ] 가격 하락 알림 (이메일/카카오톡)
- [ ] 모바일 앱 개발
- [ ] 사용자 인증 시스템
- [ ] 위시리스트 기능
- [ ] 가격 예측 AI

## 🤝 기여

이슈와 PR을 환영합니다!

## 📄 라이선스

MIT License

---

**문의:** [@jiappa4](https://github.com/jiappa4)
