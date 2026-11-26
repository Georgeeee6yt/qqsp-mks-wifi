# QQ-S Pro MKS Wi-Fi 韌體 — 版本對照

這個 repo 的版本標籤無法從推送環境建立，各版對應的 commit 列在這裡。

| 版本 | commit | 說明 |
|---|---|---|
| QQS1.3 | [`270f574`](https://github.com/Georgeeee6yt/qqsp-mks-wifi/commit/270f574c7e8f4196b04b31979fd7645c29bd34c2) | QQS1.3: free the SD list after /files hands it out; heap low-water mark |
| QQS1.2 | [`35874c0`](https://github.com/Georgeeee6yt/qqsp-mks-wifi/commit/35874c07c2c7127f3fdea868d395bbf799761abd) | QQS1.2: SD card list and starting a print from the web page |
| QQS1.1 | [`1502186`](https://github.com/Georgeeee6yt/qqsp-mks-wifi/commit/15021862eb740ed0e4045b4de1a4a279aabd3784) | QQS1.1: printer card on the web page (M2012 status, animations) |
| QQS1.0 | [`c7e9f4d`](https://github.com/Georgeeee6yt/qqsp-mks-wifi/commit/c7e9f4d4b663a014365ee9ddd9acce3a8349402a) | QQS-Pro web page (upload, Wi-Fi scan / connect / hotspot), README, mock server for testing |

## 在本機補上標籤

```sh
git tag QQS1.0 c7e9f4d4b663a014365ee9ddd9acce3a8349402a
git tag QQS1.1 15021862eb740ed0e4045b4de1a4a279aabd3784
git tag QQS1.2 35874c07c2c7127f3fdea868d395bbf799761abd
git tag QQS1.3 270f574c7e8f4196b04b31979fd7645c29bd34c2
git push origin --tags
```
