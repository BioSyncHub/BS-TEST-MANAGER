"""
Monitoramento em tempo real de processos com detecção de anomalias
Útil para testes de stress, QA automation e auditoria de segurança
"""

import pymem
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
import time
import threading
from enum import Enum


class AnomalyType(Enum):
    """Tipos de anomalias detectáveis"""
    MEMORY_SPIKE = "Spike de acesso à memória"
    PATTERN_CHANGE = "Padrão inesperado"
    REPEATED_ACCESS = "Acesso repetitivo"
    LARGE_ALLOCATION = "Alocação grande detectada"


@dataclass
class AccessPattern:
    """Padrão de acesso a memória"""
    address: int
    access_count: int = 0
    last_access: datetime = None
    total_bytes_accessed: int = 0
    anomalies: List[AnomalyType] = None
    
    def __post_init__(self):
        if self.anomalies is None:
            self.anomalies = []


class RealtimeMemoryMonitor:
    """
    Monitor em tempo real com detecção de anomalias
    """
    
    def __init__(self, process_name: str, check_interval_ms: int = 100):
        """
        Args:
            process_name: Nome do executável
            check_interval_ms: Intervalo entre verificações em ms
        """
        self.process_name = process_name
        self.check_interval_ms = check_interval_ms
        self.pm: Optional[pymem.Pymem] = None
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.access_patterns: Dict[int, AccessPattern] = {}
        self.callbacks: List[Callable] = []
        
        self._connect()
    
    def _connect(self) -> bool:
        """Conectar ao processo"""
        try:
            self.pm = pymem.Pymem(self.process_name)
            print(f"[✓] Conectado a {self.process_name}")
            return True
        except Exception as e:
            print(f"[✗] Erro ao conectar: {e}")
            return False
    
    def register_callback(self, callback: Callable):
        """Registrar callback para anomalias"""
        self.callbacks.append(callback)
    
    def trigger_callbacks(self, pattern: AccessPattern, anomaly: AnomalyType):
        """Executar callbacks registrados"""
        for callback in self.callbacks:
            try:
                callback(pattern, anomaly)
            except Exception as e:
                print(f"[✗] Erro em callback: {e}")
    
    def monitor_address(self, address: int, watch_duration_seconds: int = 10):
        """
        Monitorar um endereço específico continuamente
        
        Args:
            address: Endereço a monitorar
            watch_duration_seconds: Duração do monitoramento
        """
        if not self.pm:
            print("[✗] Não conectado")
            return
        
        self.monitoring = True
        print(f"\n[*] Monitorando 0x{address:08X} por {watch_duration_seconds}s")
        print("[*] Pressione Ctrl+C para parar\n")
        
        start_time = time.time()
        iteration = 0
        
        try:
            while self.monitoring and (time.time() - start_time) < watch_duration_seconds:
                try:
                    # Tentar ler 4 bytes do endereço
                    data = self.pm.read_bytes(address, 4)
                    
                    if address not in self.access_patterns:
                        self.access_patterns[address] = AccessPattern(address)
                    
                    pattern = self.access_patterns[address]
                    pattern.access_count += 1
                    pattern.last_access = datetime.now()
                    pattern.total_bytes_accessed += len(data)
                    
                    # Detectar anomalias
                    if pattern.access_count > 100 and iteration % 10 == 0:
                        print(f"[!] Anomalia: Acesso repetitivo ({pattern.access_count} vezes)")
                    
                    iteration += 1
                
                except Exception as e:
                    pass
                
                time.sleep(self.check_interval_ms / 1000.0)
        
        except KeyboardInterrupt:
            print("\n[*] Monitoramento interrompido")
        
        self.monitoring = False
        
        # Estatísticas finais
        if address in self.access_patterns:
            pattern = self.access_patterns[address]
            print(f"\n[ESTATÍSTICAS FINAIS]")
            print(f"Endereço: 0x{address:08X}")
            print(f"Acessos totais: {pattern.access_count}")
            print(f"Bytes acessados: {pattern.total_bytes_accessed}")
    
    def monitor_multiple_addresses(self, addresses: List[int], watch_duration_seconds: int = 10):
        """
        Monitorar múltiplos endereços simultaneamente
        """
        if not self.pm:
            print("[✗] Não conectado")
            return
        
        self.monitoring = True
        print(f"\n[*] Monitorando {len(addresses)} endereços por {watch_duration_seconds}s\n")
        
        start_time = time.time()
        iteration = 0
        
        try:
            while self.monitoring and (time.time() - start_time) < watch_duration_seconds:
                for address in addresses:
                    try:
                        data = self.pm.read_bytes(address, 4)
                        
                        if address not in self.access_patterns:
                            self.access_patterns[address] = AccessPattern(address)
                        
                        pattern = self.access_patterns[address]
                        pattern.access_count += 1
                        pattern.total_bytes_accessed += len(data)
                    
                    except:
                        pass
                
                if iteration % 10 == 0:
                    self._print_access_stats()
                
                iteration += 1
                time.sleep(self.check_interval_ms / 1000.0)
        
        except KeyboardInterrupt:
            print("\n[*] Monitoramento interrompido")
        
        self.monitoring = False
    
    def stress_test_memory_region(self, address: int, size: int, 
                                  duration_seconds: int = 5, 
                                  read_frequency_hz: int = 100):
        """
        Teste de stress: leitura contínua de região de memória
        
        Args:
            address: Endereço inicial
            size: Tamanho da região
            duration_seconds: Duração do teste
            read_frequency_hz: Frequência de leituras por segundo
        """
        if not self.pm:
            print("[✗] Não conectado")
            return
        
        print(f"\n[*] Teste de stress")
        print(f"    Região: 0x{address:08X} - 0x{address+size:08X} ({size} bytes)")
        print(f"    Duração: {duration_seconds}s")
        print(f"    Frequência: {read_frequency_hz} Hz\n")
        
        start_time = time.time()
        read_count = 0
        errors = 0
        bytes_read = 0
        
        try:
            while (time.time() - start_time) < duration_seconds:
                try:
                    data = self.pm.read_bytes(address, size)
                    bytes_read += len(data)
                    read_count += 1
                except:
                    errors += 1
                
                time.sleep(1.0 / read_frequency_hz)
        
        except KeyboardInterrupt:
            print("\n[*] Teste interrompido")
        
        # Resultados
        elapsed = time.time() - start_time
        actual_frequency = read_count / elapsed if elapsed > 0 else 0
        throughput_mb = (bytes_read / (1024 * 1024)) / elapsed if elapsed > 0 else 0
        
        print(f"\n[RESULTADOS DO TESTE DE STRESS]")
        print(f"Tempo total: {elapsed:.2f}s")
        print(f"Leituras bem-sucedidas: {read_count}")
        print(f"Erros: {errors}")
        print(f"Frequência real: {actual_frequency:.2f} Hz")
        print(f"Throughput: {throughput_mb:.2f} MB/s")
        print(f"Taxa de erro: {(errors / (read_count + errors) * 100):.2f}%}" if (read_count + errors) > 0 else "N/A")
    
    def _print_access_stats(self):
        """Imprimir estatísticas de acesso"""
        print("[ESTATÍSTICAS DE ACESSO]")
        for addr, pattern in sorted(self.access_patterns.items(), 
                                    key=lambda x: x[1].access_count, 
                                    reverse=True)[:5]:
            print(f"  0x{addr:08X}: {pattern.access_count} acessos, {pattern.total_bytes_accessed} bytes")
    
    def close(self):
        """Fechar conexão"""
        self.monitoring = False
        if self.pm:
            self.pm.close()
            print("[✓] Conexão fechada")


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

def anomaly_callback(pattern: AccessPattern, anomaly: AnomalyType):
    """Callback para anomalias"""
    print(f"[ALERTA] {anomaly.value} em 0x{pattern.address:08X}")


if __name__ == "__main__":
    print("=== Monitor em Tempo Real de Memória ===\n")
    
    monitor = RealtimeMemoryMonitor("explorer.exe", check_interval_ms=100)
    
    if monitor.pm:
        # Registrar callback
        monitor.register_callback(anomaly_callback)
        
        # Exemplo 1: Monitorar endereço único
        print("[Exemplo 1] Monitoramento de endereço único")
        monitor.monitor_address(0x400000, watch_duration_seconds=5)
        
        # Exemplo 2: Teste de stress
        print("\n[Exemplo 2] Teste de stress de região de memória")
        monitor.stress_test_memory_region(0x400000, size=4096, 
                                         duration_seconds=3, 
                                         read_frequency_hz=50)
        
        monitor.close()
    else:
        print("[✗] Falha ao conectar")
