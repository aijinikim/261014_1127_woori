# 🤗 HuggingFace 서비스 경진대회 — 수강생 지침 (2026-10-20)

> HuggingFace 모델로 **간단한 서비스**를 만들고, **새 GitHub 레포**로 제출합니다.
> 1위는 **수요일 점심 제공!** 🍱

## 1. 일정

| 시간 | 내용 |
|---|---|
| ~ **17:20** | 서비스 개발 + GitHub push + 드라이브 링크 등록 |
| 17:20 ~ 17:30 | 수강생 점검 (강사 확인, 레포 접근 가능 여부) |
| 17:30 ~ 17:50 | AI 채점 진행 · 투표 사이트에서 친구 작품 둘러보기 · 응원 채팅 |
| **17:50** | 🗳 수강생 투표 → 결과 발표 |

## 2. 점수 (100점)

| 구분 | 배점 | 방식 |
|---|---|---|
| 수강생 투표 | **65** | 1인 1표 · 본인 투표 불가 · `득표수 ÷ 최다 득표수 × 65` |
| AI 평가 | **30** | Claude가 레포를 루브릭으로 채점 (아래 6장) |
| 대진(강사) | **5** | 강사 평가 |

동점이면 **득표수 → AI 점수** 순으로 순위를 정합니다.

## 3. 이름 규칙 (꼭 지키세요)

- **레포명 / 폴더명 모두** : `261020_bucheon_huggingface_<이름이니셜>`
  - 예) 김대진 → `261020_bucheon_huggingface_kdj`
- **작업 폴더** : `wori/261020_8_hugging/261020_bucheon_huggingface_<이니셜>/`
  - 공지 원문의 `..._hugging_...` 폴더 표기는 레포명과 같게 `huggingface`로 통일합니다.
- 레포는 반드시 **Public**. 비공개이거나 없으면 AI 점수는 0점입니다.
- 레포명 규칙을 어기면 AI 점수에서 -2점입니다.

## 4. 진행 순서

### ① 모델 고르기
- [huggingface.co/models](https://huggingface.co/models)에서 태스크(텍스트 생성, 이미지 생성, 번역, 요약, 감정 분석, 이미지 분류 등)로 필터링합니다.
- 오늘 실습에서 쓴 방식인 `huggingface_hub.InferenceClient`를 추천합니다. 무거운 `torch` 설치 없이 바로 쓸 수 있습니다.

```python
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
client = InferenceClient(api_key=os.environ["HF_TOKEN"], provider="auto")

# 텍스트 생성 (v08_01 참고)
res = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1:novita",
    messages=[{"role": "user", "content": "안녕!"}],
)
print(res.choices[0].message.content)

# 이미지 생성 (v08_02 참고)
img = client.text_to_image("a cute cat in Bucheon", model="black-forest-labs/FLUX.1-schnell")
img.save("result.jpg")
```

### ② 서비스 만들기
- Claude를 활용해 자유롭게 개발하세요. CLI, **Gradio**, **Streamlit** 모두 가능합니다. 투표에서는 화면이 있는 쪽이 유리합니다.
- "누가, 왜 쓰는 서비스인지"가 한 줄로 설명되면 좋습니다.

### ③ env 관리 (보안)
```
261020_bucheon_huggingface_kdj/
├─ app.py
├─ .env              ← HF_TOKEN=hf_xxx  (커밋 금지!)
├─ .env.example      ← HF_TOKEN=        (값 없이 커밋)
├─ .gitignore        ← .env, __pycache__/, *.jpg 등
├─ requirements.txt
└─ README.md
```
- 코드에 토큰을 **직접 쓰지 마세요.** 발견되면 env 항목 0점이고 토큰 폐기 대상입니다.
- push 전에 `git status`로 `.env`가 목록에 **없는지** 확인하세요.
- 실수로 올렸다면 즉시 HF Settings → Access Tokens에서 해당 토큰을 **삭제하고 재발급**하세요.

### ④ requirements.txt
- `pip freeze > requirements.txt` 전체 덤프는 **금지**입니다. 실제로 `import`한 라이브러리만 적으세요.
```
huggingface_hub
python-dotenv
gradio
```
- 설치 확인: `python -m pip install -r requirements.txt`

### ⑤ README.md 템플릿
```markdown
# 서비스 이름
한 줄 소개 — 누가, 언제, 왜 쓰는지

## 사용 모델
- [모델명](https://huggingface.co/모델ID) — 선택 이유

## 설치
python -m pip install -r requirements.txt

## 환경 변수
.env.example을 복사해 .env를 만들고 HF_TOKEN을 입력

## 실행
python app.py

## 실행 화면
(스크린샷 또는 예시 입력/출력)

## 주의 / 한계
```

### ⑥ GitHub 업로드
1. github.com → **New repository** → 이름 `261020_bucheon_huggingface_<이니셜>` → **Public** → README 체크 **해제** → Create
2. 작업 폴더에서 아래 명령을 실행합니다.
```bash
git init
git add .
git status            # .env가 없는지 확인!
git commit -m "feat: HuggingFace 서비스 첫 업로드"
git branch -M main
git remote add origin https://github.com/<아이디>/261020_bucheon_huggingface_<이니셜>.git
git push -u origin main
```
> `wori` 폴더 자체가 이미 git 레포라면, 상위 레포의 `.gitignore`에 이 폴더를 추가해서 중복으로 커밋되지 않게 하세요.

### ⑦ 링크 등록
- **구글 드라이브 수업 자료 문서**의 `허깅페이스 깃허브` 칸에 레포 링크를 붙여넣으세요. 이 링크가 투표 사이트와 AI 채점 대상이 됩니다.

## 5. 제출 체크리스트

- [ ] 레포명 `261020_bucheon_huggingface_<이니셜>` · Public
- [ ] HuggingFace 모델을 사용하고, README에 모델 링크를 적음
- [ ] `requirements.txt` (사용 라이브러리만)
- [ ] `README.md` (소개 · 설치 · 실행 · 화면)
- [ ] `.env`는 커밋하지 않고 `.env.example` + `.gitignore`를 올림
- [ ] 코드에 토큰 하드코딩 없음
- [ ] 드라이브 문서에 링크 등록

## 6. AI 채점 루브릭 (30점)

| 항목 | 배점 | 기준 |
|---|---|---|
| HF 모델 활용 | 6 | 모델 선정 이유, 태스크 적합성 |
| 기능 완성도 | 7 | 코드가 실제 동작 가능한 구조인지, 예외 처리 |
| 창의성/서비스성 | 6 | 아이디어, 사용자 관점, UI |
| README.md | 5 | 소개 · 설치 · 실행 · 예시 · 모델 출처 |
| requirements.txt | 3 | 누락 없는 라이브러리 목록 |
| env/보안 | 3 | `.env.example` · `.gitignore`, 토큰 하드코딩 시 0점 |

감점: 레포명 규칙 위반 -2 · 레포 없음/비공개 → AI 0점.
자세한 기준은 [루브릭 페이지](/guide?doc=rubric)에서 볼 수 있습니다.

## 7. 투표 방법 (17:50)

1. 강의실 Wi-Fi에 연결된 상태로 **강사가 안내한 주소**(예: `http://192.168.0.12:8000`)에 접속합니다.
2. **본인 이름을 입력**합니다.
3. 가장 좋았던 친구 **1명**에게 투표합니다. 본인에게는 투표할 수 없고, 투표 후에는 바꿀 수 없습니다.

## 8. 자주 나오는 문제

| 증상 | 해결 |
|---|---|
| `pip` 실행 시 `Invalid version: '4.0.0-unsupported'` (pyodbc) | anaconda base 환경 문제입니다. `conda activate py311` 후 `python -m pip install -r requirements.txt` |
| `KeyError: 'HF_TOKEN'` | `.env` 위치(실행 폴더)와 `load_dotenv()` 호출을 확인하세요 |
| `401 Unauthorized` (HF) | 토큰 권한을 확인하세요. Inference Providers 사용 권한이 필요합니다 |
| 이미지 생성이 느림/실패 | `provider`를 바꾸거나 `FLUX.1-schnell` 같은 경량 모델을 사용하세요 |
| push 거부 (`rejected`) | 레포를 README 없이 만들었는지 확인하세요. 아니면 `git pull --rebase origin main` 후 push |
