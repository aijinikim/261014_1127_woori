# 평일 09:10 작업 스케줄러가 실행 — 직전 거래일 증시 요약을 카카오톡 나챗방으로 보낸다.
# stock-plugin 은 이 폴더(프로젝트 범위)에서만 켜져 있으므로 여기서 실행한다.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Set-Location "C:\Users\Woori\Desktop\wori\261026_15_claude"
New-Item -ItemType Directory -Force scheduled\logs | Out-Null
$log = "scheduled\logs\stock-brief-$(Get-Date -Format yyyyMMdd).log"

$prompt = @'
직전 거래일 증시 요약해주세요. (stock-brief 스킬대로)
- https://index.krx.co.kr/contents/IDX/0101/IDX0101.jsp 에서 조회일자를 직전 거래일로 바꿔 조회하고,
  코스피·코스닥 종가와 전일비·등락률을 화면에서 읽어 주세요.
- 첫 줄은 「[증시 요약] YYYY-MM-DD 종가 기준」(직전 거래일 날짜)으로 써 주세요.
- 카카오톡 나챗방으로 한 번 보내고, 연 탭은 모두 닫아 주세요.
'@

"=== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') 시작 ===" | Out-File $log -Append
& claude -p $prompt --chrome `
  --allowedTools "mcp__claude-in-chrome" "mcp__claude_ai_PlayMCP__KakaotalkChat-MemoChat" "Skill" "PowerShell(Get-Date*)" `
  *>> $log
"=== 종료 (exit $LASTEXITCODE) ===" | Out-File $log -Append
