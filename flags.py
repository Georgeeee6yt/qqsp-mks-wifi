Import("env")
# MKS core platform.txt: C is gnu99, C++ is c++11 (+ -U__STRICT_ANSI__ so va_list stays visible)
env.Append(CFLAGS=["-std=gnu99", "-Wpointer-arith", "-Wno-implicit-function-declaration", "-fno-inline-functions"],
           CXXFLAGS=["-std=gnu++11", "-fno-exceptions", "-fno-rtti"],
           CCFLAGS=["-U__STRICT_ANSI__", "-D__ets__", "-DICACHE_FLASH", "-mlongcalls", "-mtext-section-literals",
                    "-falign-functions=4", "-ffunction-sections", "-fdata-sections", "-Os", "-w"])
env.Append(LINKFLAGS=["-nostdlib", "-Wl,--no-check-sections", "-u", "call_user_start", "-u", "_printf_float", "-u", "_scanf_float",
                      "-Wl,-static", "-Wl,--gc-sections", "-Os"])
