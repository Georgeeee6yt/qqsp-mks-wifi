# QQ-S Pro: MKS Wi-Fi module firmware + web page

Source: makerbase-mks/MKS-WIFI `firmware_source/MksWifi` at commit 39b8053 (version string C1.0.4_201109_beta;
the module shipped with CS1.0.4_200227, whose source is not published: same protocol, plus the MKS cloud code).
First commit = the published source unchanged; later commits = QQS-Pro changes (see `git log`).

## QQS-Pro changes
- `/` serves `index.htm` from SPIFFS when it exists, else the built-in MKS page. The built-in page stays at
  `/config.htm` (and `/update_sketch`, `/update_spiffs`), so a broken page can always be replaced from a browser.
- `GET /scan`: JSON list of networks (one per name, strongest first). In hotspot mode the scan runs with AP+STA,
  so the phone that asked stays connected. (The UART scan used by the printer is unchanged.)
- `GET /status`: version, mode, SSID, IP, RSSI, MAC, printing / busy. No password.
- `/update_cfg`: arguments were URL-decoded twice (the server already decodes): "+" in a password became a space.
- Version string `QQS1.0_251125`. UART protocol to the board unchanged.
- `data/index.htm`: the page (G-code upload with progress to `/upload?X-Filename=`, Wi-Fi scan / connect / hotspot).

## Build (PlatformIO)
1. MKS core: `git clone https://github.com/makerbase-mks/Esp8266-Core-For-Arduino /tmp/mksrc/mkscore`, add a
   `package.json` (`{"name":"framework-arduinoespressif8266","version":"2.4.0"}`) and copy `tools/platformio-build.py`
   from the official PlatformIO package `platformio/framework-arduinoespressif8266@1.20400.3` into its `tools/`.
2. `pio run` -> `.pio/build/mks/firmware.bin` (= MksWifi.bin). `flags.py` adds the MKS platform.txt flags
   (gnu99 / gnu++11, -U__STRICT_ANSI__, -mlongcalls, link flags). Platform espressif8266@1.8.0 (gcc 4.8.2).
3. `pio run -t buildfs` -> `.pio/build/mks/spiffs.bin` (= MksWifi_WebView.bin, 3,125,248 bytes, block 8 KB,
   page 256; mkspiffs 0.2.0: the empty-block magic matches what the module itself formatted).
- The first 4 KB (eboot) of the build is byte-identical to MKS's release.
- Test the page without the module: `python3 tools/mock.py data log.jsonl` (port 8765).
