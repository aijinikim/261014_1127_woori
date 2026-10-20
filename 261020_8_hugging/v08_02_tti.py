import os
from huggingface_hub import InferenceClient

client = InferenceClient(
    provider="nscale",
    api_key=os.environ["HF_TOKEN"],
)

# output is a PIL.Image object
q = input("생성할 이미지를 설명해주세요 : ")
image = client.text_to_image(
    q,
    model="black-forest-labs/FLUX.1-schnell",
)

image.save("./tti_result.jpg")

print("이미지 생성이 잘 됐습니다.")