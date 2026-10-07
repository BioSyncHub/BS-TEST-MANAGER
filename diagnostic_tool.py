"""
Script de Diagnóstico Completo - Uso Imediato
Combine C++ e Python para máxima eficiência
"""

import pymem
import struct
import sys
from typing import List, Optional


class DiagnosticTool:
    """Ferramenta de diagnóstico integrada"""
    
    def __init__(self, process_name: str):
        self.process_name = process_name
        self.pm: Optional[pymem.Pymem] = None
        self.connected = False
        
        try:
            self.pm = pymem.Pymem(process_name)
            self.connected = True
            print(f"✓ Conectado a {process_name}")
        except Exception as e:
            print(f"✗ Erro ao conectar: {e}")
            print("\n[DICA] Execute este script como Administrador!")
            sys.exit(1)
    
    def find_value_int32(self, value: int) -> List[int]:
        """Encontrar todas as ocorrências de um int32"""
        print(f"\n[BUSCANDO] valor int32: {value}")
        print("─" * 60)
        
        search_bytes = struct.pack('<i', value)
        addresses = []
        
        try:
            for module in pymem.list_modules(self.pm.process_handle):
                try:
                    base = module.lpBaseOfDll
                    size = module.SizeOfImage
                    data = self.pm.read_bytes(base, size)
                    
                    offset = 0
                    while True:
                        offset = data.find(search_bytes, offset)
                        if offset == -1:
                            break
                        addresses.append(base + offset)
                        offset += 1
                
                except Exception:
                    continue
            
            print(f"✓ Busca concluída")
            print(f"  Encontradas {len(addresses)} ocorrências\n")
            
            # Exibir resultados
            for i, addr in enumerate(addresses[:10], 1):
                value_read = struct.unpack('<i', self.pm.read_bytes(addr, 4))[0]
                print(f"  [{i:2d}] 0x{addr:08X} = {value_read}")
            
            if len(addresses) > 10:
                print(f"\n  ... e mais {len(addresses) - 10} endereços")
            
            return addresses
        
        except Exception as e:
            print(f"✗ Erro durante busca: {e}")
            return []
    
    def find_value_float(self, value: float) -> List[int]:
        """Encontrar todas as ocorrências de um float"""
        print(f"\n[BUSCANDO] valor float: {value}")
        print("─" * 60)
        
        search_bytes = struct.pack('<f', value)
        addresses = []
        
        try:
            for module in pymem.list_modules(self.pm.process_handle):
                try:
                    base = module.lpBaseOfDll
                    size = module.SizeOfImage
                    data = self.pm.read_bytes(base, size)
                    
                    offset = 0
                    while True:
                        offset = data.find(search_bytes, offset)
                        if offset == -1:
                            break
                        addresses.append(base + offset)
                        offset += 1
                
                except Exception:
                    continue
            
            print(f"✓ Busca concluída")
            print(f"  Encontradas {len(addresses)} ocorrências\n")
            
            for i, addr in enumerate(addresses[:10], 1):
                value_read = struct.unpack('<f', self.pm.read_bytes(addr, 4))[0]
                print(f"  [{i:2d}] 0x{addr:08X} = {value_read}")
            
            if len(addresses) > 10:
                print(f"\n  ... e mais {len(addresses) - 10} endereços")
            
            return addresses
        
        except Exception as e:
            print(f"✗ Erro durante busca: {e}")
            return []
    
    def read_memory(self, address: int, size: int = 32) -> Optional[bytes]:
        """Ler memória de um endereço"""
        try:
            data = self.pm.read_bytes(address, size)
            
            print(f"\n[LEITURA] Endereço 0x{address:08X} ({size} bytes)")
            print("─" * 60)
            print("HEX:")
            print("  ", ' '.join(f"{b:02X}" for b in data))
            print("\nASCII:")
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
            print("  ", ascii_str)
            
            return data
        
        except Exception as e:
            print(f"✗ Erro ao ler: {e}")
            return None
    
    def find_pattern(self, pattern: str, mask: Optional[str] = None) -> List[int]:
        """Buscar padrão de bytes (formato hex)"""
        print(f"\n[PADRÃO] {pattern}")
        if mask:
            print(f"[MÁSCARA] {mask}")
        print("─" * 60)
        
        # Converter string hex para bytes
        pattern_bytes = bytes.fromhex(pattern.replace(' ', ''))
        
        if mask and len(mask) != len(pattern_bytes):
            print("✗ Máscara não corresponde ao padrão")
            return []
        
        addresses = []
        
        try:
            for module in pymem.list_modules(self.pm.process_handle):
                try:
                    base = module.lpBaseOfDll
                    size = module.SizeOfImage
                    data = self.pm.read_bytes(base, size)
                    
                    for i in range(len(data) - len(pattern_bytes) + 1):
                        match = True
                        
                        for j, byte in enumerate(pattern_bytes):
                            if mask and mask[j] == '?':
                                continue
                            
                            if data[i + j] != byte:
                                match = False
                                break
                        
                        if match:
                            addresses.append(base + i)
                
                except Exception:
                    continue
            
            print(f"✓ Busca concluída")
            print(f"  Encontradas {len(addresses)} ocorrências\n")
            
            for i, addr in enumerate(addresses[:10], 1):
                print(f"  [{i:2d}] 0x{addr:08X}")
            
            if len(addresses) > 10:
                print(f"\n  ... e mais {len(addresses) - 10} endereços")
            
            return addresses
        
        except Exception as e:
            print(f"✗ Erro: {e}")
            return []
    
    def list_modules(self):
        """Listar todos os módulos carregados"""
        print(f"\n[MÓDULOS] Processo: {self.process_name}")
        print("─" * 60)
        
        try:
            modules = list(pymem.list_modules(self.pm.process_handle))
            
            for i, module in enumerate(modules, 1):
                print(f"  [{i:2d}] {module.filename}")
                print(f"       Base: 0x{module.lpBaseOfDll:08X}")
                print(f"       Size: {module.SizeOfImage:,} bytes")
            
            print(f"\n✓ Total: {len(modules)} módulos")
        
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    def close(self):
        """Fechar conexão"""
        if self.pm:
            self.pm.close()
            print("\n✓ Conexão fechada")


def main():
    """Menu interativo"""
    print("\n" + "="*60)
    print("FERRAMENTA DE DIAGNÓSTICO DE MEMÓRIA")
    print("="*60)
    
    # Obter nome do processo
    process_name = input("\n[?] Nome do processo (ex: notepad.exe): ").strip()
    if not process_name:
        process_name = "explorer.exe"
    
    tool = DiagnosticTool(process_name)
    
    while True:
        print("\n" + "="*60)
        print("MENU")
        print("="*60)
        print("1 - Buscar valor int32")
        print("2 - Buscar valor float")
        print("3 - Buscar padrão de bytes (hex)")
        print("4 - Ler memória de um endereço")
        print("5 - Listar módulos")
        print("0 - Sair")
        
        choice = input("\n[?] Escolha uma opção (0-5): ").strip()
        
        if choice == "1":
            try:
                value = int(input("[?] Valor a buscar: "))
                tool.find_value_int32(value)
            except ValueError:
                print("✗ Valor inválido")
        
        elif choice == "2":
            try:
                value = float(input("[?] Valor a buscar: "))
                tool.find_value_float(value)
            except ValueError:
                print("✗ Valor inválido")
        
        elif choice == "3":
            pattern = input("[?] Padrão (hex, ex: 55 8B EC): ").strip().upper()
            mask = input("[?] Máscara (opcional, ex: xxx): ").strip()
            tool.find_pattern(pattern, mask if mask else None)
        
        elif choice == "4":
            try:
                addr_str = input("[?] Endereço (hex, ex: 400000): ").strip()
                address = int(addr_str, 16)
                size = int(input("[?] Tamanho em bytes (padrão 32): ") or "32")
                tool.read_memory(address, size)
            except ValueError:
                print("✗ Endereço inválido")
        
        elif choice == "5":
            tool.list_modules()
        
        elif choice == "0":
            print("\n[*] Encerrando...")
            tool.close()
            break
        
        else:
            print("✗ Opção inválida")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[*] Interrompido pelo usuário")
    except Exception as e:
        print(f"\n✗ Erro fatal: {e}")
