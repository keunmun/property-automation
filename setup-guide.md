# 📋 매물 자동화 시스템 설치 가이드

## 🎯 전체 설치 과정 개요

1. **Template 저장소 복사** → 자신의 GitHub 계정에 저장소 생성
2. **GitHub Secrets 설정** → 로그인 정보 보안 저장
3. **로컬 환경 구축** → PC에 시스템 설치
4. **테스트 실행** → 정상 동작 확인

---

## 1️⃣ Template 저장소 복사

### **단계별 진행**

1. **Template 저장소 접속**
   - https://github.com/small-creator/naverland-automation-template

2. **"Use this template" 클릭**
   - 페이지 상단의 녹색 버튼

3. **새 저장소 설정**
   - Repository name: `my-property-automation` (원하는 이름)
   - Description: `네이버부동산 매물 자동화`
   - Public/Private: **Private 권장** (개인정보 보호)

4. **"Create repository from template" 클릭**

---

## 2️⃣ GitHub Secrets 설정

### **보안 정보 저장**

1. **생성된 저장소로 이동**
   - 예: https://github.com/yourusername/my-property-automation

2. **Settings 탭 클릭**

3. **Secrets and variables → Actions 클릭**

4. **"New repository secret" 클릭하여 추가**

| Secret Name | Value | 설명 |
|-------------|-------|------|
| `LOGIN_ID` | 실제_로그인_아이디 | 사이트 로그인용 아이디 |
| `LOGIN_PASSWORD` | 실제_로그인_비밀번호 | 사이트 로그인용 비밀번호 |

### **⚠️ 중요 주의사항**
- 절대 코드에 직접 입력하지 마세요
- Secrets는 안전하게 암호화되어 저장됩니다
- 다른 사람이 볼 수 없습니다

---

## 3️⃣ 로컬 환경 구축

### **시스템 요구사항**

#### **필수 프로그램**
- **Windows 10 이상**
- **Python 3.8+** - https://www.python.org/downloads/
- **Git** - https://git-scm.com/downloads

#### **설치 확인**
```bash
# 명령 프롬프트에서 확인
python --version
git --version
```

### **자동 설치 (추천)**

1. **install.bat 다운로드**
   - [install.bat 다운로드 링크]

2. **관리자 권한으로 실행**
   - 파일 우클릭 → "관리자 권한으로 실행"

3. **안내에 따라 진행**
   - GitHub 저장소 URL 입력
   - 자동 설치 완료 대기

### **수동 설치**

#### **1단계: 폴더 구조 생성**
```bash
# 바탕화면에 작업 폴더 생성
cd Desktop
mkdir cursor
cd cursor
```

#### **2단계: 프로젝트 다운로드**
```bash
# 메인 프로젝트 클론
git clone https://github.com/small-creator/property_ad_auto_git.git

# GitHub Actions 저장소 클론
mkdir github_repos
cd github_repos
git clone https://github.com/yourusername/my-property-automation.git
```

#### **3단계: Python 패키지 설치**
```bash
cd ../property_ad_auto_git
pip install python-dotenv playwright requests beautifulsoup4
playwright install chromium
```

#### **4단계: 환경설정 파일 생성**
`.env` 파일 생성:
```env
LOGIN_ID=실제_로그인_아이디
LOGIN_PASSWORD=실제_로그인_비밀번호
REALTOR_ID=실제_중개업소_ID
GITHUB_REPO_PATH=C:\Users\사용자명\Desktop\cursor\github_repos\my-property-automation
```

---

## 4️⃣ 테스트 실행

### **GUI 프로그램 실행**

1. **바탕화면 바로가기 실행**
   - "매물자동화시스템" 아이콘 더블클릭

2. **순위 조회 테스트**
   - "📊 순위 조회" 버튼 클릭
   - 매물 목록이 표시되는지 확인

3. **예약 기능 테스트**
   - 매물 선택 후 "⏰ 최적화 예약" 클릭
   - GitHub에 파일이 업로드되는지 확인

### **GitHub Actions 확인**

1. **Actions 탭 접속**
   - 저장소 → Actions 탭

2. **워크플로우 확인**
   - "Property Automation" 존재 확인
   - 스케줄 설정 확인 (매일 자정 1분)

3. **수동 실행 테스트**
   - "Run workflow" 버튼으로 테스트
   - 테스트 모드로 시뮬레이션 실행

---

## 🔧 문제해결

### **Python 설치 오류**
```
'python' is not recognized as an internal or external command
```
**해결법**: Python 설치 시 "Add to PATH" 체크 확인

### **Git 설치 오류**
```
'git' is not recognized as an internal or external command
```
**해결법**: Git 설치 후 명령 프롬프트 재시작

### **권한 오류**
```
Permission denied
```
**해결법**: 관리자 권한으로 명령 프롬프트 실행

### **GitHub 연결 오류**
```
Authentication failed
```
**해결법**: GitHub 로그인 상태 확인, Personal Access Token 사용

### **Secrets 설정 오류**
```
❌ GitHub Secrets에 LOGIN_ID와 LOGIN_PASSWORD를 설정해주세요.
```
**해결법**: Settings → Secrets에서 값 재확인

---

## 📞 추가 지원

### **도움말 리소스**
- **📖 메인 README**: 기본 사용법
- **🐛 GitHub Issues**: 버그 리포트
- **💡 Discussions**: 질문 및 토론

### **자주 묻는 질문**

**Q: 매일 자정에 자동 실행되나요?**
A: 네, GitHub Actions가 매일 자정 1분에 자동 실행됩니다.

**Q: 컴퓨터가 꺼져있어도 실행되나요?**
A: 네, GitHub 서버에서 실행되므로 PC 상태와 무관합니다.

**Q: 여러 개의 매물을 동시에 처리할 수 있나요?**
A: 네, 한 번에 여러 매물을 선택하여 일괄 처리할 수 있습니다.

**Q: 실행 결과를 어떻게 확인하나요?**
A: GitHub Actions 탭에서 실행 로그와 결과를 확인할 수 있습니다.

---

## ✅ 설치 완료 체크리스트

```
□ Template 저장소에서 새 저장소 생성
□ GitHub Secrets 설정 (LOGIN_ID, LOGIN_PASSWORD)
□ Python 3.8+ 설치 및 PATH 설정
□ Git 설치
□ 로컬 프로젝트 다운로드
□ Python 패키지 설치 (playwright, requests 등)
□ .env 파일 생성 및 설정
□ GUI 프로그램 실행 테스트
□ 순위 조회 기능 테스트
□ GitHub Actions 워크플로우 확인
□ 예약 기능 테스트
□ 자동 실행 스케줄 확인
```

**모든 항목이 체크되면 설치 완료입니다!** 🎉
