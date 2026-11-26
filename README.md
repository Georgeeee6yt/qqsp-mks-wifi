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
- Version string `QQS1.1_251125`.
- QQS1.1: the 5 s status poll also sends `M2012` (Marlin QQS v3.2.13+). Its reply lines `QQS s=… p=… …` and
  `QQSN <file name>` are kept (not passed on) and returned by `/status` as `pr`, `pn` and `age` (ms since the last
  `QQS` line, -1 = never: older board firmware). While a page asks for `/status` (last 30 s) the poll runs every 2 s.
- QQS1.3: the SD list JSON is freed once `/files` has handed it out (or timed out). QQS1.2 kept it (up to
  ~8 KB, and the page lists the root on every load); with a print running the heap got so low that new
  connections were closed unanswered (ERR_EMPTY_RESPONSE). `/status` also gives `hmin`, the lowest free heap
  `loop()` has seen since boot; the page shows both at the bottom.
- QQS1.2: the board's `QQS…` reply lines are taken in `transfer_msg_handle` before anything else (one line per
  packet, up to 1 KB, not passed on to TCP clients). `GET /files?go=1&d=<hex 8.3 path>` sends `M2013 H<hex>`;
  `GET /files` returns `{"st":"wait"|"ok"|"timeout"|"busy", "d", "code", "total", "got", "f":[[dir,size,"hex 8.3",
  "UTF-8 name"],…]}` (list kept up to ~8 KB, streamed). `GET /print?go=1&f=<hex 8.3 path>` sends `M2014 H<hex>`;
  `GET /print` returns `{"r":code,"ms":age}` (-1 = no answer yet). G-code to the board for these goes in the
  "important" queue so the status poll cannot overwrite it. `/status` also gives `heap`.
- QQS1.2: `RepRapWebServer::_prepareHeader` adds its no-cache headers only when the handler set no Cache-Control
  (in QQS1.1 the image cache header was overridden by them).
- QQS1.1: `.gif` served as `image/gif`, `.png` as `image/png`; images get `Cache-Control: max-age=86400`.
- `data/index.htm`: the page (printer card with the printer's animation, G-code upload with progress to
  `/upload?X-Filename=`, Wi-Fi scan / connect / hotspot).
- `data/*.gif`: `tools/gen_web_anim.py` (needs `~/qqsp/sim/animsim.py` and the printer art). `print` / `heat` /
  `pause` are the printer's 214 x 87 animation frames for those states, scaled 2 x nearest; `idle` is
  `tools/art/idle_sleep.png` at 428 x 174 with the three Z's lifted out and animated.

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
