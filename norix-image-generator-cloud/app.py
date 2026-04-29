import os
import time
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from providers.claude_prompt_provider import enhance_prompt_with_claude
from providers.gemini_provider import generate_image_gemini
from providers.openai_provider import generate_image_openai


load_dotenv()


def get_secret(key: str) -> str:
    """
    Streamlit Cloud에서는 st.secrets, 로컬에서는 .env (os.getenv)에서 키를 읽어옵니다.
    """
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, "")


APP_TITLE = "노릭스 멀티 이미지팩 생성기"
MAX_PROMPTS = 80

DEFAULT_OPENAI_MODEL = "gpt-image-1"
DEFAULT_GEMINI_MODEL = "imagen-4.0-generate-001"
DEFAULT_CLAUDE_MODEL = "claude-3-5-sonnet-latest"


def sanitize_project_name(name: str) -> str:
    """
    폴더명으로 안전하게 쓸 수 있도록 프로젝트 이름을 정리합니다.
    """
    name = name.strip()

    if not name:
        return f"norix_images_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    safe_chars = []

    for ch in name:
        if ch.isalnum() or ch in ("-", "_"):
            safe_chars.append(ch)
        else:
            safe_chars.append("_")

    return "".join(safe_chars)[:80]


def parse_prompts(raw_text: str) -> list[str]:
    """
    여러 줄 프롬프트에서 빈 줄을 제거하고 최대 80개까지만 반환합니다.
    """
    prompts = []

    for line in raw_text.splitlines():
        cleaned = line.strip()
        if cleaned:
            prompts.append(cleaned)

    return prompts[:MAX_PROMPTS]


def create_zip(folder: Path) -> Path:
    """
    결과 폴더 전체를 ZIP 파일로 압축합니다.
    """
    zip_path = folder.with_suffix(".zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in folder.rglob("*"):
            if file_path.is_file():
                zipf.write(file_path, arcname=file_path.relative_to(folder))

    return zip_path


def load_existing_csv(csv_path: Path) -> pd.DataFrame:
    """
    이어하기 모드에서 기존 result.csv를 불러옵니다.
    """
    if csv_path.exists():
        return pd.read_csv(csv_path)

    return pd.DataFrame(
        columns=[
            "index",
            "provider",
            "ratio",
            "original_prompt",
            "enhanced_prompt",
            "filename",
            "status",
            "error",
            "retry_count",
        ]
    )


def get_api_key(provider: str, openai_key: str, gemini_key: str, claude_key: str) -> tuple[bool, str]:
    """
    선택한 공급자에 필요한 API 키가 있는지 확인합니다.
    """
    if provider == "OpenAI":
        return bool(openai_key), "OpenAI API 키가 필요합니다."

    if provider == "Gemini":
        return bool(gemini_key), "Gemini API 키가 필요합니다."

    if provider == "Claude 보정 + OpenAI":
        return bool(claude_key and openai_key), "Claude API 키와 OpenAI API 키가 모두 필요합니다."

    if provider == "Claude 보정 + Gemini":
        return bool(claude_key and gemini_key), "Claude API 키와 Gemini API 키가 모두 필요합니다."

    return False, "알 수 없는 공급자입니다."


def strip_numbers_from_prompt(text: str) -> str:
    """
    프롬프트에서 숫자, 통계, 금액, 퍼센트 등을 자동으로 제거합니다.
    Claude 보정을 쓰지 않을 때를 위한 보조 안전장치입니다.
    """
    import re

    # 한글 숫자 표현 (예: "3천 명", "800만 원", "30대", "10년")
    text = re.sub(r"\d+\s*[천백만억조]+\s*[원명개세대년월일분초%퍼센트]?", "", text)
    # "30대", "40대" 같은 표현
    text = re.sub(r"\d+\s*대(?=\s|$|[^a-zA-Z가-힣])", "", text)
    # 일반 숫자 (1, 1,000, 1.5 등)
    text = re.sub(r"\d{1,3}(,\d{3})+", "", text)
    text = re.sub(r"\d+(\.\d+)?", "", text)
    # 통화 기호와 단위
    text = re.sub(r"[$€¥₩]", "", text)
    # 연속된 공백 정리
    text = re.sub(r"\s+", " ", text).strip()

    return text


def koreanize_prompt(text: str) -> str:
    """
    Claude 보정을 쓰지 않을 때, 원본 프롬프트에 한국화와 실사화 키워드를 자동으로 추가합니다.
    """
    # 먼저 숫자 제거
    cleaned = strip_numbers_from_prompt(text)

    # 한국 + 실사 키워드를 영어로 강하게 추가
    suffix = (
        ", Korean people only, Korean appearance with black hair and East Asian features, "
        "set in Korea, photorealistic cinematic photograph, shot on Sony A7 IV with 85mm lens, "
        "natural lighting, real photograph style, NOT anime, NOT illustration, NOT 3D render, "
        "NO numbers or text in image"
    )

    return cleaned + suffix


def generate_image_by_provider(
    provider: str,
    prompt: str,
    output_path: Path,
    ratio_label: str,
    openai_model: str,
    gemini_model: str,
    openai_key: str,
    gemini_key: str,
) -> None:
    """
    선택한 이미지 생성 공급자에 따라 이미지를 생성합니다.
    Claude 보정 옵션에서는 이미 보정된 프롬프트가 이 함수로 들어옵니다.
    """
    if provider in ("OpenAI", "Claude 보정 + OpenAI"):
        generate_image_openai(
            prompt=prompt,
            output_path=output_path,
            model=openai_model,
            ratio_label=ratio_label,
            api_key=openai_key,
        )
        return

    if provider in ("Gemini", "Claude 보정 + Gemini"):
        generate_image_gemini(
            prompt=prompt,
            output_path=output_path,
            model=gemini_model,
            ratio_label=ratio_label,
            api_key=gemini_key,
        )
        return

    raise ValueError(f"지원하지 않는 공급자입니다: {provider}")


st.set_page_config(page_title=APP_TITLE, page_icon="🖼️", layout="wide")

st.title(APP_TITLE)
st.write("프롬프트를 한 줄에 하나씩 붙여넣으면 선택한 AI 엔진으로 이미지를 대량 생성합니다.")

with st.sidebar:
    st.header("AI 공급자 설정")

    provider = st.selectbox(
        "생성 방식",
        [
            "OpenAI",
            "Gemini",
            "Claude 보정 + OpenAI",
            "Claude 보정 + Gemini",
        ],
    )

    st.divider()

    openai_key = st.text_input(
        "OpenAI API 키",
        type="password",
        value=get_secret("OPENAI_API_KEY"),
        help="Streamlit Cloud Secrets 또는 .env의 OPENAI_API_KEY",
    )

    gemini_key = st.text_input(
        "Gemini API 키",
        type="password",
        value=get_secret("GEMINI_API_KEY"),
        help="Streamlit Cloud Secrets 또는 .env의 GEMINI_API_KEY",
    )

    claude_key = st.text_input(
        "Claude API 키",
        type="password",
        value=get_secret("ANTHROPIC_API_KEY"),
        help="Streamlit Cloud Secrets 또는 .env의 ANTHROPIC_API_KEY",
    )

    st.divider()

    openai_model = st.text_input("OpenAI 이미지 모델", value=DEFAULT_OPENAI_MODEL)
    gemini_model = st.text_input("Gemini/Imagen 이미지 모델", value=DEFAULT_GEMINI_MODEL)
    claude_model = st.text_input("Claude 프롬프트 보정 모델", value=DEFAULT_CLAUDE_MODEL)

    st.divider()

    ratio_label = st.selectbox(
        "이미지 비율",
        [
            "16:9 유튜브용",
            "16:9 PPT용",
            "9:16 쇼츠/릴스용",
            "1:1 카드뉴스용",
        ],
    )

    enhance_style = st.selectbox(
        "Claude 프롬프트 보정 스타일",
        [
            "유튜브 썸네일용",
            "타로/신타로 실사풍",
            "카드뉴스용",
            "쇼츠 배경용",
            "시네마틱 실사풍",
            "조선 무속 신비풍",
            "프리미엄 강의 광고풍",
        ],
    )

    project_name_input = st.text_input(
        "프로젝트 이름",
        placeholder="예: tarot_youtube_images",
    )

    resume_mode = st.checkbox(
        "이어하기 모드",
        value=True,
        help="이미 생성된 PNG 파일이 있으면 건너뜁니다.",
    )

    max_retries = st.slider(
        "실패 시 재시도 횟수",
        min_value=0,
        max_value=5,
        value=2,
    )

    delay_seconds = st.slider(
        "요청 사이 대기 시간",
        min_value=0.0,
        max_value=10.0,
        value=1.0,
        step=0.5,
        help="대량 생성 시 API 제한을 피하려면 1~3초 정도 권장합니다.",
    )


raw_prompts = st.text_area(
    "이미지 프롬프트 입력",
    height=320,
    placeholder=(
        "수익정지 때문에 불안한 유튜버\n"
        "손과 타로카드만 보이는 신타로 촬영 장면\n"
        "구독자 3천 명 채널에서 한 달 800만 원 수익을 상징하는 이미지"
    ),
)

prompts = parse_prompts(raw_prompts)

col1, col2, col3, col4 = st.columns(4)
col1.metric("프롬프트 수", len(prompts))
col2.metric("최대 처리", MAX_PROMPTS)
col3.metric("공급자", provider)
col4.metric("비율", ratio_label)

if len(raw_prompts.splitlines()) > MAX_PROMPTS:
    st.warning(f"최대 {MAX_PROMPTS}개까지만 처리합니다. 초과 프롬프트는 자동 제외됩니다.")

short_prompts = [p for p in prompts if len(p) < 10]
if short_prompts:
    st.info(f"너무 짧은 프롬프트가 {len(short_prompts)}개 있습니다. Claude 보정을 쓰면 품질이 좋아질 수 있습니다.")

# 세션 상태 초기화
if "stop_requested" not in st.session_state:
    st.session_state["stop_requested"] = False
if "is_generating" not in st.session_state:
    st.session_state["is_generating"] = False
if "regenerate_index" not in st.session_state:
    st.session_state["regenerate_index"] = None
if "last_project_name" not in st.session_state:
    st.session_state["last_project_name"] = ""
if "last_prompts" not in st.session_state:
    st.session_state["last_prompts"] = []


def request_stop():
    st.session_state["stop_requested"] = True


# 시작 버튼과 멈추기 버튼 나란히 배치
btn_col1, btn_col2 = st.columns([1, 1])
with btn_col1:
    start_button = st.button(
        "이미지 생성 시작",
        type="primary",
        disabled=not prompts or st.session_state.get("is_generating", False),
        use_container_width=True,
    )
with btn_col2:
    stop_button = st.button(
        "⏹ 멈추기",
        disabled=not st.session_state.get("is_generating", False),
        on_click=request_stop,
        use_container_width=True,
    )

progress_bar = st.progress(0)
log_box = st.empty()
live_gallery_area = st.container()
result_download_area = st.container()
gallery_area = st.container()

if start_button:
    key_ok, key_message = get_api_key(provider, openai_key, gemini_key, claude_key)

    if not key_ok:
        st.error(key_message)
        st.stop()

    # 생성 시작: 상태 초기화
    st.session_state["stop_requested"] = False
    st.session_state["is_generating"] = True

    project_name = sanitize_project_name(project_name_input)

    # 다시 만들기 기능을 위해 마지막 프로젝트/프롬프트 기억
    st.session_state["last_project_name"] = project_name
    st.session_state["last_prompts"] = prompts

    output_root = Path("outputs")
    output_dir = output_root / project_name
    output_dir.mkdir(parents=True, exist_ok=True)

    result_csv_path = output_dir / "result.csv"
    result_df = load_existing_csv(result_csv_path)

    logs = []
    total = len(prompts)

    # 실시간 갤러리 초기화: 4열 그리드를 미리 만들어두고 자리(placeholder)를 잡아둡니다
    with live_gallery_area:
        st.subheader("실시간 결과 (생성되는 대로 표시)")
        gallery_cols = st.columns(4)
        image_placeholders = []
        for i in range(total):
            col = gallery_cols[i % 4]
            with col:
                ph = st.empty()
                image_placeholders.append(ph)

    for i, original_prompt in enumerate(prompts, start=1):
        # 멈추기 버튼이 눌렸는지 확인
        if st.session_state.get("stop_requested", False):
            logs.append(f"⏹ 사용자가 멈추기를 눌러서 {i}/{total}에서 정지했습니다.")
            log_box.text("\n".join(logs[-15:]))
            break

        filename = f"{i:03d}.png"
        output_path = output_dir / filename

        if resume_mode and output_path.exists():
            logs.append(f"{i}/{total} 이미 존재해서 건너뜀: {filename}")

            # 이미 만들어진 이미지도 갤러리에 즉시 표시
            try:
                image_placeholders[i - 1].image(
                    str(output_path),
                    caption=f"{filename} (기존)",
                    use_container_width=True,
                )
            except Exception:
                pass

            row = {
                "index": i,
                "provider": provider,
                "ratio": ratio_label,
                "original_prompt": original_prompt,
                "enhanced_prompt": "",
                "filename": filename,
                "status": "skipped_existing",
                "error": "",
                "retry_count": 0,
            }

            result_df = pd.concat([result_df, pd.DataFrame([row])], ignore_index=True)
            result_df.to_csv(result_csv_path, index=False, encoding="utf-8-sig")

            progress_bar.progress(i / total)
            log_box.text("\n".join(logs[-15:]))
            continue

        enhanced_prompt = original_prompt
        success = False
        last_error = ""
        retry_count = 0

        for attempt in range(max_retries + 1):
            retry_count = attempt

            try:
                logs.append(f"{i}/{total} 처리 중: {filename} / 시도 {attempt + 1}")
                log_box.text("\n".join(logs[-15:]))

                if provider.startswith("Claude 보정"):
                    logs.append(f"{i}/{total} Claude 프롬프트 보정 중...")
                    log_box.text("\n".join(logs[-15:]))

                    enhanced_prompt = enhance_prompt_with_claude(
                        original_prompt=original_prompt,
                        style=enhance_style,
                        model=claude_model,
                        api_key=claude_key,
                        ratio_label=ratio_label,
                    )
                else:
                    # Claude 보정을 안 쓸 때도 자동으로 한국화 + 실사화 + 숫자 제거 적용
                    enhanced_prompt = koreanize_prompt(original_prompt)

                logs.append(f"{i}/{total} 이미지 생성 중...")
                log_box.text("\n".join(logs[-15:]))

                generate_image_by_provider(
                    provider=provider,
                    prompt=enhanced_prompt,
                    output_path=output_path,
                    ratio_label=ratio_label,
                    openai_model=openai_model,
                    gemini_model=gemini_model,
                    openai_key=openai_key,
                    gemini_key=gemini_key,
                )

                logs.append(f"{i}/{total} 생성 완료: {filename}")
                success = True

                # 갤러리에 새 이미지 즉시 표시
                try:
                    image_placeholders[i - 1].image(
                        str(output_path),
                        caption=filename,
                        use_container_width=True,
                    )
                except Exception:
                    pass

                break

            except Exception as e:
                last_error = str(e)
                logs.append(f"{i}/{total} 오류: {last_error}")

                if attempt < max_retries:
                    sleep_time = 2 + attempt * 2
                    logs.append(f"{sleep_time}초 후 재시도합니다.")
                    log_box.text("\n".join(logs[-15:]))
                    time.sleep(sleep_time)

        row = {
            "index": i,
            "provider": provider,
            "ratio": ratio_label,
            "original_prompt": original_prompt,
            "enhanced_prompt": enhanced_prompt if enhanced_prompt != original_prompt else "",
            "filename": filename if success else "",
            "status": "success" if success else "failed",
            "error": "" if success else last_error,
            "retry_count": retry_count,
        }

        result_df = pd.concat([result_df, pd.DataFrame([row])], ignore_index=True)
        result_df.to_csv(result_csv_path, index=False, encoding="utf-8-sig")

        progress_bar.progress(i / total)
        log_box.text("\n".join(logs[-15:]))

        if delay_seconds > 0:
            time.sleep(delay_seconds)

    # 생성 끝: 상태 정리
    was_stopped = st.session_state.get("stop_requested", False)
    st.session_state["is_generating"] = False
    st.session_state["stop_requested"] = False

    if was_stopped:
        st.warning("⏹ 사용자가 멈춰서 작업이 중단됐습니다. 지금까지 만든 이미지는 그대로 저장돼 있어요. '이어하기 모드'를 켜고 다시 시작하면 멈춘 지점부터 이어서 만듭니다.")
    else:
        st.success("이미지 생성 작업이 완료되었습니다.")

    zip_path = create_zip(output_dir)

    with result_download_area:
        col_csv, col_zip = st.columns(2)

        with open(result_csv_path, "rb") as f:
            col_csv.download_button(
                "결과 CSV 다운로드",
                data=f,
                file_name="result.csv",
                mime="text/csv",
            )

        with open(zip_path, "rb") as f:
            col_zip.download_button(
                "전체 이미지 ZIP 다운로드",
                data=f,
                file_name=zip_path.name,
                mime="application/zip",
            )

    with gallery_area:
        st.subheader("결과 미리보기 (마음에 안 드는 이미지는 다시 만들기)")

        image_files = sorted(output_dir.glob("*.png"))

        if image_files:
            cols = st.columns(4)

            for idx, img_path in enumerate(image_files):
                with cols[idx % 4]:
                    st.image(str(img_path), caption=img_path.name, use_container_width=True)
                    # 다시 만들기 버튼
                    img_index = int(img_path.stem)  # "001.png" → 1
                    if st.button("🔄 이 이미지 다시 만들기", key=f"regen_{img_index}"):
                        # 기존 파일 삭제하고 인덱스 저장
                        try:
                            img_path.unlink()
                        except Exception:
                            pass
                        st.session_state["regenerate_index"] = img_index
                        st.rerun()
        else:
            st.info("생성된 이미지가 없습니다.")

else:
    # 다시 만들기 요청이 있는지 확인
    regen_idx = st.session_state.get("regenerate_index")
    if regen_idx is not None and st.session_state.get("last_prompts"):
        st.info(f"🔄 {regen_idx}번 이미지를 다시 만드는 중입니다...")

        # 다시 만들기 실행
        last_prompts = st.session_state["last_prompts"]
        last_project = st.session_state["last_project_name"]

        if 1 <= regen_idx <= len(last_prompts):
            key_ok, key_message = get_api_key(provider, openai_key, gemini_key, claude_key)

            if not key_ok:
                st.error(f"{key_message} (다시 만들기 실패)")
                st.session_state["regenerate_index"] = None
            else:
                output_dir = Path("outputs") / last_project
                output_dir.mkdir(parents=True, exist_ok=True)

                original_prompt = last_prompts[regen_idx - 1]
                filename = f"{regen_idx:03d}.png"
                output_path = output_dir / filename

                try:
                    if provider.startswith("Claude 보정"):
                        st.write(f"Claude 프롬프트 보정 중...")
                        enhanced_prompt = enhance_prompt_with_claude(
                            original_prompt=original_prompt,
                            style=enhance_style,
                            model=claude_model,
                            api_key=claude_key,
                            ratio_label=ratio_label,
                        )
                    else:
                        enhanced_prompt = koreanize_prompt(original_prompt)

                    st.write(f"이미지 생성 중...")
                    generate_image_by_provider(
                        provider=provider,
                        prompt=enhanced_prompt,
                        output_path=output_path,
                        ratio_label=ratio_label,
                        openai_model=openai_model,
                        gemini_model=gemini_model,
                        openai_key=openai_key,
                        gemini_key=gemini_key,
                    )
                    st.success(f"✅ {filename} 다시 만들기 완료!")
                    st.image(str(output_path), caption=filename, use_container_width=True)
                except Exception as e:
                    st.error(f"다시 만들기 실패: {e}")
                finally:
                    st.session_state["regenerate_index"] = None
    else:
        st.info("프롬프트를 입력하고 설정을 확인한 뒤 이미지 생성 시작 버튼을 누르세요.")
