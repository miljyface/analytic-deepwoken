$totalSize = (Get-ChildItem -Path . -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$venvSize = (Get-ChildItem -Path venv -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$srcSize = (Get-ChildItem -Path src -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$dataSize = (Get-ChildItem -Path data -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum

Write-Host "BOT DISK SPACE USAGE"
Write-Host "Total Size: " $([math]::Round($totalSize / 1MB, 2)) "MB"
Write-Host "venv: " $([math]::Round($venvSize / 1MB, 2)) "MB"
Write-Host "src: " $([math]::Round($srcSize / 1MB, 2)) "MB"
Write-Host "data: " $([math]::Round($dataSize / 1MB, 2)) "MB"
