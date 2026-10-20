"""261020 HuggingFace 서비스 경진대회 — 수강생 투표 서버

실행 : python -m uvicorn app:app --host 0.0.0.0 --port 8000
규칙 : 이름 입력 → 1인 1표, 본인 투표 불가
점수 : 투표 65 + AI 30 + 대진 5 = 100
투표는 메모리에만 저장 → 서버를 끄면 초기화된다.
"""
import json
import os
import socket
import threading
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE = Path(__file__).resolve().parent
ROSTER_PATH = BASE / "roster.txt"
SCORES_PATH = Path(os.getenv("SCORES_PATH", BASE / "scores.json"))
PORT = int(os.getenv("PORT", "8000"))
VOTE_MAX, AI_MAX, INSTRUCTOR_MAX = 65, 30, 5

# AI 루브릭 (30점) — ../RUBRIC.md 와 동일
RUBRIC = [
    {"key": "model", "label": "HF 모델 활용", "max": 6, "desc": "모델 선정 이유 · 태스크 적합성"},
    {"key": "function", "label": "기능 완성도", "max": 7, "desc": "실제 동작 가능한 구조 · 예외 처리"},
    {"key": "creativity", "label": "창의성/서비스성", "max": 6, "desc": "아이디어 · 사용자 관점 · UI"},
    {"key": "readme", "label": "README.md", "max": 5, "desc": "소개 · 설치 · 실행 · 예시 · 모델 출처"},
    {"key": "requirements", "label": "requirements.txt", "max": 3, "desc": "누락 없는 라이브러리 목록"},
    {"key": "env", "label": "env/보안", "max": 3, "desc": ".env.example · .gitignore · 토큰 하드코딩 금지"},
]

lock = threading.Lock()
votes = {}  # {투표자: {"target": 받은 사람, "time": "17:51:03"}}
state = {"revealed": False}  # 강사가 공개 버튼을 눌러야 진짜 점수가 나간다


def load_roster():
    """roster.txt — 한 줄에 한 명"""
    lines = ROSTER_PATH.read_text(encoding="utf-8").splitlines()
    return [n.strip() for n in lines if n.strip() and not n.startswith("#")]


def load_scores():
    """scores.json — 요청마다 다시 읽는다. 형식은 scores.example.json 참고."""
    if not SCORES_PATH.exists():
        return {}
    try:
        return json.loads(SCORES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("[경고] scores.json 형식 오류 — AI/대진 점수를 0으로 처리합니다.")
        return {}


def clamp(value, top):
    try:
        return max(0.0, min(float(top), float(value)))
    except (TypeError, ValueError):
        return 0.0


def ai_breakdown(entry):
    """루브릭 항목별 점수 → (AI 총점, 항목 목록, 감점). items가 없으면 ai 숫자를 그대로 쓴다."""
    raw = entry.get("items") or {}
    items = []
    for r in RUBRIC:
        v = raw.get(r["key"])
        score, note = (v.get("score"), v.get("note", "")) if isinstance(v, dict) else (v, "")
        items.append({**r, "score": None if score is None else round(clamp(score, r["max"]), 1),
                      "note": str(note or "")})
    penalty = -clamp(abs(float(entry.get("penalty", 0) or 0)), AI_MAX)
    if raw:
        total = sum(i["score"] or 0 for i in items) + penalty
    else:
        total = entry.get("ai", 0)
    return round(clamp(total, AI_MAX), 1), items, penalty


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def is_host(request):
    """서버를 띄운 PC(강사 PC)에서 온 요청인지"""
    return request.client.host in ("127.0.0.1", "::1", "localhost", lan_ip())


def norm(name):
    return "".join(name.split())


app = FastAPI(title="HF 경진대회 투표")
STATIC = BASE / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def page_index():
    return FileResponse(STATIC / "index.html")


@app.get("/result")
def page_result():
    return FileResponse(STATIC / "result.html")


@app.get("/guide")
def page_guide():
    return FileResponse(STATIC / "guide.html")


@app.get("/docs/{name}")
def doc_md(name: str):
    files = {"guide": BASE.parent / "GUIDE.md", "rubric": BASE.parent / "RUBRIC.md"}
    if name not in files or not files[name].exists():
        raise HTTPException(404)
    return PlainTextResponse(files[name].read_text(encoding="utf-8"))


@app.get("/api/candidates")
def candidates():
    return load_roster()


@app.get("/api/check")
def check(name: str):
    """이름 확인 — 명단에 있는지, 이미 투표했는지 (투표 대상은 알려주지 않음)"""
    roster = {norm(n): n for n in load_roster()}
    voter = roster.get(norm(name))
    if not voter:
        raise HTTPException(404, "명단에 없는 이름입니다. 이름을 정확히 입력하세요.")
    return {"name": voter, "voted": voter in votes}


class VoteIn(BaseModel):
    name: str
    target: str


@app.post("/api/vote")
def vote(body: VoteIn):
    roster = {norm(n): n for n in load_roster()}
    voter = roster.get(norm(body.name))
    target = roster.get(norm(body.target))
    if not voter:
        raise HTTPException(404, "명단에 없는 이름입니다.")
    if not target:
        raise HTTPException(404, "투표 대상이 명단에 없습니다.")
    if voter == target:
        raise HTTPException(400, "본인에게는 투표할 수 없습니다.")
    with lock:
        if voter in votes:
            raise HTTPException(409, "이미 투표했습니다.")
        votes[voter] = {"target": target, "time": datetime.now().strftime("%H:%M:%S")}
    return {"ok": True, "name": voter, "voted_for": target}


@app.get("/api/host")
def host(request: Request):
    return {"is_host": is_host(request)}


class RevealIn(BaseModel):
    revealed: bool


@app.post("/api/reveal")
def reveal(body: RevealIn, request: Request):
    """진짜 순위 공개/가리기 — 강사 PC에서만"""
    if not is_host(request):
        raise HTTPException(403, "강사 PC에서만 공개할 수 있습니다.")
    state["revealed"] = body.revealed
    return state


@app.get("/api/result")
def result():
    """득표 순위 + AI·대진 합산. 누가 누구에게 투표했는지는 보내지 않는다.
    공개 전에는 점수 없이 이름·투표 진행률만 보낸다."""
    roster = load_roster()
    if not state["revealed"]:
        return {
            "revealed": False,
            "total": len(roster),
            "voted": len(votes),
            "not_voted": [n for n in roster if n not in votes],
            "names": roster,
        }
    scores = load_scores()
    counts = {n: 0 for n in roster}
    for v in votes.values():
        counts[v["target"]] = counts.get(v["target"], 0) + 1
    max_votes = max(counts.values(), default=0)

    rows = []
    for name, c in counts.items():
        s = scores.get(name, {})
        vote_score = round(c / max_votes * VOTE_MAX, 1) if max_votes else 0.0
        ai, items, penalty = ai_breakdown(s)
        inst = round(clamp(s.get("instructor", 0), INSTRUCTOR_MAX), 1)
        rows.append({
            "name": name,
            "votes": c,
            "vote_score": vote_score,
            "ai": ai,
            "instructor": inst,
            "total": round(vote_score + ai + inst, 1),
            "items": items,
            "penalty": penalty,
            "summary": str(s.get("summary", "")),
            "reason": str(s.get("reason", "")),
            "repo": str(s.get("repo", "")),
            "scored": bool(s),
        })
    # 동점 : 총점 → 득표수 → AI 점수
    key = lambda r: (r["total"], r["votes"], r["ai"])
    rows.sort(key=key, reverse=True)
    for i, r in enumerate(rows):
        r["rank"] = rows[i - 1]["rank"] if i and key(rows[i - 1]) == key(r) else i + 1
    return {
        "revealed": True,
        "total": len(roster),
        "voted": len(votes),
        "not_voted": [n for n in roster if n not in votes],
        "has_scores": bool(scores),
        "max": {"vote": VOTE_MAX, "ai": AI_MAX, "instructor": INSTRUCTOR_MAX},
        "max_votes": max_votes,
        "rubric": RUBRIC,
        "rows": rows,
    }


@app.on_event("startup")
def show_url():
    ip = lan_ip()
    print(f"
  수강생 투표 : http://{ip}:{PORT}")
    print(f"  결과 보기   : http://{ip}:{PORT}/result")
    print("  (투표는 메모리에만 저장 — 서버를 끄면 초기화됩니다)")
    print("  (진짜 순위 공개 버튼은 이 PC에서 /result 를 열 때만 보입니다)
")
