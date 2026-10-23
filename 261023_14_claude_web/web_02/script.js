// ===== 요소 =====
const expressionEl = document.getElementById("expression");
const resultEl = document.getElementById("result");
const keysEl = document.querySelector(".keys");
const themeToggle = document.getElementById("themeToggle");
const historyList = document.getElementById("historyList");
const historyEmpty = document.getElementById("historyEmpty");
const clearHistoryBtn = document.getElementById("clearHistory");

const SYMBOLS = { "+": "+", "-": "−", "*": "×", "/": "÷" };
const MAX_DIGITS = 15;
const HISTORY_KEY = "calc-history";
const THEME_KEY = "calc-theme";
const HISTORY_LIMIT = 20;

// ===== 저장소 (사용 불가한 환경에서도 동작하도록) =====
function storageGet(key) {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function storageSet(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch {
    // 저장 실패는 무시
  }
}

function loadHistory() {
  try {
    const data = JSON.parse(storageGet(HISTORY_KEY));
    if (!Array.isArray(data)) return [];
    // 형태가 맞지 않는 항목은 버린다
    return data
      .filter((item) => item && typeof item.expr === "string" && typeof item.result === "string")
      .slice(0, HISTORY_LIMIT);
  } catch {
    return [];
  }
}

// ===== 상태 =====
// tokens: 확정된 숫자와 연산자 (예: ["2", "+", "3", "*"])
// current: 지금 입력 중인 숫자 (연산자 직후에는 "")
let tokens = [];
let current = "0";
let lastExpression = "";
let justEvaluated = false;
let error = false;
let history = loadHistory();

// ===== 계산 =====
function clean(n) {
  // 부동소수점 오차 정리 (0.1 + 0.2 → 0.3)
  return parseFloat(n.toPrecision(12));
}

function evaluate(list) {
  // 1단계: × ÷ 먼저 처리
  const stack = [parseFloat(list[0])];
  for (let i = 1; i < list.length; i += 2) {
    const op = list[i];
    const num = parseFloat(list[i + 1]);
    if (op === "*") {
      stack.push(stack.pop() * num);
    } else if (op === "/") {
      if (num === 0) return null;
      stack.push(stack.pop() / num);
    } else {
      stack.push(op, num);
    }
  }
  // 2단계: + − 처리
  let total = stack[0];
  for (let i = 1; i < stack.length; i += 2) {
    total = stack[i] === "+" ? total + stack[i + 1] : total - stack[i + 1];
  }
  return clean(total);
}

function toInput(n) {
  // 계산 결과를 다시 입력값으로 쓸 수 있는 문자열로
  const s = String(n);
  return s.includes("e") ? n.toPrecision(12).replace(/\.?0+e/, "e") : s;
}

// ===== 표시 =====
function formatNumber(str) {
  if (str === "" || str === "-") return str;
  if (str.includes("e")) return str;
  const negative = str.startsWith("-");
  const body = negative ? str.slice(1) : str;
  const [int, dec] = body.split(".");
  const grouped = int.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return (negative ? "-" : "") + grouped + (dec !== undefined ? "." + dec : "");
}

function formatTokens(list) {
  return list.map((t) => SYMBOLS[t] || formatNumber(t)).join(" ");
}

function render() {
  resultEl.classList.remove("error", "small");

  if (error) {
    expressionEl.textContent = lastExpression;
    resultEl.textContent = "정의되지 않음";
    resultEl.classList.add("error");
  } else if (justEvaluated) {
    expressionEl.textContent = lastExpression;
    resultEl.textContent = formatNumber(current);
  } else {
    expressionEl.textContent = formatTokens(tokens);
    // 연산자 직후에는 직전 숫자를 계속 보여준다
    const shown = current !== "" ? current : tokens[tokens.length - 2] || "0";
    resultEl.textContent = formatNumber(shown);
  }

  if (resultEl.textContent.length > 11) resultEl.classList.add("small");

  // 대기 중인 연산자 강조
  const pendingOp = current === "" && !error ? tokens[tokens.length - 1] : null;
  document.querySelectorAll(".key.op").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.op === pendingOp);
  });
}

// ===== 입력 처리 =====
function reset() {
  tokens = [];
  current = "0";
  lastExpression = "";
  justEvaluated = false;
  error = false;
}

function digitCount(str) {
  return str.replace(/[^0-9]/g, "").length;
}

function normalize(str) {
  // "5." → "5", "-0" → "0"
  if (str.endsWith(".")) str = str.slice(0, -1);
  return str === "-0" ? "0" : str;
}

function inputNumber(d) {
  if (error || justEvaluated) reset();
  if (current === "0") current = d;
  else if (current === "-0") current = "-" + d;
  else if (digitCount(current) < MAX_DIGITS) current += d;
}

function inputDecimal() {
  if (error || justEvaluated) reset();
  if (current === "") current = "0.";
  else if (!current.includes(".")) current += ".";
}

function inputOperator(op) {
  if (error) return;
  if (justEvaluated) {
    // 결과를 이어서 계산
    tokens = [];
    justEvaluated = false;
  }
  if (current === "") {
    // 연산자를 연달아 누르면 교체
    if (tokens.length) tokens[tokens.length - 1] = op;
    return;
  }
  tokens.push(normalize(current), op);
  current = "";
}

function percent() {
  if (error || current === "") return;
  current = toInput(clean(parseFloat(current) / 100));
  justEvaluated = false;
}

function negate() {
  if (error || current === "") return;
  if (justEvaluated) {
    tokens = [];
    justEvaluated = false;
  }
  current = current.startsWith("-") ? current.slice(1) : "-" + current;
}

function backspace() {
  if (error) {
    reset();
    return;
  }
  if (justEvaluated) {
    // 수식 줄만 지운다. 다음 숫자 입력은 새 계산으로 시작
    lastExpression = "";
    return;
  }
  if (current === "") {
    // 연산자를 지우고 직전 숫자로 돌아간다
    if (tokens.length) {
      tokens.pop();
      current = tokens.pop();
    }
    return;
  }
  if (current.includes("e")) {
    // 지수 표기는 한 글자씩 지우면 숫자가 깨지므로 초기화
    current = "0";
    return;
  }
  current = current.slice(0, -1);
  if (current === "" || current === "-") current = tokens.length ? "" : "0";
}

function equals() {
  if (error || justEvaluated) return;

  const list = [...tokens];
  if (current === "") list.pop(); // 끝에 남은 연산자는 무시
  else list.push(normalize(current));
  if (list.length < 3) return; // 연산자가 없으면 계산할 것이 없다

  lastExpression = formatTokens(list) + " =";
  const value = evaluate(list);
  tokens = [];

  if (value === null || !isFinite(value)) {
    error = true;
    current = "0";
    return;
  }

  current = toInput(value);
  justEvaluated = true;
  addHistory(lastExpression, current);
}

function handle(action, value) {
  switch (action) {
    case "num": inputNumber(value); break;
    case "op": inputOperator(value); break;
    case "decimal": inputDecimal(); break;
    case "percent": percent(); break;
    case "negate": negate(); break;
    case "backspace": backspace(); break;
    case "clear": reset(); break;
    case "equals": equals(); break;
  }
  render();
}

// ===== 기록 =====
function addHistory(expr, result) {
  history.unshift({ expr, result });
  history = history.slice(0, HISTORY_LIMIT);
  storageSet(HISTORY_KEY, JSON.stringify(history));
  renderHistory();
}

function recall(item) {
  reset();
  current = item.result;
  lastExpression = item.expr;
  justEvaluated = true;
  render();
}

function renderHistory() {
  historyList.innerHTML = "";
  history.forEach((item) => {
    const li = document.createElement("li");
    li.tabIndex = 0;
    li.title = "이 결과 불러오기";

    const expr = document.createElement("div");
    expr.className = "h-expr";
    expr.textContent = item.expr;

    const result = document.createElement("div");
    result.className = "h-result";
    result.textContent = formatNumber(item.result);

    li.append(expr, result);
    li.addEventListener("click", () => recall(item));
    li.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        // 전역 Enter(=)와 겹치지 않도록
        e.stopPropagation();
        recall(item);
      }
    });
    historyList.appendChild(li);
  });
  historyEmpty.hidden = history.length > 0;
  clearHistoryBtn.hidden = history.length === 0;
}

clearHistoryBtn.addEventListener("click", () => {
  history = [];
  storageSet(HISTORY_KEY, "[]");
  renderHistory();
});

// ===== 테마 =====
function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  themeToggle.textContent = theme === "dark" ? "☀️" : "🌙";
}

themeToggle.addEventListener("click", () => {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  applyTheme(next);
  storageSet(THEME_KEY, next);
});

// ===== 이벤트 =====
keysEl.addEventListener("click", (e) => {
  const btn = e.target.closest(".key");
  if (!btn) return;
  if (btn.dataset.num) handle("num", btn.dataset.num);
  else if (btn.dataset.op) handle("op", btn.dataset.op);
  else handle(btn.dataset.action);
});

const KEY_MAP = {
  Enter: "equals",
  "=": "equals",
  Backspace: "backspace",
  Escape: "clear",
  Delete: "clear",
  ".": "decimal",
  "%": "percent",
};

function flash(selector) {
  const btn = keysEl.querySelector(selector);
  if (!btn) return;
  btn.classList.add("pressed");
  setTimeout(() => btn.classList.remove("pressed"), 100);
}

document.addEventListener("keydown", (e) => {
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  const key = e.key;

  if (/^[0-9]$/.test(key)) {
    handle("num", key);
    flash(`[data-num="${key}"]`);
  } else if (SYMBOLS[key]) {
    handle("op", key);
    flash(`[data-op="${key}"]`);
  } else if (KEY_MAP[key]) {
    handle(KEY_MAP[key]);
    flash(`[data-action="${KEY_MAP[key]}"]`);
  } else {
    return;
  }

  // 브라우저 기본 동작(빠른 찾기, 포커스된 버튼 클릭 등)과 겹치지 않도록
  e.preventDefault();
  if (document.activeElement && document.activeElement.classList.contains("key")) {
    document.activeElement.blur();
  }
});

// ===== 시작 =====
const savedTheme = storageGet(THEME_KEY);
const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
applyTheme(savedTheme === "dark" || savedTheme === "light" ? savedTheme : prefersDark ? "dark" : "light");
renderHistory();
render();
