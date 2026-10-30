// 대화 내역: Claude API 형식 그대로 [{ role, content }] 로 보관
const messages = [];

const log = document.getElementById('log');
const form = document.getElementById('form');
const input = document.getElementById('input');
const sendBtn = document.getElementById('send');

function addBubble(role, text) {
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.textContent = text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
  return div;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  input.value = '';
  sendBtn.disabled = true;
  addBubble('user', text);
  messages.push({ role: 'user', content: text });

  const bubble = addBubble('assistant', '…');
  let answer = '';

  try {
    // API 키는 서버(api/chat.js)에만 있다. 브라우저는 /api/chat 만 호출한다.
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    });
    if (!res.ok) throw new Error(await res.text());

    // 스트리밍 응답을 조각(chunk)마다 읽어서 말풍선에 이어 붙인다
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      answer += decoder.decode(value, { stream: true });
      bubble.textContent = answer;
      log.scrollTop = log.scrollHeight;
    }
    messages.push({ role: 'assistant', content: answer });
  } catch (err) {
    bubble.textContent = `요청 실패: ${err.message}`;
    messages.pop(); // 실패한 질문은 대화 내역에서 뺀다
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
});
