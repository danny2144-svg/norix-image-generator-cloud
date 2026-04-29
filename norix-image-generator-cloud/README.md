# 노릭스 멀티 이미지팩 생성기

프롬프트를 여러 줄로 붙여넣으면 OpenAI 또는 Gemini로 이미지를 대량 생성하고, Claude로 프롬프트를 보정할 수 있는 Streamlit 웹앱입니다.

## 지원 기능

- OpenAI 이미지 생성
- Gemini / Imagen 이미지 생성
- Claude 프롬프트 보정 후 OpenAI 이미지 생성
- Claude 프롬프트 보정 후 Gemini 이미지 생성
- 최대 80개 프롬프트 처리
- 16:9, 9:16, 1:1 비율 선택
- 결과 이미지 자동 저장
- CSV 기록
- ZIP 다운로드
- 이어하기 모드

## 설치

```bash
pip install -r requirements.txt
cp .env.example .env
```

`.env` 파일을 열고 사용할 API 키를 입력합니다.

```
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
ANTHROPIC_API_KEY=...
```

## 실행

```bash
streamlit run app.py
```

## 프롬프트 입력 예시

한 줄에 하나씩 붙여넣으면 됩니다.

```
수익정지 때문에 불안한 유튜버
손과 타로카드만 보이는 신타로 촬영 장면
구독자 3천 명 채널에서 한 달 800만 원 수익을 상징하는 이미지
```

## 결과 저장 구조

```
outputs/프로젝트이름/
  001.png
  002.png
  003.png
  result.csv
```

`result.csv`에는 인덱스, 공급자, 비율, 원본 프롬프트, 보정 프롬프트, 파일명, 상태, 에러, 재시도 횟수가 기록됩니다.

## 폴더 구조

```
norix-image-generator/
  app.py
  requirements.txt
  .env.example
  README.md
  providers/
    __init__.py
    openai_provider.py
    gemini_provider.py
    claude_prompt_provider.py
  outputs/
```
