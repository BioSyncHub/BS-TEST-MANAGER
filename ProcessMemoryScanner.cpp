#include <windows.h>
#include <iostream>
#include <string>
#include <vector>
#include <cstring>

/**
 * ProcessMemoryScanner - Classe wrapper para leitura segura de memória de processos
 * 
 * Funcionalidades:
 *  - Abertura segura de processos com verificação de privilégios
 *  - Leitura de blocos de memória com tratamento de erros
 *  - Varredura em padrão de bytes com máscara (pattern scanning)
 *  - Logging de operações
 */

class ProcessMemoryScanner
{
private:
    HANDLE hProcess;
    DWORD processId;
    bool isOpen;
    std::string lastError;

public:
    ProcessMemoryScanner() : hProcess(nullptr), processId(0), isOpen(false) {}

    ~ProcessMemoryScanner()
    {
        Close();
    }

    /**
     * Abre um processo para leitura de memória
     * Requer PROCESS_VM_READ e opcionalmente PROCESS_QUERY_INFORMATION
     */
    bool Open(DWORD pid)
    {
        if (isOpen)
        {
            lastError = "Processo já está aberto. Feche antes de abrir outro.";
            return false;
        }

        processId = pid;

        // Tentar abrir com as permissões necessárias
        hProcess = OpenProcess(
            PROCESS_VM_READ | PROCESS_QUERY_INFORMATION,
            FALSE,
            pid
        );

        if (hProcess == nullptr)
        {
            DWORD dwError = GetLastError();
            lastError = GetErrorDescription(dwError);
            return false;
        }

        isOpen = true;
        return true;
    }

    /**
     * Fecha o handle do processo
     */
    void Close()
    {
        if (hProcess != nullptr)
        {
            CloseHandle(hProcess);
            hProcess = nullptr;
        }
        isOpen = false;
    }

    /**
     * Lê um bloco de memória do processo aberto
     */
    bool Read(UINT_PTR address, std::vector<unsigned char>& buffer, SIZE_T size)
    {
        if (!isOpen)
        {
            lastError = "Nenhum processo aberto.";
            return false;
        }

        if (size == 0)
        {
            lastError = "Tamanho de leitura deve ser maior que zero.";
            return false;
        }

        buffer.resize(size);
        SIZE_T bytesRead = 0;

        BOOL success = ::ReadProcessMemory(
            hProcess,
            (LPCVOID)address,
            buffer.data(),
            size,
            &bytesRead
        );

        if (!success)
        {
            DWORD dwError = GetLastError();
            lastError = "ReadProcessMemory falhou: " + GetErrorDescription(dwError);
            
            // Redimensionar buffer para quantidade realmente lida
            buffer.resize(bytesRead);
            
            // Se bytesRead = 0, a leitura falhou completamente
            return false;
        }

        // Se menos bytes foram lidos que o solicitado, redimensionar
        if (bytesRead < size)
        {
            buffer.resize(bytesRead);
        }

        return true;
    }

    /**
     * Lê um valor genérico de um endereço (template)
     */
    template<typename T>
    bool ReadValue(UINT_PTR address, T& outValue)
    {
        std::vector<unsigned char> buffer;
        if (!Read(address, buffer, sizeof(T)))
            return false;

        if (buffer.size() < sizeof(T))
        {
            lastError = "Tamanho de buffer insuficiente.";
            return false;
        }

        std::memcpy(&outValue, buffer.data(), sizeof(T));
        return true;
    }

    /**
     * Lê uma string terminada em null
     */
    bool ReadString(UINT_PTR address, std::string& outString, SIZE_T maxLength = 256)
    {
        std::vector<unsigned char> buffer;
        if (!Read(address, buffer, maxLength))
            return false;

        // Encontrar terminador null
        auto nullPos = std::find(buffer.begin(), buffer.end(), '\0');
        if (nullPos == buffer.end())
        {
            outString = std::string(buffer.begin(), buffer.end());
        }
        else
        {
            outString = std::string(buffer.begin(), nullPos);
        }

        return true;
    }

    /**
     * Pattern scanning: busca por um padrão de bytes com máscara
     * pattern: bytes a buscar
     * mask: máscara (x = comparar, ? = ignorar)
     * startAddress, endAddress: range de busca
     * Retorna o endereço encontrado ou 0 se não encontrado
     */
    UINT_PTR ScanPattern(
        const std::vector<unsigned char>& pattern,
        const std::string& mask,
        UINT_PTR startAddress,
        UINT_PTR endAddress,
        SIZE_T chunkSize = 4096)
    {
        if (pattern.empty() || mask.empty() || pattern.size() != mask.size())
        {
            lastError = "Pattern ou mask inválida.";
            return 0;
        }

        std::vector<unsigned char> buffer(chunkSize);
        SIZE_T patternSize = pattern.size();

        // Ler em chunks e buscar padrão
        for (UINT_PTR currentAddr = startAddress; currentAddr < endAddress; currentAddr += chunkSize)
        {
            SIZE_T readSize = std::min(chunkSize, static_cast<SIZE_T>(endAddress - currentAddr));

            if (!Read(currentAddr, buffer, readSize))
                continue;

            // Comparar padrão dentro do chunk
            for (SIZE_T i = 0; i + patternSize <= buffer.size(); i++)
            {
                bool match = true;
                for (SIZE_T j = 0; j < patternSize; j++)
                {
                    if (mask[j] == 'x' && pattern[j] != buffer[i + j])
                    {
                        match = false;
                        break;
                    }
                }

                if (match)
                    return currentAddr + i;
            }
        }

        return 0;
    }

    // Getters
    bool IsOpen() const { return isOpen; }
    DWORD GetProcessId() const { return processId; }
    std::string GetLastError() const { return lastError; }

private:
    /**
     * Converte código de erro do Windows em mensagem descritiva
     */
    std::string GetErrorDescription(DWORD dwError)
    {
        LPVOID lpMsgBuf = nullptr;
        FormatMessageA(
            FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
            nullptr,
            dwError,
            MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
            (LPSTR)&lpMsgBuf,
            0,
            nullptr
        );

        std::string result;
        if (lpMsgBuf)
        {
            result = std::string((LPSTR)lpMsgBuf);
            LocalFree(lpMsgBuf);
        }
        else
        {
            result = "Erro desconhecido (0x" + std::to_string(dwError) + ")";
        }

        return result;
    }
};

// ============================================================================
// EXEMPLOS DE USO
// ============================================================================

int main()
{
    std::cout << "=== ProcessMemoryScanner - Exemplo de Uso ===" << std::endl << std::endl;

    // Exemplo 1: Leitura simples de memória
    {
        std::cout << "[Exemplo 1] Leitura simples de memória" << std::endl;
        
        ProcessMemoryScanner scanner;
        DWORD targetPID = 1234; // Substitua pelo PID real

        if (!scanner.Open(targetPID))
        {
            std::cout << "Erro ao abrir processo: " << scanner.GetLastError() << std::endl;
        }
        else
        {
            std::vector<unsigned char> buffer;
            if (scanner.Read(0x400000, buffer, 32))
            {
                std::cout << "Leitura bem-sucedida! Bytes lidos: " << buffer.size() << std::endl;
                std::cout << "Dados (hex): ";
                for (auto byte : buffer)
                    printf("%02X ", byte);
                std::cout << std::endl;
            }
            else
            {
                std::cout << "Erro: " << scanner.GetLastError() << std::endl;
            }
        }
    }

    std::cout << std::endl;

    // Exemplo 2: Leitura de valores tipados
    {
        std::cout << "[Exemplo 2] Leitura de valores tipados (int32, float)" << std::endl;
        
        ProcessMemoryScanner scanner;
        DWORD targetPID = 1234;

        if (scanner.Open(targetPID))
        {
            int32_t intValue;
            float floatValue;

            if (scanner.ReadValue<int32_t>(0x400000, intValue))
            {
                std::cout << "Valor int32 @ 0x400000: " << intValue << std::endl;
            }

            if (scanner.ReadValue<float>(0x400004, floatValue))
            {
                std::cout << "Valor float @ 0x400004: " << floatValue << std::endl;
            }
        }
    }

    std::cout << std::endl;

    // Exemplo 3: Pattern scanning
    {
        std::cout << "[Exemplo 3] Pattern scanning com máscara" << std::endl;
        
        ProcessMemoryScanner scanner;
        DWORD targetPID = 1234;

        if (scanner.Open(targetPID))
        {
            // Padrão: 55 8B EC ?? ?? (push rbp; mov rbp, rsp; ...)
            std::vector<unsigned char> pattern = { 0x55, 0x8B, 0xEC, 0x00, 0x00 };
            std::string mask = "xxx??";

            UINT_PTR found = scanner.ScanPattern(pattern, mask, 0x400000, 0x500000);
            if (found != 0)
            {
                std::cout << "Padrão encontrado em: 0x" << std::hex << found << std::dec << std::endl;
            }
            else
            {
                std::cout << "Padrão não encontrado no range especificado." << std::endl;
            }
        }
    }

    return 0;
}
