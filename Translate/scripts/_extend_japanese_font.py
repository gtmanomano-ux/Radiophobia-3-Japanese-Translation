import argparse
import html
import json
import math
import re
import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
TRANSLATE = ROOT / "Translate"
ATLAS = ROOT / "gamedata/textures/ui/ui_font_jpn.dds"
MAP = ROOT / "gamedata/textures/ui/ui_font_jpn.ini"
MANIFEST = TRANSLATE / "packets/manifest.json"
CAPTION = ROOT / "gamedata/config/text/jpn/stable_closecaption.xml"
FONT = Path(r"C:\Windows\Fonts\YuGothM.ttc")
DRAFT = TRANSLATE / "subtitles/stable_closecaption.json"
CELL_WIDTH = 22
CELL_HEIGHT = 24
STEP_X = 24
STEP_Y = 24
START_X = 5


def required_characters():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    paths = {Path(table["jpn_file"]) for table in manifest["tables"].values()}
    paths.add(CAPTION)
    result = set()
    for path in paths:
        document = path.read_text(encoding="utf-8")
        for value in re.findall(r"<text(?:\s+[^>]*)?>(.*?)</text>", document, re.S):
            result.update(char for char in html.unescape(value) if ord(char) > 127)
    result.update(char for item in json.loads(DRAFT.read_text(encoding="utf-8")) for char in item["ja"] if ord(char) > 127)
    return result


def stage():
    old_map = MAP.read_bytes()
    map_text = old_map.decode("ascii")
    current = {int(value) for value in re.findall(r"^([0-9]{5})\s*=", map_text, re.M)}
    existing_rows = [int(value) for value in re.findall(r"^[0-9]{5}\s*=\s*[0-9]+,\s*([0-9]+),", map_text, re.M)]
    start_y = max(existing_rows) + CELL_HEIGHT
    missing = sorted(required_characters() - {chr(code) for code in current}, key=ord)
    source = ATLAS.read_bytes()
    if source[:4] != b"DDS " or len(source) != 128 + 2048 * 1024 * 4:
        raise ValueError("想定したDDS形式ではありません")
    width = int.from_bytes(source[16:20], "little")
    height = int.from_bytes(source[12:16], "little")
    if (width, height) != (2048, 1024):
        raise ValueError((width, height))
    columns = (width - START_X - CELL_WIDTH) // STEP_X + 1
    if start_y + math.ceil(len(missing) / columns) * STEP_Y > height:
        raise ValueError("追加文字がDDSに収まりません")
    target = bytearray(source)
    font = ImageFont.truetype(str(FONT), 20, index=0)
    lines = []
    for index, char in enumerate(missing):
        left = START_X + (index % columns) * STEP_X
        top = start_y + (index // columns) * STEP_Y
        if any(target[128 + (y * width + x) * 4 + channel] for y in range(top, top + CELL_HEIGHT) for x in range(left, left + CELL_WIDTH) for channel in range(4)):
            raise ValueError(f"追加領域が空ではありません: {left}, {top}")
        cell = Image.new("L", (CELL_WIDTH, CELL_HEIGHT))
        if char != "\u2007":
            ImageDraw.Draw(cell).text((0, 3), char, font=font, fill=255)
            if not cell.getbbox():
                raise ValueError(f"字形を生成できません: {char}")
        ink_width = cell.getbbox()[2] if cell.getbbox() else 0
        advance = math.ceil(font.getlength(char))
        extent = min(CELL_WIDTH, max(ink_width, advance, 1))
        for y in range(CELL_HEIGHT):
            for x in range(CELL_WIDTH):
                value = cell.getpixel((x, y))
                offset = 128 + ((top + y) * width + left + x) * 4
                target[offset : offset + 4] = bytes((value, value, value, value))
        lines.append(f"{ord(char):05d} = {left}, {top}, {left + extent - 1}\r\n")
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = TRANSLATE / "backups" / f"font_extend_{now}"
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ATLAS, folder / "original_ui_font_jpn.dds")
    shutil.copy2(MAP, folder / "original_ui_font_jpn.ini")
    (folder / "ui_font_jpn.dds").write_bytes(target)
    (folder / "ui_font_jpn.ini").write_bytes(old_map + "".join(lines).encode("ascii"))
    (folder / "added_characters.txt").write_text("".join(missing), encoding="utf-8")
    print(f"stage={folder} added={len(missing)} rows={math.ceil(len(missing) / columns)}")


def install(folder):
    source_atlas = folder / "ui_font_jpn.dds"
    source_map = folder / "ui_font_jpn.ini"
    if not source_atlas.exists() or not source_map.exists():
        raise ValueError("候補ファイルがありません")
    current = MAP.read_bytes()
    original = (folder / "original_ui_font_jpn.ini").read_bytes()
    if current != original:
        raise ValueError("フォントINIが候補作成後に変わりました")
    if ATLAS.read_bytes() != (folder / "original_ui_font_jpn.dds").read_bytes():
        raise ValueError("フォントDDSが候補作成後に変わりました")
    shutil.copy2(source_atlas, ATLAS)
    shutil.copy2(source_map, MAP)
    print(f"installed={folder}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["stage", "install"])
    parser.add_argument("folder", nargs="?")
    args = parser.parse_args()
    if args.command == "stage":
        stage()
    else:
        if not args.folder:
            raise ValueError("候補フォルダを指定してください")
        install(Path(args.folder))
