# usage: make_chara_story.py spec.json outprefix
# spec: {"title":"…","panels":[{"stamp":"ebiryday","text":"ナレーション"},…]}
# outprefix-01.jpg …（フィード 1080x1350）と outprefix-01-story.jpg …（ストーリー 1080x1920）を作る
import sys, json
from PIL import Image, ImageDraw, ImageFont
spec=json.load(open(sys.argv[1])); pre=sys.argv[2]
BLACK="/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
def F(p,s): return ImageFont.truetype(p,s,index=0)
def wrap(d,text,font,maxw):
    lines=[];cur=""
    for ch in text:
        if ch=="\n": lines.append(cur);cur="";continue
        if d.textlength(cur+ch,font=font)>maxw: lines.append(cur);cur=ch
        else: cur+=ch
    if cur: lines.append(cur)
    return lines
n=len(spec["panels"])
for i,p in enumerate(spec["panels"],1):
    for story in (False,True):
        W,H=(1080,1920) if story else (1080,1350)
        top=260 if story else 40
        im=Image.new("RGB",(W,H),"#FFD166"); d=ImageDraw.Draw(im)
        # 見出し帯
        d.rounded_rectangle([40,top,W-40,top+90],radius=45,fill="#B3261E")
        d.text((80,top+45),spec.get("title","エビカニ劇場"),font=F(BLACK,44),fill="white",anchor="lm")
        d.text((W-80,top+45),f"{i}/{n}",font=F(BLACK,44),fill="#FFD166",anchor="rm")
        # スタンプ
        cs=700 if not story else 820; cx=(W-cs)//2; cy=top+120
        d.rounded_rectangle([cx+12,cy+12,cx+cs+12,cy+cs+12],radius=50,fill="#E8A93A")
        d.rounded_rectangle([cx,cy,cx+cs,cy+cs],radius=50,fill="white")
        st=Image.open(f"stamps/{p['stamp']}.png").convert("RGBA")
        s=(cs-50)/max(st.size); st=st.resize((int(st.width*s),int(st.height*s)),Image.LANCZOS)
        im.paste(st,(cx+(cs-st.width)//2,cy+(cs-st.height)//2),st)
        # ナレーション
        ny=cy+cs+40; f=F(BOLD,50 if story else 46)
        lines=wrap(d,p["text"],f,W-200)[:3]
        lh=int(f.size*1.45); bh=len(lines)*lh+60
        d.rounded_rectangle([60,ny,W-60,ny+bh],radius=30,fill="white",outline="#3A2414",width=5)
        for k,ln in enumerate(lines):
            d.text((100,ny+30+k*lh),ln,font=f,fill="#3A2414")
        foot="スワイプ👉" if (i<n and not story) else "@ebikani_fes ｜ エビカニフェス"
        if i<n and not story: foot="つづく ▶"
        d.text((W//2,H-(300 if story else 45)),foot,font=F(BLACK,40),fill="#7A1611",anchor="mm")
        im.save(f"{pre}-{i:02d}{'-story' if story else ''}.jpg","JPEG",quality=92)
