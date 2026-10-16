# Removes the scheduled task and the tlm app. Your config, tokens and post history in
# %APPDATA%\TinyLearnersMedia are kept; delete that folder to remove them too.
Unregister-ScheduledTask -TaskName "TinyLearnersMedia Worker" -Confirm:$false -ErrorAction SilentlyContinue
uv tool uninstall tiny-learners-media
Write-Host "Removed. Also delete the 'tiny-learners-media' entry from"
Write-Host "  $env:APPDATA\Claude\claude_desktop_config.json"
