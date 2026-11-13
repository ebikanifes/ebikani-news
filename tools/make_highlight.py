# usage: make_highlight.py outdir  — ハイライト表紙4種（1080x1920、中央の円に収まるデザイン）
import sys,os
from PIL import Image, ImageDraw, ImageFont
BLACK="/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
out=sys.argv[1]
items=[("gourmet","グルメ","#B3261E","#FFD166","white"),
       ("news","ニュース","#0E2A47","#E8452C","white"),
       ("mame","まめ知識","#FFF4E0","#F07C1E","#3A2414"),
       ("chara","キャラ","#FFD166","#B3261E","#0E2A47")]
for key,label,bg,ring,fg in items:
    W,H=1080,1920; im=Image.new("RGB",(W,H),bg); d=ImageDraw.Draw(im)
    cx,cy,r=W//2,H//2,330
    d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=ring,width=26)
    size=150 if len(label)<=3 else (120 if len(label)==4 else 100)
    fnt=ImageFont.truetype(BLACK,size,index=0)
    d.text((cx,cy-30),label,font=fnt,fill=fg,anchor="mm")
    d.text((cx,cy+120),"EBIKANI",font=ImageFont.truetype(BLACK,52,index=0),fill=ring,anchor="mm")
    im.save(os.path.join(out,f"highlight-{key}.jpg"),"JPEG",quality=92)
