#!/usr/bin/env python3
"""複製 2026-08 KeySilk，把型號高半位元組 1 指到內建的 16鍵3旋鈕 畫面。

不修改來源 .app。不寫入 /Applications。來源執行檔必須是 8949704 位元組。
"""

import shutil
import subprocess
import sys
from pathlib import Path

EXPECTED_SIZE = 8_949_704
EXE_REL = Path("Contents/MacOS/keysilk")
DISPLAY_NAME = "KeySilk 16x3"
# rel32 以跳轉表基底計算，不是以該列位址計算。
# 表一基底 0x100018d44，case 1 改到 0x100011541。
# 表二基底 0x100018d94，case 1 改到 0x100014640。
SITES = (
    (0x18D48, bytes.fromhex("5f88ffff"), bytes.fromhex("fd87ffff")),
    (0x18D98, bytes.fromhex("6790ffff"), bytes.fromhex("acb8ffff")),
)


def die(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def patched_bytes(data: bytes) -> bytearray:
    if len(data) != EXPECTED_SIZE:
        die(f"執行檔大小是 {len(data)}。此腳本只接受 {EXPECTED_SIZE} 位元組的 2026-08 版。")
    blob = bytearray(data)
    for offset, original, updated in SITES:
        found = bytes(blob[offset : offset + 4])
        if found == updated:
            continue
        if found != original:
            die(
                f"偏移 0x{offset:x} 的位元組是 {found.hex()}。"
                "不是這個版本。腳本沒有寫出副本。"
            )
        blob[offset : offset + 4] = updated
    return blob


def main() -> None:
    if len(sys.argv) != 3:
        die('用法: python3 patch.py "<KeySilk Smart Keyboard.app>" "<輸出.app>"')

    src = Path(sys.argv[1]).expanduser().resolve()
    dst = Path(sys.argv[2]).expanduser().resolve()
    src_exe = src / EXE_REL
    if not src_exe.is_file():
        die(f"找不到 {src_exe}")
    if src == dst:
        die("來源與輸出是同一個路徑。請指定另一個輸出路徑。")
    applications = Path("/Applications").resolve()
    if dst == applications or applications in dst.parents:
        die("不要寫入 /Applications。請把輸出放在別的目錄。")
    if dst.exists():
        die(f"輸出已存在: {dst}。請換一個路徑。")

    blob = patched_bytes(src_exe.read_bytes())
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(["ditto", str(src), str(dst)], check=True)
        (dst / EXE_REL).write_bytes(blob)
        plist = dst / "Contents/Info.plist"
        for key in ("CFBundleName", "CFBundleDisplayName"):
            subprocess.run(
                ["plutil", "-replace", key, "-string", DISPLAY_NAME, str(plist)],
                check=True,
            )
        subprocess.run(["xattr", "-cr", str(dst)], check=True)
        subprocess.run(
            ["codesign", "--force", "--deep", "--sign", "-", str(dst)],
            check=True,
        )
    except subprocess.CalledProcessError as error:
        shutil.rmtree(dst, ignore_errors=True)
        die(f"命令失敗: {error.cmd[0]}。已刪除不完整的輸出。")

    signed = (dst / EXE_REL).read_bytes()
    for offset, _original, updated in SITES:
        found = signed[offset : offset + 4]
        if found != updated:
            shutil.rmtree(dst, ignore_errors=True)
            die(f"簽章後偏移 0x{offset:x} 不是 {updated.hex()}。已刪除輸出。")

    print(dst)
    print("在確認畫面是 16 個鍵與 3 個旋鈕之前，不要按「下載至裝置」。")


if __name__ == "__main__":
    main()
