#include <windows.h>
#include <iostream>
#include <thread>
#include <chrono>
#include <vector>
#include <map>
#include <algorithm>
#include <cstdint>

/**
 * AdvancedProcessMonitor - Monitoramento avançado de processos
 * 
 * Recursos:
 *  - Leitura contínua de memória com timestamps
 *  - Detecção de mudanças em regiões de memória
 *  - Monitoramento de estruturas de dados específicas
 *  - Coleta de métricas de performance
 */

class MemorySnapshot
{
public:
    std::vector<unsigned char> data;
    UINT_PTR address;
    SIZE_T size;
    std::chrono::system_clock::time_point timestamp;
    
    MemorySnapshot(UINT_PTR addr, SIZE_T sz)
        : address(addr), size(sz), timestamp(std::chrono::system_clock::now()) {}
};

class AdvancedProcessMonitor
{
private:
    HANDLE hProcess;
    DWORD processId;
    bool monitoring;
    std::vector<MemorySnapshot> snapshots;
    std::map<UINT_PTR, std::vector<unsigned char>> lastKnownState;

public:
    AdvancedProcessMonitor() : hProcess(nullptr), processId(0), monitoring(false) {}

    ~AdvancedProcessMonitor()
    {
        StopMonitoring();
        if (hProcess) CloseHandle(hProcess);
    }

    bool Open(DWORD pid)
    {
        hProcess = OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, FALSE, pid);
        if (!hProcess) return false;
        
        processId = pid;
        return true;
    }

    /**
     * Lê múltiplas regiões de memória sequencialmente
     * Estrutura: { endereço, tamanho }
     */
    bool ReadMultipleRegions(const std::vector<std::pair<UINT_PTR, SIZE_T>>& regions)
    {
        for (const auto& region : regions)
        {
            std::vector<unsigned char> buffer(region.second);
            SIZE_T bytesRead = 0;

            BOOL success = ::ReadProcessMemory(
                hProcess,
                (LPCVOID)region.first,
                buffer.data(),
                region.second,
                &bytesRead
            );

            if (!success || bytesRead == 0)
            {
                std::cout << "Falha ao ler 0x" << std::hex << region.first << std::dec << std::endl;
                return false;
            }

            snapshots.emplace_back(region.first, bytesRead);
            snapshots.back().data = buffer;
        }

        return true;
    }

    /**
     * Detecta mudanças entre snapshots
     * Retorna vetor de (endereço, offset, valor_antigo, valor_novo)
     */
    struct MemoryChange
    {
        UINT_PTR address;
        SIZE_T offset;
        unsigned char oldValue;
        unsigned char newValue;
    };

    std::vector<MemoryChange> DetectChanges(const MemorySnapshot& oldSnapshot, 
                                            const MemorySnapshot& newSnapshot)
    {
        std::vector<MemoryChange> changes;

        if (oldSnapshot.address != newSnapshot.address)
            return changes; // Endereços diferentes, não comparar

        SIZE_T compareSize = std::min(oldSnapshot.size, newSnapshot.size);

        for (SIZE_T i = 0; i < compareSize; i++)
        {
            if (oldSnapshot.data[i] != newSnapshot.data[i])
            {
                changes.push_back({
                    oldSnapshot.address + i,
                    i,
                    oldSnapshot.data[i],
                    newSnapshot.data[i]
                });
            }
        }

        return changes;
    }

    /**
     * Monitora endereço específico continuamente
     * interval_ms: intervalo entre leituras em milissegundos
     */
    void StartContinuousMonitoring(UINT_PTR targetAddress, SIZE_T regionSize, 
                                   unsigned int interval_ms, unsigned int durationSeconds)
    {
        monitoring = true;
        std::vector<unsigned char> buffer(regionSize);
        auto startTime = std::chrono::steady_clock::now();

        std::cout << "[Monitor] Iniciando monitoramento de 0x" << std::hex << targetAddress 
                  << std::dec << " por " << durationSeconds << " segundos" << std::endl;

        int iteracao = 0;
        while (monitoring && std::chrono::steady_clock::now() - startTime < 
               std::chrono::seconds(durationSeconds))
        {
            SIZE_T bytesRead = 0;
            BOOL success = ::ReadProcessMemory(
                hProcess,
                (LPCVOID)targetAddress,
                buffer.data(),
                regionSize,
                &bytesRead
            );

            if (success && bytesRead > 0)
            {
                // Detectar mudanças comparado ao estado anterior
                auto it = lastKnownState.find(targetAddress);
                if (it != lastKnownState.end())
                {
                    std::vector<MemoryChange> changes;
                    for (SIZE_T i = 0; i < bytesRead && i < it->second.size(); i++)
                    {
                        if (buffer[i] != it->second[i])
                        {
                            changes.push_back({
                                targetAddress + i, i,
                                it->second[i], buffer[i]
                            });
                        }
                    }

                    if (!changes.empty())
                    {
                        std::cout << "[Iter " << iteracao << "] " << changes.size() 
                                  << " mudanças detectadas:" << std::endl;
                        for (const auto& change : changes)
                        {
                            std::cout << "  0x" << std::hex << change.address << std::dec
                                      << ": 0x" << std::hex << (int)change.oldValue 
                                      << " -> 0x" << (int)change.newValue << std::endl;
                        }
                    }
                }

                lastKnownState[targetAddress] = buffer;
            }

            iteracao++;
            std::this_thread::sleep_for(std::chrono::milliseconds(interval_ms));
        }

        monitoring = false;
        std::cout << "[Monitor] Monitoramento concluído após " << iteracao << " iterações" << std::endl;
    }

    void StopMonitoring()
    {
        monitoring = false;
    }

    /**
     * Análise de padrão de acesso de memória
     * Calcula estatísticas de leitura
     */
    struct MemoryStats
    {
        SIZE_T totalBytes;
        SIZE_T unchangedBytes;
        float changePercentage;
        std::chrono::milliseconds readTime;
    };

    MemoryStats AnalyzeMemoryRegion(UINT_PTR address, SIZE_T size, unsigned int samples)
    {
        MemoryStats stats = { 0, 0, 0.0f, std::chrono::milliseconds(0) };
        std::vector<unsigned char> baseline(size);
        std::vector<unsigned char> current(size);
        SIZE_T bytesRead = 0;

        // Ler baseline
        auto startTime = std::chrono::high_resolution_clock::now();
        ::ReadProcessMemory(hProcess, (LPCVOID)address, baseline.data(), size, &bytesRead);
        auto endTime = std::chrono::high_resolution_clock::now();

        stats.readTime = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime);
        stats.totalBytes = bytesRead;

        // Fazer múltiplas amostras e medir variações
        SIZE_T totalUnchanged = 0;
        for (unsigned int i = 0; i < samples; i++)
        {
            ::ReadProcessMemory(hProcess, (LPCVOID)address, current.data(), size, &bytesRead);
            
            SIZE_T unchangedCount = 0;
            for (SIZE_T j = 0; j < std::min(baseline.size(), current.size()); j++)
            {
                if (baseline[j] == current[j])
                    unchangedCount++;
            }
            totalUnchanged += unchangedCount;
        }

        stats.unchangedBytes = totalUnchanged / samples;
        stats.changePercentage = ((float)(stats.totalBytes - stats.unchangedBytes) / stats.totalBytes) * 100.0f;

        return stats;
    }

    /**
     * Comparação de dois snapshots com relatório detalhado
     */
    void CompareSnapshots(const MemorySnapshot& snap1, const MemorySnapshot& snap2)
    {
        if (snap1.address != snap2.address || snap1.size != snap2.size)
        {
            std::cout << "Snapshots incompatíveis para comparação" << std::endl;
            return;
        }

        auto changes = DetectChanges(snap1, snap2);
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(
            snap2.timestamp - snap1.timestamp
        );

        std::cout << "\n=== Relatório de Comparação ===" << std::endl;
        std::cout << "Endereço: 0x" << std::hex << snap1.address << std::dec << std::endl;
        std::cout << "Tamanho: " << snap1.size << " bytes" << std::endl;
        std::cout << "Tempo decorrido: " << duration.count() << " ms" << std::endl;
        std::cout << "Mudanças detectadas: " << changes.size() << std::endl;

        if (!changes.empty())
        {
            std::cout << "\nPrimeiras 10 mudanças:" << std::endl;
            for (size_t i = 0; i < std::min(size_t(10), changes.size()); i++)
            {
                const auto& change = changes[i];
                std::cout << "  [" << i << "] Offset 0x" << std::hex << change.offset 
                          << ": " << std::dec << (int)change.oldValue 
                          << " -> " << (int)change.newValue << std::endl;
            }
        }
    }
};

// ============================================================================
// EXEMPLO: Monitoramento em Tempo Real
// ============================================================================

int main()
{
    std::cout << "=== AdvancedProcessMonitor - Exemplo de Uso ===" << std::endl << std::endl;

    AdvancedProcessMonitor monitor;
    DWORD targetPID = 1234; // Substitua pelo PID real

    if (!monitor.Open(targetPID))
    {
        std::cerr << "Falha ao abrir processo" << std::endl;
        return 1;
    }

    // Exemplo 1: Ler múltiplas regiões
    {
        std::cout << "[Exemplo 1] Leitura de múltiplas regiões" << std::endl;
        
        std::vector<std::pair<UINT_PTR, SIZE_T>> regions = {
            { 0x400000, 256 },   // Seção .text
            { 0x600000, 512 },   // Seção .data
            { 0x700000, 128 }    // Seção .rdata
        };

        if (monitor.ReadMultipleRegions(regions))
        {
            std::cout << "Leitura bem-sucedida de " << regions.size() << " regiões" << std::endl;
        }
    }

    std::cout << std::endl;

    // Exemplo 2: Análise de memória
    {
        std::cout << "[Exemplo 2] Análise de região de memória" << std::endl;
        
        auto stats = monitor.AnalyzeMemoryRegion(0x400000, 4096, 5);
        std::cout << "Bytes totais: " << stats.totalBytes << std::endl;
        std::cout << "Bytes inalterados: " << stats.unchangedBytes << std::endl;
        std::cout << "Percentual de mudança: " << stats.changePercentage << "%" << std::endl;
        std::cout << "Tempo de leitura: " << stats.readTime.count() << " ms" << std::endl;
    }

    std::cout << std::endl;

    // Exemplo 3: Monitoramento contínuo em thread separada
    {
        std::cout << "[Exemplo 3] Monitoramento contínuo (10 segundos)" << std::endl;
        
        std::thread monitorThread(&AdvancedProcessMonitor::StartContinuousMonitoring,
                                  &monitor, 0x400000, 256, 500, 10);
        
        monitorThread.join();
    }

    return 0;
}
