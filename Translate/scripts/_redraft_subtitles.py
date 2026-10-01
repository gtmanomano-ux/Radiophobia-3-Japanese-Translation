import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests


PATH = Path(__file__).resolve().parents[1] / "subtitles/stable_closecaption.json"
OVERRIDES = {
    "cc_tutorial_1-2": "ゾーンで命を落とさずに済む。",
    "cc_tutorial_1-3": "仮に死んだとしても、\\nいつ、どう死んだか皆に伝わる。",
    "cc_tutorial_1-4": "冗談だ。\\n使い方を説明しよう。",
    "cc_tutorial_2-1": "最初の項目には、\\nお前の任務が載っている。",
    "cc_tutorial_3-1": "大抵の任務には、詳細を確認するボタンがある。",
    "cc_tutorial_4-1": "新しい任務を受けると、",
    "cc_tutorial_4-2": "ミニマップのマーカーは\\n自動的にその任務へ切り替わる。",
    "cc_tutorial_5-1": "次だ。二つ目の項目はマップ。",
    "cc_tutorial_6-1": "上にあるボタンで\\n地図を拡大、縮小できる。",
    "cc_tutorial_7-1": "現在地を地図の中央に表示することもできる。",
    "cc_tutorial_9-1": "触ってみれば分かる。難しくない。",
    "cc_tutorial_9-2": "ほかには……連絡先もあるな。",
    "cc_tutorial_11-1": "半径50メートル以内にいる\\nストーカーの一覧だ。",
    "cc_tutorial_11-2": "それぞれの簡単な情報、階級、所属と、",
    "cc_tutorial_11-3": "お前に対する態度が分かる。",
    "cc_tutorial_11-4": "今のお前は中立だ。",
    "cc_tutorial_11-5": "これからどう扱われるかは、\\nお前の行動次第だぞ。",
    "cc_tutorial_11-6": "誰かを助けたら、",
    "cc_tutorial_11-7": "お前への態度がどう変わるか\\n確かめてみるといい。",
    "cc_tutorial_12-1": "近くに敵がいるときは気をつけろ。",
    "cc_tutorial_12-2": "ミニマップでは赤く表示される。",
    "cc_tutorial_12-3": "味方は緑、\\n中立の相手は黄色だ。",
    "cc_tutorial_12-4": "死んだストーカーのPDAは灰色になる。",
    "cc_tutorial_12-5": "漁る気があるなら、目印にしろ。",
    "cc_tutorial_12-6": "ほかには……そうだ、日記がある。",
    "cc_tutorial_13-1": "これは説明するまでもないな。",
    "cc_tutorial_13-2": "必要な情報も、ニュースも、\\n全部ここに記録される。",
    "cc_tutorial_13-3": "今俺が話していることも\\n後から読み返せるぞ。",
    "cc_tutorial_13-4": "ランキングもある。",
    "cc_tutorial_14-1": "俺が知る腕利きのストーカー、上位20人だ。",
    "cc_tutorial_14-2": "この情報は時々更新している。",
    "cc_tutorial_14-3": "競争相手がいたほうが\\n張り合いも出るだろう？",
    "cc_tutorial_14-4": "いつかお前も上位に入るかもな。\\n何が起きるか分からん。",
    "cc_tutorial_14-5": "お前自身の実績は\\n統計の項目に記録される。",
    "cc_tutorial_14_1-1": "簡単だろう。次は百科事典だ。",
    "cc_tutorial_15-1": "ゾーンの情報や\\n生き延びるための知恵が、",
    "cc_tutorial_15-2": "ほかのストーカーから届くたびに\\n自動で記録される。",
    "cc_tutorial_15-3": "だいたいこんなところだ。",
    "cc_tutorial_15_1-1": "ああ、もう一つ。",
    "cc_tutorial_15_1-2": "そのPDAには広帯域受信機が付いている。",
    "cc_tutorial_15_1-3": "優れものだぞ。近くの軍の通信まで\\n傍受できる。",
    "cc_tutorial_15_1-4": "ただし受信範囲は広くない。\\nせいぜい500メートルだ。",
    "cc_tutorial_15_1-5": "俺の無線なら30キロ先まで届く。",
    "cc_tutorial_15_1-6": "だから、お前の居場所はいつでも分かる。",
    "cc_tutorial_15_1-7": "任務や最新の情報を\\n俺から送ってやる。",
    "cc_tutorial_15_1-8": "役に立つ助言もできるかもしれん。",
    "cc_tutorial_15_1-9": "どうだ、分かったか？",
}


def google(text):
    for attempt in range(5):
        try:
            response = requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": "en", "tl": "ja", "dt": "t", "q": text},
                timeout=20,
            )
            response.raise_for_status()
            translated = "".join(part[0] for part in response.json()[0] if part[0])
            if translated.strip():
                return translated
        except Exception:
            time.sleep(1 + attempt * 2)
    raise RuntimeError(text)


def main():
    entries = json.loads(PATH.read_text(encoding="utf-8"))
    work = {}
    for item in entries:
        if item["id"] in OVERRIDES or item["id"].startswith("cc_characters_voice-scenario-trader-trader_monolog1-") or item["id"] in {"ui_mm_cc_captioning", "ui_mm_cc_none", "ui_mm_cc_speechonly", "cc_tutorial_1-1"}:
            continue
        for part in item["en"].split("\\n"):
            if part.strip():
                work[part] = None
    with ThreadPoolExecutor(max_workers=6) as pool:
        jobs = {pool.submit(google, part): part for part in work}
        for index, job in enumerate(as_completed(jobs), 1):
            part = jobs[job]
            work[part] = job.result()
            if index % 50 == 0:
                print(f"translated={index}/{len(jobs)}", flush=True)
    for item in entries:
        if item["id"] in OVERRIDES:
            item["ja"] = OVERRIDES[item["id"]]
        elif item["en"] in work:
            item["ja"] = work[item["en"]]
        elif item["id"].startswith("cc_characters_voice-scenario-trader-trader_monolog1-") or item["id"] in {"ui_mm_cc_captioning", "ui_mm_cc_none", "ui_mm_cc_speechonly", "cc_tutorial_1-1"}:
            continue
        else:
            item["ja"] = "\\n".join(work[part] if part.strip() else "" for part in item["en"].split("\\n"))
    PATH.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"saved={len(entries)}")


if __name__ == "__main__":
    main()
