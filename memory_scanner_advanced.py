"""
Ferramenta avançada de auditoria de memória com classe wrapper
Inclui monitoramento contínuo, comparação de snapshots e estatísticas
"""

import pymem
import pymem.exception
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import struct
import time
from enum import Enum


class ValueType(Enum):
    """Tipos de valores suportados para varredura"""
    INT32 = ('i', 4)
    UINT32 = ('I', 4)
    INT64 = ('q', 8)
    UINT64 = ('Q', 8)
    FLOAT = ('f', 4)
    DOUBLE = ('d', 8)
    BYTE = ('B', 1)


@dataclass
class MemorySnapshot:
    """Captura de estado de memória em um ponto no tempo"""
    address: int
    data: bytes
    timestamp: datetime
    size: int = field(init=False)
    
    def __post_init__(self):
        self.size = len(self.data)


@dataclass
class MemoryScanResult:
    """Resultado detalhado de uma varredura"""
    success: bool = False
    addresses: List[int] = field(default_factory=list)
    error_message: str = ""
    bytes_scanned: int = 0
    matches_found: int = 0
    scan_time_ms: float = 0.0


class AdvancedMemoryScanner:
    """
    Scanner avançado de memória com suporte a múltiplos tipos de varredura
    e monitoramento contínuo
    """
    
    def __init__(self, process_name: str):
        """
        Inicializar scanner e conectar ao processo
        
        Args:
            process_name: Nome do executável (ex: 'notepad.exe')
        """
        self.process_name = process_name
        self.pm: Optional[pymem.Pymem] = None
        self.connected = False
        self.snapshots: Dict[int, List[MemorySnapshot]] = {}  # addr -> [snapshots]
        
        self._connect()
    
    def _connect(self) -> bool:
        """Conectar ao processo"""
        try:
            self.pm = pymem.Pymem(self.process_name)
            self.connected = True
            print(f"[✓] Conectado a {self.process_name}")
            return True
        except pymem.exception.ProcessNotFound:
            print(f"[✗] Processo não encontrado: {self.process_name}")
        except pymem.exception.AccessDenied:
            print(f"[✗] Acesso negado. Execute como administrador")
        except Exception as e:
            print(f"[✗] Erro: {type(e).__name__}: {e}")
        
        self.connected = False
        return False
    
    def close(self):
        """Fechar conexão com o processo"""
        if self.pm:
            self.pm.close()
            self.connected = False
            print("[✓] Conexão fechada")
    
    def scan_value(self, value, value_type: ValueType = ValueType.INT32) -> MemoryScanResult:
        """
        Escanear memória procurando um valor específico
        
        Args:
            value: Valor a procurar
            value_type: Tipo do valor (int32, float, etc)
        
        Returns:
            MemoryScanResult com endereços encontrados
        """
        if not self.connected:
            return MemoryScanResult(error_message="Não conectado ao processo")
        
        result = MemoryScanResult()
        start_time = time.time()
        
        try:
            # Converter valor para bytes
            format_char, expected_size = value_type.value
            value_bytes = struct.pack(f'<{format_char}', value)
            
            print(f"[*] Procurando {value_type.name}: {value}")
            print(f"[*] Padrão de bytes: {value_bytes.hex()}")
            
            # Iterar sobre módulos do processo
            for module in pymem.list_modules(self.pm.process_handle):
                try:
                    module_base = module.lpBaseOfDll
                    module_size = module.SizeOfImage
                    
                    data = self.pm.read_bytes(module_base, module_size)
                    result.bytes_scanned += len(data)
                    
                    # Procurar padrão
                    offset = 0
                    while True:
                        offset = data.find(value_bytes, offset)
                        if offset == -1:
                            break
                        
                        absolute_address = module_base + offset
                        result.addresses.append(absolute_address)
                        result.matches_found += 1
                        
                        offset += 1
                
                except Exception as e:
                    pass
            
            result.success = True
        
        except struct.error as e:
            result.error_message = f"Erro ao converter valor: {e}"
        except Exception as e:
            result.error_message = f"Erro: {type(e).__name__}: {e}"
        
        result.scan_time_ms = (time.time() - start_time) * 1000
        return result
    
    def read_memory_region(self, address: int, size: int) -> Optional[bytes]:
        """
        Ler região contígua de memória
        
        Args:
            address: Endereço inicial
            size: Número de bytes a ler
        
        Returns:
            Bytes lidos ou None se falhar
        """
        if not self.connected:
            return None
        
        try:
            return self.pm.read_bytes(address, size)
        except Exception as e:
            print(f"[✗] Erro ao ler memória: {e}")
            return None
    
    def read_value(self, address: int, value_type: ValueType):
        """
        Ler um valor específico de um endereço
        
        Args:
            address: Endereço de memória
            value_type: Tipo do valor a ler
        
        Returns:
            Valor lido ou None se falhar
        """
        if not self.connected:
            return None
        
        try:
            format_char, size = value_type.value
            data = self.pm.read_bytes(address, size)
            
            if len(data) < size:
                return None
            
            unpacked = struct.unpack(f'<{format_char}', data)
            return unpacked[0]
        
        except Exception as e:
            print(f"[✗] Erro ao ler valor: {e}")
            return None
    
    def scan_pattern(self, pattern: bytes, mask: Optional[str] = None) -> MemoryScanResult:
        """
        Escanear usando padrão de bytes com máscara opcional
        
        Args:
            pattern: Padrão de bytes
            mask: Máscara (x=comparar, ?=ignorar)
        
        Returns:
            MemoryScanResult com endereços encontrados
        """
        if not self.connected:
            return MemoryScanResult(error_message="Não conectado")
        
        result = MemoryScanResult()
        start_time = time.time()
        
        if not pattern:
            result.error_message = "Padrão vazio"
            return result
        
        if mask and len(mask) != len(pattern):
            result.error_message = "Comprimento do mask não corresponde"
            return result
        
        try:
            print(f"[*] Procurando padrão: {pattern.hex()}")
            if mask:
                print(f"[*] Máscara: {mask}")
            
            for module in pymem.list_modules(self.pm.process_handle):
                try:
                    module_base = module.lpBaseOfDll
                    module_size = module.SizeOfImage
                    
                    data = self.pm.read_bytes(module_base, module_size)
                    result.bytes_scanned += len(data)
                    
                    # Comparar com máscara
                    for i in range(len(data) - len(pattern) + 1):
                        match = True
                        
                        for j, byte in enumerate(pattern):
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
            result.error_message = f"Erro: {type(e).__name__}: {e}"
        
        result.scan_time_ms = (time.time() - start_time) * 1000
        return result
    
    def capture_snapshot(self, address: int, size: int) -> Optional[MemorySnapshot]:
        """
        Capturar snapshot da memória em um endereço
        
        Args:
            address: Endereço inicial
            size: Tamanho
        
        Returns:
            MemorySnapshot ou None se falhar
        """
        data = self.read_memory_region(address, size)
        if data is None:
            return None
        
        snapshot = MemorySnapshot(address, data, datetime.now())
        
        # Armazenar histórico
        if address not in self.snapshots:
            self.snapshots[address] = []
        self.snapshots[address].append(snapshot)
        
        return snapshot
    
    def compare_snapshots(self, address: int, index1: int = -2, index2: int = -1) -> List[Tuple[int, bytes, bytes]]:
        """
        Comparar dois snapshots da mesma memória
        
        Args:
            address: Endereço da memória
            index1: Índice do primeiro snapshot (-1 = mais recente)
            index2: Índice do segundo snapshot
        
        Returns:
            Lista de (offset, valor_antigo, valor_novo) para mudanças
        """
        if address not in self.snapshots or len(self.snapshots[address]) < 2:
            return []
        
        try:
            snap1 = self.snapshots[address][index1]
            snap2 = self.snapshots[address][index2]
            
            changes = []
            min_size = min(len(snap1.data), len(snap2.data))
            
            for i in range(min_size):
                if snap1.data[i] != snap2.data[i]:
                    changes.append((i, snap1.data[i], snap2.data[i]))
            
            return changes
        
        except IndexError:
            return []
    
    def print_results(self, result: MemoryScanResult, description: str = ""):
        """Imprimir resultados formatados"""
        print("\n" + "="*70)
        print(f"RESULTADO - {description}")
        print("="*70)
        
        if result.success:
            print(f"[✓] Varredura concluída")
            print(f"[*] Bytes escaneados: {result.bytes_scanned:,}")
            print(f"[*] Correspondências: {result.matches_found}")
            print(f"[*] Tempo: {result.scan_time_ms:.2f} ms")
            
            if result.addresses:
                print(f"\n[ENDEREÇOS]:")
                for i, addr in enumerate(result.addresses[:10], 1):
                    print(f"  {i:3d}. 0x{addr:08X}")
                
                if len(result.addresses) > 10:
                    print(f"  ... +{len(result.addresses) - 10} mais")
            else:
                print("[!] Nenhuma correspondência")
        else:
            print(f"[✗] Erro: {result.error_message}")
        
        print("="*70 + "\n")


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("=== Scanner Avançado de Memória ===\n")
    
    # Criar scanner
    scanner = AdvancedMemoryScanner("explorer.exe")
    
    if scanner.connected:
        # Exemplo 1: Varredura de int32
        print("[Exemplo 1] Procurando int32: 100")
        result = scanner.scan_value(100, ValueType.INT32)
        scanner.print_results(result, "Int32: 100")
        
        # Exemplo 2: Varredura de float
        print("[Exemplo 2] Procurando float: 3.14")
        result = scanner.scan_value(3.14, ValueType.FLOAT)
        scanner.print_results(result, "Float: 3.14")
        
        # Exemplo 3: Pattern scanning
        print("[Exemplo 3] Procurando padrão")
        pattern = b'\x55\x8B\xEC'
        result = scanner.scan_pattern(pattern)
        scanner.print_results(result, f"Padrão: {pattern.hex()}")
        
        # Exemplo 4: Ler valor de endereço específico
        if result.addresses:
            print(f"[Exemplo 4] Lendo valor do primeiro endereço encontrado")
            addr = result.addresses[0]
            value = scanner.read_value(addr, ValueType.INT32)
            print(f"Valor em 0x{addr:08X}: {value}\n")
        
        # Exemplo 5: Capture de snapshots
        if result.addresses:
            print("[Exemplo 5] Captura de snapshots")
            addr = result.addresses[0]
            snap1 = scanner.capture_snapshot(addr, 32)
            print(f"Snapshot 1 capturado: 0x{addr:08X}, {len(snap1.data)} bytes")
            
            time.sleep(1)
            snap2 = scanner.capture_snapshot(addr, 32)
            print(f"Snapshot 2 capturado: 0x{addr:08X}, {len(snap2.data)} bytes")
            
            changes = scanner.compare_snapshots(addr)
            print(f"Mudanças detectadas: {len(changes)}")
        
        scanner.close()
    else:
        print("[✗] Falha ao conectar")
