from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ATLAS = Image.open(r"F:\Games\Radiophobia 3\gamedata\textures\ui\ui_font_jpn.dds")
COORDS = {"任": (1345, 168, 1367, 192), "字": (1753, 264, 1775, 288), "幕": (1849, 288, 1871, 312)}
FONTS = [
    "meiryo.ttc", "meiryob.ttc", "msgothic.ttc", "msyh.ttc", "msyhbd.ttc",
    "YuGothR.ttc", "YuGothM.ttc", "YuGothB.ttc",
    "NotoSansJP-Regular.otf", "NotoSansJP-Medium.otf", "NotoSansJP-Bold.otf",
]


def score(target, font, character):
    best = (float("inf"), None)
    for dx in range(-4, 5):
        for dy in range(-5, 6):
            canvas = Image.new("L", (22, 24))
            ImageDraw.Draw(canvas).text((dx, dy), character, font=font, fill=255)
            image = np.asarray(canvas, dtype=np.float32)
            error = np.mean((target - image) ** 2)
            if error < best[0]:
                best = (error, (dx, dy))
    return best


for name in FONTS:
    path = Path("C:/Windows/Fonts") / name
    for index in range(4):
        for size in range(19, 27):
            try:
                font = ImageFont.truetype(str(path), size=size, index=index)
            except OSError:
                continue
            scores = []
            for character, box in COORDS.items():
                target = np.asarray(ATLAS.crop(box).getchannel("A"), dtype=np.float32)
                scores.append(score(target, font, character))
            print(f"{name}|{index}|{size}|{np.mean([x[0] for x in scores]):.0f}|{[x[1] for x in scores]}")
