'use strict';

const OPERATOR_SYMBOLS = { '+': '+', '-': '−', '*': '×', '/': '÷' };
const MAX_DIGITS = 15;
const ERROR_MESSAGE = '0으로 나눌 수 없어요';
const SOUND_STORAGE_KEY = 'calc-sound';

// 부동소수 오차 정리 (0.1 + 0.2 → 0.3)
function tidy(n) {
  return parseFloat(n.toPrecision(12));
}

function numberToString(n) {
  if (Object.is(n, -0)) return '0';
  const abs = Math.abs(n);
  if (abs !== 0 && (abs >= 1e15 || abs < 1e-9)) {
    return String(parseFloat(n.toExponential(8)));
  }
  return String(n);
}

// [숫자, 연산자, 숫자, ...] — × ÷ 먼저, + − 다음
function evaluate(list) {
  const terms = [Number(list[0])];
  const signs = [];
  for (let i = 1; i < list.length; i += 2) {
    const op = list[i];
    const n = Number(list[i + 1]);
    const last = terms.length - 1;
    if (op === '*') {
      terms[last] *= n;
    } else if (op === '/') {
      if (n === 0) throw new RangeError('division by zero');
      terms[last] /= n;
    } else {
      signs.push(op);
      terms.push(n);
    }
  }
  let result = terms[0];
  signs.forEach((op, i) => {
    result = op === '+' ? result + terms[i + 1] : result - terms[i + 1];
  });
  if (!Number.isFinite(result)) throw new RangeError('overflow');
  return tidy(result);
}

// 표시용 — 정수부에만 콤마
function formatNumber(str) {
  if (str.includes('e')) return str;
  const negative = str.startsWith('-');
  const body = negative ? str.slice(1) : str;
  const [int, frac] = body.split('.');
  const grouped = int.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return (negative ? '-' : '') + grouped + (frac !== undefined ? '.' + frac : '');
}

function formatExpression(list) {
  return list
    .map((t, i) => (i % 2 === 1 ? OPERATOR_SYMBOLS[t] : formatNumber(t)))
    .join(' ');
}

function createCalculator() {
  let tokens = [];      // 확정된 [숫자, 연산자, ...]
  let current = '0';    // 입력 중인 숫자, 연산자 직후에는 null
  let justEvaluated = false;
  let error = false;
  let lastExpression = '';

  function reset() {
    tokens = [];
    current = '0';
    justEvaluated = false;
    error = false;
    lastExpression = '';
  }

  function startFreshIfNeeded() {
    if (error || justEvaluated) reset();
  }

  return {
    digit(d) {
      startFreshIfNeeded();
      if (current === null) current = '0';
      if (current.replace(/\D/g, '').length >= MAX_DIGITS) return;
      if (current === '0') current = d;
      else if (current === '-0') current = '-' + d;
      else current += d;
    },

    dot() {
      startFreshIfNeeded();
      if (current === null) current = '0';
      if (!current.includes('.')) current += '.';
    },

    operator(op) {
      if (error) { reset(); return; }
      if (justEvaluated) {
        tokens = [];
        justEvaluated = false;
        lastExpression = '';
      }
      if (current === null) {
        tokens[tokens.length - 1] = op;
      } else {
        tokens.push(numberToString(Number(current)), op);
        current = null;
      }
    },

    equals() {
      if (error || justEvaluated) return;
      const list = current === null ? tokens.slice(0, -1) : [...tokens, current];
      if (list.length < 3) return;
      const expression = formatExpression(list.map((t, i) => (i % 2 ? t : numberToString(Number(t))))) + ' =';
      try {
        current = numberToString(evaluate(list));
        lastExpression = expression;
        justEvaluated = true;
      } catch {
        error = true;
        lastExpression = expression;
      }
      tokens = [];
    },

    percent() {
      if (error) { reset(); return; }
      if (current === null) return;
      current = numberToString(tidy(Number(current) / 100));
    },

    negate() {
      if (error) reset();
      if (current === null) current = '0';
      current = current.startsWith('-') ? current.slice(1) : '-' + current;
    },

    backspace() {
      if (error) { reset(); return; }
      if (justEvaluated) {
        lastExpression = '';
        justEvaluated = false;
        return;
      }
      if (current === null) {
        tokens.pop();
        current = tokens.pop();
        return;
      }
      current = current.slice(0, -1);
      if (current === '' || current === '-') current = '0';
    },

    clear: reset,

    // 화면에 그릴 상태
    view() {
      if (error) {
        return { expression: lastExpression, result: ERROR_MESSAGE, raw: null, error: true, pendingOp: null };
      }
      const shown = current === null ? tokens[tokens.length - 2] : current;
      const live = current === null ? tokens : [...tokens, current];
      return {
        expression: justEvaluated ? lastExpression : (tokens.length ? formatExpression(live) : ''),
        result: formatNumber(shown),
        raw: shown,
        error: false,
        pendingOp: current === null ? tokens[tokens.length - 1] : null,
      };
    },
  };
}

// 효과음 — Web Audio로 짧은 클릭음 합성
function createSound() {
  let ctx = null;
  return function play(tone) {
    try {
      ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
      if (ctx.state === 'suspended') ctx.resume();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const now = ctx.currentTime;
      osc.type = 'sine';
      osc.frequency.value = tone === 'equals' ? 660 : 1100;
      gain.gain.setValueAtTime(0.0001, now);
      gain.gain.exponentialRampToValueAtTime(0.08, now + 0.005);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.06);
      osc.connect(gain).connect(ctx.destination);
      osc.start(now);
      osc.stop(now + 0.07);
    } catch {
      // 오디오를 쓸 수 없는 환경이면 무음
    }
  };
}

function readSoundSetting() {
  try {
    return localStorage.getItem(SOUND_STORAGE_KEY) !== 'off';
  } catch {
    return true;
  }
}

function writeSoundSetting(on) {
  try {
    localStorage.setItem(SOUND_STORAGE_KEY, on ? 'on' : 'off');
  } catch {
    // 저장 불가 환경에서는 이번 방문 동안만 유지
  }
}

function init() {
  const calc = createCalculator();
  const playSound = createSound();
  const exprEl = document.querySelector('[data-expr]');
  const resultEl = document.querySelector('[data-result]');
  const toastEl = document.querySelector('[data-toast]');
  const toggleEl = document.querySelector('[data-sound-toggle]');
  const opKeys = document.querySelectorAll('[data-action="operator"]');
  let soundOn = readSoundSetting();
  let toastTimer = null;

  function fitResult(text) {
    const len = text.length;
    const size = len <= 9 ? 56 : len <= 12 ? 44 : len <= 16 ? 34 : 28;
    resultEl.style.setProperty('--result-size', size + 'px');
  }

  function render() {
    const v = calc.view();
    exprEl.textContent = v.expression;
    exprEl.scrollLeft = exprEl.scrollWidth;
    resultEl.textContent = v.result;
    resultEl.classList.toggle('is-error', v.error);
    resultEl.dataset.raw = v.raw ?? '';
    if (!v.error) fitResult(v.result);
    opKeys.forEach((key) => {
      key.setAttribute('aria-pressed', String(key.dataset.value === v.pendingOp));
    });
  }

  function renderToggle() {
    toggleEl.setAttribute('aria-checked', String(soundOn));
  }

  function feedback(action) {
    if (!soundOn) return;
    playSound(action);
    if (navigator.vibrate) navigator.vibrate(10);
  }

  function run(action, value) {
    if (typeof calc[action] !== 'function') return;
    calc[action](value);
    feedback(action);
    render();
  }

  function showToast() {
    clearTimeout(toastTimer);
    toastEl.hidden = false;
    toastEl.classList.remove('is-leaving');
    toastTimer = setTimeout(() => {
      toastEl.classList.add('is-leaving');
      toastTimer = setTimeout(() => { toastEl.hidden = true; }, 150);
    }, 1500);
  }

  async function copyResult() {
    const raw = resultEl.dataset.raw;
    if (!raw) return;
    try {
      await navigator.clipboard.writeText(raw);
      showToast();
    } catch {
      // 클립보드 권한이 없으면 조용히 무시
    }
  }

  document.querySelector('.keypad').addEventListener('click', (e) => {
    const key = e.target.closest('[data-action]');
    if (key) run(key.dataset.action, key.dataset.value);
  });

  resultEl.addEventListener('click', copyResult);

  toggleEl.addEventListener('click', () => {
    soundOn = !soundOn;
    writeSoundSetting(soundOn);
    renderToggle();
  });

  const KEY_ALIASES = { '=': 'Enter', Delete: 'Escape', x: '*', X: '*' };

  document.addEventListener('keydown', (e) => {
    if (e.altKey || e.metaKey) return;
    if (e.ctrlKey) {
      if (e.key.toLowerCase() === 'c' && !String(window.getSelection())) copyResult();
      return;
    }
    const name = KEY_ALIASES[e.key] || e.key;
    const key = document.querySelector(`[data-key="${CSS.escape(name)}"]`);
    if (!key) return;
    e.preventDefault();
    key.classList.add('is-pressed');
    setTimeout(() => key.classList.remove('is-pressed'), 120);
    run(key.dataset.action, key.dataset.value);
  });

  renderToggle();
  render();
}

document.addEventListener('DOMContentLoaded', init);
