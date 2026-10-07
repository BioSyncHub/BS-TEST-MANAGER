#include <windows.h>
#include <iostream>
#include <string>
#include <vector>

// Estrutura para armazenar resultado da leitura
struct MemoryReadResult
{
    bool success;
    std::vector<unsigned char> data;
    std::string errorMessage;
    DWORD lastErrorCode;
};

// Função auxiliar para obter mensagem de erro do Windows
std::string GetWindowsErrorMessage(DWORD errorCode)
{
    LPVOID lpMsgBuf = nullptr;
    FormatMessageA(
        FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
        nullptr,
        errorCode,
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
    return result;
}

// Função principal para ler memória de um processo
// Parâmetros:
//   - processId: PID do processo alvo
//   - baseAddress: Endereço de memória a ser lido
//   - bytesToRead: Quantidade de bytes a ler
// Retorna: Estrutura MemoryReadResult com dados ou informações de erro
MemoryReadResult ReadProcessMemory(DWORD processId, UINT_PTR baseAddress, SIZE_T bytesToRead)
{
    MemoryReadResult result = { false, {}, "", 0 };

    // Validação de entrada
    if (processId == 0)
    {
        result.errorMessage = "Process ID inválido (0)";
        result.lastErrorCode = ERROR_INVALID_PARAMETER;
        return result;
    }

    if (bytesToRead == 0 || bytesToRead > 1024 * 1024) // Limite de 1MB para segurança
    {
        result.errorMessage = "Quantidade de bytes inválida (0 ou > 1MB)";
        result.lastErrorCode = ERROR_INVALID_PARAMETER;
        return result;
    }

    // Abrir processo com permissão de leitura de memória
    // PROCESS_VM_READ: Necessário para ler memória do processo
    // PROCESS_QUERY_INFORMATION: Necessário em alguns casos para obter informações do processo
    HANDLE hProcess = OpenProcess(
        PROCESS_VM_READ | PROCESS_QUERY_INFORMATION,
        FALSE, // Não herdar handle
        processId
    );

    if (hProcess == nullptr)
    {
        result.lastErrorCode = GetLastError();
        result.errorMessage = "Falha ao abrir processo. ";
        
        if (result.lastErrorCode == ERROR_ACCESS_DENIED)
        {
            result.errorMessage += "Acesso negado (privilégios insuficientes).";
        }
        else if (result.lastErrorCode == ERROR_INVALID_PARAMETER)
        {
            result.errorMessage += "Process ID não encontrado.";
        }
        else
        {
            result.errorMessage += GetWindowsErrorMessage(result.lastErrorCode);
        }

        return result;
    }

    // Alocar buffer para dados lidos
    std::vector<unsigned char> buffer(bytesToRead);

    // Variável para armazenar quantidade de bytes realmente lidos
    SIZE_T bytesRead = 0;

    // Ler memória do processo
    BOOL readSuccess = ::ReadProcessMemory(
        hProcess,
        (LPCVOID)baseAddress,
        buffer.data(),
        bytesToRead,
        &bytesRead
    );

    if (!readSuccess)
    {
        result.lastErrorCode = GetLastError();
        result.errorMessage = "Falha ao ler memória do processo. ";

        if (result.lastErrorCode == ERROR_PARTIAL_COPY)
        {
            result.errorMessage += "Leitura parcial (endereço parcialmente inválido).";
        }
        else if (result.lastErrorCode == ERROR_INVALID_PARAMETER)
        {
            result.errorMessage += "Endereço de memória inválido.";
        }
        else
        {
            result.errorMessage += GetWindowsErrorMessage(result.lastErrorCode);
        }

        CloseHandle(hProcess);
        return result;
    }

    // Se bytesRead for menor que bytesToRead, foi uma leitura parcial
    if (bytesRead < bytesToRead)
    {
        buffer.resize(bytesRead);
    }

    // Sucesso
    result.success = true;
    result.data = buffer;
    result.lastErrorCode = 0;

    // Fechar handle do processo
    CloseHandle(hProcess);

    return result;
}

// ============================================================================
// EXEMPLO DE USO
// ============================================================================

int main()
{
    // Exemplo 1: Ler 32 bytes do endereço 0x400000 do processo com PID 1234
    DWORD targetPID = 1234; // Substitua pelo PID real
    UINT_PTR targetAddress = 0x400000;
    SIZE_T bytesToRead = 32;

    std::cout << "Tentando ler memória do processo PID: " << targetPID << std::endl;
    std::cout << "Endereço: 0x" << std::hex << targetAddress << std::dec << std::endl;
    std::cout << "Bytes: " << bytesToRead << std::endl << std::endl;

    MemoryReadResult result = ReadProcessMemory(targetPID, targetAddress, bytesToRead);

    if (result.success)
    {
        std::cout << "[SUCESSO] Leitura concluída!" << std::endl;
        std::cout << "Bytes lidos: " << result.data.size() << std::endl;
        std::cout << "Dados (hex): ";

        for (unsigned char byte : result.data)
        {
            printf("%02X ", byte);
        }
        std::cout << std::endl;
    }
    else
    {
        std::cout << "[ERRO] Falha na leitura" << std::endl;
        std::cout << "Código de erro: " << result.lastErrorCode << std::endl;
        std::cout << "Mensagem: " << result.errorMessage << std::endl;
    }

    return 0;
}
