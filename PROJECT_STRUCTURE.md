# 프로젝트 구조

```
find-item2/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions 자동 배포 설정
├── .gitignore                  # Git 제외 파일 목록
├── index.html                  # 메인 웹 애플리케이션
├── README.md                   # 프로젝트 소개
├── DEPLOY_GUIDE.md            # 배포 가이드
├── package.json               # 프로젝트 메타데이터
├── setup-and-push.bat         # Windows 자동 배포 스크립트
└── setup-and-push.sh          # Mac/Linux 자동 배포 스크립트
```

## 파일 설명

### 핵심 파일

#### `index.html`
- React 기반의 단일 페이지 애플리케이션
- 가격 비교 검색 UI 및 로직
- 반응형 디자인 (모바일/태블릿/데스크톱)
- 주요 기능:
  - 상품 검색 인터페이스
  - 가격 비교 테이블
  - 통계 요약 (최저가, 평균가, 무료배송 비중)
  - 순위별 배지 표시
  - 쇼핑몰 링크 제공

### 설정 파일

#### `.github/workflows/deploy.yml`
- GitHub Actions 워크플로우
- main 브랜치에 푸시 시 자동 배포
- GitHub Pages로 자동 배포 설정

#### `.gitignore`
- Git 버전 관리에서 제외할 파일
- node_modules, 빌드 파일, IDE 설정 등

#### `package.json`
- 프로젝트 메타데이터
- 레포지토리 정보
- GitHub Pages 호스팅 URL

### 문서 파일

#### `README.md`
- 프로젝트 개요 및 소개
- 주요 기능 설명
- 사용 방법
- 기술 스택

#### `DEPLOY_GUIDE.md`
- 상세한 배포 가이드
- GitHub Pages 설정 방법
- 문제 해결 가이드

### 배포 스크립트

#### `setup-and-push.bat` (Windows)
- Windows용 자동 배포 스크립트
- Git 초기화 및 GitHub 푸시 자동화

#### `setup-and-push.sh` (Mac/Linux)
- Mac/Linux용 자동 배포 스크립트
- Git 초기화 및 GitHub 푸시 자동화

## 기술 구조

### Frontend
- **React 18**: UI 컴포넌트 및 상태 관리
- **Vanilla CSS**: 커스텀 스타일링
  - Gradient 디자인
  - 반응형 레이아웃
  - 애니메이션 효과

### 배포
- **GitHub Pages**: 정적 사이트 호스팅
- **GitHub Actions**: CI/CD 자동화

## 데이터 흐름

```
사용자 입력 (검색어)
    ↓
검색 버튼 클릭
    ↓
API 호출 시뮬레이션 (현재는 데모 데이터)
    ↓
데이터 정렬 (최저실현가 기준)
    ↓
결과 테이블 렌더링
    ↓
통계 분석 표시
```

## 향후 확장 계획

### 백엔드 추가 (필요시)
```
find-item2-backend/
├── api/
│   ├── scraper.js         # 웹 스크래핑
│   ├── parser.js          # 데이터 파싱
│   └── routes.js          # API 라우트
├── database/
│   └── schema.sql         # DB 스키마
└── server.js              # Express 서버
```

### 실제 API 연동
- 쇼핑몰 API 연동
- 웹 스크래핑 구현
- 가격 히스토리 추적
- 사용자 알림 기능

## 개발 환경 설정

### 로컬 테스트
```bash
# 간단한 HTTP 서버 실행
python -m http.server 8000

# 브라우저에서 접속
http://localhost:8000
```

### 코드 수정 후 재배포
```bash
git add .
git commit -m "Update: 변경 사항"
git push origin main
```

자동으로 GitHub Actions가 실행되어 사이트가 업데이트됩니다.
