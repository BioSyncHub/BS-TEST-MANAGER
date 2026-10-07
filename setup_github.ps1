#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script para criar repositório GitHub e fazer push automático
    
.DESCRIPTION
    Este script:
    1. Valida Git instalado
    2. Configura Git local
    3. Inicializa repositório
    4. Faz commit de todos os arquivos
    5. Cria repositório no GitHub (via GitHub CLI)
    6. Faz push dos arquivos
    
.NOTES
    Pré-requisitos:
    - Git (https://git-scm.com/download/win)
    - GitHub CLI (https://cli.github.com/)
    - Autenticação GitHub CLI: `gh auth login`
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$Username = "BioSyncHub",
    
    [Parameter(Mandatory=$false)]
    [string]$RepoName = "memory-scanner-tools",
    
    [Parameter(Mandatory=$false)]
    [string]$RepoDescription = "Python e C++ para auditoria de memória de processos Windows",
    
    [Parameter(Mandatory=$false)]
    [string]$ProjectPath = "c:\BS-TEST-MANAGER"
)

Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  GitHub Repository Creator - Memory Scanner   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar pré-requisitos
Write-Host "[1/6] Verificando pré-requisitos..." -ForegroundColor Yellow

# Verificar Git
try {
    $gitVersion = git --version 2>&1
    Write-Host "  ✓ Git encontrado: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Git não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instale Git em: https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}

# Verificar GitHub CLI
try {
    $ghVersion = gh --version 2>&1
    Write-Host "  ✓ GitHub CLI encontrado: $ghVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ GitHub CLI não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instale GitHub CLI em: https://cli.github.com/" -ForegroundColor Red
    Write-Host "Depois autentique com: gh auth login" -ForegroundColor Red
    exit 1
}

# Verificar autenticação GitHub
Write-Host ""
Write-Host "[2/6] Verificando autenticação GitHub..." -ForegroundColor Yellow
try {
    $whoami = gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ! Você precisa fazer login no GitHub" -ForegroundColor Yellow
        Write-Host "    Execute: gh auth login" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
    Write-Host "  ✓ Autenticado no GitHub" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Erro ao verificar autenticação" -ForegroundColor Red
    exit 1
}

# Navegar para diretório do projeto
Write-Host ""
Write-Host "[3/6] Navegando para $ProjectPath..." -ForegroundColor Yellow
if (!(Test-Path $ProjectPath)) {
    Write-Host "  ✗ Diretório não encontrado!" -ForegroundColor Red
    exit 1
}

Set-Location $ProjectPath
Write-Host "  ✓ Diretório configurado" -ForegroundColor Green

# Verificar se já é um repositório Git
if (Test-Path ".git") {
    Write-Host ""
    Write-Host "  ⓘ Repositório Git já existe" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "[3/6] Inicializando Git..." -ForegroundColor Yellow
    git init
    Write-Host "  ✓ Git inicializado" -ForegroundColor Green
}

# Configurar Git (se necessário)
Write-Host ""
Write-Host "[4/6] Configurando Git..." -ForegroundColor Yellow

$gitConfig = git config --local user.email
if (!$gitConfig) {
    Write-Host "  ! Configurando user.name e user.email..." -ForegroundColor Yellow
    git config --local user.name $Username
    git config --local user.email "$($Username)@github.com"
}
Write-Host "  ✓ Git configurado" -ForegroundColor Green

# Adicionar arquivos
Write-Host ""
Write-Host "[5/6] Adicionando arquivos..." -ForegroundColor Yellow
git add .
$fileCounts = (git status --porcelain | Measure-Object).Count
Write-Host "  ✓ $fileCounts arquivos adicionados" -ForegroundColor Green

# Fazer commit
Write-Host ""
Write-Host "  Fazendo commit..." -ForegroundColor Cyan
$commitMessage = "Initial commit: Memory Scanner Tools (Python + C++)"
git commit -m $commitMessage --quiet
Write-Host "  ✓ Commit realizado" -ForegroundColor Green

# Verificar se repositório já existe no GitHub
Write-Host ""
Write-Host "[6/6] Criando repositório no GitHub..." -ForegroundColor Yellow

$repoExists = gh repo view "$Username/$RepoName" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ⓘ Repositório já existe em GitHub" -ForegroundColor Cyan
} else {
    Write-Host "  Criando novo repositório..." -ForegroundColor Cyan
    gh repo create $RepoName --public --description $RepoDescription --source=. --remote=origin --push
    Write-Host "  ✓ Repositório criado" -ForegroundColor Green
}

# Fazer push
Write-Host ""
Write-Host "  Fazendo push para GitHub..." -ForegroundColor Cyan

# Verificar branch padrão
$currentBranch = git rev-parse --abbrev-ref HEAD
git push -u origin $currentBranch
Write-Host "  ✓ Push realizado com sucesso!" -ForegroundColor Green

# Resumo
Write-Host ""
Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║             ✓ CONCLUÍDO COM SUCESSO           ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Seu repositório está disponível em:" -ForegroundColor Cyan
Write-Host "  https://github.com/$Username/$RepoName" -ForegroundColor Yellow
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Cyan
Write-Host "  1. Visite: https://github.com/$Username/$RepoName" -ForegroundColor White
Write-Host "  2. Verifique os arquivos foram para GitHub" -ForegroundColor White
Write-Host "  3. Adicione uma descrição no README.md" -ForegroundColor White
Write-Host "  4. Configure Topics (tags) no GitHub" -ForegroundColor White
Write-Host ""
Write-Host "Para clonar em outro lugar:" -ForegroundColor Cyan
Write-Host "  git clone https://github.com/$Username/$RepoName" -ForegroundColor Yellow
Write-Host ""
