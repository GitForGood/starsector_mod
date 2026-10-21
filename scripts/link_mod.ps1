# Link Mod to Starsector Mods Folder
# Creates a directory junction so edits in this repo are instantly live in-game without copying.

param (
    [string]$StarsectorDir = "C:\Program Files (x86)\Fractal Softworks\Starsector",
    [switch]$Unlink = $false
)

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ModId = "Carcinus Shipyards"
$ModsDir = Join-Path $StarsectorDir "mods"
$TargetDir = Join-Path $ModsDir $ModId

if (-not (Test-Path $ModsDir)) {
    Write-Error "Starsector mods directory not found at '$ModsDir'. Please pass -StarsectorDir <path>"
    exit 1
}

if ($Unlink) {
    if (Test-Path $TargetDir) {
        cmd /c rmdir "$TargetDir"
        Write-Host "Unlinked: Removed junction at '$TargetDir'" -ForegroundColor Yellow
    } else {
        Write-Host "No junction found at '$TargetDir'" -ForegroundColor Gray
    }
    exit 0
}

if (Test-Path $TargetDir) {
    Write-Host "Junction already exists at: $TargetDir" -ForegroundColor Green
} else {
    New-Item -ItemType Junction -Path $TargetDir -Target $RepoRoot | Out-Null
    Write-Host "Created Junction: '$TargetDir' -> '$RepoRoot'" -ForegroundColor Green
}

Write-Host "`nMod is linked! To playtest in Starsector:" -ForegroundColor Cyan
Write-Host " 1. Start Starsector launcher and ensure 'Carcinus Shipyards' is checked in the Mods list."
Write-Host " 2. In combat or campaign (with Console Commands), press Ctrl+Backspace and run:"
Write-Host "    addship carcinus_Assault"
Write-Host "    or"
Write-Host "    addship carcinus_Strike`n"
