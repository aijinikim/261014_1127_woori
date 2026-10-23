const statusEl = document.getElementById("status");
const historyEl = document.getElementById("history");
const codeEl = document.getElementById("code");
const runBtn = document.getElementById("run");

let pyodide = null;
let pyRun = null;
let pyReset = null;
let outBuffer = [];      // 실행 1회분 stdout/stderr
const inputLog = [];     // ↑/↓ 로 불러올 이전 코드
let logIndex = 0;

// 1. Pyodide 로딩 + 파이썬 헬퍼 정의
async function init() {
  try {
    pyodide = await loadPyodide();
    pyodide.setStdout({ batched: (line) => outBuffer.push(line) });
    pyodide.setStderr({ batched: (line) => outBuffer.push(line) });

    pyodide.runPython(`
from pyodide.code import eval_code
ns = {}

def _run(src):
    r = eval_code(src, ns)   # 마지막 줄이 식이면 그 값을 반환
    return None if r is None else repr(r)

def _reset():
    ns.clear()
`);
    pyRun = pyodide.globals.get("_run");
    pyReset = pyodide.globals.get("_reset");

    statusEl.textContent = "준비 완료";
    statusEl.className = "status ready";
    runBtn.disabled = false;
    codeEl.focus();
  } catch (err) {
    statusEl.textContent = "로딩 실패";
    statusEl.className = "status failed";
    addEntry([["error", "Pyodide를 불러오지 못했습니다. 인터넷 연결을 확인하세요.\n" + err]]);
  }
}

// 2. 기록 영역에 카드 추가
function addEntry(lines) {
  const hint = historyEl.querySelector(".hint");
  if (hint) hint.remove();

  const entry = document.createElement("div");
  entry.className = "entry";
  for (const [type, text] of lines) {
    const pre = document.createElement("pre");
    pre.className = type;
    if (type === "error") {
      // traceback 중 마지막 줄(예: ZeroDivisionError: ...)만 강조
      const rows = text.trimEnd().split("\n");
      const last = rows.pop();
      pre.textContent = rows.length ? rows.join("\n") + "\n" : "";
      const b = document.createElement("b");
      b.textContent = last;
      pre.appendChild(b);
    } else {
      pre.textContent = text;
    }
    entry.appendChild(pre);
  }
  historyEl.appendChild(entry);
  historyEl.scrollTop = historyEl.scrollHeight;
}

// 3. 코드 실행
function run() {
  const code = codeEl.value;
  if (!pyRun || !code.trim()) return;

  const lines = [["input", code.split("\n").map((l, i) => (i ? "... " : ">>> ") + l).join("\n")]];
  outBuffer = [];
  try {
    const result = pyRun(code);
    if (outBuffer.length) lines.push(["stdout", outBuffer.join("\n")]);
    if (result !== undefined) lines.push(["result", result]);
  } catch (err) {
    if (outBuffer.length) lines.push(["stdout", outBuffer.join("\n")]);
    lines.push(["error", err.message]);
  }
  addEntry(lines);

  inputLog.push(code);
  logIndex = inputLog.length;
  codeEl.value = "";
  codeEl.focus();
}

// 4. 커서 위치에 문자열 삽입
function insertText(text) {
  codeEl.focus();
  codeEl.setRangeText(text, codeEl.selectionStart, codeEl.selectionEnd, "end");
}

// 버튼 패드
document.querySelectorAll("[data-insert]").forEach((btn) => {
  btn.addEventListener("click", () => insertText(btn.dataset.insert));
});

document.getElementById("backspace").addEventListener("click", () => {
  const start = codeEl.selectionStart;
  const end = codeEl.selectionEnd;
  codeEl.focus();
  if (start !== end) codeEl.setRangeText("", start, end, "end");
  else if (start > 0) codeEl.setRangeText("", start - 1, start, "end");
});

document.getElementById("clear").addEventListener("click", () => {
  codeEl.value = "";
  codeEl.focus();
});

document.getElementById("reset").addEventListener("click", () => {
  if (!pyReset) return;
  pyReset();
  addEntry([["info", "변수를 초기화했습니다."]]);
});

runBtn.addEventListener("click", run);

// 키보드: Ctrl+Enter 실행, Tab 들여쓰기, 빈 입력창에서 ↑/↓ 이전 코드
codeEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
    e.preventDefault();
    run();
  } else if (e.key === "Tab") {
    e.preventDefault();
    insertText("    ");
  } else if ((e.key === "ArrowUp" || e.key === "ArrowDown") && inputLog.length &&
             (codeEl.value === "" || codeEl.value === inputLog[logIndex])) {
    e.preventDefault();
    logIndex += e.key === "ArrowUp" ? -1 : 1;
    logIndex = Math.max(0, Math.min(inputLog.length, logIndex));
    codeEl.value = inputLog[logIndex] ?? "";
  }
});

init();
