# KeySilk 16鍵3旋鈕修補

這個倉庫只有一支修補腳本。倉庫裡沒有 KeySilk 程式。

2026-08 版 KeySilk 把這台鍵盤的型號高半位元組 1 當成未知裝置。腳本複製該程式，把兩處跳轉改到程式內建的 16鍵3旋鈕 畫面。腳本只接受執行檔大小為 8949704 位元組的那一版。

## 限制

不要把 KeySilk 的 .app 放進這個倉庫。

在確認畫面是 16 個鍵與 3 個旋鈕之前，不要按「下載至裝置」。該按鈕會把畫面上的設定寫進鍵盤。

腳本只寫你指定的副本。腳本不改 `/Applications` 裡的程式。

## 用法

1. 從 KeySilk 下載 2026-08 的 Mac 版。檔名是 KeySilk Smart Keyboard。
2. 解壓縮，得到 `KeySilk Smart Keyboard.app`。
3. 執行下面的命令。

```sh
python3 patch.py "/path/to/KeySilk Smart Keyboard.app" "$HOME/Downloads/KeySilk-16x3.app"
```

4. 打開產生的 `KeySilk-16x3.app`。
5. 確認狀態列顯示 16鍵3旋鈕，畫面是 4×4 鍵與右側 3 個旋鈕。

## 腳本改了什麼

執行檔 `Contents/MacOS/keysilk` 有兩處：

1. 偏移 `0x18d48`：`5f88ffff` 改成 `fd87ffff`。這一處改顯示「鍵盤」。
2. 偏移 `0x18d98`：`6790ffff` 改成 `acb8ffff`。這一處改進入內建的 16鍵3旋鈕 畫面。

接著腳本清除擴充屬性，並用 ad-hoc 簽章。

位元組已經是修補後的值時，腳本仍會複製並簽章。大小或位元組不符時，腳本停止，不寫出副本。
