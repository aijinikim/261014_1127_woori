// Vercel Function: POST /api/chat
// 브라우저가 보낸 대화 내역을 Claude에 전달하고, 답변을 글자 단위로 스트리밍한다.
// API 키는 Vercel 환경변수 ANTHROPIC_API_KEY 에서 SDK가 자동으로 읽는다.
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

const SYSTEM_PROMPT = '당신은 친절한 한국어 도우미입니다. 짧고 명확하게 답하세요.';
const MAX_HISTORY = 20; // 너무 긴 대화로 비용이 커지는 것을 막는다

export async function POST(request) {
  let messages;
  try {
    ({ messages } = await request.json());
  } catch {
    return new Response('JSON 형식이 아닙니다.', { status: 400 });
  }
  if (!Array.isArray(messages) || messages.length === 0) {
    return new Response('messages 배열이 필요합니다.', { status: 400 });
  }

  const stream = client.beta.messages.stream({
    model: 'claude-opus-5-5',
    max_tokens: 64000,
    output_config: { effort: 'low' }, // 채팅은 low 로 충분, 응답이 빠르다
    // 안전 분류기가 거절하면 서버가 다른 모델로 자동 재시도
    betas: ['server-side-fallback-2026-07-01'],
    fallbacks: 'default',
    system: SYSTEM_PROMPT,
    messages: messages.slice(-MAX_HISTORY),
  });

  const encoder = new TextEncoder();
  const body = new ReadableStream({
    async start(controller) {
      try {
        for await (const event of stream) {
          if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
            controller.enqueue(encoder.encode(event.delta.text));
          }
        }
        const final = await stream.finalMessage();
        if (final.stop_reason === 'refusal') {
          controller.enqueue(encoder.encode('\n[이 요청에는 답변할 수 없습니다]'));
        }
      } catch (err) {
        console.error(err);
        controller.enqueue(encoder.encode('\n[오류가 발생했습니다. Vercel 로그를 확인하세요]'));
      }
      controller.close();
    },
  });

  return new Response(body, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
}
