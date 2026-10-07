#!/usr/bin/env pwsh
# Setup de repositorio Git usando autenticacao do VS Code

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "     Publicar no GitHub - Memory Scanner               " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Locais possiveis do Git
$gitPaths = @(
    "C:\Program Files\Git\bin\git.exe",
    "C:\Program Files (x86)\Git\bin\git.exe",
    "git"
)

$gitExe = $null
foreach ($path in $gitPaths) {
    if (Test-Path $path) {
        $gitExe = $path
        break
    }
}

if (-not $gitExe) {
    Write-Host "[ERRO] Git nao foi encontrado!" -ForegroundColor Red
    Write-Host "Instale Git de: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/3] Configurando Git..." -ForegroundColor Yellow

# Adicionar diretorio como safe
Write-Host "  - Configurando permissoes..." -ForegroundColor Cyan
& $gitExe config --global --add safe.directory "C:\BS-TEST-MANAGER"

# Remover .git se existir
if (Test-Path ".git") {
    Write-Host "  - Limpando repositorio anterior..." -ForegroundColor Cyan
    Remove-Item -Recurse -Force ".git" -ErrorAction SilentlyContinue
}

# Inicializar
Write-Host "  - Inicializando repositorio..." -ForegroundColor Cyan
Set-Location c:\BS-TEST-MANAGER
& $gitExe init

# Configurar usuario
Write-Host "  - Configurando usuario..." -ForegroundColor Cyan
& $gitExe config user.name "BioSyncHub"
& $gitExe config user.email "biosync@github.com"

Write-Host ""
Write-Host "[2/3] Adicionando arquivos..." -ForegroundColor Yellow
& $gitExe add .

Write-Host ""
Write-Host "[3/3] Fazendo commit..." -ForegroundColor Yellow
& $gitExe commit -m "Initial commit: Memory Scanner Tools (Python + C++)"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "           [OK] REPOSITORIO PRONTO                     " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "  1. No VS Code, abra a aba 'Source Control' (Ctrl+Shift+G)" -ForegroundColor White
Write-Host "  2. Clique no botao 'Publish to GitHub'" -ForegroundColor White
Write-Host "  3. Escolha 'Public repository'" -ForegroundColor White
Write-Host "  4. Aguarde a publicacao" -ForegroundColor White
Write-Host ""
Write-Host "Seu repositorio:" -ForegroundColor Cyan
Write-Host "  https://github.com/BioSyncHub/memory-scanner-tools" -ForegroundColor Yellow
Write-Host ""
