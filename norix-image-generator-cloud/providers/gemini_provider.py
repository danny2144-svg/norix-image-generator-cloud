from pathlib import Path

from google import genai
from google.genai import types


def gemini_aspect_ratio_from_label(ratio_label: str) -> str:
    """
    Gemini / Imagen 이미지 생성용 aspect_ratio 매핑입니다.
    Imagen 모델은 aspect_ratio를 지원합니다.
    """
    if ratio_label.startswith("16:9"):
        return "16:9"
    if ratio_label.startswith("9:16"):
        return "9:16"
    return "1:1"


def generate_image_gemini(
    prompt: str,
    output_path: Path,
    model: str,
    ratio_label: str,
    api_key: str,
) -> None:
    """
    Gemini Imagen API로 이미지를 만들고 PNG로 저장합니다.
    Google 공식 예시는 client.models.generate_images(...) 구조를 사용합니다.
    SDK나 모델 버전에 따라 응답 구조가 바뀌면 response.generated_images 부분을 확인하세요.
    """
    client = genai.Client(api_key=api_key)
    aspect_ratio = gemini_aspect_ratio_from_label(ratio_label)

    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio=aspect_ratio,
        ),
    )

    if not response.generated_images:
        raise RuntimeError("Gemini 이미지 생성 결과가 비어 있습니다.")

    generated_image = response.generated_images[0]

    # google-genai SDK의 generated_image.image 객체는 save 메서드를 지원합니다.
    generated_image.image.save(str(output_path))
