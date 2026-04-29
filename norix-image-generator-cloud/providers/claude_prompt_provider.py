import anthropic


def build_style_instruction(style: str) -> str:
    style_map = {
        "유튜브 썸네일용": (
            "Create a high-impact YouTube thumbnail prompt with strong contrast, "
            "clear subject, dramatic lighting, and clean empty space for Korean title text."
        ),
        "타로/신타로 실사풍": (
            "Create a realistic tarot or Korean spiritual tarot scene. Include hands, cards, "
            "warm candlelight, subtle Korean spiritual atmosphere, and cinematic realism."
        ),
        "카드뉴스용": (
            "Create a clean square social media card image prompt with a premium educational mood "
            "and clear empty space for Korean text."
        ),
        "쇼츠 배경용": (
            "Create a vertical short-form video background prompt with strong visual hook, "
            "clear top text space, and cinematic realism."
        ),
        "시네마틱 실사풍": (
            "Create a realistic cinematic scene with natural lighting, emotional depth, "
            "clear composition, and professional camera direction."
        ),
        "조선 무속 신비풍": (
            "Create a mystical Korean shamanic scene inspired by Joseon-era aesthetics, "
            "traditional fabric, candlelight, brass ritual objects, fog, and sacred atmosphere."
        ),
        "프리미엄 강의 광고풍": (
            "Create a premium online course advertisement visual with a clean desk, laptop, "
            "growth charts, professional atmosphere, and strong empty space for Korean text."
        ),
    }

    return style_map.get(style, style_map["시네마틱 실사풍"])


def enhance_prompt_with_claude(
    original_prompt: str,
    style: str,
    model: str,
    api_key: str,
    ratio_label: str,
) -> str:
    """
    Claude는 이미지를 직접 생성하지 않고, 이미지 생성용 영어 프롬프트를 다듬는 역할만 합니다.
    Anthropic Messages API를 사용합니다.
    """
    client = anthropic.Anthropic(api_key=api_key)

    style_instruction = build_style_instruction(style)

    system_prompt = """
You are an expert image prompt engineer.
Rewrite the user's Korean or English idea into a high-quality English image generation prompt.

Rules:
- Return only the final prompt.
- Do not add explanations.
- Do not include quotation marks.
- Preserve the original intent.
- Make the prompt specific and visual.
- Include subject, scene, mood, lighting, camera angle, style, and composition.
- If Korean text is needed, do NOT ask the image model to render Korean text.
- Instead, ask for clean empty space for Korean title text.
- Avoid copyrighted characters, brand logos, and real public figures.
"""

    user_prompt = f"""
Original idea:
{original_prompt}

Required style:
{style_instruction}

Required aspect ratio:
{ratio_label}

Rewrite into one strong English image generation prompt.
"""

    response = client.messages.create(
        model=model,
        max_tokens=700,
        system=system_prompt.strip(),
        messages=[
            {
                "role": "user",
                "content": user_prompt.strip(),
            }
        ],
    )

    # Anthropic 응답은 content 블록 배열입니다.
    # 일반 텍스트 응답은 response.content[0].text 에 들어옵니다.
    return response.content[0].text.strip()
