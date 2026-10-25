# Script sementara: commit + push project pomodoro_tui ke GitHub, lalu uji install dari GitHub.
$ErrorActionPreference = 'Continue'
$repo = 'D:\01_Uromastyx_VScode\01_Belajar_python'
$proj = 'D:\01_Uromastyx_VScode\01_Belajar_python\03_Mini_Projects\pomodoro_tui'
Set-Location $repo

Write-Host '===== 0. Hapus artefak sementara ====='
$junk = Join-Path $repo '03_Mini_Projects\.dsh-acl-recovery'
if (Test-Path $junk) { Remove-Item $junk -Recurse -Force -ErrorAction SilentlyContinue }
Write-Host "junk tersisa: $(Test-Path $junk)"

Write-Host '===== 1. Status & fetch ====='
git status --short
$env:GIT_TERMINAL_PROMPT = '0'
git fetch origin main 2>&1
Write-Host "FETCH_EXIT=$LASTEXITCODE"
git log --oneline -1 origin/main

Write-Host '===== 2. Stage folder project ====='
git add -- '03_Mini_Projects/pomodoro_tui'
Write-Host "ADD_EXIT=$LASTEXITCODE"
$staged = git diff --cached --name-status -- '03_Mini_Projects/pomodoro_tui'
Write-Host "file staged: $(($staged | Measure-Object -Line).Lines)"
$staged | Select-Object -First 5

Write-Host '===== 3. Commit HANYA folder project ====='
git -c user.name='kuru' -c user.email='sankarulepus@gmail.com' commit -m 'feat(pomodoro_tui): FOKUS - pomodoro TUI, install gampang + jalan satu baris' -- '03_Mini_Projects/pomodoro_tui' 2>&1
$commitExit = $LASTEXITCODE
Write-Host "COMMIT_EXIT=$commitExit"

Write-Host '===== 4. Push ke GitHub ====='
$pushOk = $false
if ($commitExit -eq 0) {
    git push origin main 2>&1
    if ($LASTEXITCODE -eq 0) { $pushOk = $true }
}
Write-Host "PUSH_OK=$pushOk"
git status -sb
git log --oneline -3

Write-Host '===== 5. Uji install dari GitHub di venv sementara ====='
if ($pushOk) {
    Set-Location $proj
    $globalPython = 'C:\Users\a7916\AppData\Local\Programs\Python\Python313\python.exe'
    Remove-Item '.venv-gh-test' -Recurse -Force -ErrorAction SilentlyContinue
    & $globalPython -m venv '.venv-gh-test'
    $gpy = (Resolve-Path '.venv-gh-test\Scripts\python.exe').Path
    $env:PIP_NO_CACHE_DIR = '1'
    Remove-Item 'gh-out.log', 'gh-err.log' -Force -ErrorAction SilentlyContinue
    & $gpy -m pip install --quiet 'git+https://github.com/ujangboy/belajar-python.git#subdirectory=03_Mini_Projects/pomodoro_tui' 2>&1 | Select-Object -Last 3
    Write-Host "GH_PIP_EXIT=$LASTEXITCODE"
    $cmdExe = Join-Path (Split-Path $gpy) 'pomodoro.exe'
    Write-Host "POMODORO_EXE=$(Test-Path $cmdExe)"
    if (Test-Path $cmdExe) {
        $p = Start-Process -FilePath $cmdExe -WorkingDirectory $proj -PassThru -NoNewWindow -RedirectStandardOutput 'gh-out.log' -RedirectStandardError 'gh-err.log'
        Start-Sleep -Seconds 10
        $p.Refresh()
        Write-Host "GH_APP_ALIVE=$(-not $p.HasExited)"
        if (-not $p.HasExited) { cmd /c "taskkill /PID $($p.Id) /T /F" 2>$null | Out-Null }
        Get-Content 'gh-err.log' -Tail 5 -ErrorAction SilentlyContinue
    }
    Remove-Item 'gh-out.log', 'gh-err.log' -Force -ErrorAction SilentlyContinue
    Remove-Item '.venv-gh-test' -Recurse -Force -ErrorAction SilentlyContinue
    if (Test-Path '.venv-gh-test') { cmd /c 'rmdir /s /q ".venv-gh-test"' 2>$null }
    Write-Host "GH_CLEANUP_OK=$(-not (Test-Path '.venv-gh-test'))"
    Set-Location $repo
} else {
    Write-Host 'push gagal -> uji install dari GitHub dilewati'
}

Write-Host '===== RINGKASAN ====='
Write-Host "COMMIT_EXIT=$commitExit PUSH_OK=$pushOk"
Write-Host "STATUS_AKHIR:"
git status -sb
Write-Host "HEAD:"
git log --oneline -2
