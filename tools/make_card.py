import sys, json
from PIL import Image, ImageDraw, ImageFont
# usage: make_card.py spec.json out.jpg
spec=json.load(open(sys.argv[1])); out=sys.argv[2]
W,H=1080,1350
BLACK="/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
REG="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
import os
if not os.path.exists(BOLD): BOLD=BLACK
def f(p,s): return ImageFont.truetype(p,s,index=0)
# theme: "blue"（既定）or "red"
THEMES={
 "blue":dict(bg="#0E2A47",waves=["#123659","#16416A","#1B4C7B"],band="#E8452C",bandtag="#FFE1D6",pill="#F5A623",pilltext="#0E2A47",accent="#E8452C",body="#DCE6F0",src="#BFD0E0"),
 "cream":dict(bg="#FFF4E0",waves=["#FFE6C2","#FFD9A6","#FFCB8A"],band="#F07C1E",bandtag="#FFF4E0",pill="#0E2A47",pilltext="#FFFFFF",accent="#F07C1E",body="#4A3A2A",src="#7A5A3A",head="#3A2414",foot="#3A2414"),
 "red":dict(bg="#B3261E",waves=["#A12019","#8E1B15","#7A1611"],band="#0E2A47",bandtag="#CFE0F2",pill="#FFD166",pilltext="#7A1611",accent="#FFD166",body="#FBE4DF",src="#F6C9C0"),
}
T=THEMES.get(spec.get("theme","blue"),THEMES["blue"])
img=Image.new("RGB",(W,H),T["bg"]); d=ImageDraw.Draw(img)
# wave stripes bottom
for i,c in enumerate(T["waves"]):
    y=H-260+i*70
    d.rectangle([0,y,W,H],fill=c)
# top band
d.rectangle([0,0,W,150],fill=T["band"])
d.text((60,42),"EBIKANI NEWS",font=f(BLACK,58),fill="white")
d.text((W-60,58),spec.get("tag","カニ"),font=f(BOLD,40),fill=T["bandtag"],anchor="ra")
# category pill
cat=spec.get("category","ニュース")
cf=f(BOLD,40); tw=d.textlength(cat,font=cf)
d.rounded_rectangle([60,210,60+tw+60,280],radius=35,fill=T["pill"])
d.text((90,245),cat,font=cf,fill=T["pilltext"],anchor="lm")
# headline wrap
def wrap(text,font,maxw):
    lines=[];cur=""
    for ch in text:
        if ch=="\n": lines.append(cur);cur="";continue
        if d.textlength(cur+ch,font=font)>maxw: lines.append(cur);cur=ch
        else: cur+=ch
    if cur: lines.append(cur)
    return lines
hf=f(BLACK,82); y=330
for ln in wrap(spec["headline"],hf,W-120):
    d.text((60,y),ln,font=hf,fill=T.get("head","white")); y+=112
y+=30
d.rectangle([60,y,200,y+8],fill=T["accent"]); y+=50
bf=f(REG,44)
for ln in wrap(spec["body"],bf,W-120):
    d.text((60,y),ln,font=bf,fill=T["body"]); y+=68
# footer
d.text((60,H-150),"出典："+spec["source"],font=f(REG,32),fill=T["src"])
d.text((60,H-95),"@ebikani_fes ｜ エビカニフェス",font=f(BOLD,38),fill=T.get("foot","white"))
img.save(out,"JPEG",quality=90)
