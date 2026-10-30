// 접속 주소: 로컬이면 파일/localhost, 배포 후엔 xxx.vercel.app
const host = location.host || '로컬 파일';
document.getElementById('host').textContent = host;

// vercel.app 도메인이면 배포된 환경으로 표시
const env = host.endsWith('.vercel.app') ? 'Vercel 배포' : '로컬';
document.getElementById('env').textContent = env;

// 1초마다 시계 갱신
const clock = document.getElementById('clock');
function tick() {
  clock.textContent = new Date().toLocaleTimeString('ko-KR');
}
tick();
setInterval(tick, 1000);

// 좋아요 버튼 (새로고침하면 초기화)
let likes = 0;
const likeCount = document.getElementById('likeCount');
document.getElementById('likeBtn').addEventListener('click', () => {
  likes += 1;
  likeCount.textContent = likes;
});
