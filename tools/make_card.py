import sys, json, os
from PIL import Image, ImageDraw, ImageFont
# usage: make_card.py spec.json out.jpg
# spec: theme(blue/red/cream), tag, category, headline, body, source, format(feed/story 省略時feed)
spec=json.load(open(sys.argv[1])); out=sys.argv[2]
STORY=spec.get("format","feed")=="story"
W,H=(1080,1920) if STORY else (1080,1350)
OY=230 if STORY else 0          # ストーリーは上部のUI（プロフィール名など）を避ける
BOTTOM=H-(260 if STORY else 0)  # ストーリーは下部の返信欄を避ける
BLACK="/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
REG="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if not os.path.exists(BOLD): BOLD=BLACK
def f(p,s): return ImageFont.truetype(p,s,index=0)
THEMES={
 "blue":dict(bg="#0E2A47",waves=["#123659","#16416A","#1B4C7B"],band="#E8452C",bandtag="#FFE1D6",pill="#F5A623",pilltext="#0E2A47",accent="#E8452C",body="#DCE6F0",src="#BFD0E0"),
 "cream":dict(bg="#FFF4E0",waves=["#FFE6C2","#FFD9A6","#FFCB8A"],band="#F07C1E",bandtag="#FFF4E0",pill="#0E2A47",pilltext="#FFFFFF",accent="#F07C1E",body="#4A3A2A",src="#7A5A3A",head="#3A2414",foot="#3A2414"),
 "red":dict(bg="#B3261E",waves=["#A12019","#8E1B15","#7A1611"],band="#0E2A47",bandtag="#CFE0F2",pill="#FFD166",pilltext="#7A1611",accent="#FFD166",body="#FBE4DF",src="#F6C9C0"),
}
T=THEMES.get(spec.get("theme","blue"),THEMES["blue"])
img=Image.new("RGB",(W,H),T["bg"]); d=ImageDraw.Draw(img)
# 下部の波帯
wtop=BOTTOM-260 if not STORY else BOTTOM-200
for i,c in enumerate(T["waves"]):
    d.rectangle([0,wtop+i*70,W,H],fill=c)
# 上部の帯
if STORY: d.rectangle([0,0,W,OY+150],fill=T["band"])
else: d.rectangle([0,0,W,150],fill=T["band"])
d.text((60,OY+42),"EBIKANI NEWS",font=f(BLACK,58),fill="white")
d.text((W-60,OY+58),spec.get("tag","カニ"),font=f(BOLD,40),fill=T["bandtag"],anchor="ra")
# カテゴリ
cat=spec.get("category","ニュース")
cf=f(BOLD,40); tw=d.textlength(cat,font=cf)
y0=OY+210+(40 if STORY else 0)
d.rounded_rectangle([60,y0,60+tw+60,y0+70],radius=35,fill=T["pill"])
d.text((90,y0+35),cat,font=cf,fill=T["pilltext"],anchor="lm")
def wrap(text,font,maxw):
    lines=[];cur=""
    for ch in text:
        if ch=="\n": lines.append(cur);cur="";continue
        if d.textlength(cur+ch,font=font)>maxw: lines.append(cur);cur=ch
        else: cur+=ch
    if cur: lines.append(cur)
    return lines
hs=90 if STORY else 82; hf=f(BLACK,hs); y=y0+120+(20 if STORY else 0)
for ln in wrap(spec["headline"],hf,W-120):
    d.text((60,y),ln,font=hf,fill=T.get("head","white")); y+=int(hs*1.37)
y+=30
d.rectangle([60,y,200,y+8],fill=T["accent"]); y+=50
bs=48 if STORY else 44; bf=f(REG,bs)
for ln in wrap(spec["body"],bf,W-120):
    d.text((60,y),ln,font=bf,fill=T["body"]); y+=int(bs*1.55)
# フッター
d.text((60,BOTTOM-150),"出典："+spec["source"],font=f(REG,32),fill=T["src"])
d.text((60,BOTTOM-95),"@ebikani_fes ｜ エビカニフェス",font=f(BOLD,38),fill=T.get("foot","white"))
img.save(out,"JPEG",quality=90)
