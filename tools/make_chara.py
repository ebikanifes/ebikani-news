# usage: make_chara.py stamp.png out.jpg [story]
# スタンプ画像を、キャラ投稿用の黄色い背景に大きく配置する
import sys
from PIL import Image, ImageDraw, ImageFont
src,out=sys.argv[1],sys.argv[2]; story=len(sys.argv)>3 and sys.argv[3]=="story"
W,H=(1080,1920) if story else (1080,1350)
BLACK="/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
bg=Image.new("RGB",(W,H),"#FFD166"); d=ImageDraw.Draw(bg)
# 白い角丸カード
cw=920; ch=920; cx=(W-cw)//2; cy=(H-ch)//2-(0 if story else 30)
d.rounded_rectangle([cx+14,cy+14,cx+cw+14,cy+ch+14],radius=60,fill="#E8A93A")
d.rounded_rectangle([cx,cy,cx+cw,cy+ch],radius=60,fill="white")
st=Image.open(src).convert("RGBA")
s=860/max(st.size); st=st.resize((int(st.width*s),int(st.height*s)),Image.LANCZOS)
bg.paste(st,(cx+(cw-st.width)//2,cy+(ch-st.height)//2),st)
f=ImageFont.truetype(BLACK,44,index=0)
ty=cy+ch+(70 if not story else 120)
d.text((W//2,ty),"@ebikani_fes ｜ エビカニフェス",font=f,fill="#7A1611",anchor="mm")
bg.save(out,"JPEG",quality=92)
