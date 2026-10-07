@echo off
REM Script simples para publicar no GitHub
REM Usa autenticacao do VS Code

setlocal enabledelayedexpansion

echo ========================================================
echo     Publicar no GitHub - Memory Scanner                
echo ========================================================
echo.

REM Verificar se git existe
where git >nul 2>nul
if errorlevel 1 (
    echo [ERRO] Git nao esta instalado
    echo Instale Git de: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/3] Inicializando repositorio Git...
git init
git config user.name "BioSyncHub"
git config user.email "biosync@github.com"

echo [2/3] Adicionando arquivos...
git add .

echo [3/3] Fazendo commit...
git commit -m "Initial commit: Memory Scanner Tools (Python + C++)"

echo.
echo ========================================================
echo [OK] Repositorio local pronto
echo ========================================================
echo.
echo Proximos passos:
echo 1. Abra VS Code
echo 2. Clique na aba "Source Control" (Ctrl+Shift+G)
echo 3. Clique em "Publish to GitHub"
echo 4. Escolha "Public repository"
echo 5. Aguarde a publicacao
echo.
echo Depois visite: https://github.com/BioSyncHub/memory-scanner-tools
echo.
pause
