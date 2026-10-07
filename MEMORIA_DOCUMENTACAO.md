# Documentação Técnica: Leitura de Memória de Processos no Windows

## 1. Permissões Necessárias (Process Access Rights)

### PROCESS_VM_READ
- **Valor**: 0x0010
- **Necessário para**: Ler memória via `ReadProcessMemory()`
- **Nível de Privilégio**: Usuário normal pode ler seu próprio processo; processos de terceiros requerem privilégios administrativos ou debug privileges

### PROCESS_QUERY_INFORMATION
- **Valor**: 0x0400
- **Necessário para**: Obter informações básicas do processo (status, prioridade, etc.)
- **Útil para**: Validar que o processo ainda está ativo antes de tentar ler memória

### ACCESS_DENIED (Error 5)
Motivos comuns:
- Processo pertence a outro usuário
- Processo é do sistema (csrss.exe, svchost.exe)
- Falta de privilégios de administrador
- Proteção DEP/ASLR em processos sensíveis

**Solução**: Executar com privilégios elevados ou requerer SeDebugPrivilege

## 2. APIs Utilizadas

### OpenProcess
```cpp
HANDLE OpenProcess(
  DWORD dwDesiredAccess,  // Permissões desejadas
  BOOL  bInheritHandle,   // Herança de handle
  DWORD dwProcessId       // PID do processo
);
```

**Retorna**: Handle do processo ou NULL em caso de erro
**GetLastError()**: ERROR_INVALID_PARAMETER, ERROR_ACCESS_DENIED, etc.

### ReadProcessMemory
```cpp
BOOL ReadProcessMemory(
  HANDLE  hProcess,           // Handle do processo
  LPCVOID lpBaseAddress,      // Endereço a ler
  LPVOID  lpBuffer,           // Buffer de destino
  SIZE_T  nSize,              // Bytes a ler
  SIZE_T* lpNumberOfBytesRead // (opcional) Bytes realmente lidos
);
```

**Retorna**: TRUE se sucesso, FALSE se erro
**lpNumberOfBytesRead**: Crítico para detectar leituras parciais
**GetLastError()**: 
- ERROR_PARTIAL_COPY: Parte do endereço é válida, parte não
- ERROR_INVALID_PARAMETER: Endereço completamente inválido

### CloseHandle
```cpp
BOOL CloseHandle(HANDLE hObject);
```
**Crítico**: Sempre fechar handles para evitar vazamento de recursos

## 3. Tratamento de Erros

### Erros Comuns e Soluções

| Erro | Código | Causa | Solução |
|------|--------|-------|--------|
| ERROR_INVALID_PARAMETER | 87 | PID inválido ou inexistente | Validar PID com GetProcessList() |
| ERROR_ACCESS_DENIED | 5 | Permissões insuficientes | Executar como administrador |
| ERROR_PARTIAL_COPY | 299 | Endereço parcialmente inválido | Validar endereço ou reduzir bytesToRead |
| ERROR_INVALID_ADDRESS | - | Endereço protegido ou inacessível | Verificar MEMORY_BASIC_INFORMATION |

### Best Practices

1. **Sempre validar entrada**:
   ```cpp
   if (processId == 0 || bytesToRead == 0) return false;
   ```

2. **Verificar handle de retorno**:
   ```cpp
   if (hProcess == nullptr) {
       DWORD err = GetLastError();
       // Tratar erro
   }
   ```

3. **Validar bytes lidos**:
   ```cpp
   SIZE_T bytesRead = 0;
   ReadProcessMemory(..., &bytesRead);
   if (bytesRead < bytesToRead) {
       // Leitura parcial ou falha
   }
   ```

4. **Usar RAII para cleanup**:
   ```cpp
   class ProcessHandle {
       HANDLE h;
   public:
       ~ProcessHandle() { if (h) CloseHandle(h); }
   };
   ```

## 4. Exemplo: Elevação de Privilégios

Para ler processos de terceiros, pode ser necessário habilitar SeDebugPrivilege:

```cpp
BOOL EnableDebugPrivilege()
{
    HANDLE hToken;
    TOKEN_PRIVILEGES priv;
    
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &hToken))
        return FALSE;
    
    if (!LookupPrivilegeValue(nullptr, SE_DEBUG_NAME, &priv.Privileges[0].Luid))
    {
        CloseHandle(hToken);
        return FALSE;
    }
    
    priv.PrivilegeCount = 1;
    priv.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
    
    BOOL success = AdjustTokenPrivileges(hToken, FALSE, &priv, 0, nullptr, nullptr);
    CloseHandle(hToken);
    
    return success;
}
```

Chamada:
```cpp
EnableDebugPrivilege();
HANDLE h = OpenProcess(PROCESS_VM_READ, FALSE, targetPID);
```

## 5. Compilação

### Visual Studio (MSVC)
```bash
cl /std:c++17 ProcessMemoryReader.cpp kernel32.lib advapi32.lib
```

### MinGW (GCC)
```bash
g++ -std=c++17 ProcessMemoryReader.cpp -o ProcessMemoryReader.exe -lkernel32 -ladvapi32
```

### CMake
```cmake
cmake_minimum_required(VERSION 3.10)
project(MemoryScanner)
set(CMAKE_CXX_STANDARD 17)
add_executable(memory_scanner ProcessMemoryScanner.cpp)
target_link_libraries(memory_scanner kernel32 advapi32)
```

## 6. Considerações de Segurança

### Arquitetura x86 vs x64
- **x86 (32-bit)**: Espaço de endereços até 0xFFFFFFFF
- **x64 (64-bit)**: Espaço de endereços até 0xFFFFFFFFFFFFFFFF
- Use `UINT_PTR` para compatibilidade

### ASLR (Address Space Layout Randomization)
- Endereços mudam a cada inicialização
- Solução: Usar offsets relativos a base de módulo
- Obter base com `GetModuleBaseAddress()` ou mapear via `GetModuleHandleEx()`

### DEP (Data Execution Prevention)
- Não afeta leitura, apenas execução
- Sempre respeitar permissões de página

### Memory Protection
```cpp
MEMORY_BASIC_INFORMATION mbi;
VirtualQueryEx(hProcess, lpAddress, &mbi, sizeof(mbi));

// Verificar se é legível
if (mbi.Protect & (PAGE_READONLY | PAGE_READWRITE | PAGE_EXECUTE_READ))
{
    // Legível
}
```

## 7. Testes de Stress (QA Automation)

Para testes de stress em sua própria aplicação:

```cpp
void StressTestMemoryReader(DWORD selfPID)
{
    ProcessMemoryScanner scanner;
    scanner.Open(selfPID);
    
    // Ler um vetor globalmente alocado
    std::vector<unsigned char> buffer;
    
    for (int i = 0; i < 10000; i++)
    {
        if (!scanner.Read(0x400000, buffer, 4096))
        {
            std::cerr << "Falha na iteração " << i << std::endl;
            break;
        }
    }
}
```

## 8. Integração com ONNX Runtime

Para monitorar consumo de memória de modelos ONNX:

```cpp
// Obter alocações internas da session
UINT_PTR sessionMemAddr = /* endereço da OrtSession */;
std::vector<unsigned char> sessionData;
scanner.Read(sessionMemAddr, sessionData, sizeof(OrtSession));

// Validar integridade de estruturas durante inferência
scanner.Read(modelWeightsAddr, weightsBuffer, expectedSize);
```

## Referências
- [Windows API - Process Memory Functions](https://docs.microsoft.com/en-us/windows/win32/memory/process-memory)
- [Windows Internals - Part 1&2](https://docs.microsoft.com/en-us/windows/win32/sysinfo/about-processes-and-threads)
- [PROCESS_INFORMATION Access Rights](https://docs.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights)
