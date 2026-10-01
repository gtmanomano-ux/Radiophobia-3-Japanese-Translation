# -*- coding: utf-8 -*-
"""
Polishing script for stable_dialogs_escape__001.json
"""
import json
from pathlib import Path

src_path = Path(__file__).resolve().parents[1] / 'packets/03_dialogue/stable_dialogs_escape__001.json'
dst_path = Path(__file__).resolve().parents[1] / 'packets/03_dialogue/gemini/stable_dialogs_escape__001.json'

with open(src_path, 'r', encoding='utf-8') as f:
    packet = json.load(f)

# Define improved translations for all 68 entries
# Maintaining exact trailing spaces/newlines as appropriate
improved = {
    # 0: joke_bandit_9
    # Leader flesh boasting to others
    0: 'フレッシュの群れがぐるぐる走り回ってた。するとリーダーが立ち止まって言った。「兄弟たち……でっけえ音を立てたか？」\n\\n「立てたぞ！」\n\\n「ものすごい砂ぼこりを巻き上げたか？」\n\\n「そうとも、巻き上げた！」\n\\n「じゃあ俺たち、ほとんど馬みたいなもんだな！」\n         ',

    # 1: dialog_bandit_1
    # Bandit lecture about surviving in the Zone
    1: '人間を作るのは服じゃない。ここじゃ大事なのは中身だけだ、身なりなんざどうでもいい。ゾーンは裏に売春宿がついた安酒場でもなけりゃ、幼稚園でもないんだ。言いたいこと、分かるか？ どんなプロ仕様の装備やイカした銃を持っていようが、金が腐るほどあってアーティファクトで泳いでいようが、頭ん中がクソ塗れでポケットに手を突っ込んでボケッとしてたら、あっさりくたばるだけだ！ 二度目のチャンスなんかない、失敗は一度きりだ！ だから言ってるだろ、気を引き締めろ！ 周りに注意を払え！ いつだって目を光らせておけ！ そうしないと、ヴィトカ・ノージーの二の舞になるぞ。あいつには何百回も言ってやったんだ、「あの隙間のそばを通るな、あっちへ行くな！」ってな。なのに聞く耳を持ちやがらなかった！ 今じゃ死体すら見つかりゃしない。 \\nPDAに通知が来やがったよ――「ストーカー死亡：ヴィトカ・ノージー。死因：不明……」\n         ',

    # 2: trader_relation_stalker_3 (Sidorovich)
    # Stalker rep low (20k)
    2: 'ああ、あんた、この辺のストーカーをだいぶ怒らせてくれたようだな。今のうちに態度を改めねえと、連中が結託して、寝込みを襲って楽にしてくれるぞ。俺がいつでもかばってやれると思うなよ。ここは容赦のない世界だ。腐ったリンゴを間引くのがストーカー流ってもんさ。分かるだろ？ いいか、マークド・ワン。ゾーンで生き延びるのに頼れるのは、いつだって信頼と評判だけだ。あんたはその両方をドブに捨ててるんだぞ……まあいい、俺があんたの評判を立て直してやる。だが、信頼を取り戻すのはあんた自身だ。2万ルーブル出せば、今夜は安心して眠れるようにしてやるよ。罪もきれいさっぱり洗い流してな、へへへ……',

    # 3: trader_relation_stalker_5 (Sidorovich)
    # Stalker rep very low (40k)
    3: 'おやおや、悪魔のお出ましか。マークド・ワン、死のトラックから助け出して、わざわざ健康な体に戻してやったのはな、あんたが野獣になって俺の上客どもを皆殺しにするためじゃないぞ！ ローナー連中と何の揉め事があるか知らんが、いい加減にしておけ。俺の商売を台無しにする気か！ ……分かったよ、仲裁してほしいんだろ？ なら相応の金を払ってもらおうか！ あんたのせいで被った損失の穴埋めに、4万ルーブルきっちり出してもらおう。何とか話をまとめてやるが、保証はできんぞ。さあ、とっとと出ていって、俺が片をつけるまで身を潜めてろ。',

    # 4: trader_relation_stalker_7 (Sidorovich)
    # Stalker rep terrible (60k)
    4: '誰かと思えば、ヒトラーの生まれ変わり、ゾーン謹製の殺人マシーン様のお出ましじゃないか！ 今日だけで何人のストーカーを血祭りにあげたんだ、この頭のイカれたサイコ野郎が？ 狂犬みたいに射殺してやりたいところだが、あんたをこのバンカーから生きて帰す理由が一つでもあるか！？ あんたをブチ殺せば商売は大繁盛、界隈のストーカーどもは朝まで大宴会で、俺は酒を浴びるほど売りさばけるんだぞ。散々引っかき回しておいて、のこのこやって来て仲裁してくれだと！？ いったいどうやって収めろってんだ！？ 俺に思いつく解決策は、あんたの頭蓋骨に弾丸をブチ込むことくらいだ！ クソッ、酒でも飲まなきゃやってられん……分かったよ、マークド・ワン。あんたのほうから接触してきたんだ、わざわざこのキャンプに乗り込んで手打ちを頼みに来るその度胸だけは認めてやる。情けをかけてやるよ、俺の店に与えた損害の埋め合わせをするチャンスをやろう。6万ルーブル置いていけ。盗まれたPDAだの、マーセナリーズの仕業だのに見せかけて、この大虐殺を誰か別の奴のせいにでっち上げてやる……考える時間をくれ。それまでどこかに隠れて、しばらく顔を見せるな！',

    # 5: trader_relation_stalker_9 (Player to Sidorovich)
    5: '分かった。これでローナーどもが大人しくなってくれるといいが。',

    # 6: trader_relation_stalker_12 (Player to Sidorovich)
    6: 'よし。争いが減れば、それだけ厄介事も減る。',

    # 7: escape_trader_start_dialog_111 (Sidorovich)
    # Main quest to find Nimble
    7: '仕事があるぞ、マークド・ワン……ニンブルというストーカーを探してほしい。極めて重要な情報を持っていたんだが、鉄道橋のあたりで行方不明になった。生死は問わん、とにかく情報の入ったフラッシュドライブが必要なんだ。近くのキャンプにいるウルフに話を聞いてみろ。あいつなら、ニンブルの居場所に心当たりがあるはずだ。',

    # 8: escape_trader_start_dialog_1111 (Player)
    8: 'それだけか？',

    # 9: escape_trader_start_dialog_199 (Sidorovich)
    9: '待て。ほら、このピストルと弾を持っていけ。武器もなしじゃ、ゾーンじゃ二秒と生き残れんぞ！ そういえば、ここに担ぎ込まれたとき、ナイフを持っていたな。頭がまともに働いていないと危ないから預かっておいたんだが、もう大丈夫そうだな。ほら、返してやるよ。',

    # 10: escape_trader_start_dialog_1999 (Player)
    10: 'ありがとう。',

    # 11: escape_trader_start_dialog_51 (Player)
    11: '仕事を片づけてきた。アーティファクトはこれだ。',

    # 12: escape_trader_start_dialog_511 (Sidorovich)
    12: '見事だ、マークド・ワン。あと一つだけ小さな頼みを聞いてくれれば、これで貸し借りなしだ。',

    # 13: escape_trader_start_dialog_5111 (Player)
    13: '頼みって何だ？',

    # 14: escape_trader_start_dialog_521211 (Player)
    14: 'ほら、受け取れ。',

    # 15: escape_trader_start_dialog_5212111 (Sidorovich)
    15: 'よし……これでテストは合格とみなしてやろう。ルーキー村には近づかんほうが身のためだぞ。',

    # 16: escape_trader_start_dialog_571 (Sidorovich)
    16: 'で、アーティファクトは持ってきたんだろうな？',

    # 17: escape_trader_start_dialog_5711 (Player)
    17: 'まだだ。',

    # 18: escape_trader_start_dialog_57111 (Sidorovich)
    18: 'おいおい、それを持ってくるまでは話すことなんかないぞ。分かったな？',

    # 19: escape_trader_start_dialog_6 (Sidorovich)
    19: 'マークド・ワン、もう話すことは全部話したぞ。さっさと出ていけ！',

    # 20: tutorial_wounded_give_medkit_21111111 (Tolik/Wounded stalker)
    # Advice on PDA and stashes
    20: 'そうか……なら、一ついいアドバイスをしてやるよ。タダだが、役に立つ知恵だ。ゾーンで一番大事なものは何だと思う？ 金じゃない、情報だ！ 情報があれば危険を避けられるし、獲物のありかも分かる。もうPDAは持ってるか？ ストーカーなら誰でも使ってる。情報を受信したり送信したり、保存したりできるんだ。全体チャットで獲物のありかのヒントや助言を共有してくれる奴も多い。誰かが手つかずの死体を見つけて位置を流せば、そこがお宝を探す絶好のチャンスになるってわけだ。\\n \\nもちろん、ここじゃ日常茶飯事で人が死ぬから、くたばったストーカーに出くわすこともある。そいつらのPDAを拾ってデータを吸い出すんだ。持ち主次第じゃ、PDAをいい値で買い取ってくれる奴もいるぞ。データ転送は至って簡単で、どのPDAにもデコーダーが入ってるから、ボタン一つで自分のPDAに情報を移せる。ゾーンのあちこちに隠されたスタッシュを示すマップマーカーも手に入るぞ。中にはお宝がぎっしり詰まってるのさ。',

    # 21: escape_trader_car_trade_11 (Player)
    21: 'コルドンだ。',

    # 22: escape_trader_car_trade_111 (Sidorovich)
    22: '「ゴートリング」のポンコツなら、駐車場まで届くよう手配してやれるぞ。使い古しだがちゃんとタイヤは4つ付いてる、たったの9,000ルーブルだ！ 代金は前払い、返金は受けつけんぞ！\\n \\n\n\t\tそれが怖けりゃ、一番奥の家のそばにあるザポロージェツを勝手に持っていけ……エンジンがかかればの話だがな、へへっ！..',

    # 23: escape_trader_car_trade_1111 (Player)
    23: '……いいだろう、その「ポンコツ」を持ってきてくれ。',

    # 24: escape_trader_car_trade_1112 (Player)
    24: 'くそっ、なんてぼったくりだ！ やめておく……泥道を歩くよ。',

    # 25: escape_trader_car_trade_11111 (Sidorovich)
    25: '「ゴートリング」はあんたのもんだ。自動車工場のガレージで受け取れ。',

    # 26: escape_trader_car_trade_12 (Player)
    26: 'ガーベジだ。',

    # 27: escape_trader_car_trade_121 (Sidorovich)
    27: 'ガーベジだな……そうさな……「モスクヴィッチ2141」とUAZがあるぞ。いつも通り、代金は前払いだ。',

    # 28: escape_trader_car_trade_1211 (Player)
    28: '「モスクヴィッチ」にしておくか……',

    # 29: escape_trader_car_trade_12111 (Sidorovich)
    29: '「モスクヴィッチ」はあんたのもんだ。車両置き場に置いてあるぞ。',

    # 30: escape_trader_car_trade_1212 (Player)
    30: 'UAZを手配してくれ。',

    # 31: escape_trader_car_trade_12121 (Sidorovich)
    31: '商談成立だ。デューティーの検問所の手前、廃墟のそばに置いておく。',

    # 32: escape_trader_car_trade_1213 (Player)
    32: '考え直した、やっぱりやめておく……',

    # 33: escape_trader_car_trade_13 (Player)
    33: 'アフロプロムだ。',

    # 34: escape_trader_car_trade_131 (Sidorovich)
    34: 'そうだな……UAZ「ゴートリング」か「ニーヴァ」を届けてやれるぞ。でなけりゃ、軍からモスクヴィッチを「拝借」してみる手もあるがな……へへへ……',

    # 35: escape_trader_car_trade_1311 (Player)
    35: 'UAZにしておく……それだけの価値はあるんだろうな……',

    # 36: escape_trader_car_trade_13111 (Sidorovich)
    36: '鉄道トンネルのそばで受け取れ。さあ、とっとと行け！',

    # 37: escape_trader_car_trade_1312 (Player)
    37: '「ニーヴァ」を手配してくれ。',

    # 38: escape_trader_car_trade_13121 (Sidorovich)
    38: '研究所から続く道に置いてあるぞ……',

    # 39: escape_trader_car_trade_1313 (Player)
    39: 'あんたは一体いつになったら、人から金を巻き上げるのをやめるんだか……',

    # 40: escape_trader_car_trade_14 (Player)
    40: 'ダークバレーだ。',

    # 41: escape_trader_car_trade_141 (Sidorovich)
    41: 'あそこなら「ブリック」を回せるぞ。たったの15,000ルーブルポッキリだ。あそこはかなり危険な場所だからな、値段に跳ね返るのは当然だろ、分かるな？',

    # 42: escape_trader_car_trade_1411 (Player)
    42: 'まあ、いいだろう……',

    # 43: escape_trader_car_trade_14111 (Sidorovich)
    43: '「ブリック」はボロフのキャンプの向かい、ガソリンスタンドで待機させておくぞ。',

    # 44: escape_trader_car_trade_1412 (Player)
    44: 'おっと……やっぱり気が変わったよ……',

    # 45: escape_trader_car_trade_15 (Player)
    45: 'ロストクだ。',

    # 46: escape_trader_car_trade_151 (Sidorovich)
    46: 'ロストクだな……なら「ニーヴァ」だ。前払いで12,000ルーブルだぞ。',

    # 47: escape_trader_car_trade_1511 (Player)
    47: '何でそんなに高いんだ？ ……まあいい、手配してくれ……',

    # 48: escape_trader_car_trade_15111 (Sidorovich)
    48: '道路沿い、タンクローリーのそばで受け取れ。',

    # 49: escape_trader_car_trade_1512 (Player)
    49: '高すぎるな……またの機会にするよ。',

    # 50: escape_trader_car_trade_17 (Player)
    50: 'ヤンターだ。',

    # 51: escape_trader_car_trade_171 (Sidorovich)
    51: '上客だな！ あそこなら「ロップイヤー」を回してやれるぞ！ 小さくてポンコツだがな！ それでもたったの8,000ルーブルだ！',

    # 52: escape_trader_car_trade_1711 (Player)
    52: 'じゃあその「ロップイヤー」にしておく……後悔しないといいが……',

    # 53: escape_trader_car_trade_17111 (Sidorovich)
    53: '持ってけ！ 渓谷に入ればすぐに見つかるぞ。',

    # 54: escape_trader_car_trade_1712 (Player)
    54: 'いや、やっぱり後にしておくよ……',

    # 55: escape_trader_car_trade_18 (Player)
    55: '冗談じゃない！',

    # 56: escape_trader_factions_1 (Player)
    56: 'ストーカーどもに……その……付け狙われてるんだ！ 何とかしてくれないか？',

    # 57: escape_trader_factions_2 (Sidorovich)
    57: 'やってやれんことはないが、タダとはいかんぞ。20,000ルーブルで話をつけてやる。どうだ？',

    # 58: escape_trader_factions_3 (Player)
    58: '頼む。あのストーカーどもに付きまとわれるのはもう御免だ。',

    # 59: escape_trader_factions_4 (Player)
    59: '断る。そこまで大金をはたいて揉み消す気はない。',

    # 60: horror_time_story_4 (Player)
    60: 'ああ、まさにそれだ！',

    # 61: horror_time_story_5 (Stalker response to scary rumor)
    61: 'へっ！ ガキじゃあるまいし、そんな噂本気にしてんのか？',

    # 62: horror_time_story_6 (Stalker telling story)
    62: 'いや、マジで本当の話なんだって、聞いてくれよ。',

    # 63: horror_time_story_8 (Player)
    63: 'なるほどな。教えてくれて恩に着るよ。',

    # 64: escape_trader_start_dialog_19911 (Player)
    64: '分かった。他には何か情報はないか？',

    # 65: escape_trader_start_dialog_1991111 (Player)
    65: 'すぐ向かう……',

    # 66: escape_trader_start_dialog_771 (Sidorovich)
    66: 'で、アーティファクトは持ってきたんだろうな？',

    # 67: escape_trader_start_dialog_771211 (Player)
    67: 'どんな頼みだ？'
}

# Update entries
for idx, new_ja in improved.items():
    packet['entries'][idx]['JA_new'] = new_ja

import os
os.makedirs(os.path.dirname(dst_path), exist_ok=True)

with open(dst_path, 'w', encoding='utf-8') as f:
    json.dump(packet, f, ensure_ascii=False, indent=2)

print(f"Successfully updated and saved {len(improved)} entries to {dst_path}")
