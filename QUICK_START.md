# 🚀 빠른 시작 가이드

## 프로젝트 위치
```
C:\Users\netwo\Documents\find-item2
```

## ⚡ 3단계로 배포하기

### 1️⃣ GitHub에 레포지토리 생성
1. https://github.com/new 접속
2. Repository name: `find-item2`
3. Public 선택
4. "Create repository" 클릭

### 2️⃣ 자동 배포 스크립트 실행

**Windows 사용자:**
```cmd
cd C:\Users\netwo\Documents\find-item2
setup-and-push.bat
```

**Mac/Linux 사용자:**
```bash
cd /Users/netwo/Documents/find-item2
chmod +x setup-and-push.sh
./setup-and-push.sh
```

### 3️⃣ GitHub Pages 활성화
1. https://github.com/jiappa4/find-item2/settings/pages 접속
2. Source: `GitHub Actions` 선택
3. 1-3분 대기
4. ✅ 완료: https://jiappa4.github.io/find-item2/

## 📋 체크리스트

배포 전:
- [ ] GitHub 계정 로그인 (jiappa4)
- [ ] Git 설치 확인 (`git --version`)
- [ ] GitHub에서 레포지토리 생성

배포 후:
- [ ] Actions 탭에서 배포 확인
- [ ] GitHub Pages 설정 확인
- [ ] 웹사이트 접속 테스트

## 🎯 완성된 기능

✅ **가격 비교 검색**
- 주요 쇼핑몰 통합 검색
- 최저실현가 계산 (기본가 + 배송비 - 할인)
- 가격순 정렬

✅ **데이터 시각화**
- 순위별 배지 (금/은/동)
- 쇼핑몰별 색상 구분
- 무료배송 표시

✅ **통계 분석**
- 최저가 찾기
- 평균 가격
- 무료배송 비중
- 할인율 분석

✅ **반응형 디자인**
- 모바일 최적화
- 태블릿 지원
- 데스크톱 UI

✅ **자동 배포**
- GitHub Actions CI/CD
- 코드 푸시 시 자동 업데이트

## 📱 데모 데이터

현재 "신일 팬히터 1200" 검색 시:
- 네이버쇼핑: 38,900원 (최저가)
- 쿠팡: 42,900원
- 11번가: 43,500원
- G마켓: 40,900원
- 옥션: 41,900원

## 🔧 커스터마이징

### 검색어 변경
`index.html` 파일의 81번째 줄:
```javascript
const [searchQuery, setSearchQuery] = useState('신일 팬히터 1200');
```

### 색상 테마 변경
CSS 그라디언트 색상:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### 데모 데이터 수정
`index.html`의 `searchProducts` 함수 내 `demoData` 배열 수정

## 🌐 접속 URL

**개발 환경 (로컬):**
```bash
python -m http.server 8000
# http://localhost:8000
```

**프로덕션 (GitHub Pages):**
```
https://jiappa4.github.io/find-item2/
```

## 📞 도움말

### 문제 발생 시

1. **Git 관련 오류**
   - `DEPLOY_GUIDE.md` 참조
   - 문제 해결 섹션 확인

2. **배포 실패**
   - GitHub Actions 탭 확인
   - 오류 로그 확인

3. **페이지 안 열림**
   - 배포 완료 대기 (1-3분)
   - 캐시 삭제 후 재접속

### 문서 참고

- 📖 `README.md` - 프로젝트 소개
- 🚀 `DEPLOY_GUIDE.md` - 배포 상세 가이드
- 🏗️ `PROJECT_STRUCTURE.md` - 구조 설명

## 🎉 축하합니다!

프로젝트가 성공적으로 생성되었습니다!
이제 위의 3단계만 따라하시면 웹사이트가 배포됩니다.

---

**프로젝트 생성 완료**
- 생성 위치: `C:\Users\netwo\Documents\find-item2`
- GitHub 레포: `jiappa4/find-item2`
- 배포 URL: `https://jiappa4.github.io/find-item2/`

행운을 빕니다! 🚀
