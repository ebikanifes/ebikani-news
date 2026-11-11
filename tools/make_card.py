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
img=Image.new("RGB",(W,H),"#0E2A47"); d=ImageDraw.Draw(img)
# wave stripes bottom
for i,c in enumerate(["#123659","#16416A","#1B4C7B"]):
    y=H-260+i*70
    d.rectangle([0,y,W,H],fill=c)
# top band
d.rectangle([0,0,W,150],fill="#E8452C")
d.text((60,42),"EBIKANI NEWS",font=f(BLACK,58),fill="white")
d.text((W-60,58),spec.get("tag","カニ"),font=f(BOLD,40),fill="#FFE1D6",anchor="ra")
# category pill
cat=spec.get("category","ニュース")
cf=f(BOLD,40); tw=d.textlength(cat,font=cf)
d.rounded_rectangle([60,210,60+tw+60,280],radius=35,fill="#F5A623")
d.text((90,245),cat,font=cf,fill="#0E2A47",anchor="lm")
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
    d.text((60,y),ln,font=hf,fill="white"); y+=112
y+=30
d.rectangle([60,y,200,y+8],fill="#E8452C"); y+=50
bf=f(REG,44)
for ln in wrap(spec["body"],bf,W-120):
    d.text((60,y),ln,font=bf,fill="#DCE6F0"); y+=68
# footer
d.text((60,H-150),"出典："+spec["source"],font=f(REG,32),fill="#BFD0E0")
d.text((60,H-95),"@ebikani_fes ｜ エビカニフェス",font=f(BOLD,38),fill="white")
img.save(out,"JPEG",quality=90)
