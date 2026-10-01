import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape


TRANSLATE = Path(__file__).resolve().parents[1]
GAME = TRANSLATE.parent
PACKETS = TRANSLATE / "packets"
MANIFEST = PACKETS / "manifest.json"
JPN = (GAME / "gamedata" / "config" / "text" / "jpn").resolve()
STRING = re.compile(r"<string\b(?P<attrs>[^>]*)>(?P<body>.*?)</string\s*>", re.DOTALL)
TEXT = re.compile(r"<text(?:\s+[^>]*)?>(?P<content>.*?)</text\s*>", re.DOTALL)
ID = re.compile(r"\bid\s*=\s*(['\"])(?P<value>.*?)\1", re.DOTALL)
DECL = re.compile(r"encoding\s*=\s*(['\"])(?P<value>[^'\"]+)\1", re.IGNORECASE)
NUMERIC_ENTITY = re.compile(r"&#(?:[0-9]+|x[0-9a-fA-F]+);")


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_packets(manifest):
    by_table = defaultdict(dict)
    packet_files = sorted(path for path in PACKETS.rglob("*.json") if path != MANIFEST)
    require(len(packet_files) == manifest["packet_count"], "Packet file count changed")
    total = 0
    pending = []
    separators = []
    for path in packet_files:
        packet = json.loads(path.read_text(encoding="utf-8"))
        entries = packet["entries"]
        require(len(entries) == packet["entry_count"], f"Entry count differs: {path}")
        for entry in entries:
            table = entry["source_table"]
            require(table in manifest["tables"], f"Unknown table: {table}")
            key = (entry["string_id"], int(entry["occurrence"]))
            require(key not in by_table[table], f"Duplicate packet entry: {table}:{key}")
            require(entry["key"] == f"{table}:{key[0]}#{key[1]}", f"Key differs: {entry['key']}")
            source = Path(entry["source_file"]).resolve()
            expected = Path(manifest["tables"][table]["jpn_file"]).resolve()
            require(source == expected, f"Source file differs: {entry['key']}")
            target = entry["JA_new"]
            require(isinstance(target, str) and target != "", f"Empty translation: {entry['key']}")
            if "［判読不能］" in target:
                pending.append((table, key))
            if target.strip() == "":
                require(entry["EN"].strip() == "" and target == entry["EN"], f"Changed separator: {entry['key']}")
                separators.append((table, key))
            by_table[table][key] = entry
            total += 1
    require(total == manifest["active_entry_count"], "Total packet entry count changed")
    for table, meta in manifest["tables"].items():
        require(len(by_table[table]) == meta["jpn_entry_count"], f"Table entry count differs: {table}")
    expected_pending = {("news_main_new_script_text", (f"news_main_new_{number}", 1)) for number in range(803, 813)}
    require(set(pending) == expected_pending, "Unreadable source set changed")
    require(len(separators) == 15, "Separator set changed")
    return by_table, pending, separators


def decode(raw, encoding):
    if encoding.lower() == "utf-8" and raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig"), True
    return raw.decode(encoding), False


def fix_document(text, table):
    suffix_fixed = False
    if table == "stable_dialogs_garbage" and text.endswith("</string_table>\r\nin"):
        text = text[:-2]
        suffix_fixed = True
    declaration = DECL.search(text[:200])
    require(declaration is not None, f"XML encoding declaration missing: {table}")
    header_fixed = declaration.group("value").lower() != "utf-8"
    if header_fixed:
        text = text[: declaration.start("value")] + "UTF-8" + text[declaration.end("value") :]
    return text, header_fixed, suffix_fixed


def mask_markup(text):
    pattern = re.compile(r"<!--.*?-->|<!\[CDATA\[.*?\]\]>", re.DOTALL)
    return pattern.sub(lambda match: " " * len(match.group()), text)


def string_spans(text, table):
    masked = mask_markup(text)
    spans = []
    counts = defaultdict(int)
    for match in STRING.finditer(masked):
        id_match = ID.search(match.group("attrs"))
        require(id_match is not None, f"String without id: {table}")
        string_id = id_match.group("value")
        counts[string_id] += 1
        key = (string_id, counts[string_id])
        text_matches = list(TEXT.finditer(match.group("body")))
        require(len(text_matches) == 1, f"Text element count differs: {table}:{key}")
        inner = text_matches[0]
        start = match.start("body") + inner.start("content")
        end = match.start("body") + inner.end("content")
        spans.append((key, start, end))
    return spans


def parsed_bytes(data, table):
    root = ET.fromstring(data)
    require(root.tag == "string_table", f"Unexpected root: {table}")
    parsed = []
    counts = defaultdict(int)
    for string in root.findall("string"):
        string_id = string.attrib["id"]
        counts[string_id] += 1
        node = string.find("text")
        require(node is not None and len(node) == 0, f"Unsupported text structure: {table}:{string_id}")
        parsed.append(((string_id, counts[string_id]), node.text or ""))
    return parsed


def parsed_strings(text, table):
    return parsed_bytes(text.encode("utf-8"), table)


def encode_content(value, old_raw, newline):
    require("\r" not in value, "Translation contains a raw carriage return")
    result = escape(value)
    if "&quot;" in old_raw:
        result = result.replace('"', "&quot;")
    if "&apos;" in old_raw:
        result = result.replace("'", "&apos;")
    for match in NUMERIC_ENTITY.finditer(old_raw):
        entity = match.group()
        codepoint = int(entity[3:-1], 16) if entity.startswith("&#x") else int(entity[2:-1])
        result = result.replace(chr(codepoint), entity)
    return result.replace("\n", newline)


def build_table(raw, table, meta, entries, source_encoding, check_current):
    text, bom = decode(raw, source_encoding)
    text, header_fixed, suffix_fixed = fix_document(text, table)
    spans = string_spans(text, table)
    parsed = parsed_strings(text, table)
    require([key for key, _, _ in spans] == [key for key, _ in parsed], f"XML lexical structure differs: {table}")
    require(len(parsed) == meta["jpn_entry_count"], f"XML entry count differs: {table}")
    require(set(entries) == {key for key, _ in parsed}, f"Packet/XML key set differs: {table}")
    newline = "\r\n" if "\r\n" in text else "\n"
    replacements = []
    applied = 0
    expected = []
    for (key, start, end), (_, current) in zip(spans, parsed):
        entry = entries[key]
        if check_current:
            require(current == entry["JA_current"],
                    f"Original text differs: {table}:{key} XML={current[:120]!r} packet={entry['JA_current'][:120]!r}")
        target = entry["JA_new"].replace("\r\n", "\n")
        require("\r" not in target, f"Translation contains a bare carriage return: {table}:{key}")
        hold = "［判読不能］" in target or target.strip() == ""
        if hold:
            expected.append((key, current))
            continue
        expected.append((key, target))
        if current != target:
            replacements.append((start, end, encode_content(target, text[start:end], newline)))
            applied += 1
    if replacements:
        pieces = []
        cursor = 0
        for start, end, replacement in replacements:
            pieces.extend((text[cursor:start], replacement))
            cursor = end
        pieces.append(text[cursor:])
        text = "".join(pieces)
    verified = parsed_strings(text, table)
    require(verified == expected, f"Applied text differs after XML parsing: {table}")
    if table == "stable_game_credits":
        declaration = DECL.search(text[:200])
        require(declaration is not None, "Credits XML encoding declaration missing")
        text = text[: declaration.start("value")] + "windows-1251" + text[declaration.end("value") :]
        output = text.encode("windows-1251", "xmlcharrefreplace")
        require(parsed_bytes(output, table) == expected, "Credits numeric references changed text")
        header_fixed = False
    else:
        output = (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")
    return output, applied, header_fixed, suffix_fixed


def atomic_write(path, data):
    handle, temporary = tempfile.mkstemp(prefix=".packet_apply_", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("diagnose", "check", "apply", "verify"))
    parser.add_argument("--backup")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    by_table, pending, separators = load_packets(manifest)
    if args.mode == "verify":
        require(args.backup is not None, "Verification requires --backup")
        backup = Path(args.backup).resolve()
        require(backup.is_dir(), f"Backup directory missing: {backup}")
        applied = 0
        changed_files = 0
        for table, meta in manifest["tables"].items():
            path = Path(meta["jpn_file"]).resolve()
            backup_file = backup / path.name
            original = backup_file.read_bytes() if backup_file.is_file() else path.read_bytes()
            require(sha256(original) == meta["jpn_sha256"], f"Original backup hash differs: {table}")
            expected, count, _, _ = build_table(
                original, table, meta, by_table[table], meta["jpn_detected_encoding"], True
            )
            require(path.read_bytes() == expected, f"Live XML differs from packet application: {table}")
            require(len(parsed_bytes(expected, table)) == meta["jpn_entry_count"], f"Live XML cannot be parsed: {table}")
            changed_files += int(expected != original)
            applied += count
        print(f"verified_tables={len(manifest['tables'])} changed_files={changed_files} "
              f"applied_entries={applied} pending={len(pending)} separators={len(separators)} "
              "live_xml_differences=0")
        return
    if args.mode == "diagnose":
        mismatches = []
        for table, meta in manifest["tables"].items():
            path = Path(meta["jpn_file"])
            raw = path.read_bytes()
            require(sha256(raw) == meta["jpn_sha256"], f"Target changed after packet creation: {table}")
            source, _ = decode(raw, meta["jpn_detected_encoding"])
            source, _, _ = fix_document(source, table)
            for key, current in parsed_strings(source, table):
                packet_text = by_table[table][key]["JA_current"]
                if current != packet_text:
                    mismatches.append((table, key, current, packet_text))
        print(f"source_text_mismatches={len(mismatches)}")
        for table, key, current, packet_text in mismatches:
            print(f"{table}:{key} XML={current[:160]!r} packet={packet_text[:160]!r}")
        return
    planned = []
    applied_entries = 0
    header_fixes = 0
    suffix_fixes = 0
    for table, meta in manifest["tables"].items():
        path = Path(meta["jpn_file"]).resolve()
        require(path.parent == JPN and path.stem == table, f"Target path outside JPN table folder: {path}")
        original = path.read_bytes()
        require(sha256(original) == meta["jpn_sha256"], f"Target changed after packet creation: {table}")
        output, count, header_fixed, suffix_fixed = build_table(
            original, table, meta, by_table[table], meta["jpn_detected_encoding"], True
        )
        second_encoding = "windows-1251" if table == "stable_game_credits" else "utf-8"
        second, second_count, second_header, second_suffix = build_table(
            output, table, meta, by_table[table], second_encoding, False
        )
        require(second == output and second_count == 0 and not second_header and not second_suffix,
                f"Reapplication would change file: {table}")
        if output != original:
            planned.append((path, original, output))
        applied_entries += count
        header_fixes += int(header_fixed)
        suffix_fixes += int(suffix_fixed)
    print(f"packets={manifest['packet_count']} entries={manifest['active_entry_count']} "
          f"changed_files={len(planned)} applied_entries={applied_entries} "
          f"pending={len(pending)} separators={len(separators)} "
          f"utf8_declarations={header_fixes} xml_suffix_repairs={suffix_fixes} "
          "reapply_diff=0")
    if args.mode == "check":
        return
    backup = TRANSLATE / "backups" / f"packet_apply_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    require(not backup.exists(), f"Backup path already exists: {backup}")
    backup.mkdir(parents=True)
    for path, original, _ in planned:
        destination = backup / path.name
        shutil.copy2(path, destination)
        require(destination.read_bytes() == original, f"Backup differs: {path.name}")
    try:
        for path, _, output in planned:
            atomic_write(path, output)
            require(path.read_bytes() == output, f"Written XML differs: {path.name}")
    except Exception:
        for path, original, _ in planned:
            atomic_write(path, original)
        raise
    print(f"backup={backup}")
    print(f"target={JPN}")


if __name__ == "__main__":
    main()
