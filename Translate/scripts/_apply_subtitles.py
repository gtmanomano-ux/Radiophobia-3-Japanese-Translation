import argparse
import html
import json
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
TRANSLATE = ROOT / "Translate"
ARCHIVE = TRANSLATE / "downloads/Radiophobia3.14Chinese.zip"
SOURCE = "gamedata/config/text/eng/stable_closecaption.xml"
CAPTIONS = ROOT / "gamedata/config/text/jpn/stable_closecaption.xml"
CREDITS = ROOT / "gamedata/config/text/jpn/stable_game_credits.xml"
DRAFT = TRANSLATE / "subtitles/stable_closecaption.json"
FONT_MAP = ROOT / "gamedata/textures/ui/ui_font_jpn.ini"


def source():
    with zipfile.ZipFile(ARCHIVE) as archive:
        raw = archive.read(SOURCE).decode("cp1251")
    entries = ET.fromstring("<root>" + raw + "</root>").findall("string")
    return raw, [(entry.attrib["id"], entry.findtext("text") or "") for entry in entries]


def draft():
    import argostranslate.translate

    _, entries = source()
    languages = {lang.code: lang for lang in argostranslate.translate.get_installed_languages()}
    translator = languages["en"].get_translation(languages["ja"])
    overrides = {
        "ui_mm_cc_captioning": "字幕",
        "ui_mm_cc_none": "オフ",
        "ui_mm_cc_speechonly": "オン",
        "cc_characters_voice-scenario-trader-trader_monolog1-1": "さて、マークド・ワン。お前を助けたのは俺だ。",
        "cc_characters_voice-scenario-trader-trader_monolog1-2": "慈善事業でやったわけじゃない。",
        "cc_characters_voice-scenario-trader-trader_monolog1-3": "俺の仕事をいくつか片づけろ。それで貸し借りなしだ。",
        "cc_characters_voice-scenario-trader-trader_monolog1-4": "記憶がどれだけ早く戻るか、見せてもらおう。",
        "cc_characters_voice-scenario-trader-trader_monolog1-5": "お前の事情も、こちらで調べてみる。",
        "cc_characters_voice-scenario-trader-trader_monolog1-6": "なぜストレロクを追うのかは知らん。",
        "cc_characters_voice-scenario-trader-trader_monolog1-7": "だがお前の勝手だ。殺したいなら、理由があるんだろう。",
        "cc_tutorial_1-1": "これがお前のPDAだ。\\nなかなか便利な代物だぞ。",
    }
    result = []
    for index, (key, english) in enumerate(entries, 1):
        if key in overrides:
            japanese = overrides[key]
        else:
            japanese = "\\n".join(translator.translate(part) if part.strip() else "" for part in english.split("\\n"))
        result.append({"id": key, "en": english, "ja": japanese})
        if index % 50 == 0:
            print(f"translated={index}/{len(entries)}", flush=True)
    DRAFT.parent.mkdir(parents=True, exist_ok=True)
    DRAFT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"draft={DRAFT} entries={len(result)}")


def apply():
    raw, entries = source()
    translated = json.loads(DRAFT.read_text(encoding="utf-8"))
    by_id = {entry["id"]: entry for entry in translated}
    if len(by_id) != len(entries) or set(by_id) != {key for key, _ in entries}:
        raise ValueError("字幕IDが原本と一致しません")
    for key, english in entries:
        if by_id[key]["en"] != english or (not by_id[key]["ja"].strip() and english != "blank"):
            raise ValueError(f"字幕の原文または訳文が不正です: {key}")
    font_keys = {int(value) for value in re.findall(r"^([0-9]{5})\s*=", FONT_MAP.read_text(encoding="ascii", errors="replace"), re.M)}
    missing = sorted({char for item in translated for char in item["ja"] if ord(char) > 127 and ord(char) not in font_keys})
    if missing:
        raise ValueError(f"日本語フォントにない文字: {missing}")
    pattern = re.compile(r'(<string\s+id="([^"]+)"\s*>(?:\s|<!--.*?-->)*<text>)(.*?)(</text>\s*</string>)', re.S)
    seen = []

    def replace(match):
        key = match.group(2)
        seen.append(key)
        japanese = by_id[key]["ja"]
        escaped = html.escape(japanese, quote=False)
        return match.group(1) + escaped + match.group(4)

    output = pattern.sub(replace, raw)
    if seen != [key for key, _ in entries]:
        raise ValueError(f"字幕XMLの並びまたは構造が一致しません: seen={len(seen)} expected={len(entries)} missing={list(set(by_id) - set(seen))[:20]}")
    ET.fromstring("<root>" + output + "</root>")
    current_credits = CREDITS.read_bytes()
    if b'encoding="windows-1251"' in current_credits[:100]:
        credits_text = current_credits.decode("cp1251")
        credits_text = re.sub(r"&#(\d+);", lambda match: chr(int(match.group(1))), credits_text)
        credits_text = credits_text.replace('encoding="windows-1251"', 'encoding="UTF-8"', 1)
    else:
        credits_text = current_credits.decode("utf-8")
    old = 'text\\eng\\stable_closecaption.xml'
    new = 'text\\jpn\\stable_closecaption.xml'
    if old not in credits_text and new not in credits_text:
        raise ValueError("字幕の読み込み先が見つかりません")
    new_credits = credits_text.replace(old, new).encode("utf-8")
    backup = TRANSLATE / "backups" / ("subtitle_apply_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    backup.mkdir(parents=True)
    shutil.copy2(CAPTIONS, backup / CAPTIONS.name)
    shutil.copy2(CREDITS, backup / CREDITS.name)
    CAPTIONS.write_bytes(output.encode("utf-8"))
    CREDITS.write_bytes(new_credits)
    print(f"applied={len(entries)} backup={backup}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["draft", "apply"])
    args = parser.parse_args()
    globals()[args.command]()
