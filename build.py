#!/usr/bin/env python3
"""data/ の素材から index.html を組み立てる。 使い方: python3 build.py"""
import json, glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

# 原文（正字）を日本の新字体へ寄せる。1対1で安全に置き換えられる字だけ。
KYU = "學爲說樂禮德與國亂舊歸實盡萬寶變譽讓辭顏衞靈鄉黨惡愛聽從來對當黨點體會圖聲學覺觀勸權歡齊濟齒藝衆眞愼獨勞榮營單戰獸嚴廣鑛擧拜賣讀續屬數樞樣樓條狀將獎壯裝莊藏臟壞懷價假佛拂傳轉團應擇澤釋譯驛兩滿彌餘豫縣縱總繩絲經繼續緣纖聰職肅臺與舉舍號處虛蟲蠶衞視覽證讚豐賴贊踐輕辨辯邊遲鄰醫釀鐵鑄關險隱雙難靜顯飮餘驗髮鬪鷄麥黃黑默齋齡龍龜攝敎敍晝曉曆曾櫻歲歷殘殺毆氣沒淨渴溫灣燈爭犧獻畫畵瘦癡發盜眞碎祕祿禪稱穩竊竝粹肅腦臟與覺豫貳賤醉鹽"
SHIN = "学為説楽礼徳与国乱旧帰実尽万宝変誉譲辞顔衛霊郷党悪愛聴従来対当党点体会図声学覚観勧権歓斉済歯芸衆真慎独労栄営単戦獣厳広鉱挙拝売読続属数枢様楼条状将奨壮装荘蔵臓壊懐価仮仏払伝転団応択沢釈訳駅両満弥余予県縦総縄糸経継続縁繊聡職粛台与挙舎号処虚虫蚕衛視覧証讃豊頼賛践軽弁弁辺遅隣医醸鉄鋳関険隠双難静顕飲余験髪闘鶏麦黄黒黙斎齢竜亀摂教叙昼暁暦曽桜歳歴残殺殴気没浄渇温湾灯争犠献画画痩痴発盗真砕秘禄禅称穏窃並粋粛脳臓与覚予弐賎酔塩"
assert len(KYU) == len(SHIN), (len(KYU), len(SHIN))
TABLE = str.maketrans(KYU, SHIN)

SCENES = {"lonely", "lead", "grow", "judge", "trust", "vision", "decide", "profit", "fail", "self"}
EMOS = {"不安", "怒り", "孤独", "迷い", "焦り", "落胆", "慢心", "疲れ"}

sh = json.load(open(os.path.join(DATA, "shimomura.json"), encoding="utf-8"))
gb = json.load(open(os.path.join(DATA, "genbun.json"), encoding="utf-8"))
tags = {}
for f in sorted(glob.glob(os.path.join(DATA, "out_*.json"))):
    for o in json.load(open(f, encoding="utf-8")):
        tags[o["n"]] = o

rows, problems = [], []
for o in sh:
    t = tags.get(o["n"])
    if not t:
        problems.append(f"n={o['n']} タグなし")
        continue
    src = [i for i in t.get("src", []) if 1 <= i <= len(gb[o["bi"] - 1])]
    if not src:
        problems.append(f"n={o['n']} 原文の対応なし")
    genbun = "".join(gb[o["bi"] - 1][i - 1] for i in src).translate(TABLE)
    scenes = [s for s in t.get("scenes", []) if s in SCENES][:3]
    emo = [e for e in t.get("emo", []) if e in EMOS][:2]
    rel = int(t.get("rel", 0))
    if rel > 0 and not scenes:
        rel = 0
    yaku = re.sub(r"[ \t　]+\n", "\n", o["text"]).strip()
    rows.append([o["n"], o["bi"] - 1, o["no"], genbun, t["kaki"].strip(), t["hito"].strip(),
                 t.get("toi", "").strip() if rel > 0 else "", scenes, emo, rel, yaku])

if problems:
    print("\n".join(problems), file=sys.stderr)
tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
out = tpl.replace("/*DATA*/[]", payload)
# artifact.html＝Artifact公開用（外枠なし）、index.html＝単体で開ける版（GitHub Pagesなど）
open(os.path.join(HERE, "artifact.html"), "w", encoding="utf-8").write(out)
HEAD = '<!doctype html>\n<html lang="ja">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n<style>body{margin:0}</style>\n'
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(HEAD + out)
print(f"{len(rows)}章 / index.html {len(out.encode())//1024}KB / rel分布", {r: sum(1 for x in rows if x[9] == r) for r in (3, 2, 1, 0)})
