cmake_minimum_required(VERSION 3.10)
project(ProcessMemoryTools LANGUAGES CXX)

# Configurar padrão C++
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Variáveis de configuração
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

# ============================================================================
# Alvo 1: ProcessMemoryReader (Exemplo básico)
# ============================================================================
add_executable(ProcessMemoryReader 
    ProcessMemoryReader.cpp
)

target_link_libraries(ProcessMemoryReader PRIVATE
    kernel32
    advapi32
)

# Configurações específicas do MSVC
if(MSVC)
    target_compile_options(ProcessMemoryReader PRIVATE
        /W4           # Nível 4 de warnings
        /WX           # Tratar warnings como erros
        /EHsc         # Exception handling
        /D_CRT_SECURE_NO_WARNINGS
    )
    set_target_properties(ProcessMemoryReader PROPERTIES
        VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}"
    )
endif()

# ============================================================================
# Alvo 2: ProcessMemoryScanner (Classe wrapper com pattern scanning)
# ============================================================================
add_executable(ProcessMemoryScanner
    ProcessMemoryScanner.cpp
)

target_link_libraries(ProcessMemoryScanner PRIVATE
    kernel32
    advapi32
)

if(MSVC)
    target_compile_options(ProcessMemoryScanner PRIVATE
        /W4 /WX /EHsc /D_CRT_SECURE_NO_WARNINGS
    )
    set_target_properties(ProcessMemoryScanner PROPERTIES
        VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}"
    )
endif()

# ============================================================================
# Alvo 3: AdvancedProcessMonitor (Monitoramento contínuo)
# ============================================================================
add_executable(AdvancedProcessMonitor
    AdvancedProcessMonitor.cpp
)

target_link_libraries(AdvancedProcessMonitor PRIVATE
    kernel32
    advapi32
)

if(MSVC)
    target_compile_options(AdvancedProcessMonitor PRIVATE
        /W4 /WX /EHsc /D_CRT_SECURE_NO_WARNINGS
    )
    set_target_properties(AdvancedProcessMonitor PROPERTIES
        VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}"
    )
endif()

# ============================================================================
# Configuração geral de plataforma
# ============================================================================

# Garantir que estamos compilando para Windows
if(NOT WIN32)
    message(FATAL_ERROR "Este projeto requer Windows (WIN32)")
endif()

# Definir macro para Windows
add_definitions(-D_WINDOWS -D_WIN64)

# ============================================================================
# Instalação
# ============================================================================

install(TARGETS 
    ProcessMemoryReader
    ProcessMemoryScanner
    AdvancedProcessMonitor
    RUNTIME DESTINATION bin
)

install(FILES
    MEMORIA_DOCUMENTACAO.md
    BUILD_INSTRUCTIONS.md
    DESTINATION docs
)

# ============================================================================
# Sumário
# ============================================================================

message(STATUS "")
message(STATUS "=== BuildConfiguration ===")
message(STATUS "CMake Version: ${CMAKE_VERSION}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Generator: ${CMAKE_GENERATOR}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Output Directory: ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")
message(STATUS "")
message(STATUS "Targets:")
message(STATUS "  - ProcessMemoryReader (Basic example)")
message(STATUS "  - ProcessMemoryScanner (Class wrapper with pattern scanning)")
message(STATUS "  - AdvancedProcessMonitor (Continuous monitoring)")
message(STATUS "")
