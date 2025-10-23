$totalSize = (Get-ChildItem -Path . -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$venvSize = (Get-ChildItem -Path venv -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$srcSize = (Get-ChildItem -Path src -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$dataSize = (Get-ChildItem -Path data -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$assetsSize = (Get-ChildItem -Path assets -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum

Write-Host ""
Write-Host "📊 BOT DISK SPACE USAGE" -ForegroundColor Cyan
Write-Host "=================================================="
Write-Host "Total Size:  $([math]::Round($totalSize / 1MB, 2)) MB" -ForegroundColor Green
Write-Host ""
Write-Host "Breakdown by directory:"
Write-Host "  venv:    $([math]::Round($venvSize / 1MB, 2)) MB" -ForegroundColor Yellow
Write-Host "  src:     $([math]::Round($srcSize / 1MB, 2)) MB"
Write-Host "  data:    $([math]::Round($dataSize / 1MB, 2)) MB"
Write-Host "  assets:  $([math]::Round($assetsSize / 1MB, 2)) MB"
Write-Host "  other:   $([math]::Round(($totalSize - $venvSize - $srcSize - $dataSize - $assetsSize) / 1MB, 2)) MB"
Write-Host "=================================================="

$fileCount = (Get-ChildItem -Path . -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host ""
Write-Host "Total Files: " -NoNewline
Write-Host "$fileCount" -ForegroundColor Cyan
