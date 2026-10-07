# 📤 Guia: Publicar no GitHub

## ⚠️ Pré-requisitos

Você precisa instalar dois programas antes de publicar:

### 1️⃣ Git
**O que é:** Sistema de controle de versão

**Como instalar:**
1. Visite: https://git-scm.com/download/win
2. Clique em "64-bit Git for Windows Setup"
3. Siga o instalador (recomendado: usar padrões)
4. Reinicie o terminal PowerShell

**Verificar instalação:**
```powershell
git --version
# Deve exibir: git version 2.xxx.x
```

### 2️⃣ GitHub CLI
**O que é:** Ferramenta para gerenciar GitHub pelo terminal

**Como instalar:**
1. Visite: https://cli.github.com/
2. Clique em "Download for Windows"
3. Execute o instalador
4. Reinicie o terminal PowerShell

**Verificar instalação:**
```powershell
gh --version
# Deve exibir: gh version x.x.x
```

### 3️⃣ Autenticar no GitHub
**Passo essencial antes de fazer push**

```powershell
gh auth login

# Responda as perguntas:
# ? What account do you want to log into? → GitHub.com
# ? What is your preferred protocol for Git operations? → HTTPS
# ? Authenticate Git with your GitHub credentials? → Yes
# ? How would you like to authenticate GitHub CLI? → Login with a web browser
```

---

## 🚀 Publicar o Projeto

### Método 1: Script Automático (Recomendado)

```powershell
# Abrir PowerShell como Administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Navegar para o projeto
cd c:\BS-TEST-MANAGER

# Executar o script
.\setup_github.ps1
```

**O script fará automaticamente:**
✅ Inicializar Git  
✅ Configurar usuário  
✅ Fazer commit de todos os arquivos  
✅ Criar repositório no GitHub  
✅ Fazer push  

---

### Método 2: Passos Manuais

Se preferir fazer manualmente:

```powershell
# 1. Entrar no diretório
cd c:\BS-TEST-MANAGER

# 2. Inicializar Git
git init

# 3. Configurar usuário (primeira vez)
git config user.name "BioSyncHub"
git config user.email "seu-email@gmail.com"

# 4. Adicionar todos os arquivos
git add .

# 5. Fazer commit
git commit -m "Initial commit: Memory Scanner Tools"

# 6. Criar repositório no GitHub
gh repo create memory-scanner-tools `
  --public `
  --description "Python e C++ para auditoria de memória de processos Windows" `
  --source=. `
  --remote=origin `
  --push

# 7. Verificar
git log
```

---

## ✅ Verificar que Funcionou

### No Terminal:
```powershell
# Ver histórico de commits
git log

# Ver URL remota
git remote -v
```

### No GitHub:
1. Visite: https://github.com/BioSyncHub/memory-scanner-tools
2. Você deve ver todos os arquivos do projeto
3. Verifique:
   - ✅ Arquivos Python
   - ✅ Arquivos C++
   - ✅ Documentação (.md)
   - ✅ CMakeLists.txt
   - ✅ requirements.txt

---

## 📝 Próximos Passos (Opcionais)

### Adicionar Descrição do Repositório
1. Visite: https://github.com/BioSyncHub/memory-scanner-tools/settings
2. Preencha:
   - **Description**: Memory Scanner - Python & C++ Windows internals tools
   - **Homepage URL**: (deixar em branco)

### Adicionar Topics (Tags)
1. Na página principal do repo, clique em ⚙️ Settings
2. Procure por "Topics"
3. Adicione: `python`, `cpp`, `windows`, `memory`, `scanner`, `qa-testing`

### Adicionar Arquivo .gitattributes (Opcional)
```powershell
# Cria arquivo para melhorar compatibilidade Windows
@"
* text=auto
*.py text eol=lf
*.cpp text eol=lf
*.md text eol=lf
*.txt text eol=lf
*.exe binary
*.dll binary
"@ | Out-File .gitattributes -Encoding UTF8

git add .gitattributes
git commit -m "Add .gitattributes for line endings"
git push
```

---

## 🐛 Troubleshooting

### Erro: "git command not found"
→ Git não foi instalado corretamente  
→ Solução: Reinstale Git de https://git-scm.com/download/win

### Erro: "gh command not found"
→ GitHub CLI não foi instalado  
→ Solução: Instale de https://cli.github.com/

### Erro: "fatal: not a git repository"
→ Git não foi inicializado no diretório  
→ Solução: Execute `git init` primeiro

### Erro: "fatal: 'origin' does not appear to be a 'git' repository"
→ Repositório remoto não foi configurado  
→ Solução: Execute `gh repo create memory-scanner-tools --source=. --remote=origin --push`

### Erro: "authentication required"
→ Você não fez login no GitHub  
→ Solução: Execute `gh auth login` primeiro

### Erro: "branch not fully merged"
→ Conflito de branches  
→ Solução: Verifique com `git status` e `git log`

---

## 💡 Dicas

### Ver status dos arquivos
```powershell
git status
```

### Ver o que foi commitado
```powershell
git log --oneline
```

### Desfazer último commit (ainda não foi feito push)
```powershell
git reset HEAD~1
```

### Fazer novo commit com mudanças
```powershell
git add .
git commit -m "Descrição das mudanças"
git push
```

### Clonar o repositório em outro local
```powershell
git clone https://github.com/BioSyncHub/memory-scanner-tools
cd memory-scanner-tools
```

---

## 📚 Recursos

- [Git Documentation](https://git-scm.com/doc)
- [GitHub CLI Manual](https://cli.github.com/manual)
- [GitHub Guides](https://guides.github.com/)
- [Pro Git Book](https://git-scm.com/book/en/v2)

---

## ✨ Estrutura Final no GitHub

Seu repositório terá esta estrutura:

```
memory-scanner-tools/
├── 🐍 Python
│   ├── diagnostic_tool.py
│   ├── memory_scanner_basic.py
│   ├── memory_scanner_advanced.py
│   ├── memory_monitor_realtime.py
│   └── requirements.txt
│
├── 💻 C++
│   ├── ProcessMemoryReader.cpp
│   ├── ProcessMemoryScanner.cpp
│   ├── AdvancedProcessMonitor.cpp
│   └── CMakeLists.txt
│
├── 📖 Documentação
│   ├── README.md
│   ├── PYTHON_QUICKSTART.md
│   ├── PYMEM_DOCUMENTACAO.md
│   ├── MEMORIA_DOCUMENTACAO.md
│   ├── BUILD_INSTRUCTIONS.md
│   ├── COMPARACAO_CPP_PYTHON.md
│   ├── INDEX.md
│   └── GUIA_GITHUB.md (este arquivo)
│
├── 🔧 Configuração
│   ├── .gitignore
│   ├── setup_github.ps1
│   └── .git/
│
└── 📄 Arquivos raiz
    └── git remote -v
```

---

**Depois que fizer push, compartilhe o link:**
```
https://github.com/BioSyncHub/memory-scanner-tools
```

Sucesso! 🎉
