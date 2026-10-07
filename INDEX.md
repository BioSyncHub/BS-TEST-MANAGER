# 📁 BS-TEST-MANAGER: Índice Completo de Arquivos

## 🎯 Onde Começar?

### ⭐ **PRIMEIRA VEZ? LEIA ISTO:**
1. [README.md](README.md) - Visão geral e checklist
2. [PYTHON_QUICKSTART.md](PYTHON_QUICKSTART.md) - 5 minutos de Python
3. Execute: `python diagnostic_tool.py` - Menu interativo

---

## 📂 Estrutura Completa

### 🐍 PYTHON (Recomendado para Iniciar)

#### Scripts Prontos para Usar
| Arquivo | Descrição | Dificuldade |
|---------|-----------|------------|
| **diagnostic_tool.py** ⭐ | Menu interativo completo | Iniciante |
| memory_scanner_basic.py | Exemplo básico (conectar + escanear) | Iniciante |
| memory_scanner_advanced.py | Classe wrapper com recursos avançados | Intermediário |
| memory_monitor_realtime.py | Monitoramento contínuo + teste stress | Intermediário |

#### Documentação Python
| Arquivo | Conteúdo |
|---------|---------|
| PYTHON_QUICKSTART.md | Guia de 5 minutos |
| PYMEM_DOCUMENTACAO.md | Referência completa |
| requirements.txt | Dependências (pip install) |

---

### C++ (Para Alta Performance)

#### Código Fonte
| Arquivo | Funcionalidade | Linhas |
|---------|---------------|--------|
| ProcessMemoryReader.cpp | APIs básicas (OpenProcess, ReadProcessMemory) | ~150 |
| ProcessMemoryScanner.cpp | Classe wrapper + pattern scanning | ~400 |
| AdvancedProcessMonitor.cpp | Monitoramento contínuo + estatísticas | ~500 |

#### Build System
| Arquivo | Descrição |
|---------|-----------|
| CMakeLists.txt | Build configuration (Visual Studio/MinGW) |
| BUILD_INSTRUCTIONS.md | Guia completo de compilação |

#### Documentação C++
| Arquivo | Conteúdo |
|---------|---------|
| MEMORIA_DOCUMENTACAO.md | APIs Windows, permissões, erro handling |

---

### 📚 Comparações e Guias

| Arquivo | Propósito |
|---------|----------|
| COMPARACAO_CPP_PYTHON.md | C++ vs Python (lado a lado) |
| README.md | Visão geral do projeto |

---

## 🚀 Guia de Início Rápido

### 1️⃣ Instalação (2 minutos)
```bash
# Abrir PowerShell como Administrador
pip install -r requirements.txt
```

### 2️⃣ Executar (1 minuto)
```bash
python diagnostic_tool.py
```

### 3️⃣ Menu
```
1 - Buscar valor int32        ← Procurar "100"
2 - Buscar valor float        ← Procurar "3.14"
3 - Buscar padrão (hex)       ← Padrão avançado
4 - Ler memória               ← Ver conteúdo
5 - Listar módulos            ← Estrutura do processo
```

---

## 📋 Navegação por Caso de Uso

### 🎮 "Quero escanear um processo agora"
```
👉 Leia: README.md (seção "Início Rápido")
👉 Execute: python diagnostic_tool.py
```

### 🔬 "Quero entender como funciona"
```
👉 Leia: PYTHON_QUICKSTART.md
👉 Veja: memory_scanner_basic.py
👉 Aprenda: PYMEM_DOCUMENTACAO.md
```

### ⚡ "Preciso de máxima performance"
```
👉 Estude: COMPARACAO_CPP_PYTHON.md
👉 Compile: ProcessMemoryReader.cpp
👉 Guia: BUILD_INSTRUCTIONS.md
```

### 🔧 "Quero usar em uma aplicação"
```
👉 Escolha: Python (rápido) ou C++ (rápido)
👉 Integre: memory_scanner_advanced.py (classe)
👉 Teste: memory_monitor_realtime.py
```

### 🐛 "Estou tendo problemas"
```
👉 Leia: README.md (seção "Troubleshooting")
👉 Verifique: PYMEM_DOCUMENTACAO.md (erros)
👉 Compile: BUILD_INSTRUCTIONS.md (C++)
```

---

## 📊 Matriz de Referência Rápida

### Por Linguagem

**PYTHON**
| Necessidade | Arquivo |
|------------|---------|
| Menu interativo | diagnostic_tool.py |
| Escanear valor | memory_scanner_basic.py |
| Padrão scanning | memory_scanner_advanced.py |
| Tempo real | memory_monitor_realtime.py |
| Documentação | PYMEM_DOCUMENTACAO.md |

**C++**
| Necessidade | Arquivo |
|------------|---------|
| Exemplo básico | ProcessMemoryReader.cpp |
| Classe wrapper | ProcessMemoryScanner.cpp |
| Monitoramento | AdvancedProcessMonitor.cpp |
| Compilar | CMakeLists.txt |
| Instruções | BUILD_INSTRUCTIONS.md |

### Por Nível

**INICIANTE**
- diagnostic_tool.py (execute!)
- PYTHON_QUICKSTART.md (leia!)
- README.md (entenda!)

**INTERMEDIÁRIO**
- memory_scanner_advanced.py (estude!)
- PYMEM_DOCUMENTACAO.md (referência)
- ProcessMemoryScanner.cpp (veja código C++)

**AVANÇADO**
- AdvancedProcessMonitor.cpp (threading)
- MEMORIA_DOCUMENTACAO.md (APIs nativas)
- COMPARACAO_CPP_PYTHON.md (otimizações)

---

## 🔑 Funcionalidades por Arquivo

### diagnostic_tool.py
```
✅ Conectar a processo (por nome)
✅ Escanear int32, float
✅ Escanear padrão de bytes com máscara
✅ Ler memória de endereço
✅ Listar módulos do processo
✅ Menu interativo
✅ Tratamento de erros completo
```

### memory_scanner_advanced.py
```
✅ Classe AdvancedMemoryScanner
✅ Suporte a múltiplos tipos (INT32, INT64, FLOAT, DOUBLE)
✅ Pattern scanning com máscara
✅ Snapshots de memória
✅ Comparação entre snapshots
✅ Estatísticas de acessos
```

### memory_monitor_realtime.py
```
✅ Monitoramento contínuo (thread)
✅ Detecção de anomalias
✅ Teste de stress de memória
✅ Medição de throughput
✅ Callbacks para eventos
```

### ProcessMemoryReader.cpp
```
✅ OpenProcess() com permissões corretas
✅ ReadProcessMemory() com verificação
✅ Estrutura MemoryReadResult
✅ Tratamento de erros Windows
✅ Conversão de códigos de erro
```

### ProcessMemoryScanner.cpp
```
✅ Classe ProcessMemoryScanner
✅ Método Read() genérico
✅ ReadValue<T>() com templates
✅ ReadString() para strings
✅ ScanPattern() com máscara
✅ RAII (cleanup automático)
```

### AdvancedProcessMonitor.cpp
```
✅ Monitoramento contínuo
✅ Snapshots com timestamp
✅ Comparação de snapshots
✅ Leitura de múltiplas regiões
✅ Estatísticas de memória
✅ Detecção de mudanças
```

---

## 📖 Leitura Recomendada (por tempo)

### 5 Minutos
- Leia README.md
- Execute diagnostic_tool.py
- Teste uma busca simples

### 30 Minutos
- PYTHON_QUICKSTART.md
- Memory_scanner_basic.py
- PYMEM_DOCUMENTACAO.md (primeiras seções)

### 2 Horas
- PYMEM_DOCUMENTACAO.md (completo)
- Memory_scanner_advanced.py
- COMPARACAO_CPP_PYTHON.md
- Experimente todos os scripts Python

### 1 Dia
- BUILD_INSTRUCTIONS.md
- Compile os projetos C++
- MEMORIA_DOCUMENTACAO.md
- AdvancedProcessMonitor.cpp

---

## 🎓 Mapa de Aprendizado

```
┌─────────────────────────────────────────┐
│  diagnostic_tool.py (experiência)       │ ← COMECE AQUI
└────────────┬────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────┐
│  PYTHON_QUICKSTART.md                   │
│  (entender conceitos básicos)           │
└────────────┬────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────┐
│  memory_scanner_basic.py                │
│  (código Python simples)                │
└────────────┬────────────────────────────┘
             │
             ├─────────────────────────────────┐
             │                                 │
             ↓                                 ↓
┌───────────────────────────┐   ┌──────────────────────┐
│  PYMEM_DOCUMENTACAO.md    │   │ ProcessMemoryReader.│
│  (referência Python)      │   │ cpp (código C++)    │
└───────────────┬───────────┘   └──────────┬──────────┘
                │                         │
                ↓                         ↓
┌───────────────────────────┐   ┌──────────────────────┐
│ memory_scanner_advanced.py│   │ BUILD_INSTRUCTIONS  │
│ (recursos avançados)      │   │ (compilar)          │
└───────────────┬───────────┘   └──────────┬──────────┘
                │                         │
                ↓                         ↓
┌───────────────────────────┐   ┌──────────────────────┐
│ memory_monitor_realtime.py│   │ MEMORIA_DOCUMENTACAO│
│ (tempo real + stress)     │   │ (APIs Windows)      │
└───────────────────────────┘   └──────────────────────┘
```

---

## ✅ Checklist de Instalação

- [ ] Python 3.7+ instalado
- [ ] `pip install -r requirements.txt` executado
- [ ] Executar como Administrador
- [ ] `python diagnostic_tool.py` funciona
- [ ] Consegue conectar a um processo
- [ ] Consegue fazer uma busca simples

---

## 🔗 Ligações Cruzadas

### Se você está lendo...

**diagnostic_tool.py**
→ Próximos: PYTHON_QUICKSTART.md, memory_scanner_basic.py

**memory_scanner_basic.py**
→ Próximos: PYMEM_DOCUMENTACAO.md, memory_scanner_advanced.py

**memory_scanner_advanced.py**
→ Próximos: PYMEM_DOCUMENTACAO.md, memory_monitor_realtime.py

**ProcessMemoryReader.cpp**
→ Próximos: MEMORIA_DOCUMENTACAO.md, ProcessMemoryScanner.cpp

**ProcessMemoryScanner.cpp**
→ Próximos: AdvancedProcessMonitor.cpp, BUILD_INSTRUCTIONS.md

**PYMEM_DOCUMENTACAO.md**
→ Referência cruzada: PYTHON_QUICKSTART.md, todos .py

**MEMORIA_DOCUMENTACAO.md**
→ Referência cruzada: BUILD_INSTRUCTIONS.md, todos .cpp

**COMPARACAO_CPP_PYTHON.md**
→ Decida entre Python e C++ com base em seu caso

---

## 📞 Perguntas Frequentes

### "Por onde começo?"
→ diagnostic_tool.py, depois README.md

### "Quero aprender Python"
→ PYTHON_QUICKSTART.md, memory_scanner_basic.py

### "Preciso de performance máxima"
→ COMPARACAO_CPP_PYTHON.md, ProcessMemoryReader.cpp

### "Como compilo C++?"
→ BUILD_INSTRUCTIONS.md

### "O que significa essa máscara de bytes?"
→ PYMEM_DOCUMENTACAO.md seção "Pattern Scanning"

### "Estou recebendo erro de acesso"
→ README.md "Troubleshooting" e PYMEM_DOCUMENTACAO.md "Erros"

---

## 🎯 Objetivos Alcançáveis

### Semana 1
- [ ] Entender conceitos básicos (memória, endereços, bytes)
- [ ] Executar diagnostic_tool.py com sucesso
- [ ] Fazer varredura manual de um processo

### Semana 2
- [ ] Modificar memory_scanner_basic.py para seu caso
- [ ] Entender pattern scanning com máscara
- [ ] Ler memory_scanner_advanced.py e entender classes

### Semana 3
- [ ] Compilar código C++ com sucesso
- [ ] Comparar performance Python vs C++
- [ ] Implementar sua própria ferramenta baseada nos exemplos

### Mês 1
- [ ] Integrar em seu fluxo de QA Automation
- [ ] Otimizar para seu caso específico
- [ ] Dominar a stack Python + C++

---

## 📄 Arquivo de Índice

Este arquivo: `INDEX.md` (você está aqui!)
- Navegação principal
- Mapa de aprendizado
- Referência cruzada

---

**Última atualização:** Outubro 2026  
**Total de arquivos:** 16  
**Total de linhas de código:** ~2000+  
**Tempo para dominar:** 1-4 semanas (dependendo da experiência)

---

**Comece agora:** `python diagnostic_tool.py` 🚀
