# 화면 가운데에 "Claude 답변 완료" 팝업을 띄운다. 5초 후 자동으로 닫히고, 클릭·확인·Esc로 즉시 닫힌다.
param(
    [string]$Project  = '-',
    [string]$Keywords = '-'
)

Add-Type -AssemblyName System.Windows.Forms, System.Drawing, PresentationCore
[System.Windows.Forms.Application]::EnableVisualStyles()

function ConvertFrom-B64([string]$s) {
    if (-not $s -or $s -eq '-') { return '' }
    try { [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($s)) } catch { '' }
}

# 둥근 사각형 경로 (r = 모서리 반지름)
function New-RoundedPath([float]$x, [float]$y, [float]$w, [float]$h, [float]$r) {
    $d = $r * 2
    $p = New-Object Drawing.Drawing2D.GraphicsPath
    $p.AddArc($x, $y, $d, $d, 180, 90)
    $p.AddArc($x + $w - $d, $y, $d, $d, 270, 90)
    $p.AddArc($x + $w - $d, $y + $h - $d, $d, $d, 0, 90)
    $p.AddArc($x, $y + $h - $d, $d, $d, 90, 90)
    $p.CloseFigure()
    $p
}

$projectName = ConvertFrom-B64 $Project
$keywordList = @((ConvertFrom-B64 $Keywords) -split "`n" | Where-Object { $_ })
$seconds     = 5
$radius      = 15
$soundFile   = Join-Path $PSScriptRoot 'sounds\ding.mp3'  # 효과음 (mp3·wav 모두 가능)

# 색상·폰트
$bg        = [Drawing.Color]::FromArgb(32, 33, 40)
$accent    = [Drawing.Color]::FromArgb(217, 119, 87)
$green     = [Drawing.Color]::FromArgb(74, 222, 128)
$fg        = [Drawing.Color]::FromArgb(240, 240, 245)
$muted     = [Drawing.Color]::FromArgb(160, 163, 175)
$dim       = [Drawing.Color]::FromArgb(115, 118, 130)
$boxFill   = [Drawing.Color]::FromArgb(43, 44, 53)
$boxLine   = [Drawing.Color]::FromArgb(62, 64, 76)
$chipFill  = [Drawing.Color]::FromArgb(64, 217, 119, 87)
$chipText  = [Drawing.Color]::FromArgb(247, 196, 176)
$fontKr    = 'Malgun Gothic'
$chipFont  = New-Object Drawing.Font($fontKr, 9)
$boxTitleFont = New-Object Drawing.Font($fontKr, 8)

# 키워드 박스 레이아웃 계산 (칩을 한 줄씩 채우고 넘치면 다음 줄로)
$width  = 400
$boxX   = 24; $boxY = 94; $boxW = $width - 48
$pad    = 12; $chipH = 24; $chipGap = 6; $boxTitleH = 22
$chips  = @()
$boxH   = 0
if ($keywordList) {
    $cx = $boxX + $pad; $cy = $boxY + $pad + $boxTitleH
    $flags = [Windows.Forms.TextFormatFlags]::NoPadding
    foreach ($k in $keywordList) {
        $tw = [Windows.Forms.TextRenderer]::MeasureText($k, $chipFont, [Drawing.Size]::Empty, $flags).Width
        $cw = [Math]::Min($tw + 20, $boxW - $pad * 2)
        if ($cx + $cw -gt $boxX + $boxW - $pad -and $cx -gt $boxX + $pad) {
            $cx = $boxX + $pad; $cy += $chipH + $chipGap
        }
        $chips += [pscustomobject]@{ Text = $k; Rect = New-Object Drawing.Rectangle($cx, $cy, $cw, $chipH) }
        $cx += $cw + $chipGap
    }
    $boxH = ($cy + $chipH + $pad) - $boxY
}
$height = if ($boxH) { $boxY + $boxH + 66 } else { 160 }

$form = New-Object Windows.Forms.Form
$form.FormBorderStyle = 'None'
$form.StartPosition   = 'Manual'
$form.TopMost         = $true
$form.ShowInTaskbar   = $false
$form.KeyPreview      = $true
$form.ClientSize      = New-Object Drawing.Size($width, $height)
$form.BackColor       = $bg
$form.Text            = 'Claude 답변 완료'
$form.Region          = New-Object Drawing.Region (New-RoundedPath 0 0 $width $height $radius)

# 가장 오른쪽 모니터의 작업 영역 가운데에 배치 (모니터가 하나면 그 화면 가운데)
$work = ([Windows.Forms.Screen]::AllScreens | Sort-Object { $_.Bounds.X } | Select-Object -Last 1).WorkingArea
$form.Location = New-Object Drawing.Point(
    [int]($work.X + ($work.Width - $width) / 2),
    [int]($work.Y + ($work.Height - $height) / 2))

# 둥근 테두리 + 키워드 박스
$form.Add_Paint({
    param($s, $e)
    $g = $e.Graphics
    $g.SmoothingMode = [Drawing.Drawing2D.SmoothingMode]::AntiAlias

    $pen = New-Object Drawing.Pen($accent, 2)
    $g.DrawPath($pen, (New-RoundedPath 1 1 ($s.ClientSize.Width - 2) ($s.ClientSize.Height - 2) ($radius - 1)))
    $pen.Dispose()

    if ($chips) {
        $boxPath = New-RoundedPath $boxX $boxY $boxW $boxH 10
        $brush = New-Object Drawing.SolidBrush($boxFill); $g.FillPath($brush, $boxPath); $brush.Dispose()
        $pen = New-Object Drawing.Pen($boxLine, 1); $g.DrawPath($pen, $boxPath); $pen.Dispose()

        $titleRect = New-Object Drawing.Rectangle(($boxX + $pad), ($boxY + $pad - 2), ($boxW - $pad * 2), $boxTitleH)
        [Windows.Forms.TextRenderer]::DrawText($g, '핵심 키워드', $boxTitleFont, $titleRect, $dim, $boxFill,
            [Windows.Forms.TextFormatFlags]::Left -bor [Windows.Forms.TextFormatFlags]::Top -bor [Windows.Forms.TextFormatFlags]::NoPadding)

        $brush = New-Object Drawing.SolidBrush($chipFill)
        foreach ($c in $chips) {
            $r = $c.Rect
            $g.FillPath($brush, (New-RoundedPath $r.X $r.Y $r.Width $r.Height 12))
            [Windows.Forms.TextRenderer]::DrawText($g, $c.Text, $chipFont, $r, $chipText,
                [Windows.Forms.TextFormatFlags]::HorizontalCenter -bor [Windows.Forms.TextFormatFlags]::VerticalCenter -bor
                [Windows.Forms.TextFormatFlags]::NoPadding -bor [Windows.Forms.TextFormatFlags]::EndEllipsis)
        }
        $brush.Dispose()
    }
})

function New-Label($text, $x, $y, $w, $h, $font, $color, $align = 'TopLeft') {
    $l = New-Object Windows.Forms.Label
    $l.Text      = $text
    $l.Location  = New-Object Drawing.Point($x, $y)
    $l.Size      = New-Object Drawing.Size($w, $h)
    $l.Font      = $font
    $l.ForeColor = $color
    $l.BackColor = [Drawing.Color]::Transparent
    $l.TextAlign = $align
    $form.Controls.Add($l)
    $l
}

New-Label ([string][char]0x2714) 22 18 34 34 (New-Object Drawing.Font('Segoe UI Symbol', 18, [Drawing.FontStyle]::Bold)) $green | Out-Null
New-Label 'Claude 답변 완료' 58 22 320 30 (New-Object Drawing.Font($fontKr, 14, [Drawing.FontStyle]::Bold)) $fg | Out-Null
New-Label "프로젝트: $projectName" 26 64 250 22 (New-Object Drawing.Font($fontKr, 10)) $muted | Out-Null
New-Label (Get-Date -Format 'HH:mm:ss') ($width - 126) 64 100 22 (New-Object Drawing.Font($fontKr, 9)) $dim 'TopRight' | Out-Null

$countdown = New-Label "${seconds}초 후 자동으로 닫힘" 26 ($height - 42) 240 20 (New-Object Drawing.Font($fontKr, 9)) $dim

$ok = New-Object Windows.Forms.Button
$ok.Text      = '확인'
$ok.Location  = New-Object Drawing.Point(($width - 112), ($height - 50))
$ok.Size      = New-Object Drawing.Size(88, 32)
$ok.Font      = New-Object Drawing.Font($fontKr, 10, [Drawing.FontStyle]::Bold)
$ok.FlatStyle = 'Flat'
$ok.FlatAppearance.BorderSize = 0
$ok.BackColor = $accent
$ok.ForeColor = [Drawing.Color]::White
$ok.Cursor    = [Windows.Forms.Cursors]::Hand
$ok.Region    = New-Object Drawing.Region (New-RoundedPath 0 0 88 32 8)
$ok.Add_Click({ $form.Close() })
$form.Controls.Add($ok)
$form.AcceptButton = $ok

# 폼·라벨 어디를 클릭해도 닫힘, Esc로도 닫힘
$form.Add_Click({ $form.Close() })
foreach ($c in $form.Controls) { if ($c -is [Windows.Forms.Label]) { $c.Add_Click({ $form.Close() }) } }
$form.Add_KeyDown({ param($s, $e) if ($e.KeyCode -eq 'Escape') { $form.Close() } })

# 카운트다운
$timer = New-Object Windows.Forms.Timer
$timer.Interval = 1000
$timer.Add_Tick({
    $script:seconds--
    if ($script:seconds -le 0) { $timer.Stop(); $form.Close() }
    else { $countdown.Text = "$($script:seconds)초 후 자동으로 닫힘" }
})

# 숨김 프로세스로 실행되면 첫 ShowWindow가 숨김 설정을 물려받으므로, 한 번 숨겼다가 다시 표시한다
$form.Add_Shown({
    $form.Hide(); $form.Show(); $form.Activate(); $timer.Start()

    # 효과음 재생 (비동기, mp3 지원) — 파일이 없거나 재생에 실패하면 시스템 기본 알림음
    try {
        if (-not (Test-Path $soundFile)) { throw 'no sound file' }
        $script:player = New-Object System.Windows.Media.MediaPlayer
        $script:player.Open([Uri]$soundFile)
        $script:player.Play()
        $script:soundClock = [Diagnostics.Stopwatch]::StartNew()
    } catch { [System.Media.SystemSounds]::Asterisk.Play() }
})
[System.Windows.Forms.Application]::Run($form)

# 팝업을 바로 닫아도 효과음이 끊기지 않도록 재생이 끝날 때까지 대기 (최대 5초)
if ($script:player -and $script:soundClock) {
    $length = if ($script:player.NaturalDuration.HasTimeSpan) { $script:player.NaturalDuration.TimeSpan.TotalMilliseconds } else { 3000 }
    $remain = [Math]::Min($length, 5000) - $script:soundClock.ElapsedMilliseconds
    if ($remain -gt 0) { Start-Sleep -Milliseconds ([int]$remain) }
    $script:player.Close()
}
$timer.Dispose()
$form.Dispose()
