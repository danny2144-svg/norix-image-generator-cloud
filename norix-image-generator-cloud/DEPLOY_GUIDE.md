# 🚀 웹에서 바로 쓰는 배포 가이드

터미널 없이 **브라우저만으로** 노릭스 이미지팩 생성기를 웹앱으로 띄우는 방법입니다.
한 번 배포하면 휴대폰, PC 어디서든 URL로 접속해서 쓸 수 있어요.

---

## 전체 흐름 (총 3단계, 약 15분)

1. GitHub 회원가입 + 이 코드 업로드
2. Streamlit Cloud 회원가입 + 앱 배포
3. API 키 등록

---

## 1단계 — GitHub에 코드 올리기

### 1-1. GitHub 회원가입

이미 계정 있으면 건너뛰세요.

1. https://github.com/signup 접속
2. 이메일 / 비밀번호 / 사용자명 입력
3. 이메일 인증 완료

### 1-2. 새 저장소 만들기

1. https://github.com/new 접속
2. **Repository name**: `norix-image-generator` (원하는 이름 아무거나)
3. **Private** 선택 (남이 못 보게)
4. 다른 옵션 건드리지 말고 아래 **Create repository** 클릭

### 1-3. 파일 업로드

저장소 만들고 나면 화면에 "uploading an existing file" 링크가 보여요. 또는 주소창에 `/upload` 붙이면 됩니다.

1. 화면의 **uploading an existing file** 링크 클릭 (또는 `Add file → Upload files`)
2. ZIP 압축 푼 폴더 안의 **모든 파일과 폴더**를 드래그해서 업로드 영역에 떨어뜨리기
   - ⚠️ `norix-image-generator` 폴더 자체가 아니라 그 **안의 내용물**을 올려야 합니다
   - 올라가야 할 것: `app.py`, `requirements.txt`, `README.md`, `.env.example`, `.gitignore`, `providers/` 폴더, `.streamlit/` 폴더, `outputs/` 폴더
3. 업로드되면 화면 아래로 내려서 **Commit changes** 초록 버튼 클릭

> 💡 `.streamlit` 같은 점(.)으로 시작하는 폴더가 안 보일 수 있어요. 윈도우 탐색기 상단 "보기" → "숨긴 항목" 체크하면 보입니다.

업로드 끝!

---

## 2단계 — Streamlit Cloud에 앱 배포

### 2-1. Streamlit Cloud 회원가입

1. https://share.streamlit.io 접속
2. **Continue with GitHub** 클릭
3. GitHub 로그인 → 권한 허용 (Streamlit이 저장소 읽도록 허용)

### 2-2. 새 앱 만들기

1. 우측 상단 **Create app** 버튼 클릭
2. **Deploy a public app from GitHub** 또는 **Deploy from existing repo** 선택
3. 폼에 입력:
   - **Repository**: `본인계정/norix-image-generator` 선택
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: 원하는 주소 (예: `noriks-image`) — 비워두면 자동 생성
4. **Advanced settings** (밑줄 친 글씨) 클릭
5. **Python version**: 3.11 선택 (안정적)
6. 일단 **Save** → **Deploy** 누르기

> ⚠️ 처음 배포는 5~10분 걸려요. "Your app is in the oven 🍞" 같은 화면이 뜨면 정상이에요. 기다리세요.

배포가 끝나도 처음에는 화면에 "API 키가 필요합니다" 같은 에러가 뜰 수 있어요. 정상이에요. 다음 단계에서 키 넣어주면 됩니다.

---

## 3단계 — API 키 등록

### 3-1. Secrets 메뉴 열기

배포된 앱 페이지 우측 하단 햄버거 메뉴(⋮) → **Settings** → 좌측 **Secrets** 탭

또는 https://share.streamlit.io 에서 앱 카드 우측 ⋮ → **Settings** → **Secrets**

### 3-2. 키 붙여넣기

빈 텍스트 박스에 아래 형식으로 입력합니다. **쓸 키만** 채우면 됩니다.

```toml
OPENAI_API_KEY = "sk-proj-여기에_실제_키"
GEMINI_API_KEY = "여기에_실제_Gemini_키"
ANTHROPIC_API_KEY = "sk-ant-여기에_실제_Claude_키"
```

⚠️ 큰따옴표(`"`) 꼭 붙이세요. 등호(`=`) 양쪽 띄어쓰기도 그대로요.

**Save** 버튼 클릭. 앱이 자동으로 재시작합니다 (1~2분 대기).

---

## 4단계 — 사용

배포된 URL (예: `https://noriks-image.streamlit.app`) 접속.

- 휴대폰 즐겨찾기에 추가하면 앱처럼 쓸 수 있어요
- 사이드바에서 **AI 공급자, 비율, 스타일** 선택
- 가운데 입력창에 프롬프트 한 줄에 하나씩 붙여넣기
- **이미지 생성 시작** 버튼 클릭
- 끝나면 화면 아래 **결과 ZIP 다운로드** 버튼으로 받기

---

## ❓ 문제 생기면 자주 보는 것들

### "ModuleNotFoundError" 에러
- `requirements.txt`가 GitHub에 안 올라갔을 가능성. 저장소에서 확인하세요.

### "API 키가 필요합니다" 가 계속 뜸
- Secrets에서 큰따옴표 빠졌거나, 줄바꿈에 공백 들어갔을 가능성
- 위 형식 그대로 복사해서 키 부분만 바꿔 넣어보세요

### 이미지가 안 만들어지고 401/403 에러
- API 키가 잘못됐거나, OpenAI는 organization verification 안 된 계정일 수 있어요
- OpenAI 모델을 사이드바에서 `dall-e-3`로 바꿔보세요

### Cloud에서 생성된 이미지가 사라져요
- Streamlit Cloud는 앱 재시작하면 파일이 초기화돼요. 이건 정상이에요
- 그래서 작업 끝나면 **꼭 ZIP 다운로드 받아서 컴퓨터에 저장**하세요

### 코드 수정하고 싶을 때
- GitHub 저장소에서 파일 클릭 → 연필 아이콘(✏️) → 수정 → Commit
- 1~2분 후 Streamlit Cloud가 자동으로 재배포해요

---

## 🔒 보안 메모

- 저장소를 **Private**으로 만들었으니 코드는 본인만 볼 수 있어요
- API 키는 Secrets에 넣으니 코드에는 안 들어가요 (안전)
- 앱 URL을 아는 사람은 누구나 접속해서 키를 사용할 수 있어요
  - 본인만 쓰려면 **Settings → Sharing → Viewer access**에서 제한 가능 (특정 이메일만 허용)
