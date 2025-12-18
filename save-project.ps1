# Только структура папок (как tree)
Get-ChildItem -Recurse | Where-Object { $_.FullName -notmatch 'node_modules|\.git' } | ForEach-Object {
    $depth = ($_.FullName.Split('\').Count - ($PWD.Path.Split('\').Count))
    "  " * $depth + $(if ($_.PSIsContainer) { "[$($_.Name)]" } else { $_.Name })
} | Out-File -FilePath project_structure.txt -Encoding UTF8

# Содержимое только ключевых файлов (Vue.js)
Get-ChildItem -Recurse -File -Include *.vue, *.js, *.json | 
    Where-Object { $_.FullName -notmatch 'node_modules|\.git|dist|build' } |
    ForEach-Object {
        "`n" + "="*50 + "`n"
        "ФАЙЛ: $($_.FullName.Replace("$PWD\", ''))`n"
        "="*50 + "`n"
        Get-Content $_ -ErrorAction SilentlyContinue -Encoding UTF8
    } | Out-File -FilePath project_code.txt -Encoding UTF8

Write-Host "✅ Готово! Структура в project_structure.txt, код в project_code.txt"