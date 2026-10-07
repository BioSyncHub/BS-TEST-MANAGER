# Instruções de Build - Process Memory Tools

## Pré-requisitos

- **Windows 10/11** (x64 recomendado)
- **Visual Studio 2019+** ou **Visual Studio Build Tools**
- **CMake 3.10+**
- Privilégios de administrador (opcional, para ler processos de terceiros)

## Método 1: CMake + Visual Studio (Recomendado)

### Passo 1: Gerar projeto Visual Studio
```powershell
mkdir build
cd build
cmake .. -G "Visual Studio 17 2022" -A x64
```

**Outras versões de Visual Studio:**
- Visual Studio 2022: `"Visual Studio 17 2022"`
- Visual Studio 2019: `"Visual Studio 16 2019"`
- Visual Studio 2017: `"Visual Studio 15 2017"`

### Passo 2: Compilar
```powershell
# Via CMake
cmake --build . --config Release

# Ou abrir em VS e compilar pela IDE
start ProcessMemoryTools.sln
```

### Passo 3: Executar
```powershell
# Binários gerados em: build/bin/Release/
.\build\bin\Release\ProcessMemoryReader.exe
.\build\bin\Release\ProcessMemoryScanner.exe
.\build\bin\Release\AdvancedProcessMonitor.exe
```

---

## Método 2: MSVC Command Line (vcvarsall.bat)

### Passo 1: Configurar ambiente
```powershell
# Encontrar vcvarsall.bat (Visual Studio Build Tools)
# Exemplo para VS 2022:
& "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64

# Ou para VS 2019:
& "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
```

### Passo 2: Compilar diretamente
```powershell
cd c:\BS-TEST-MANAGER

# Compilar ProcessMemoryReader.cpp
cl /std:c++17 /EHsc /W4 ProcessMemoryReader.cpp /link kernel32.lib advapi32.lib /OUT:ProcessMemoryReader.exe

# Compilar ProcessMemoryScanner.cpp
cl /std:c++17 /EHsc /W4 ProcessMemoryScanner.cpp /link kernel32.lib advapi32.lib /OUT:ProcessMemoryScanner.exe

# Compilar AdvancedProcessMonitor.cpp
cl /std:c++17 /EHsc /W4 AdvancedProcessMonitor.cpp /link kernel32.lib advapi32.lib /OUT:AdvancedProcessMonitor.exe
```

---

## Método 3: MinGW-w64

### Passo 1: Instalar MinGW-w64
Baixar de: https://www.mingw-w64.org/

### Passo 2: Compilar
```bash
cd /c/BS-TEST-MANAGER

g++ -std=c++17 -Wall -O2 ProcessMemoryReader.cpp -o ProcessMemoryReader.exe -lkernel32 -ladvapi32

g++ -std=c++17 -Wall -O2 ProcessMemoryScanner.cpp -o ProcessMemoryScanner.exe -lkernel32 -ladvapi32

g++ -std=c++17 -Wall -O2 AdvancedProcessMonitor.cpp -o AdvancedProcessMonitor.exe -lkernel32 -ladvapi32 -pthread
```

---

## Método 4: Clang-cl (LLVM)

```powershell
# Configurar ambiente MSVC primeiro
& "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64

# Compilar com clang-cl
clang-cl /std:c++17 /EHsc ProcessMemoryReader.cpp /link kernel32.lib advapi32.lib

clang-cl /std:c++17 /EHsc ProcessMemoryScanner.cpp /link kernel32.lib advapi32.lib

clang-cl /std:c++17 /EHsc AdvancedProcessMonitor.cpp /link kernel32.lib advapi32.lib
```

---

## Compilação com Otimizações de Performance

### Release com otimizações
```powershell
cmake --build build --config Release --verbose
```

**Flags MSVC para Release:**
- `/O2` - Otimização máxima para velocidade
- `/Oi` - Intrínsicas habilitadas
- `/Ot` - Favorecer velocidade sobre tamanho
- `/GL` - Whole Program Optimization (LTO)

---

## Troubleshooting

### Erro: "kernel32.lib not found"
**Solução**: Verificar se o Visual Studio Build Tools foi instalado corretamente
```powershell
Get-Command cl
# Deve retornar caminho do compilador
```

### Erro: "Cannot open file cl.exe"
**Solução**: Executar vcvarsall.bat antes de compilar
```powershell
& "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
```

### Erro: "fatal error C1083: Cannot open include file"
**Solução**: Verificar Windows SDK
```powershell
# Instalar Windows SDK via VS Installer
# Ou reinstalar Visual Studio Build Tools com opção "Desktop Development with C++"
```

### Aviso: Conversão de inteiros
Se receber warnings como `C4267` (conversão de size_t para unsigned int):
```cpp
// Adicionar ao início do arquivo:
#pragma warning(disable: 4267 4244)
```

---

## Teste de Compilação Rápida (PowerShell)

```powershell
# Script para compilar todos os arquivos
$files = @(
    "ProcessMemoryReader.cpp",
    "ProcessMemoryScanner.cpp",
    "AdvancedProcessMonitor.cpp"
)

foreach ($file in $files) {
    $output = $file -replace "\.cpp$", ".exe"
    Write-Host "Compilando $file -> $output"
    
    cl /std:c++17 /EHsc /W3 "$file" /link kernel32.lib advapi32.lib /OUT:"$output"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $output compilado com sucesso" -ForegroundColor Green
    } else {
        Write-Host "✗ Erro ao compilar $file" -ForegroundColor Red
    }
}
```

---

## Verificação Pós-Build

### Confirmar que executáveis funcionam
```powershell
# Listar dependências DLL
dumpbin /dependents ProcessMemoryReader.exe

# Esperar: kernel32.dll, advapi32.dll, msvcrt.dll

# Executar (com PID correto como argumento)
# Exemplo: ler memória do próprio explorer.exe
Get-Process explorer | ForEach-Object { Write-Host "explorer.exe PID: $($_.Id)" }
```

---

## Integração com Visual Studio IDE

### Abrir projeto Visual Studio
```powershell
# Após gerar com CMake
start build\ProcessMemoryTools.sln
```

### Debug
- Definir breakpoints nos arquivos `.cpp`
- Usar Debug > Start Debugging (F5)
- Testar com PID do próprio VS ou outro processo

---

## Próximas Etapas

1. **Substituir PIDs** nos exemplos com PIDs reais:
   ```cpp
   DWORD targetPID = /* obter via GetProcessId() ou Windows Task Manager */
   ```

2. **Adicionar tratamento de elevação de privilégios** se necessário:
   - Incluir `EnableDebugPrivilege()` da documentação
   - Executar como administrador

3. **Integrar com seu framework de testes**:
   - Incorporar classes em seu projeto
   - Chamar via C++/CLI ou P/Invoke do C#

---

## Referências
- [MSDN: Compiling with MSVC](https://docs.microsoft.com/en-us/cpp/build/building-on-the-command-line)
- [CMake on Windows](https://cmake.org/cmake/help/latest/manual/cmake-generators.7.html)
- [Windows SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/)
