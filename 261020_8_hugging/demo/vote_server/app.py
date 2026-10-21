"""261020 HuggingFace 서비스 경진대회 — 수강생 투표 서버

실행 : python -m uvicorn app:app --host 0.0.0.0 --port 8000
규칙 : 이름 입력 → 1인 1표, 본인 투표 불가
점수 : 투표 65 + AI 30 + 대진 5 = 100
투표는 메모리에만 저장 → 서버를 끄면 초기화된다.
결과 공개 단계 (강사 비밀번호 필요) : 0 발표 전 → 1 수강생 투표 결과 반영 → 2 AI + 대진 점수 반영
"""
import json
import os
import secrets
import socket
import threading
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")
ROSTER_PATH = BASE / "roster.txt"
SCORES_PATH = Path(os.getenv("SCORES_PATH", BASE / "scores.json"))
PORT = int(os.getenv("PORT", "8000"))
VOTE_MAX, AI_MAX, INSTRUCTOR_MAX = 65, 30, 5
BONUS_MAX = 2  # 가산점 상한 (예: 시스템 프롬프트를 영어로 작성 +1). AI 총점은 그래도 30을 넘지 않는다

# 강사 비밀번호 — .env 의 ADMIN_PASSWORD. 비어 있으면 실행할 때마다 임시 비밀번호를 만들어 터미널에 보여준다.
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()
TEMP_PASSWORD = not ADMIN_PASSWORD
if TEMP_PASSWORD:
    ADMIN_PASSWORD = f"{secrets.randbelow(10000):04d}"

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
notices = {}  # {기기 IP: {"id": 번호, "msg": 메시지}} — 결과 화면을 연 특정 기기에 팝업
seen = {}  # {기기 IP: 마지막으로 결과 화면을 불러온 시각}
state = {"stage": 0}  # 0 발표 전(가짜 경쟁) · 1 투표 결과만 · 2 AI + 대진까지 합산


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
    """루브릭 항목별 점수 → (AI 총점, 항목 목록, 감점, 가산점). items가 없으면 ai 숫자를 그대로 쓴다."""
    raw = entry.get("items") or {}
    items = []
    for r in RUBRIC:
        v = raw.get(r["key"])
        score, note = (v.get("score"), v.get("note", "")) if isinstance(v, dict) else (v, "")
        items.append({**r, "score": None if score is None else round(clamp(score, r["max"]), 1),
                      "note": str(note or "")})
    penalty = -clamp(abs(float(entry.get("penalty", 0) or 0)), AI_MAX)
    bonus = clamp(entry.get("bonus", 0), BONUS_MAX)
    if raw:
        total = sum(i["score"] or 0 for i in items) + penalty + bonus
    else:
        total = entry.get("ai", 0)
    return round(clamp(total, AI_MAX), 1), items, penalty, bonus


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
    return request.client.host in ("127.0.0.1", "::1", lan_ip())


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


class StageIn(BaseModel):
    stage: int
    password: str


@app.post("/api/stage")
def set_stage(body: StageIn):
    """결과 공개 단계 변경 — 강사 비밀번호 필요"""
    if not secrets.compare_digest(body.password.encode(), ADMIN_PASSWORD.encode()):
        time.sleep(1)  # 비밀번호 무작위 대입 지연
        raise HTTPException(401, "비밀번호가 틀렸습니다.")
    if body.stage not in (0, 1, 2):
        raise HTTPException(400, "stage는 0, 1, 2 중 하나입니다.")
    state["stage"] = body.stage
    return state


class NoticeIn(BaseModel):
    ip: str
    msg: str
    password: str = ""


@app.post("/api/notice")
def send_notice(body: NoticeIn, request: Request):
    """특정 기기(IP)의 결과 화면에 팝업 메시지 — 강사 PC이거나 비밀번호가 맞아야 한다"""
    if not is_host(request) and not secrets.compare_digest(body.password.encode(), ADMIN_PASSWORD.encode()):
        time.sleep(1)
        raise HTTPException(401, "비밀번호가 틀렸습니다.")
    msg = body.msg.strip()[:200]
    if not msg:
        raise HTTPException(400, "메시지를 입력하세요.")
    prev = notices.get(body.ip.strip(), {}).get("id", 0)
    notices[body.ip.strip()] = {"id": prev + 1, "msg": msg}
    return {"ok": True, "ip": body.ip.strip(), "online": time.time() - seen.get(body.ip.strip(), 0) < 15}


@app.get("/api/clients")
def clients(request: Request):
    """최근 15초 안에 결과 화면을 연 기기 목록 — 강사 PC에서만"""
    if not is_host(request):
        raise HTTPException(403, "강사 PC에서만 볼 수 있습니다.")
    now = time.time()
    host_ips = {"127.0.0.1", "::1", lan_ip()}
    return [{"ip": ip, "ago": round(now - t), "host": ip in host_ips}
            for ip, t in sorted(seen.items(), key=lambda kv: -kv[1]) if now - t < 15]


@app.get("/api/result")
def result(request: Request):
    """단계별 결과. 누가 누구에게 투표했는지는 보내지 않는다.
    0단계 : 이름·투표 진행률만 / 1단계 : 투표 점수만 / 2단계 : AI·대진 합산"""
    roster = load_roster()
    stage = state["stage"]
    ip = request.client.host
    seen[ip] = time.time()
    base = {
        "notice": notices.get(ip),
        "stage": stage,
        "total": len(roster),
        "voted": len(votes),
        "not_voted": [n for n in roster if n not in votes],
    }
    if stage == 0:
        return {**base, "names": roster}

    counts = {n: 0 for n in roster}
    for v in votes.values():
        counts[v["target"]] = counts.get(v["target"], 0) + 1
    max_votes = max(counts.values(), default=0)
    scores = load_scores() if stage == 2 else {}  # 2단계 전에는 AI·대진 점수를 읽지도 보내지도 않는다

    rows = []
    for name, c in counts.items():
        s = scores.get(name, {})
        vote_score = round(c / max_votes * VOTE_MAX, 1) if max_votes else 0.0
        ai, items, penalty, bonus = ai_breakdown(s)
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
            "bonus": bonus,
            "bonus_note": str(s.get("bonus_note", "")),
            "instructor_items": [
                {"label": str(i.get("label", "")), "max": clamp(i.get("max", 1), INSTRUCTOR_MAX),
                 "score": clamp(i.get("score", 0), INSTRUCTOR_MAX), "note": str(i.get("note", ""))}
                for i in (s.get("instructor_items") or []) if isinstance(i, dict)
            ],
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
        **base,
        "has_scores": bool(scores),
        "max": {"vote": VOTE_MAX, "ai": AI_MAX, "instructor": INSTRUCTOR_MAX},
        "max_votes": max_votes,
        "rubric": RUBRIC,
        "rows": rows,
    }


@app.on_event("startup")
def show_url():
    ip = lan_ip()
    print(f"\n  수강생 투표 : http://{ip}:{PORT}")
    print(f"  결과 보기   : http://{ip}:{PORT}/result")
    print("  (투표는 메모리에만 저장 — 서버를 끄면 초기화됩니다)")
    if TEMP_PASSWORD:
        print(f"  강사 비밀번호 (임시) : {ADMIN_PASSWORD}   ← .env 의 ADMIN_PASSWORD 로 고정할 수 있습니다")
    else:
        print("  강사 비밀번호 : .env 의 ADMIN_PASSWORD")
    print()
