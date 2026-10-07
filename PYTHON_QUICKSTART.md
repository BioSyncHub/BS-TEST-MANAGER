# Guia Rápido: Usar Pymem

## 1. Instalação Rápida

```powershell
# Abrir PowerShell como Administrador

# Instalar pymem
pip install pymem

# Verificar instalação
python -c "import pymem; print('OK')"
```

## 2. Seu Primeiro Scan

```python
import pymem
import struct

# Conectar ao processo
pm = pymem.Pymem("notepad.exe")

# Procurar pelo valor 100
search_value = 100
search_bytes = struct.pack('<i', search_value)

results = []
for module in pymem.list_modules(pm.process_handle):
    try:
        data = pm.read_bytes(module.lpBaseOfDll, module.SizeOfImage)
        offset = 0
        while True:
            offset = data.find(search_bytes, offset)
            if offset == -1:
                break
            results.append(module.lpBaseOfDll + offset)
            offset += 1
    except:
        pass

print(f"Encontrados {len(results)} resultados:")
for addr in results[:5]:
    print(f"  0x{addr:08X}")

pm.close()
```

## 3. Usar os Scripts Fornecidos

### Script Básico
```bash
python memory_scanner_basic.py
```

Editar o arquivo e alterar:
```python
process_name = "explorer.exe"  # Seu processo
search_value = 100  # Seu valor
```

### Script Avançado
```bash
python memory_scanner_advanced.py
```

Oferece mais funcionalidades como pattern scanning e snapshots.

### Monitor em Tempo Real
```bash
python memory_monitor_realtime.py
```

Monitora mudanças contínuas e detecta anomalias.

## 4. Executar como Administrador

⚠️ **Importante**: Para ler processos de terceiros, execute como Administrador

### PowerShell
```powershell
# Abrir PowerShell como Admin e rodar:
python C:\BS-TEST-MANAGER\memory_scanner_basic.py
```

### CMD
```cmd
# Abrir CMD como Admin e rodar:
python C:\BS-TEST-MANAGER\memory_scanner_basic.py
```

### Atalho direto
1. Criar arquivo `run_as_admin.bat`:
```batch
@echo off
python C:\BS-TEST-MANAGER\memory_scanner_basic.py
pause
```

2. Clique direito > "Executar como administrador"

## 5. Troubleshooting

### "ProcessNotFound"
- Verifique o nome do executável em Gerenciador de Tarefas
- Cuidado com maiúsculas/minúsculas: `Explorer.exe` ≠ `explorer.exe`

### "AccessDenied"
- Execute como administrador
- Não é possível ler processos do sistema sem privilégios

### "MemoryReadError"
- Endereço pode estar protegido
- Use try/except para tratamento

### Pymem não importa
```bash
pip install --upgrade pymem
# Se falhar, reinstale:
pip uninstall pymem -y
pip install pymem==1.14.0
```

## 6. Exemplos Rápidos

### Encontrar PID e conectar
```python
import pymem
import psutil

# Encontrar PID pelo nome
def find_pid(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            return proc.info['pid']
    return None

pid = find_pid("explorer.exe")
if pid:
    pm = pymem.Pymem(process_id=pid)
    print(f"Conectado ao PID {pid}")
```

### Ler uint32
```python
import struct

value_bytes = pm.read_bytes(0x400000, 4)
value = struct.unpack('<I', value_bytes)[0]  # I = unsigned
print(f"Valor: {value}")
```

### Ler string
```python
raw = pm.read_bytes(0x400000, 256)
string = raw.split(b'\x00')[0].decode('utf-8', errors='ignore')
print(f"String: {string}")
```

### Escrever valor
```python
import struct

# Escrever valor 42 no endereço
new_value = struct.pack('<i', 42)
pm.write_bytes(0x400000, new_value)
```

### Listar módulos
```python
for module in pymem.list_modules(pm.process_handle):
    print(f"{module.filename}")
    print(f"  Base: 0x{module.lpBaseOfDll:08X}")
    print(f"  Size: {module.SizeOfImage} bytes")
```

## 7. Padrões Úteis

### Máscara de padrão
```python
# Procurar: "55 8B EC 48 ??"
pattern = b'\x55\x8b\xec\x48\x00'
mask = 'xxxx?'  # x = comparar, ? = ignorar

# A máscara diz para ignorar o último byte
```

### Struct pack/unpack
```python
import struct

# Pack (Python -> bytes)
data = struct.pack('<i', 100)  # int32 = 4 bytes

# Unpack (bytes -> Python)
value = struct.unpack('<i', data)[0]
```

## 8. Próximos Passos

1. **Adapte os scripts** para seu próprio processo
2. **Estude a documentação** em `PYMEM_DOCUMENTACAO.md`
3. **Combine com testes** para QA Automation
4. **Integre com suas ferramentas** de diagnóstico

## Links Úteis
- Documentação: `PYMEM_DOCUMENTACAO.md`
- Exemplos avançados: `memory_scanner_advanced.py`
- Monitor real-time: `memory_monitor_realtime.py`
