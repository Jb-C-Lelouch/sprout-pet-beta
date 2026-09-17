"""Botanical pixel silhouettes with shared ground anchors and relative scale."""
import math
import random


def field_pixels():
    from pixel_art import Pixels
    p=Pixels(130,48);rng=random.Random(93)
    outline=[(3,18),(9,12),(18,13),(25,8),(39,7),(47,4),(62,7),(73,5),(87,10),(98,9),(109,14),(116,13),(123,19),(122,26),(127,31),(120,35),(114,41),(99,40),(90,44),(76,42),(63,46),(49,43),(37,44),(26,39),(15,38),(12,32),(5,29),(7,23)]
    p.polygon([(x,y+1) for x,y in outline],'#58653b')
    p.polygon(outline,'#765333')
    p.polygon([(round(65+(x-65)*.94),round(25+(y-25)*.87)) for x,y in outline],'#88613c')
    # Curved, broken cultivation marks rather than parallel ruler-straight rows.
    for start in (16,24,33):
        for x in range(14,117):
            y=round(start+2*math.sin(x/22)+x/100)
            if rng.random()<.73 and p.rows[y][x]:
                p.rect(x,y,1,1,'#705032')
                if p.rows[y+1][x]:p.rect(x,y+1,1,1,'#9b7548')
    mask=[row[:] for row in p.rows]
    for _ in range(760):
        x=rng.randrange(130);y=rng.randrange(48)
        if mask[y][x]:p.rect(x,y,1,1,rng.choice(('#977046','#a17c50','#795536','#654b32')))
    # Turf breaks into the rim; scattered pebbles never form a continuous border.
    for x,y in outline[::2]:
        p.line(x-2,y,x+2,y,'#657a43');p.line(x,y,x-1,y-3,'#819651')
        p.rect(x+2,y-2,1,2,'#a5ad68')
    for x,y in ((17,35),(103,39),(120,27),(39,8),(8,20)):
        p.oval(x,y,4,3,'#766f52');p.rect(x+1,y,2,1,'#aca084')
    return p


def draw_plant(species,stage):
    from pixel_art import Pixels
    p=Pixels(80,96);rng=random.Random(species+str(stage));cx=40;ground=92
    dark='#405b36';green='#658947';light='#99b566';vein='#b5c680'
    scale=(0,.28,.52,.76,1)[stage]
    def stem(x,y,xx,yy,width=1):
        p.line(x,y,xx,yy,dark,width)
        if width>1:p.line(x+1,y,xx+1,yy,green)
    def leaf(x,y,xx,yy,width=3,color=green,serrated=False):
        dx=xx-x;dy=yy-y;length=max(1,math.hypot(dx,dy));nx=-dy/length;ny=dx/length
        pts=[(x,y)]
        for side,ts in ((1,(.25,.5,.75)),(-1,(.75,.5,.25))):
            if side==-1:pts.append((xx,yy))
            for t in ts:
                w=width*math.sin(math.pi*t)
                pts.append((round(x+dx*t+nx*w*side),round(y+dy*t+ny*w*side)))
        p.polygon(pts,dark)
        inner=[(round(x+(a-x)*.86),round(y+(b-y)*.86)) for a,b in pts]
        p.polygon(inner,color);p.line(x,y,xx,yy,light)
        if serrated:
            for t in (.35,.6):
                a=round(x+dx*t);b=round(y+dy*t)
                for s in (-1,1):p.line(a,b,round(a+nx*width*s+dx*.12),round(b+ny*width*s+dy*.12),color)
    def flower(x,y,r,color,center):
        for i in range(10):
            angle=i*math.pi/5
            xx=round(x+math.cos(angle)*r);yy=round(y+math.sin(angle)*r*.8)
            p.line(x,y,xx,yy,color,2 if r>4 else 1)
        p.oval(x-2,y-2,5,4,center);p.rect(x,y-1,1,1,'#f0d284')
    if stage==0:
        p.line(37,92,43,92,'#82633d');p.rect(39,91,2,1,'#b79a65');return p
    if species=='cherry':
        height=round(76*scale);top=ground-height
        p.line(cx,ground,cx-2,top+9,'#6d563b',max(2,round(5*scale)))
        p.line(cx+2,ground-2,cx+1,top+16,'#98744c',2)
        for i,(dx,dy) in enumerate(((-23,18),(21,21),(-13,5),(12,3),(0,-3))):
            x=cx+round(dx*scale);y=top+round((dy+8)*scale)
            p.line(cx,ground-round(height*.4),x,y,'#70583c',max(1,round(2*scale)))
            radius=max(3,round(14*scale))
            for _ in range(round(24*scale)+3):
                a=rng.random()*math.tau;r=radius*math.sqrt(rng.random())
                px=round(x+math.cos(a)*r);py=round(y+math.sin(a)*r*.64)
                if stage==4:
                    p.oval(px-3,py-2,7,5,rng.choice(('#c48e99','#dba4ad','#e8b9bd','#efc7c7')))
                    if rng.random()<.6:
                        p.rect(px-1,py,3,1,'#f9ded4');p.rect(px,py-1,1,3,'#f9ded4');p.rect(px,py,1,1,'#c6976e')
                else:leaf(px,py,px+rng.choice((-4,4)),py-3,2,rng.choice((dark,green,light)))
        p.line(37,92,44,92,'#766040');return p
    if species=='clover':
        for i in range(2+stage*3):
            x=40+rng.randrange(-14,15);y=90-rng.randrange(0,5)
            stem(40,92,x,y);stem(x,y,x-1,y-4)
            for dx,dy in ((-3,-2),(2,-2),(0,-5)):
                p.oval(x+dx-2,y+dy-2,5,4,dark);p.oval(x+dx-1,y+dy-2,3,3,green);p.rect(x+dx,y+dy-1,1,1,vein)
        if stage>=3:
            for x,y in ((33,77),(47,81)):
                stem(x,91,x+1,y);p.oval(x-1,y-2,5,4,light if stage==3 else '#e9e4ca')
                if stage==4:p.rect(x,y-2,2,1,'#fff5df')
        return p
    if species in ('carrot','radish','lettuce','daisy'):
        if species=='carrot':
            if stage>=3:p.oval(38,89,5,3,'#c28c48');p.rect(40,89,2,1,'#e4aa58')
            for i in range(3+stage):
                endx=40+round((i-(2+stage)/2)*3*scale);endy=92-round((13+(i%3)*5)*scale)
                stem(40,91,endx,endy)
                for t in (.35,.55,.75):
                    x=round(40+(endx-40)*t);y=round(91+(endy-91)*t)
                    for side in (-1,1):
                        tipx=x+side*round(5*scale+1);tipy=y-3
                        p.line(x,y,tipx,tipy,green);p.line(tipx-side,y-2,tipx,tipy-2,light)
        elif species=='radish':
            if stage>=3:p.oval(37,89,7,3,'#b75d6d');p.rect(38,89,3,1,'#dc8e91')
            for i in range(3+stage):
                x=40+round((i-(2+stage)/2)*4*scale);y=91-round((10+(i%3)*4)*scale)
                leaf(40,91,x,y,3,green if i%2 else light,True)
        elif species=='lettuce':
            for ring in range(3):
                radius=max(3,round((16-ring*4)*scale))
                for i in range(7):
                    a=i*math.tau/7+ring*.5
                    x=40+round(math.cos(a)*radius);y=88+round(math.sin(a)*radius*.4)-ring*3
                    w=max(2,round((7-ring)*scale));h=max(3,round((8-ring)*scale))
                    p.polygon([(40,91-ring*2),(x-w,y),(x-w+1,y-h+2),(x-2,y-h+1),(x,y-h),(x+3,y-h+2),(x+w,y-h+2),(x+w,y),(x+2,y+3)],dark)
                    p.polygon([(40,90-ring*2),(x-w+1,y-1),(x-w+2,y-h+3),(x,y-h+1),(x+w-1,y-h+3),(x+w-1,y),(x+1,y+2)],(green,light,'#b3c97b')[ring])
                    p.line(40,90-ring*2,x,y-h+3,'#8faa60' if ring==0 else '#d1d995')
        else:
            for i in range(7):
                a=i*math.tau/7;leaf(40,92,40+round(math.cos(a)*10*scale),90+round(math.sin(a)*4)-2,2)
            for i in range(1 if stage<3 else 3):
                x=40+(i-1)*7;y=92-round((19-i*3)*scale)
                stem(40+(i-1)*4,91,x,y)
                if stage>=3:
                    if stage==3:p.oval(x-1,y-2,3,4,light)
                    else:flower(x,y,4,'#f4eed6','#d5ad52')
        return p
    height=round({'mint':32,'tomato':46,'sunflower':59,'calendula':28}[species]*scale)
    top=ground-height
    if species=='sunflower':
        stem(40,92,39,top,2)
        for i in range(2+stage):
            y=88-i*max(3,height//(3+stage));side=-1 if i%2 else 1
            leaf(40,y,40+side*round(12*scale),y-7,4 if stage>2 else 2,green,True)
        if stage==3:p.oval(36,top-3,8,7,green)
        if stage==4:
            flower(39,top,8,'#e8bd51','#765333');p.oval(35,top-4,9,8,'#735039')
            for x,y in ((37,-2),(40,-1),(38,1),(41,2)):p.rect(x,top+y,1,1,'#b99653')
        return p
    # Multiple unequal stems and pinnate/paired leaves replace the generic sprout.
    for j in range(1 if stage==1 else 3):
        tipx=40+(j-1)*round(10*scale);tipy=top+j*3
        stem(40,92,tipx,tipy,2 if species=='tomato' else 1)
        for i in range(2+stage):
            t=(i+1)/(3+stage);x=round(40+(tipx-40)*t);y=round(92+(tipy-92)*t)
            for side in (-1,1):
                leaf(x,y,x+side*round((8 if species=='tomato' else 6)*scale+2),y-4,2 if species!='tomato' else 3,green if i%2 else light,True)
        if species=='mint' and stage==4:
            for k in range(4):p.rect(tipx-1,tipy-k*2,3,1,'#b5a6c1')
        elif species=='calendula' and stage>=3:
            if stage==3:p.oval(tipx-2,tipy-3,4,4,green)
            else:flower(tipx,tipy,5,'#e9a34e','#b47b36')
        elif species=='tomato' and stage>=2:
            x=tipx+4;y=tipy+10
            if stage==2:flower(x,y,2,'#e4c467','#cda347')
            else:
                for dx,dy in ((0,0),(-4,7)):
                    p.oval(x+dx-2,y+dy,5,5,'#ba614b' if stage==4 else '#7b994d')
                    p.rect(x+dx-1,y+dy+1,1,1,'#eca581' if stage==4 else light)
                    p.line(x+dx-2,y+dy,x+dx+2,y+dy,dark)
    return p
