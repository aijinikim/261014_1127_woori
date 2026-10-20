# HF 경진대회 투표 서버

수강생이 접속해서 **본인 이름을 입력**하고, 본인을 뺀 친구 한 명에게 **1표**를 줍니다.
결과 화면에서 **투표(65) + AI(30) + 대진(5)** 을 합산해 순위를 보여줍니다.

| 주소 | 용도 |
|---|---|
| `/` | 투표 (이름 입력 → 작품 선택 → 투표) + 결과 보기 버튼 |
| `/result` | 득표·합산 순위, 미투표자 (3초마다 자동 갱신, 언제든 볼 수 있음) |
| `/guide` | 경진대회 지침 (`../GUIDE.md`, `?doc=rubric`) |

## 실행

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```
터미널에 나오는 주소(예: `http://192.168.0.12:8000`)를 수강생에게 안내합니다.

> ⚠️ 투표는 **메모리에만 저장**됩니다. 서버를 끄면(`Ctrl + C`) 투표가 모두 초기화됩니다.
> 투표 중에는 서버를 끄지 마세요.

다른 기기에서 접속이 안 되면 관리자 PowerShell에서 방화벽을 엽니다.
```powershell
New-NetFirewallRule -DisplayName "hf-vote-8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

## 명단 — `roster.txt`

한 줄에 한 명씩 적습니다(형식은 `roster.example.txt`). 수정하면 바로 반영됩니다.
입력한 이름의 띄어쓰기는 무시합니다(`홍 길동` = `홍길동`).

## AI · 대진 점수 — `scores.json`

루브릭 항목별로 넣으면 결과 화면에서 이름을 누를 때 **항목별 막대와 근거**가 보입니다. 전체 예시는 `scores.example.json`을 참고하세요.
```json
{
  "홍길동": {
    "summary": "키워드로 만드는 4컷 AI 동화",
    "repo": "https://github.com/.../261020_bucheon_huggingface_hgd",
    "items": {
      "model":        { "score": 5, "note": "선정 이유 명시" },
      "function":     { "score": 6, "note": "API 실패 처리 없음" },
      "creativity":   { "score": 5, "note": "" },
      "readme":       { "score": 4, "note": "실행 화면 없음" },
      "requirements": { "score": 3, "note": "" },
      "env":          { "score": 3, "note": "" }
    },
    "penalty": 0,
    "reason": "총평",
    "instructor": 4
  },
  "김철수": { "ai": 18.5, "instructor": 3 }
}
```
- 루브릭(서버의 `RUBRIC`, `../RUBRIC.md`와 같음): model 6 · function 7 · creativity 6 · readme 5 · requirements 3 · env 3 = 30
- AI 점수 = 항목 합 + `penalty`(예: -2)이며 0~30으로 자릅니다. 항목마다 만점을 넘으면 만점으로 자릅니다.
- `items` 없이 `"ai": 숫자`만 넣어도 됩니다. 이 경우 상세 화면에 총점만 표시됩니다. `instructor`는 0~5입니다.
- 키는 `roster.txt`의 이름과 같아야 합니다.
- 결과 화면이 3초마다 다시 읽으므로 **서버를 재시작하지 않아도** 바로 합산됩니다. 재시작하면 투표가 지워지니 주의하세요.

## 결과 화면 (`/result`)

- 누적 막대(투표·AI·대진)가 **아래 순위부터 서서히 차오르고**, 총점 숫자도 함께 올라갑니다. **▶ 다시 재생** 버튼으로 다시 볼 수 있습니다.
- 이름(행)을 누르면 세부 점수가 열립니다. 투표 환산식, 루브릭 6개 항목 점수와 근거, 감점, 총평, 대진 점수를 볼 수 있습니다.
- 투표를 마친 수강생은 **📊 내 점수 보기**(`/result?me=이름`)로 들어오면 본인 행이 강조되고 상세가 자동으로 열립니다.
- **표로 보기**로 숫자 표도 볼 수 있습니다.

## 규칙 · 점수

- 명단에 있는 이름만 투표할 수 있고, 본인에게는 투표할 수 없습니다. 1인 1표이며 변경할 수 없습니다.
- 누가 누구에게 투표했는지는 어디에도 공개하지 않습니다.
- 투표 점수 = `득표수 ÷ 최다 득표수 × 65`, 총점 = 투표 + AI + 대진입니다.
- 동점이면 득표수, 그다음 AI 점수 순으로 순위를 정합니다.

`roster.txt`(실명)와 `scores.json`은 커밋하지 않습니다.
