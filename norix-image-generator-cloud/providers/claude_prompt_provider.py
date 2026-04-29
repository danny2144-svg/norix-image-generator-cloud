import anthropic


def build_style_instruction(style: str) -> str:
    style_map = {
        "유튜브 썸네일용": (
            "Photorealistic Korean YouTube thumbnail. Shot on professional camera, "
            "strong cinematic contrast, dramatic natural lighting, Korean person as the subject, "
            "real photograph aesthetic, clean empty space for Korean title text. NO illustration, NO anime."
        ),
        "타로/신타로 실사풍": (
            "Photorealistic Korean spiritual tarot reading scene. Real Korean hands holding cards, "
            "warm candlelight, traditional Korean spiritual atmosphere (신당, 한국 무속), "
            "shot on 85mm lens, cinematic realism, documentary photography style. NO illustration, NO anime."
        ),
        "카드뉴스용": (
            "Photorealistic clean square social media card with Korean educational atmosphere. "
            "If a person appears, they MUST be Korean. Real photograph style, premium minimalist mood, "
            "clean empty space for Korean text. NO illustration, NO anime, NO 3D render."
        ),
        "쇼츠 배경용": (
            "Photorealistic vertical short-form video background for Korean audience. "
            "Korean people if any human is shown, real-photograph cinematic style, "
            "strong visual hook, clear top text space. NO illustration, NO anime."
        ),
        "시네마틱 실사풍": (
            "Photorealistic cinematic scene set in Korea with Korean people. "
            "Natural lighting, emotional depth, professional camera direction, "
            "shot on Sony A7 IV with 85mm lens, shallow depth of field, real photograph quality."
        ),
        "조선 무속 신비풍": (
            "Photorealistic mystical Korean shamanic scene inspired by Joseon-era aesthetics. "
            "Traditional Korean fabric (한복, 무복), candlelight, brass ritual objects (놋그릇), "
            "fog, sacred atmosphere, Korean shaman appearance, cinematic real photograph. "
            "NO anime, NO illustration, NO fantasy art style."
        ),
        "프리미엄 강의 광고풍": (
            "Photorealistic premium Korean online course advertisement visual. "
            "Korean person if shown, clean Korean office or home setting, professional atmosphere, "
            "natural light, cinematic real photograph, strong empty space for Korean text. "
            "NO numbers, NO charts with figures, NO illustration."
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
You are an expert image prompt engineer for a KOREAN YouTube channel.
Rewrite the user's Korean or English idea into a high-quality English image generation prompt.

ABSOLUTE RULES (NEVER VIOLATE):

1. KOREAN PEOPLE ONLY:
   - All people in the image MUST be Korean.
   - Always specify: "Korean person", "Korean man", "Korean woman", "Korean people".
   - Describe Korean facial features clearly: black hair, dark brown eyes, East Asian features, Korean appearance.
   - NEVER describe people as: Caucasian, Western, European, American, African, Hispanic, Indian, Middle Eastern, mixed-race, ambiguous ethnicity.
   - Even if the original idea does not mention people's ethnicity, default to Korean.
   - Setting should feel Korean: Korean home, Korean street, Korean office, Korean cafe, Hangul signage in background if relevant.

2. UNIFIED PHOTOREALISTIC STYLE:
   - ALWAYS generate photorealistic, cinematic, real-photograph style images.
   - NEVER use: anime, manga, illustration, cartoon, 3D render, CGI, painting, drawing, stylized, watercolor, oil painting, sketch, comic book, Pixar, Disney, Studio Ghibli style.
   - Always include these style anchors: "photorealistic", "cinematic photography", "shot on Sony A7 IV", "85mm lens", "natural lighting", "shallow depth of field", "professional photography", "documentary style realism".
   - Color tone should be consistent: warm natural tones, soft cinematic grading.

3. NO NUMBERS OR STATISTICS IN IMAGE:
   - NEVER include any numbers, statistics, percentages, prices, currency amounts, dates, counts, or numerical figures in the prompt.
   - If the original idea contains numbers (like "3,000 subscribers", "8 million won", "30 years old", "Top 10"), DESCRIBE THE FEELING OR SITUATION instead.
   - Example: "한 달 800만 원 수익" → describe a feeling of financial success and relief on a Korean person's face, not the number itself.
   - Example: "구독자 3천 명 채널" → describe a small but growing YouTube channel atmosphere, not the number.
   - The image should NEVER show text, signs, charts, screens, or graphics with numbers on them.

4. GENERAL OUTPUT RULES:
   - Return only the final prompt. No explanations, no quotation marks.
   - Make the prompt specific and visual.
   - Include subject, scene, mood, lighting, camera angle, composition.
   - If Korean text is needed in the design, ask for "clean empty space for Korean title text" instead of rendering Korean characters.
   - Avoid copyrighted characters, brand logos, and real public figures.
"""

    user_prompt = f"""
Original idea (in Korean, may contain numbers — STRIP all numbers and replace with feelings/situations):
{original_prompt}

Required style direction:
{style_instruction}

Required aspect ratio:
{ratio_label}

Rewrite into ONE strong English image generation prompt.
Remember: Korean people only. Photorealistic only. No numbers or statistics in the image.
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
