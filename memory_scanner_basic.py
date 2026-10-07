"""
Ferramenta básica de diagnóstico de memória usando pymem
Conecta a um processo e realiza varredura de valores específicos
"""

import pymem
import pymem.exception
from typing import List, Optional, Tuple
import struct


class MemoryScanResult:
    """Estrutura para armazenar resultado da varredura"""
    def __init__(self):
        self.success: bool = False
        self.addresses: List[int] = []
        self.error_message: str = ""
        self.bytes_scanned: int = 0
        self.matches_found: int = 0


def connect_to_process(process_name: str) -> Optional[pymem.Pymem]:
    """
    Conecta a um processo ativo pelo nome do executável
    
    Args:
        process_name: Nome do executável (ex: 'meu_programa.exe')
    
    Returns:
        Objeto pymem.Pymem ou None se falhar
    """
    try:
        # pymem tenta conectar ao processo automaticamente
        pm = pymem.Pymem(process_name)
        print(f"[✓] Conectado ao processo: {process_name}")
        print(f"[✓] PID: {pm.process_handle}")
        return pm
    
    except pymem.exception.ProcessNotFound:
        print(f"[✗] Processo não encontrado: {process_name}")
        return None
    
    except pymem.exception.AccessDenied:
        print(f"[✗] Acesso negado ao processo. Execute como administrador.")
        return None
    
    except Exception as e:
        print(f"[✗] Erro ao conectar: {type(e).__name__}: {e}")
        return None


def scan_value_int32(pm: pymem.Pymem, search_value: int) -> MemoryScanResult:
    """
    Escaneia a memória do processo em busca de um valor inteiro (int32)
    
    Args:
        pm: Objeto pymem.Pymem conectado ao processo
        search_value: Valor inteiro a procurar (int32)
    
    Returns:
        MemoryScanResult com lista de endereços encontrados
    """
    result = MemoryScanResult()
    
    # Validação
    if not (-2**31) <= search_value <= 2**31 - 1:
        result.error_message = "Valor fora do range int32 (-2^31 a 2^31-1)"
        return result
    
    try:
        # Converter valor para bytes (little-endian)
        search_bytes = struct.pack('<i', search_value)
        
        print(f"[*] Procurando pelo valor: {search_value} (0x{search_value:08X})")
        print(f"[*] Padrão de bytes: {search_bytes.hex()}")
        print(f"[*] Escaneando memória...")
        
        # Iterar sobre os módulos do processo
        for module in pymem.list_modules(pm.process_handle):
            try:
                # Ler dados do módulo
                module_base = module.lpBaseOfDll
                module_size = module.SizeOfImage
                
                # Ler bloco de memória
                try:
                    data = pm.read_bytes(module_base, module_size)
                    result.bytes_scanned += len(data)
                    
                    # Procurar pela sequência de bytes
                    offset = 0
                    while True:
                        offset = data.find(search_bytes, offset)
                        if offset == -1:
                            break
                        
                        # Endereço absoluto = base do módulo + offset
                        absolute_address = module_base + offset
                        result.addresses.append(absolute_address)
                        result.matches_found += 1
                        
                        offset += 1  # Continuar procurando
                
                except Exception as e:
                    # Falha ao ler este módulo, continuar com próximo
                    pass
            
            except Exception as e:
                pass
        
        result.success = True
        
    except struct.error as e:
        result.error_message = f"Erro ao converter valor: {e}"
    
    except Exception as e:
        result.error_message = f"Erro durante varredura: {type(e).__name__}: {e}"
    
    return result


def scan_value_float(pm: pymem.Pymem, search_value: float) -> MemoryScanResult:
    """
    Escaneia a memória em busca de um valor ponto flutuante (float32)
    
    Args:
        pm: Objeto pymem.Pymem conectado ao processo
        search_value: Valor float a procurar
    
    Returns:
        MemoryScanResult com lista de endereços encontrados
    """
    result = MemoryScanResult()
    
    try:
        search_bytes = struct.pack('<f', search_value)
        
        print(f"[*] Procurando pelo valor float: {search_value}")
        print(f"[*] Padrão de bytes: {search_bytes.hex()}")
        
        for module in pymem.list_modules(pm.process_handle):
            try:
                module_base = module.lpBaseOfDll
                module_size = module.SizeOfImage
                
                data = pm.read_bytes(module_base, module_size)
                result.bytes_scanned += len(data)
                
                offset = 0
                while True:
                    offset = data.find(search_bytes, offset)
                    if offset == -1:
                        break
                    
                    absolute_address = module_base + offset
                    result.addresses.append(absolute_address)
                    result.matches_found += 1
                    
                    offset += 1
            
            except:
                pass
        
        result.success = True
    
    except Exception as e:
        result.error_message = f"Erro durante varredura: {type(e).__name__}: {e}"
    
    return result


def scan_pattern_bytes(pm: pymem.Pymem, pattern: bytes, mask: str = None) -> MemoryScanResult:
    """
    Escaneia memória usando padrão de bytes com máscara (opcional)
    
    Args:
        pm: Objeto pymem.Pymem conectado ao processo
        pattern: Padrão de bytes (ex: b'\x55\x8B\xEC')
        mask: Máscara opcional (ex: 'xxx' = todos importantes, 'x?x' = ignorar byte do meio)
    
    Returns:
        MemoryScanResult com lista de endereços encontrados
    """
    result = MemoryScanResult()
    
    if not pattern:
        result.error_message = "Padrão vazio"
        return result
    
    try:
        if mask and len(mask) != len(pattern):
            result.error_message = "Comprimento do mask não corresponde ao padrão"
            return result
        
        print(f"[*] Procurando padrão: {pattern.hex()}")
        if mask:
            print(f"[*] Máscara: {mask}")
        
        for module in pymem.list_modules(pm.process_handle):
            try:
                module_base = module.lpBaseOfDll
                module_size = module.SizeOfImage
                
                data = pm.read_bytes(module_base, module_size)
                result.bytes_scanned += len(data)
                
                # Implementar matching com máscara
                for i in range(len(data) - len(pattern) + 1):
                    match = True
                    
                    for j, byte in enumerate(pattern):
                        # Se mask[j] == 'x', byte deve coincidir
                        # Se mask[j] == '?', ignorar
                        if mask and mask[j] == '?':
                            continue
                        
                        if data[i + j] != byte:
                            match = False
                            break
                    
                    if match:
                        absolute_address = module_base + i
                        result.addresses.append(absolute_address)
                        result.matches_found += 1
            
            except:
                pass
        
        result.success = True
    
    except Exception as e:
        result.error_message = f"Erro durante varredura de padrão: {type(e).__name__}: {e}"
    
    return result


def print_results(result: MemoryScanResult, value_desc: str = ""):
    """Imprime resultados da varredura de forma formatada"""
    print("\n" + "="*70)
    print(f"RESULTADO DA VARREDURA - {value_desc}")
    print("="*70)
    
    if result.success:
        print(f"[✓] Varredura concluída com sucesso")
        print(f"[*] Bytes escaneados: {result.bytes_scanned:,}")
        print(f"[*] Correspondências encontradas: {result.matches_found}")
        
        if result.addresses:
            print(f"\n[ENDEREÇOS ENCONTRADOS]:")
            for i, addr in enumerate(result.addresses[:10], 1):  # Mostrar até 10
                print(f"  {i:3d}. 0x{addr:08X} ({addr})")
            
            if len(result.addresses) > 10:
                print(f"  ... e mais {len(result.addresses) - 10} endereços")
        else:
            print("[!] Nenhuma correspondência encontrada")
    else:
        print(f"[✗] Erro: {result.error_message}")
    
    print("="*70 + "\n")


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("=== Ferramenta de Varredura de Memória (pymem) ===\n")
    
    # Exemplo 1: Conectar a um processo e escanear int32
    print("[Exemplo 1] Varredura de valor inteiro")
    print("-" * 70)
    
    process_name = "explorer.exe"  # Alterar para o processo desejado
    pm = connect_to_process(process_name)
    
    if pm:
        # Escanear valor inteiro
        search_value = 100
        result = scan_value_int32(pm, search_value)
        print_results(result, f"Procurando int32: {search_value}")
        
        # Exemplo 2: Escanear valor float
        print("\n[Exemplo 2] Varredura de valor float")
        print("-" * 70)
        
        search_float = 3.14
        result_float = scan_value_float(pm, search_float)
        print_results(result_float, f"Procurando float: {search_float}")
        
        # Exemplo 3: Pattern scanning
        print("\n[Exemplo 3] Varredura de padrão de bytes")
        print("-" * 70)
        
        # Padrão: 55 8B EC (push rbp; mov rbp, rsp)
        pattern = b'\x55\x8B\xEC'
        result_pattern = scan_pattern_bytes(pm, pattern)
        print_results(result_pattern, f"Padrão: {pattern.hex()}")
        
        # Fechar conexão
        pm.close()
        print("[✓] Conexão fechada")
    
    else:
        print("[✗] Não foi possível conectar ao processo")
