# GitHub Pages 자동 배포 가이드

## 📋 사전 준비

1. GitHub 계정 필요: `jiappa4`
2. Git 설치 확인
3. GitHub Personal Access Token 준비 (선택사항)

## 🚀 배포 방법

### 방법 1: 자동 스크립트 사용 (권장)

#### Windows
```cmd
setup-and-push.bat
```

#### Mac/Linux
```bash
chmod +x setup-and-push.sh
./setup-and-push.sh
```

### 방법 2: 수동 Git 명령어

```bash
# 1. Git 저장소 초기화
git init

# 2. 모든 파일 추가
git add .

# 3. 커밋 생성
git commit -m "Initial commit: Price comparison web application"

# 4. 메인 브랜치로 변경
git branch -M main

# 5. 원격 저장소 추가
git remote add origin https://github.com/jiappa4/find-item2.git

# 6. GitHub에 푸시
git push -u origin main
```

## ⚙️ GitHub Pages 활성화

1. **레포지토리로 이동**
   - https://github.com/jiappa4/find-item2

2. **Settings 클릭**
   - 상단 메뉴에서 "Settings" 탭 선택

3. **Pages 메뉴 선택**
   - 왼쪽 사이드바에서 "Pages" 클릭

4. **Source 설정**
   - Source: `GitHub Actions` 선택
   - (또는 `Deploy from a branch` → `main` branch → `/root` 선택)

5. **배포 완료 대기**
   - Actions 탭에서 배포 진행 상황 확인
   - 완료되면 녹색 체크 표시

6. **사이트 접속**
   - https://jiappa4.github.io/find-item2/

## 🔄 업데이트 배포

코드 수정 후 자동으로 재배포됩니다:

```bash
git add .
git commit -m "Update: 설명"
git push origin main
```

## 🔑 인증 방법

### HTTPS 인증
- Username: `jiappa4`
- Password: GitHub Personal Access Token 사용
  - https://github.com/settings/tokens 에서 생성

### SSH 인증 (권장)
```bash
# SSH 키 생성
ssh-keygen -t ed25519 -C "your_email@example.com"

# SSH 키를 GitHub에 등록
# https://github.com/settings/keys

# 원격 URL을 SSH로 변경
git remote set-url origin git@github.com:jiappa4/find-item2.git
```

## 📝 문제 해결

### 레포지토리가 없다는 오류
```
remote: Repository not found.
```
**해결방법:**
1. https://github.com/new 접속
2. Repository name: `find-item2`
3. Create repository 클릭

### 인증 실패
```
remote: Permission denied
```
**해결방법:**
- Personal Access Token 사용
- 또는 SSH 키 설정

### 푸시 충돌
```
! [rejected] main -> main (fetch first)
```
**해결방법:**
```bash
git pull origin main --rebase
git push origin main
```

## 🌐 배포 확인

1. **Actions 탭 확인**
   - https://github.com/jiappa4/find-item2/actions
   - 워크플로우 실행 상태 확인

2. **사이트 접속**
   - https://jiappa4.github.io/find-item2/

3. **배포 시간**
   - 보통 1-3분 소요

## 💡 추가 팁

- 커밋 메시지는 명확하게 작성
- 정기적으로 백업 유지
- 민감한 정보는 .gitignore에 추가
- 브랜치를 활용한 개발 권장

## 📞 지원

문제가 발생하면 GitHub Issues를 활용하세요:
https://github.com/jiappa4/find-item2/issues
