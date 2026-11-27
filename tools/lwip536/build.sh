#!/bin/sh
# QQS1.5: the core's open-source lwIP 1.4 (tools/sdk/lwip/src of makerbase-mks/Esp8266-Core-For-Arduino)
# rebuilt with TCP_MSS=536 instead of 1460. Segments then fit a Tailscale tunnel (MTU 1280); with 1460 a
# phone reaching the module through a Tailscale subnet router got pages cut off half way (George 2026-11-27).
# usage: tools/lwip536/build.sh <mks core dir>   -> tools/lwip536/liblwip_gcc.a (same name as the core's: the linker script maps it to flash by name)
set -e
CORE=${1:-/tmp/mksrc/mkscore}
OUT=$(cd "$(dirname "$0")" && pwd)
TC=$(ls -d ~/.platformio/packages/toolchain-xtensa*/bin | head -1)
W=$(mktemp -d); cp -r "$CORE/tools/sdk/lwip" "$W/"
cd "$W/lwip/src"
make -s TOOLS_PATH="$TC/xtensa-lx106-elf-" SDK_PATH="$CORE/tools/sdk" LWIP_LIB=liblwip_gcc.a \
  BUILD_DEFINES="-D__ets__ -DICACHE_FLASH -U__STRICT_ANSI__ -DLWIP_OPEN_SRC -DTCP_MSS=536" all
cp liblwip_gcc.a "$OUT/"
