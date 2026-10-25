#!/usr/bin/env python3
"""Склейка 2 скриншотов рядом с подписями а) б) — для компактной вставки в отчёт."""
import sys
from PIL import Image, ImageDraw, ImageFont
out=sys.argv[1]; files=sys.argv[2:]
ims=[Image.open(f).convert('RGB') for f in files]
h=max(i.height for i in ims)
ims=[i.resize((int(i.width*h/i.height),h)) if i.height!=h else i for i in ims]
gap=30; lab=44
W=sum(i.width for i in ims)+gap*(len(ims)-1); 
canvas=Image.new('RGB',(W,h+lab),'white')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',26)
d=ImageDraw.Draw(canvas); x=0
for k,i in enumerate(ims):
    canvas.paste(i,(x,0))
    t=['а)','б)','в)','г)'][k]
    d.text((x+i.width//2-12,h+8),t,fill='black',font=font)
    x+=i.width+gap
canvas.save(out); print(out, canvas.size)
