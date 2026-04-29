import base64
import io
from pathlib import Path

from openai import OpenAI
from PIL import Image


def openai_size_from_ratio(ratio_label: str) -> str:
    """
    OpenAI 이미지 모델용 size 매핑입니다.
    모델에 따라 지원 size가 달라질 수 있으니 오류가 나면 이 부분을 조정하세요.
    """
    if ratio_label.startswith("16:9"):
        return "1536x1024"
    if ratio_label.startswith("9:16"):
        return "1024x1536"
    return "1024x1024"


def generate_image_openai(
    prompt: str,
    output_path: Path,
    model: str,
    ratio_label: str,
    api_key: str,
) -> None:
    """
    OpenAI 이미지 생성 API로 이미지를 만들고 PNG로 저장합니다.
    응답 구조가 SDK 버전에 따라 달라질 경우 response.data[0].b64_json 부분을 확인하세요.
    """
    client = OpenAI(api_key=api_key)
    size = openai_size_from_ratio(ratio_label)

    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        n=1,
    )

    b64_data = response.data[0].b64_json
    image_bytes = base64.b64decode(b64_data)

    image = Image.open(io.BytesIO(image_bytes))
    image.save(output_path, format="PNG")
