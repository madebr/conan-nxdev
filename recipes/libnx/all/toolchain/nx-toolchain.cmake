cmake_minimum_required(VERSION 3.7)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}")

set(CMAKE_SYSTEM_NAME "Nintendo Switch")
set(CMAKE_SYSTEM_PROCESSOR "aarch64")

if(NOT DEVKITPRO)
    set(DEVKITPRO $ENV{DEVKITPRO})
endif()
if(NOT DEVKITPRO)
    message(FATAL_ERROR "DEVKITPRO (environment) variable not set")
endif()

if(NOT LIBNX)
    set(LIBNX $ENV{LIBNX})
endif()
if(NOT LIBNX)
    message(FATAL_ERROR "LIBNX (environment) variable not set")
endif()

set(tools "${DEVKITPRO}/bin/aarch64-none-elf-")

set(CMAKE_C_COMPILER "${tools}gcc")
set(CMAKE_CXX_COMPILER "${tools}g++")

set(SWITCH ON)
set(NINTENDOSWITCH ON)
set(NX ON)
