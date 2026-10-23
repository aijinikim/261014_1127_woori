// ===== 상수 =====
const FLOOR_Y = 440;        // SVG 바닥선 y
const PX_PER_CM = 420 / 220; // 그림 전체 높이 420 = 220cm
const FIGURE_CM = 220;      // 실루엣 원본 크기(cm)
const REF_BMI = 22;         // 기준 실루엣 BMI

// 입력 유효 범위
const LIMITS = {
  height: { min: 100, max: 250, msg: "키는 100–250cm 사이로 입력하세요" },
  weight: { min: 20, max: 300, msg: "몸무게는 20–300kg 사이로 입력하세요" },
  age: { min: 1, max: 120, msg: "나이는 1–120세 사이로 입력하세요" },
};

// WHO 성인 BMI 기준 (max 미만이면 해당 단계)
const CATEGORIES = [
  { max: 18.5, label: "저체중", tone: "under" },
  { max: 25, label: "정상", tone: "normal" },
  { max: 30, label: "과체중", tone: "over" },
  { max: 35, label: "비만 1단계", tone: "obese" },
  { max: 40, label: "비만 2단계", tone: "obese" },
  { max: Infinity, label: "비만 3단계", tone: "obese" },
];

// ===== 계산 함수 =====

// BMI = 몸무게(kg) / 키(m)^2, 소수 첫째 자리 반올림
function calcBMI(heightCm, weightKg) {
  const m = heightCm / 100;
  return Math.round((weightKg / (m * m)) * 10) / 10;
}

// BMI → WHO 단계 (몇 번째 단계인지 index 포함)
function classifyWHO(bmi) {
  const index = CATEGORIES.findIndex((c) => bmi < c.max);
  return { ...CATEGORIES[index], index };
}

// 정상 BMI(18.5–24.9)에 해당하는 몸무게 범위
function normalRange(heightCm) {
  const m2 = (heightCm / 100) ** 2;
  return { min: 18.5 * m2, max: 24.9 * m2 };
}

// 기초대사량 (Mifflin-St Jeor)
function calcBMR(heightCm, weightKg, age, sex) {
  const base = 10 * weightKg + 6.25 * heightCm - 5 * age;
  return Math.round(sex === "male" ? base + 5 : base - 161);
}

// 값 검사: 빈칸이면 null, 범위 밖이면 error, 정상이면 value
function validate(name, raw) {
  if (raw.trim() === "") return { value: null, error: "" };
  const value = Number(raw);
  const { min, max, msg } = LIMITS[name];
  if (!Number.isFinite(value) || value < min || value > max) {
    return { value: null, error: msg };
  }
  return { value, error: "" };
}

// ===== 화면 요소 =====
const $ = (id) => document.getElementById(id);
const form = $("form");
const stage = $("stage");
const result = $("result");
const scaleItems = $("scale").querySelectorAll("li");

const fmt1 = (n) => n.toFixed(1);
const fmtInt = (n) => n.toLocaleString("ko-KR");

// 키 눈금자 그리기 (10cm마다 눈금, 20cm마다 숫자)
function drawRuler() {
  const ns = "http://www.w3.org/2000/svg";
  const ruler = $("ruler");
  const line = document.createElementNS(ns, "line");
  line.setAttribute("class", "ruler-line");
  line.setAttribute("x1", 40); line.setAttribute("x2", 40);
  line.setAttribute("y1", FLOOR_Y - 220 * PX_PER_CM); line.setAttribute("y2", FLOOR_Y);
  ruler.appendChild(line);

  for (let cm = 0; cm <= 220; cm += 10) {
    const y = FLOOR_Y - cm * PX_PER_CM;
    const major = cm % 20 === 0;
    const tick = document.createElementNS(ns, "line");
    tick.setAttribute("class", major ? "ruler-tick ruler-tick-major" : "ruler-tick");
    tick.setAttribute("x1", major ? 32 : 36); tick.setAttribute("x2", 40);
    tick.setAttribute("y1", y); tick.setAttribute("y2", y);
    ruler.appendChild(tick);

    if (major && cm > 0) {
      const label = document.createElementNS(ns, "text");
      label.setAttribute("class", "ruler-label");
      label.setAttribute("x", 28); label.setAttribute("y", y + 4);
      label.setAttribute("text-anchor", "end");
      label.textContent = cm;
      ruler.appendChild(label);
    }
  }
}

// 실루엣 크기 갱신: 키 → 전체 크기, BMI → 몸통 폭
function updateSilhouette(heightCm, bmi) {
  const s = heightCm / FIGURE_CM;
  const w = Math.min(1.6, Math.max(0.7, 1 + (bmi - REF_BMI) * 0.045));

  $("ghost").style.transform = `scale(${s})`;
  $("user").style.transform = `scale(${s})`;
  $("user-body").style.transform = `scaleX(${w})`;

  // 머리 꼭대기 위치에 키 표시선
  const topY = FLOOR_Y - heightCm * PX_PER_CM;
  $("height-mark").style.transform = `translateY(${topY}px)`;
  $("height-mark-label").textContent = `${fmt1(heightCm).replace(/\.0$/, "")}cm`;
}

// 필드 오류 표시
function showError(name, error) {
  $(`${name}-error`).textContent = error;
  $(name).closest(".field").classList.toggle("is-invalid", error !== "");
}

// 결과 비우기 (입력이 없거나 잘못됐을 때)
function clearResult(message) {
  stage.dataset.tone = "none";
  result.dataset.tone = "none";
  $("bmi-value").textContent = "—";
  $("category").textContent = message;
  $("range").textContent = "—";
  $("range-gap").textContent = "";
  $("bmr").textContent = "—";
  scaleItems.forEach((li) => li.classList.remove("is-current"));
  $("stage-svg").setAttribute("aria-label", "체형 비교 그림");
}

// 입력값을 읽어 화면 전체를 다시 그림
function render() {
  const h = validate("height", $("height").value);
  const w = validate("weight", $("weight").value);
  const a = validate("age", $("age").value);
  const sex = form.elements.sex.value;

  showError("height", h.error);
  showError("weight", w.error);
  showError("age", a.error);

  if (h.value === null || w.value === null) {
    clearResult(h.error || w.error ? "입력값을 확인하세요" : "키와 몸무게를 입력하세요");
    return;
  }

  const bmi = calcBMI(h.value, w.value);
  const cat = classifyWHO(bmi);
  const range = normalRange(h.value);

  stage.dataset.tone = cat.tone;
  result.dataset.tone = cat.tone;
  $("bmi-value").textContent = fmt1(bmi);
  $("category").textContent = cat.label;
  $("range").textContent = `${fmt1(range.min)}–${fmt1(range.max)} kg`;

  // 정상 범위와의 차이
  let gap = "";
  if (w.value < range.min) gap = `정상 범위까지 ${fmt1(range.min - w.value)}kg 늘리기`;
  else if (w.value > range.max) gap = `정상 범위까지 ${fmt1(w.value - range.max)}kg 줄이기`;
  $("range-gap").textContent = gap;

  $("bmr").textContent = a.value === null
    ? "나이를 입력하면 계산합니다"
    : `${fmtInt(calcBMR(h.value, w.value, a.value, sex))} kcal/일`;

  scaleItems.forEach((li, i) => li.classList.toggle("is-current", i === cat.index));

  updateSilhouette(h.value, bmi);
  $("stage-svg").setAttribute(
    "aria-label",
    `키 ${h.value}cm, BMI ${fmt1(bmi)} ${cat.label}. 점선은 같은 키에 BMI 22인 체형입니다.`
  );
}

// ===== 시작 =====
drawRuler();
form.addEventListener("input", render);
form.addEventListener("submit", (e) => e.preventDefault());
render();
