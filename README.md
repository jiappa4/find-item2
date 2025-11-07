# 가격 비교 도구 🔍

한국 주요 쇼핑몰의 상품 가격을 직접 입력하여 최저가를 비교하는 실용적인 웹 도구입니다.

![Version](https://img.shields.io/badge/version-2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🌐 라이브 데모

**https://jiappa4.github.io/find-item2/**

## ✨ 주요 기능

### 1️⃣ 쇼핑몰 자동 열기
- 버튼 클릭 한 번으로 주요 쇼핑몰 검색 페이지 자동 오픈
- 네이버쇼핑, 쿠팡, 11번가, G마켓, 옥션 지원

### 2️⃣ 가격 비교
- 상품 정보 입력 (쇼핑몰, 상품명, 가격, 배송비)
- 최저실현가 자동 계산 (할인가 + 배송비)
- 실시간 가격순 정렬

### 3️⃣ 통계 분석
- 최저가 자동 하이라이트
- 평균 가격 계산
- 무료배송 비중 분석
- 가격 차이 비교

### 4️⃣ 편리한 UI
- 반응형 디자인 (모바일/태블릿/PC)
- 직관적인 입력 폼
- 순위별 메달 뱃지 (🥇🥈🥉)
- 상품 추가/삭제 기능

## 🎯 사용 방법

### STEP 1: 검색어 입력
```
예: "신일 팬히터 1200"
```

### STEP 2: 쇼핑몰 열기
"🛒 쇼핑몰 열기" 버튼 클릭
→ 주요 쇼핑몰이 새 탭으로 자동 오픈

### STEP 3: 가격 확인
각 쇼핑몰에서 상품 가격, 할인가, 배송비 확인

### STEP 4: 상품 추가
"➕ 추가" 버튼으로 상품 정보 입력
- 쇼핑몰명 (필수)
- 상품명 (필수)
- 할인가 (필수)
- 정가, 옵션, 배송비, 링크 (선택)

### STEP 5: 자동 비교
입력 즉시 최저가 순으로 자동 정렬 및 통계 표시!

## 📊 제공 정보

각 상품별로 다음 정보를 제공:
- ✅ 순위 (메달 뱃지)
- ✅ 쇼핑몰명
- ✅ 상품명 및 옵션
- ✅ 정가 (취소선)
- ✅ 할인가 (강조)
- ✅ 배송비 (무료/유료 구분)
- ✅ **최저실현가** (할인가 + 배송비)
- ✅ 상품 링크 (바로가기)
- ✅ 삭제 버튼

## 💡 핵심 개선 사항

### 이전 버전 (v1.0)
❌ 하드코딩된 데모 데이터
❌ 실제 가격과 불일치
❌ API 의존성

### 현재 버전 (v2.0)
✅ 사용자 직접 입력 방식
✅ 실제 시장 가격 반영
✅ API 불필요 (완전 클라이언트 사이드)
✅ 쇼핑몰 자동 열기 기능
✅ 실시간 정렬 및 통계

## 🛠️ 기술 스택

- **Frontend**: Vanilla JavaScript
- **Styling**: Tailwind CSS (CDN)
- **Storage**: In-memory (세션 기반)
- **Deployment**: GitHub Pages

## 📱 반응형 지원

- ✅ Desktop (1024px+)
- ✅ Tablet (768px - 1023px)
- ✅ Mobile (~ 767px)

## 🚀 로컬 실행

### 방법 1: Python
```bash
cd find-item2
python -m http.server 8000
# 접속: http://localhost:8000
```

### 방법 2: Live Server (VS Code)
1. VS Code에서 프로젝트 열기
2. Live Server 확장 프로그램 설치
3. index.html 우클릭 → "Open with Live Server"

## 📦 설치

```bash
# 저장소 클론
git clone https://github.com/jiappa4/find-item2.git

# 디렉토리 이동
cd find-item2

# 브라우저에서 index.html 열기
```

## 🔄 업데이트 배포

```bash
# 변경사항 커밋
git add .
git commit -m "Update: 설명"
git push origin main

# 또는 스크립트 사용
update-github.bat
```

1-2분 후 자동으로 GitHub Pages에 반영됩니다.

## 📸 스크린샷

### 메인 화면
- 검색창 + 쇼핑몰 열기 버튼
- 상품 추가 폼

### 결과 화면
- 가격 비교 테이블
- 순위별 메달 배지
- 통계 요약 카드

### 모바일 화면
- 반응형 레이아웃
- 터치 친화적 UI

## ⚠️ 주의사항

### 데이터 저장
- 현재 버전은 **세션 기반** (새로고침 시 데이터 초기화)
- 영구 저장이 필요한 경우 브라우저의 localStorage 활용 가능

### 가격 정보
- 사용자가 **직접 입력**한 정보 기반
- 실시간 API 연동 아님
- 가격 변동 시 재입력 필요

### 브라우저 호환성
- 모던 브라우저 권장 (Chrome, Firefox, Safari, Edge)
- ES6+ 문법 사용

## 🎓 사용 팁

### 효율적인 비교 방법
1. 동일 시간대에 여러 쇼핑몰 확인
2. 쿠폰 적용 후 최종 가격 입력
3. 배송비 포함 필수 확인
4. 정기 할인 이벤트 체크

### 정확한 가격 입력
- 쿠폰 할인가 반영
- 추가 할인 이벤트 확인
- 배송비 조건 확인 (무료 배송 기준)

## 🔮 향후 계획

### v3.0 (예정)
- [ ] localStorage로 데이터 영구 저장
- [ ] CSV/Excel 내보내기
- [ ] 가격 알림 기능
- [ ] 히스토리 추적
- [ ] 다크 모드

### v4.0 (예정)
- [ ] 백엔드 API 서버 구축
- [ ] 실제 쇼핑몰 API 연동
- [ ] 자동 가격 수집
- [ ] 회원 시스템
- [ ] 가격 변동 알림

## 🤝 기여

이슈와 PR을 환영합니다!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

## 👤 작성자

**GitHub:** [@jiappa4](https://github.com/jiappa4)  
**Project Link:** [https://github.com/jiappa4/find-item2](https://github.com/jiappa4/find-item2)

## 🙏 감사의 말

이 프로젝트는 실용성을 최우선으로 설계되었습니다.  
복잡한 API 없이도 효과적인 가격 비교가 가능함을 보여줍니다.

---

⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요!

**Happy Shopping! 🛍️**
