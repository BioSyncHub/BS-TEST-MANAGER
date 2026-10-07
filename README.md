# BS-TEST-MANAGER: Ferramentas de Diagnóstico e Auditoria de Memória

**Versão**: 1.0  
**Plataforma**: Windows 10/11 (32/64 bits)  
**Linguagens**: C++ e Python  
**Objetivo**: Ferramentas de diagnóstico, testes de stress e auditoria de segurança

---

## 📋 Conteúdo

### C++ (APIs Nativas)
- **ProcessMemoryReader.cpp** - Exemplo básico com OpenProcess/ReadProcessMemory
- **ProcessMemoryScanner.cpp** - Classe wrapper com pattern scanning
- **AdvancedProcessMonitor.cpp** - Monitoramento contínuo com comparação de snapshots
- **CMakeLists.txt** - Build system (Visual Studio/CMake)
- **BUILD_INSTRUCTIONS.md** - Guia de compilação completo

### Python (Pymem)
- **memory_scanner_basic.py** - Script básico: conectar e escanear valores
- **memory_scanner_advanced.py** - Classe AdvancedMemoryScanner com recursos avançados
- **memory_monitor_realtime.py** - Monitoramento em tempo real com detecção de anomalias
- **diagnostic_tool.py** - **Interface interativa pronta para usar** 👈
- **requirements.txt** - Dependências Python
- **PYMEM_DOCUMENTACAO.md** - Documentação completa sobre pymem
- **PYTHON_QUICKSTART.md** - Guia rápido de início

### Documentação
- **MEMORIA_DOCUMENTACAO.md** - APIs Windows, permissões, tratamento de erros
- **README.md** - Este arquivo

---

## 🚀 Início Rápido (Python)

### 1. Instalação
```bash
# Abrir PowerShell como Administrador
pip install -r requirements.txt
```

### 2. Usar a ferramenta interativa
```bash
python diagnostic_tool.py
```

Escolha no menu:
- Buscar valor int32
- Buscar valor float
- Buscar padrão de bytes
- Ler memória de um endereço
- Listar módulos do processo

### 3. Exemplos de Uso

**Buscar valor 100 no notepad:**
```bash
python diagnostic_tool.py
> Nome do processo: notepad.exe
> Opção 1: Buscar valor int32
> Valor a buscar: 100
```

**Buscar padrão no explorer:**
```bash
python diagnostic_tool.py
> Nome do processo: explorer.exe
> Opção 3: Buscar padrão de bytes (hex)
> Padrão: 55 8B EC
> Máscara: xxx
```

---

## 🛠️ Scripts Python

### diagnostic_tool.py (Menu Interativo)
Menu amigável com 5 opções. **Ideal para uso rápido**.
```bash
python diagnostic_tool.py
```

### memory_scanner_basic.py
Exemplo básico - conecta e escaneia um valor específico.
```bash
python memory_scanner_basic.py
```

### memory_scanner_advanced.py
Classe wrapper com templates, pattern scanning e snapshots.
```bash
python memory_scanner_advanced.py
```

### memory_monitor_realtime.py
Monitoramento contínuo com teste de stress.
```bash
python memory_monitor_realtime.py
```

---

## 🔨 Compilação C++

### Método 1: CMake (Recomendado)
```powershell
mkdir build
cd build
cmake .. -G "Visual Studio 17 2022" -A x64
cmake --build . --config Release

# Executáveis em: build\bin\Release\
.\ProcessMemoryReader.exe
```

### Método 2: MSVC direto
```powershell
# Abrir Developer Command Prompt para Visual Studio

cl /std:c++17 /EHsc ProcessMemoryReader.cpp /link kernel32.lib advapi32.lib
```

### Método 3: MinGW
```bash
g++ -std:c++17 -Wall -O2 ProcessMemoryReader.cpp -o ProcessMemoryReader.exe -lkernel32 -ladvapi32
```

---

## 📚 Documentação

### Para Python
- **PYTHON_QUICKSTART.md** - Guia rápido (5 minutos)
- **PYMEM_DOCUMENTACAO.md** - Referência completa (estruturas, tipos, erros)

### Para C++
- **BUILD_INSTRUCTIONS.md** - Como compilar (detalhado)
- **MEMORIA_DOCUMENTACAO.md** - APIs Windows, permissões, segurança

---

## ✨ Características

### Python (Pymem)
✅ Conectar a processos pelo nome ou PID  
✅ Escanear valores int32, int64, float, double  
✅ Pattern scanning com máscara (x=comparar, ?=ignorar)  
✅ Leitura/escrita de memória  
✅ Snapshots e comparação de mudanças  
✅ Monitoramento em tempo real com threading  
✅ Teste de stress e estatísticas  

### C++
✅ APIs nativas Windows (OpenProcess, ReadProcessMemory)  
✅ Tratamento robusto de erros  
✅ Classe wrapper com RAII  
✅ Pattern scanning eficiente  
✅ Suporte x86/x64  
✅ Integração com ONNX Runtime  
✅ Compilação com CMake/Visual Studio

---

## ⚠️ Requisitos

### Python
- Python 3.7+
- Privilégios de administrador (para ler terceiros)
- Windows 10/11

### C++
- Visual Studio 2019+ ou MinGW
- CMake 3.10+
- Windows SDK
- Privilégios de administrador (opcional)

---

## 📝 Exemplos

### Python: Encontrar valor e ler memória
```python
from diagnostic_tool import DiagnosticTool

tool = DiagnosticTool("notepad.exe")
addresses = tool.find_value_int32(100)

if addresses:
    tool.read_memory(addresses[0], size=64)

tool.close()
```

### C++: Escanear padrão
```cpp
ProcessMemoryScanner scanner;
scanner.Open(targetPID);

std::vector<unsigned char> pattern = {0x55, 0x8B, 0xEC};
UINT_PTR found = scanner.ScanPattern(pattern, "xxx", 0x400000, 0x500000);

std::cout << "Padrão encontrado em: 0x" << std::hex << found << std::endl;
```

---

## 🔐 Segurança

### ✅ Boas Práticas
- Sempre verificar se conectou ao processo antes de ler
- Usar try/except para tratamento de erros
- Executar como administrador quando necessário
- Respeitar permissões de página de memória
- Fechar handles/conexões explicitamente

### ⚠️ Limitações
- Não pode ler memória protegida (PAGE_NOACCESS)
- ASLR randomiza endereços entre execuções
- Alguns processos têm proteção anti-cheat
- Requer privilégios de administrador para terceiros

---

## 📊 Casos de Uso

### ✅ Usos Válidos
- Ferramentas de acessibilidade
- QA Automation e testes de stress
- Debugging e diagnóstico próprio
- Auditoria de segurança em software próprio
- Análise de performance de modelos IA (ONNX)

### ❌ Usos Não Permitidos
- Reverse engineering de software protegido
- Contorno de proteções anti-cheat
- Modificação não autorizada
- Extração de dados sensíveis

---

## 🐛 Troubleshooting

### "Processo não encontrado"
```
Solução: Verificar nome exato em Gerenciador de Tarefas
Cuidado: case-sensitive em alguns contextos
```

### "Acesso negado"
```
Solução: Executar como administrador
Windows 10/11 requer elevação para processos de terceiros
```

### "pymem não importa"
```bash
pip install --upgrade pymem
pip install pymem==1.14.0
```

### "Falha ao compilar C++"
```
Verificar:
1. Visual Studio Build Tools instalado
2. Windows SDK disponível
3. vcvarsall.bat configurado
```

---

## 📖 Estrutura de Projeto

```
BS-TEST-MANAGER/
├── C++ (Nativo)
│   ├── ProcessMemoryReader.cpp        # Básico
│   ├── ProcessMemoryScanner.cpp       # Wrapper
│   ├── AdvancedProcessMonitor.cpp     # Avançado
│   ├── CMakeLists.txt                 # Build system
│   └── BUILD_INSTRUCTIONS.md          # Como compilar
│
├── Python (Pymem)
│   ├── diagnostic_tool.py             # 👈 Use isto!
│   ├── memory_scanner_basic.py        # Básico
│   ├── memory_scanner_advanced.py     # Avançado
│   ├── memory_monitor_realtime.py     # Tempo real
│   ├── requirements.txt               # Dependências
│   ├── PYMEM_DOCUMENTACAO.md          # Referência
│   └── PYTHON_QUICKSTART.md           # Guia rápido
│
├── Documentação
│   ├── MEMORIA_DOCUMENTACAO.md        # APIs C++
│   └── README.md                      # Este arquivo
```

---

## 🎯 Próximos Passos

1. **Experimente Python primeiro**: Execute `diagnostic_tool.py`
2. **Leia a documentação**: `PYMEM_DOCUMENTACAO.md`
3. **Adapte os scripts** para seu processo específico
4. **Combine com C++** para máxima performance (se necessário)
5. **Integre em seus testes** de QA ou ferramentas

---

## 📞 Suporte Técnico

### Referências
- [Pymem GitHub](https://github.com/srounet/Pymem)
- [Windows API Docs](https://docs.microsoft.com/en-us/windows/win32/)
- [Python struct module](https://docs.python.org/3/library/struct.html)

### Arquivos de Ajuda
- **PYTHON_QUICKSTART.md** - Primeiros passos (5 min)
- **PYMEM_DOCUMENTACAO.md** - Referência completa
- **MEMORIA_DOCUMENTACAO.md** - APIs Windows
- **BUILD_INSTRUCTIONS.md** - Compilação C++

---

## ✅ Checklist de Início

- [ ] Python 3.7+ instalado
- [ ] `pip install -r requirements.txt`
- [ ] Executar como Administrador
- [ ] Testar: `python diagnostic_tool.py`
- [ ] Ler: `PYTHON_QUICKSTART.md`
- [ ] Adaptar para seu processo
- [ ] Integrar em seus testes

---

## 📄 Licença

Estas ferramentas são fornecidas para uso em:
- Ferramentas de acessibilidade
- QA Automation e testes
- Diagnóstico e auditoria própria

Use responsavelmente e respeite a segurança.

---

**Última atualização**: Outubro 2026  
**Versão Python**: 3.7+  
**Versão C++**: C++17  
**Plataforma**: Windows 10/11
