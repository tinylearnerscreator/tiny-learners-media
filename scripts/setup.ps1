<#
.SYNOPSIS
  One-shot Windows setup for Tiny Learners Media.

.DESCRIPTION
  1. Installs uv (Python manager) and ffmpeg (via winget) if missing
  2. Installs the `tlm` app (Python is downloaded automatically by uv)
  3. Creates and opens config.toml for your Google / TikTok app credentials
  4. Registers the MCP server in Claude Desktop
  5. Registers a scheduled task that finishes scheduled and interrupted uploads
     every 5 minutes even when Claude is closed

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
  powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 -WithBrowser   # + TikTok Studio fallback
#>
param(
    [switch]$WithBrowser,
    [switch]$NoTask
)
$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot

function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User") + ";" +
                "$env:USERPROFILE\.local\bin"
}

Write-Host "`n== Tiny Learners Media setup ==`n" -ForegroundColor Cyan

# 1. uv ---------------------------------------------------------------------------
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv..."
    powershell -ExecutionPolicy ByPass -NoProfile -Command "irm https://astral.sh/uv/install.ps1 | iex"
    Refresh-Path
}

# 2. ffmpeg -------------------------------------------------------------------------
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "Installing ffmpeg (winget Gyan.FFmpeg)..."
    winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
    Refresh-Path
}
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Warning "ffmpeg is still not on PATH. Close and reopen PowerShell, then re-run this script."
    exit 1
}

# 3. the app ------------------------------------------------------------------------
Write-Host "Installing the tlm app..."
$extra = @()
if ($WithBrowser) { $extra = @("--with", "playwright") }
uv tool install --force --python 3.12 @extra --editable "$Repo"
uv tool update-shell | Out-Null
$BinDir = (uv tool dir --bin).Trim()
$Tlm = Join-Path $BinDir "tlm.exe"
$Tlmw = Join-Path $BinDir "tlmw.exe"
$env:Path = "$BinDir;$env:Path"

# 4. config ---------------------------------------------------------------------------
& $Tlm init
Write-Host "Fill in config.toml (it just opened in Notepad), save it, then press Enter here."
Read-Host | Out-Null

# 5. Claude Desktop ---------------------------------------------------------------
& $Tlm claude-config

# 6. background worker ----------------------------------------------------------
if (-not $NoTask) {
    $name = "TinyLearnersMedia Worker"
    $action = New-ScheduledTaskAction -Execute $Tlmw -Argument "worker"
    $every5 = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
              -RepetitionInterval (New-TimeSpan -Minutes 5)
    $settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable `
                -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
                -ExecutionTimeLimit (New-TimeSpan -Hours 12)
    try {
        $logon = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
        Register-ScheduledTask -TaskName $name -Action $action -Trigger @($every5, $logon) `
            -Settings $settings -Description "Uploads scheduled/interrupted Tiny Learners videos" -Force | Out-Null
    } catch {
        Register-ScheduledTask -TaskName $name -Action $action -Trigger $every5 `
            -Settings $settings -Description "Uploads scheduled/interrupted Tiny Learners videos" -Force | Out-Null
    }
    Write-Host "Scheduled task '$name' registered (runs every 5 minutes)."
}

Write-Host "`nNext steps:" -ForegroundColor Green
Write-Host "  tlm auth google     # sign in to YouTube + Drive (browser opens)"
Write-Host "  tlm auth tiktok     # sign in to TikTok"
Write-Host "  tlm doctor          # check everything"
Write-Host "  Restart Claude Desktop, then ask Claude: 'post G:\My Drive\...\ep12.mp4 to YouTube and TikTok'"
