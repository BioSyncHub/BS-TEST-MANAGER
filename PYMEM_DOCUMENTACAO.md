# Documentação: Leitura de Memória com Pymem em Python

## 1. O que é Pymem?

**Pymem** é uma biblioteca Python que fornece acesso direto à memória de processos Windows, permitindo:
- Conectar a processos pelo nome ou PID
- Ler/escrever dados em endereços de memória
- Escanear padrões de bytes
- Acessar módulos e seções de código

## 2. Instalação

### Pré-requisitos
- Python 3.7+
- Windows 10/11
- Privilégios de administrador (para processos de terceiros)

### Instalação via pip
```bash
pip install pymem
```

### Instalação de todas as dependências
```bash
cd c:\BS-TEST-MANAGER
pip install -r requirements.txt
```

## 3. Conceitos Fundamentais

### Conexão a um Processo
```python
import pymem

# Conectar pelo nome do executável
pm = pymem.Pymem("explorer.exe")

# Conectar pelo PID
pm = pymem.Pymem(process_id=1234)

# Fechar conexão
pm.close()
```

### Leitura de Memória

#### Ler bytes brutos
```python
# Ler 4 bytes a partir do endereço 0x400000
data = pm.read_bytes(0x400000, 4)
# Retorna: b'\x55\x8b\xec\x48'
```

#### Ler valores tipados
```python
import struct

# Ler int32 (4 bytes)
data = pm.read_bytes(0x400000, 4)
value = struct.unpack('<i', data)[0]  # < = little-endian

# Ler float (4 bytes)
data = pm.read_bytes(0x400000, 4)
value = struct.unpack('<f', data)[0]

# Ler string terminada em null
data = pm.read_bytes(0x400000, 256)
string = data.split(b'\x00')[0].decode('utf-8')
```

#### Formatos struct.unpack
| Formato | Tipo | Tamanho |
|---------|------|--------|
| 'i' | int32 signed | 4 bytes |
| 'I' | uint32 unsigned | 4 bytes |
| 'q' | int64 signed | 8 bytes |
| 'Q' | uint64 unsigned | 8 bytes |
| 'f' | float32 | 4 bytes |
| 'd' | float64 (double) | 8 bytes |
| 's' | char (string) | N bytes |

Sempre usar '<' para little-endian (padrão Windows x64)

### Escrita de Memória
```python
import struct

# Escrever int32 (valor 100)
value_bytes = struct.pack('<i', 100)
pm.write_bytes(0x400000, value_bytes)

# Escrever múltiplos bytes
pm.write_bytes(0x400000, b'\x90\x90\x90\x90')  # NOP sled
```

## 4. Varredura (Scanning)

### Scan de Valor Simples
```python
import struct

def scan_int32(pm, value):
    """Escanear processo procurando um int32"""
    search_bytes = struct.pack('<i', value)
    results = []
    
    for module in pymem.list_modules(pm.process_handle):
        try:
            base = module.lpBaseOfDll
            size = module.SizeOfImage
            data = pm.read_bytes(base, size)
            
            # Procurar todas as ocorrências
            offset = 0
            while True:
                offset = data.find(search_bytes, offset)
                if offset == -1:
                    break
                results.append(base + offset)
                offset += 1
        except:
            pass
    
    return results
```

### Scan com Pattern e Mask
```python
def scan_pattern(pm, pattern, mask=None):
    """Escanear com padrão e máscara opcional"""
    results = []
    
    for module in pymem.list_modules(pm.process_handle):
        try:
            base = module.lpBaseOfDll
            size = module.SizeOfImage
            data = pm.read_bytes(base, size)
            
            for i in range(len(data) - len(pattern) + 1):
                match = True
                for j, byte in enumerate(pattern):
                    if mask and mask[j] == '?':
                        continue
                    if data[i + j] != byte:
                        match = False
                        break
                
                if match:
                    results.append(base + i)
        except:
            pass
    
    return results

# Uso: procurar por "55 8B EC 48 ??" (push rbp; mov rbp, rsp; mov rax, ?)
pattern = b'\x55\x8b\xec\x48\x00'
mask = 'xxxx?'
addrs = scan_pattern(pm, pattern, mask)
```

## 5. Acesso a Módulos

### Listar Módulos
```python
for module in pymem.list_modules(pm.process_handle):
    print(f"Módulo: {module.filename}")
    print(f"  Base: 0x{module.lpBaseOfDll:08X}")
    print(f"  Tamanho: {module.SizeOfImage} bytes")
```

### Obter Base de um Módulo
```python
# Encontrar base de um módulo específico
for module in pymem.list_modules(pm.process_handle):
    if "kernel32.dll" in module.filename:
        kernel32_base = module.lpBaseOfDll
        break

# Ler a partir da base + offset
data = pm.read_bytes(kernel32_base + 0x1000, 4)
```

## 6. Tratamento de Erros

### Exceções Comuns
```python
import pymem.exception

try:
    pm = pymem.Pymem("inexistente.exe")
except pymem.exception.ProcessNotFound:
    print("Processo não encontrado")

except pymem.exception.AccessDenied:
    print("Acesso negado - execute como administrador")

except pymem.exception.MemoryReadError:
    print("Falha ao ler memória")

except Exception as e:
    print(f"Erro geral: {type(e).__name__}: {e}")
```

### Leitura Segura
```python
def safe_read(pm, address, size):
    """Ler memória com tratamento de erro"""
    try:
        return pm.read_bytes(address, size)
    except:
        return None

data = safe_read(pm, 0x400000, 256)
if data:
    print("Leitura bem-sucedida")
else:
    print("Falha na leitura")
```

## 7. Exemplos Práticos

### Exemplo 1: Encontrar Valor e Ler Próximas Estruturas
```python
def find_and_inspect(pm, process_name, search_value):
    pm = pymem.Pymem(process_name)
    
    # Procurar pelo valor
    search_bytes = struct.pack('<i', search_value)
    for module in pymem.list_modules(pm.process_handle):
        try:
            data = pm.read_bytes(module.lpBaseOfDll, module.SizeOfImage)
            offset = data.find(search_bytes)
            
            if offset != -1:
                addr = module.lpBaseOfDll + offset
                print(f"Encontrado em: 0x{addr:08X}")
                
                # Ler 32 bytes ao redor
                context = pm.read_bytes(addr - 16, 64)
                print(f"Contexto (hex): {context.hex()}")
                
                return addr
        except:
            pass
    
    return None
```

### Exemplo 2: Varredura em Tempo Real
```python
def continuous_scan(pm, address, size, duration_seconds=5):
    """Monitorar mudanças em região de memória"""
    import time
    
    print(f"Monitorando 0x{address:08X} por {duration_seconds}s")
    
    last_state = None
    start = time.time()
    iterations = 0
    
    while (time.time() - start) < duration_seconds:
        try:
            current_state = pm.read_bytes(address, size)
            
            if last_state and current_state != last_state:
                for i, (old, new) in enumerate(zip(last_state, current_state)):
                    if old != new:
                        print(f"[MUDANÇA] Offset +0x{i:02X}: 0x{old:02X} -> 0x{new:02X}")
            
            last_state = current_state
            iterations += 1
            time.sleep(0.1)
        except:
            pass
    
    print(f"Monitoramento concluído ({iterations} iterações)")
```

### Exemplo 3: Auditoria de Seção de Código
```python
def audit_code_section(pm, process_name):
    """Auditar seção .text procurando padrões suspeitos"""
    pm = pymem.Pymem(process_name)
    
    # Padrões suspeitos
    patterns = {
        "JMP longe": b'\xe9',  # jmp offset32
        "NOP sled": b'\x90\x90\x90\x90',
        "RET imediato": b'\xc3',
    }
    
    for module in pymem.list_modules(pm.process_handle):
        if ".text" in module or "CODE" in module:
            try:
                data = pm.read_bytes(module.lpBaseOfDll, min(module.SizeOfImage, 10000))
                
                for pattern_name, pattern_bytes in patterns.items():
                    if pattern_bytes in data:
                        count = data.count(pattern_bytes)
                        print(f"[{module.filename}] {pattern_name}: {count} ocorrências")
            except:
                pass
```

## 8. Performance e Limitações

### Velocidade de Leitura
- Leituras pequenas (< 1KB): ~1-10 µs
- Leituras médias (1-10KB): ~10-100 µs
- Leituras grandes (> 100KB): ~1-10 ms

### Otimizações
```python
# ❌ Lento: múltiplas leituras pequenas
for i in range(100):
    byte = pm.read_bytes(0x400000 + i, 1)

# ✅ Rápido: uma leitura grande
data = pm.read_bytes(0x400000, 100)
```

### Limitações
- Não pode ler memória protegida (PAGE_NOACCESS)
- Requer privilégios de administrador para processos de terceiros
- ASLR torna endereços variáveis entre execuções
- Alguns processos têm proteção anti-cheat

## 9. Casos de Uso

### ✅ Usos Válidos
- Ferramentas de acessibilidade
- QA Automation e testes de stress
- Debugging e diagnóstico
- Auditoria de segurança em software próprio
- Análise de performance

### ❌ Usos Não Permitidos
- Reverse engineering de software protegido
- Contorno de proteções anti-cheat
- Modificação não autorizada de aplicações
- Extração de dados sensíveis

## 10. Integração com ONNX Runtime

Para monitorar modelos de IA durante inferência:

```python
def monitor_onnx_inference(pm, model_buffer_addr, model_size):
    """Monitorar alocações durante execução de modelo"""
    
    import time
    
    baseline = pm.read_bytes(model_buffer_addr, model_size)
    
    # ... executar inferência ...
    
    time.sleep(0.5)  # Aguardar processamento
    
    current = pm.read_bytes(model_buffer_addr, model_size)
    
    # Calcular delta
    changes = sum(1 for a, b in zip(baseline, current) if a != b)
    print(f"Mudanças de memória: {changes} bytes ({changes/model_size*100:.2f}%)")
```

## Referências
- [Pymem GitHub](https://github.com/srounet/Pymem)
- [Pymem Documentation](https://pymem.readthedocs.io/)
- [Windows Process Memory API](https://docs.microsoft.com/en-us/windows/win32/memory/process-memory)
- [Python struct module](https://docs.python.org/3/library/struct.html)
