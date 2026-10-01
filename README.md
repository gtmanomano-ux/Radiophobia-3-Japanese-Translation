# Radiophobia 3 日本語化

Radiophobia 3 1.20向け日本語化の作業データと、ゲームへ適用済みのパッチを公開しています。

## ダウンロード・導入

[Releases](https://github.com/gtmanomano-ux/Radiophobia-3-Japanese-Translation/releases)から日本語化ZIPをダウンロードしてください。

ゲームを終了して既存ファイルをバックアップし、ZIP内の `gamedata` と `fsgame.ltx` を `Radiophobia 3.exe` があるフォルダへ上書きコピーします。配布版は日本語専用の言語設定です。

詳しくは [使い方.md](使い方.md) を参照してください。リリースZIPにも同じ手順を収録しています。

## 構成

| 場所 | 内容 |
|---|---|
| `gamedata` | 適用済み日本語XML、フォント、表示設定、セーブ名修正 |
| `Translate/packets` | 9ジャンルの翻訳パケット、会話グラフ、修正用データ |
| `Translate/glossaly` | 15分類の用語辞書 |
| `Translate/subtitles` | 字幕の作業データ |
| `Translate/scripts` | 翻訳・適用・フォント追加スクリプト |
| `Translate/*.md` | 執筆方針、辞書の規則、パケット適用手順 |

作業スクリプトは初回用のハッシュ照合や外部入力への依存があります。導入するだけなら実行不要です。字幕生成スクリプトが参照する中国語パッチ原本は `Translate/downloads/Radiophobia3.14Chinese.zip` へ別途配置してください。ゲーム本体・外部原本・バックアップ・個人のログやセーブデータは収録していません。

配布データは現在までの成果物で、すべての文章の校正完了や新規環境での動作確認完了を意味しません。
