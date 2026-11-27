Import("env")
# QQS1.5+: link our lwIP built with a smaller TCP_MSS (tools/lwip/liblwip_gcc.a, built by tools/lwip/build.sh) in place of the core's (1460).
# Same file name on purpose: the linker script puts "*liblwip_gcc.a:" code in flash (irom0) by name.
import os
env.Prepend(LIBPATH=[os.path.join(env.subst("$PROJECT_DIR"), "tools", "lwip")])
