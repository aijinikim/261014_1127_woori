// 계산기 상태: 숫자와 연산자를 순서대로 담는 토큰 배열 + 현재 입력 중인 숫자
const state = {
  tokens: [],
  current: "0",
  justEvaluated: false,
};

const OP_SYMBOL = { "+": "+", "-": "−", "*": "×", "/": "÷" };
const PRECEDENCE = { "+": 1, "-": 1, "*": 2, "/": 2 };
const MAX_DIGITS = 16;

const expressionEl = document.getElementById("expression");
const resultEl = document.getElementById("result");
const historyEl = document.getElementById("history");
const historyListEl = document.getElementById("historyList");
const historyEmptyEl = document.getElementById("historyEmpty");

let history = loadHistory();

// ---------- 계산 로직 ----------

// 연산자 우선순위(×, ÷ 먼저)를 지켜 토큰 배열을 계산
function evaluate(tokens) {
  const output = [];
  const ops = [];

  const apply = () => {
    const op = ops.pop();
    const b = output.pop();
    const a = output.pop();
    if (op === "/" && b === 0) throw new Error("0으로 나눌 수 없습니다");
    output.push(
      op === "+" ? a + b : op === "-" ? a - b : op === "*" ? a * b : a / b
    );
  };

  for (const t of tokens) {
    if (typeof t === "number") {
      output.push(t);
    } else {
      while (ops.length && PRECEDENCE[ops[ops.length - 1]] >= PRECEDENCE[t]) apply();
      ops.push(t);
    }
  }
  while (ops.length) apply();
  return output[0];
}

// 부동소수점 오차 정리 (0.1 + 0.2 → 0.3)
function cleanNumber(n) {
  if (!isFinite(n)) throw new Error("계산할 수 없습니다");
  return parseFloat(n.toPrecision(12));
}

function formatNumber(str) {
  if (str === "-") return "-";
  const [int, dec] = String(str).split(".");
  const negative = int.startsWith("-");
  const digits = negative ? int.slice(1) : int;
  if (digits.includes("e")) return str;
  const withComma = Number(digits).toLocaleString("en-US");
  return (negative ? "-" : "") + withComma + (dec !== undefined ? "." + dec : "");
}

function tokensToText(tokens) {
  return tokens
    .map((t) => (typeof t === "number" ? formatNumber(String(t)) : OP_SYMBOL[t]))
    .join(" ");
}

// ---------- 입력 처리 ----------

function inputNumber(n) {
  if (state.justEvaluated) resetAll();
  const digitCount = state.current.replace(/[-.]/g, "").length;
  if (digitCount >= MAX_DIGITS) return;
  state.current = state.current === "0" ? n : state.current === "-0" ? "-" + n : state.current + n;
  render();
}

function inputDecimal() {
  if (state.justEvaluated) resetAll();
  if (state.current === null) state.current = "0";
  if (!state.current.includes(".")) state.current += ".";
  render();
}

function inputOperator(op) {
  state.justEvaluated = false;
  if (state.current === null) {
    // 연산자를 연달아 누르면 마지막 연산자를 교체
    if (state.tokens.length) state.tokens[state.tokens.length - 1] = op;
  } else {
    state.tokens.push(parseFloat(state.current));
    state.tokens.push(op);
    state.current = null;
  }
  render(op);
}

function equals() {
  if (state.current === null && !state.tokens.length) return;
  const tokens = [...state.tokens];
  if (state.current !== null) tokens.push(parseFloat(state.current));
  else tokens.pop(); // 끝에 남은 연산자 제거
  if (tokens.length < 3) return;

  const exprText = tokensToText(tokens) + " =";
  try {
    const value = cleanNumber(evaluate(tokens));
    addHistory(exprText, value);
    state.tokens = [];
    state.current = String(value);
    state.justEvaluated = true;
    render(null, exprText);
  } catch (err) {
    showError(err.message, exprText);
  }
}

function clearAll() {
  resetAll();
  render();
}

function resetAll() {
  state.tokens = [];
  state.current = "0";
  state.justEvaluated = false;
}

function backspace() {
  if (state.justEvaluated) return clearAll();
  if (state.current === null) return;
  state.current = state.current.slice(0, -1);
  if (state.current === "" || state.current === "-") state.current = "0";
  render();
}

function negate() {
  if (state.current === null) state.current = "0";
  state.current = state.current.startsWith("-") ? state.current.slice(1) : "-" + state.current;
  state.justEvaluated = false;
  render();
}

function percent() {
  if (state.current === null) return;
  state.current = String(cleanNumber(parseFloat(state.current) / 100));
  render();
}

// ---------- 화면 ----------

function render(activeOp = null, exprOverride = null) {
  resultEl.classList.remove("error");
  const shown = state.current ?? String(state.tokens[state.tokens.length - 2] ?? 0);
  const text = formatNumber(shown);
  resultEl.textContent = text;
  resultEl.classList.toggle("small", text.length > 11);

  expressionEl.textContent = exprOverride ?? tokensToText(state.tokens);

  document.querySelectorAll(".key.op").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.op === activeOp);
  });
}

function showError(message, exprText) {
  resetAll();
  state.justEvaluated = true;
  expressionEl.textContent = exprText;
  resultEl.textContent = message;
  resultEl.classList.add("error");
  resultEl.classList.remove("small");
}

// ---------- 기록 ----------

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem("calc-history")) || [];
  } catch {
    return [];
  }
}

function saveHistory() {
  try {
    localStorage.setItem("calc-history", JSON.stringify(history));
  } catch {}
}

function addHistory(expr, value) {
  history.unshift({ expr, value });
  history = history.slice(0, 30);
  saveHistory();
  renderHistory();
}

function renderHistory() {
  historyListEl.innerHTML = "";
  history.forEach(({ expr, value }) => {
    const li = document.createElement("li");
    li.innerHTML = `<div class="h-expr"></div><div class="h-result"></div>`;
    li.querySelector(".h-expr").textContent = expr;
    li.querySelector(".h-result").textContent = formatNumber(String(value));
    // 기록을 누르면 그 결과값을 불러옴
    li.addEventListener("click", () => {
      resetAll();
      state.current = String(value);
      state.justEvaluated = true;
      render();
    });
    historyListEl.appendChild(li);
  });
  historyEmptyEl.style.display = history.length ? "none" : "block";
}

// ---------- 이벤트 ----------

const actions = {
  clear: clearAll,
  backspace,
  percent,
  negate,
  decimal: inputDecimal,
  equals,
};

document.querySelector(".keys").addEventListener("click", (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  if (btn.dataset.num) inputNumber(btn.dataset.num);
  else if (btn.dataset.op) inputOperator(btn.dataset.op);
  else if (btn.dataset.action) actions[btn.dataset.action]();
});

// 키보드 입력 지원
document.addEventListener("keydown", (e) => {
  const k = e.key;
  let selector = null;

  if (/^[0-9]$/.test(k)) {
    inputNumber(k);
    selector = `[data-num="${k}"]`;
  } else if (["+", "-", "*", "/"].includes(k)) {
    e.preventDefault();
    inputOperator(k);
    selector = `[data-op="${k}"]`;
  } else if (k === "." || k === ",") {
    inputDecimal();
    selector = `[data-action="decimal"]`;
  } else if (k === "Enter" || k === "=") {
    e.preventDefault();
    equals();
    selector = `[data-action="equals"]`;
  } else if (k === "Backspace") {
    backspace();
    selector = `[data-action="backspace"]`;
  } else if (k === "Escape" || k === "Delete") {
    clearAll();
    selector = `[data-action="clear"]`;
  } else if (k === "%") {
    percent();
    selector = `[data-action="percent"]`;
  }

  // 눌린 버튼에 잠깐 눌림 효과
  const btn = selector && document.querySelector(`.keys ${selector}`);
  if (btn) {
    btn.classList.add("pressed");
    setTimeout(() => btn.classList.remove("pressed"), 100);
  }
});

document.getElementById("clearHistory").addEventListener("click", () => {
  history = [];
  saveHistory();
  renderHistory();
});

document.getElementById("historyToggle").addEventListener("click", () => {
  historyEl.classList.toggle("open");
});

// 테마 전환 (선택값 저장)
const themeBtn = document.getElementById("themeToggle");
function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  themeBtn.textContent = theme === "dark" ? "☀️" : "🌙";
}
themeBtn.addEventListener("click", () => {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  applyTheme(next);
  try {
    localStorage.setItem("calc-theme", next);
  } catch {}
});

let savedTheme = null;
try {
  savedTheme = localStorage.getItem("calc-theme");
} catch {}
applyTheme(
  savedTheme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
);

render();
renderHistory();
