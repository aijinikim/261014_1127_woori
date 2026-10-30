# Stop 훅 진입점: stdin의 훅 JSON을 읽고 팝업(popup.ps1)을 별도 프로세스로 띄운 뒤 바로 종료한다.
$ErrorActionPreference = 'SilentlyContinue'

function ConvertTo-B64([string]$s) {
    if (-not $s) { return '-' }  # 빈 인자는 Start-Process에서 사라지므로 자리표시자 사용
    [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($s))
}

# 답변에서 키워드 추출: 제목(#)·굵은 글씨(**)·인라인 코드(`)를 등장 순서대로, 중복 없이 최대 $max개
function Get-Keywords([string]$text, [int]$max = 4) {
    $text = [regex]::Replace($text, '```[\s\S]*?```', ' ')  # 코드 블록은 제외
    $pattern = '(?m)^#{1,6}\s+(?<k>.+?)\s*$|\*\*(?<k>[^*\r\n]+?)\*\*|`(?<k>[^`\r\n]+?)`'
    $seen = @{}
    $result = @()
    foreach ($m in [regex]::Matches($text, $pattern)) {
        $k = ($m.Groups['k'].Value -replace '[*`]', '').Trim().TrimEnd(':', '.', ',', '：')
        if ($k.Length -lt 2 -or $k.Length -gt 20) { continue }
        if ($seen.ContainsKey($k.ToLower())) { continue }
        $seen[$k.ToLower()] = $true
        $result += $k
        if ($result.Count -ge $max) { break }
    }

    # 키워드가 없으면 첫 문장을 짧게 잘라 사용
    if (-not $result) {
        $plain = $text -replace '[`*#>|\[\]]', ''
        $first = ($plain -split '[.!?。\r\n]' | Where-Object { $_.Trim() } | Select-Object -First 1)
        if ($first) {
            $first = $first.Trim()
            if ($first.Length -gt 20) { $first = $first.Substring(0, 20) + '…' }
            $result = @($first)
        }
    }
    $result
}

try {
    [Console]::InputEncoding = [Text.Encoding]::UTF8
    $raw = [Console]::In.ReadToEnd()

    $data = $null
    if ($raw) { try { $data = $raw | ConvertFrom-Json } catch {} }

    # 프로젝트명: 훅 JSON의 cwd → 없으면 현재 폴더
    $project = ''
    if ($data -and $data.cwd) { $project = Split-Path $data.cwd -Leaf }
    if (-not $project) { $project = Split-Path (Get-Location).Path -Leaf }

    $keywords = @()
    if ($data -and $data.last_assistant_message) { $keywords = @(Get-Keywords $data.last_assistant_message) }

    $popup = Join-Path $PSScriptRoot 'popup.ps1'
    $argList = @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-STA', '-WindowStyle', 'Hidden',
        '-File', "`"$popup`"",
        '-Project', (ConvertTo-B64 $project),
        '-Keywords', (ConvertTo-B64 ($keywords -join "`n"))
    )
    Start-Process -FilePath 'powershell.exe' -ArgumentList $argList -WindowStyle Hidden
} catch {}

exit 0
