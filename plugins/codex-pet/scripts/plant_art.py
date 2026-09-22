"""Botanical pixel silhouettes with shared ground anchors and relative scale."""
import math
import random


def field_pixels():
    from pixel_art import Pixels
    p=Pixels(130,48);rng=random.Random(93)
    outline=[(3,18),(9,12),(18,13),(25,8),(39,7),(47,4),(62,7),(73,5),(87,10),(98,9),(109,14),(116,13),(123,19),(122,26),(127,31),(120,35),(114,41),(99,40),(90,44),(76,42),(63,46),(49,43),(37,44),(26,39),(15,38),(12,32),(5,29),(7,23)]
    p.polygon([(x,y+1) for x,y in outline],'#58653b')
    p.polygon(outline,'#60472f')
    p.polygon([(round(65+(x-65)*.94),round(25+(y-25)*.87)) for x,y in outline],'#765536')
    mask=[row[:] for row in p.rows]
    for _ in range(240):
        x=rng.randrange(130);y=rng.randrange(48)
        if mask[y][x]:
            w=rng.randrange(3,8);h=rng.randrange(3,6)
            for yy in range(y,min(48,y+h)):
                for xx in range(x,min(130,x+w)):
                    nx=(xx-x-w/2)/(w/2);ny=(yy-y-h/2)/(h/2)
                    if mask[yy][xx] and nx*nx+ny*ny<.9:
                        color='#9b794b' if nx<.2 and ny<-.2 else '#57412c' if ny>.4 else '#85633e'
                        p.rect(xx,yy,1,1,color)
    # Turf breaks into the rim; scattered pebbles never form a continuous border.
    for x,y in outline[::2]:
        p.line(x-2,y,x+2,y,'#657a43');p.line(x,y,x-1,y-3,'#819651')
        p.rect(x+2,y-2,1,2,'#a5ad68')
    for x,y in ((17,35),(103,39),(120,27),(39,8),(8,20)):
        p.oval(x,y,4,3,'#766f52');p.rect(x+1,y,2,1,'#aca084')
    return p


def draw_plant(species,stage):
    from pixel_art import Pixels
    p=Pixels(80,96);rng=random.Random(species);cx=40;ground=92
    dark='#3c5931';green='#63883c';light='#95b252';vein='#c0cd7b'
    # Compressed garden scale: groundcover < rosettes < herbs < tall annuals < tree.
    # Crop maturity is harvest foliage, not a second-year flowering stalk.
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
        p.polygon(inner,color)
        p.line(x,y,xx,yy,light)
        if length>7:
            for t in (.28,.48,.68):
                vx=x+dx*t;vy=y+dy*t
                for side in (-1,1):
                    p.line(round(vx),round(vy),round(vx+dx*.14+nx*width*.65*side),round(vy+dy*.14+ny*width*.65*side),light if side<0 else '#4d722f')
            p.line(round(x+dx*.35),round(y+dy*.35),round(x+dx*.85),round(y+dy*.85),vein)
        if serrated:
            for t in (.35,.6):
                a=round(x+dx*t);b=round(y+dy*t)
                for s in (-1,1):p.line(a,b,round(a+nx*width*s+dx*.12),round(b+ny*width*s+dy*.12),color)
    def flower(x,y,r,color,center):
        # Discrete tapered petals leave a readable rim around the flower centre.
        for i in range(12):
            angle=i*math.tau/12
            dx=math.cos(angle);dy=math.sin(angle)*.85
            xx=round(x+dx*r);yy=round(y+dy*r)
            p.line(x,y,xx,yy+1,'#b88646' if color!='#f4eed6' else '#b8ac8a',2)
            p.line(x,y,xx,yy,color,2)
            p.rect(xx,yy,1,1,'#fff4d9' if color=='#f4eed6' else '#f8cf7b')
        p.oval(x-1,y-1,3,3,center);p.rect(x-1,y-1,1,1,'#f2d47c')
    if stage==0:
        p.line(37,92,43,92,'#795a35');p.rect(38,91,1,1,'#a78652');p.rect(41,92,2,1,'#b09661');return p
    if stage==1 and species!='clover':
        stem(40,92,40,86)
        width=1 if species=='carrot' else 2
        leaf(40,87,34,81,width,green);leaf(40,87,46,79,width,light)
        return p
    if species=='cherry':
        # A spreading crown supported by low forks, with stable lobes at every age.
        height=round(84*scale);top=ground-height
        def point(dx,dy):return (cx+round(dx*scale),top+round(dy*scale))
        def branch(points,color,width):
            for a,b in zip(points,points[1:]):p.line(*point(*a),*point(*b),color,max(1,round(width*scale)))
        branch([(0,84),(-2,64),(0,46),(-7,29)],'#644c3c',6)
        branch([(-1,82),(-3,64),(-1,47),(-8,30)],'#ac8256',2)
        for pts in [[(0,61),(-13,48),(-24,32)],[(-1,48),(15,37),(25,20)],[(0,43),(3,24),(-2,12)]]:
            branch(pts,'#6d503e',3);branch(pts,'#97714c',1)
        for dx,dy in [(-4,80),(-2,69),(0,59)]:
            x,y=point(dx,dy);p.line(x,y,x+2,y,'#604a39')
        lobes=[(-19,31,15,13),(18,28,16,14),(-7,15,19,14),
               (11,13,17,12),(-25,22,10,11),(27,23,9,10),
               (0,30,19,16),(-15,40,13,11),(17,39,13,11),(-1,44,14,10)]
        palette=('#a66d86','#be8097','#d798ab','#e8afbb','#f3c9cf','#ffe3dd') if stage==4 else ('#425b36','#597441','#718c4c','#8ba45d','#a7b975','#c5cd91')
        for i,(dx,dy,rx,ry) in enumerate(lobes):
            x,y=point(dx,dy);rx=max(3,round(rx*scale));ry=max(3,round(ry*scale))
            # Overlapping scallops establish connected masses before blossom texture.
            p.oval(x-rx,y-ry,rx*2,ry*2,palette[0])
            p.oval(x-rx+1,y-ry,rx*2-2,ry*2-3,palette[2])
            p.oval(x-rx+2,y-ry,rx+max(2,rx//2),ry+max(2,ry//2),palette[3])
            for j in range(22):
                ang=rng.random()*math.tau;r=math.sqrt(rng.random())*.94
                xx=round(x+math.cos(ang)*rx*r);yy=round(y+math.sin(ang)*ry*r)
                tone=4 if yy<y-2 else 2 if xx<x else 1
                w=max(2,round((3+rng.randrange(3))*scale))
                p.oval(xx-w//2,yy-w//2,w+1,w,palette[tone])
                if stage==4 and j%3==0:
                    p.rect(xx,yy-1,1,3,palette[5]);p.rect(xx-1,yy,3,1,palette[4])
                    p.rect(xx,yy,1,1,'#d7a275')
                elif stage==3 and j%4==0:p.rect(xx,yy,2,2,'#d5a1aa')
        p.line(35,92,46,92,'#766040')
        if stage==4:
            for x,y in ((29,91),(34,89),(48,91),(52,90)):
                p.rect(x,y,2,1,'#e6b3be')
        return p
    if species=='clover':
        for i in range(2+stage*3):
            x=40+rng.randrange(-14,15);y=90-rng.randrange(0,5)
            stem(40,92,x,y);stem(x,y,x-1,y-4)
            for dx,dy in ((-3,-2),(2,-2),(0,-5)):
                p.oval(x+dx-2,y+dy-2,5,4,dark);p.oval(x+dx-1,y+dy-2,3,3,green)
                p.line(x+dx-1,y+dy-1,x+dx,y+dy,vein);p.rect(x+dx+1,y+dy-1,1,1,light)
        if stage>=3:
            for x,y in ((33,77),(47,81)):
                stem(x,91,x+1,y);p.oval(x-1,y-2,5,4,light if stage==3 else '#e9e4ca')
                if stage==4:p.rect(x,y-2,2,1,'#fff5df')
        return p
    if species in ('carrot','radish','lettuce','daisy'):
        if species=='carrot':
            # Carrot leaves are divided twice: main rachis, pinnae, tiny pinnules.
            shoots=[(-15,18), (14,21), (-8,26), (7,29), (-2,33), (-18,14), (18,15)]
            count={2:3,3:5,4:7}[stage]
            for i,(dx,height) in enumerate(shoots[:count]):
                endx=40+round(dx*scale);endy=91-round(height*scale)
                stem(40,91,endx,endy)
                dx=endx-40;dy=endy-91;length=max(1,math.hypot(dx,dy));nx=-dy/length;ny=dx/length
                for t in (.34,.48,.62,.76,.88):
                    x=40+dx*t;y=91+dy*t
                    spread=(1-t)*9*scale+1
                    for side in (-1,1):
                        tipx=x+nx*spread*side+dx*.08;tipy=y+ny*spread*side+dy*.08
                        p.line(round(x),round(y),round(tipx),round(tipy),green)
                        for u in (.45,.8):
                            bx=x+(tipx-x)*u;by=y+(tipy-y)*u
                            p.line(round(bx),round(by),round(bx+dx/length*3),round(by+dy/length*3),light if i%2 else '#789b44')
                            p.rect(round(bx),round(by)+1,1,1,dark)
                        p.rect(round(tipx),round(tipy),1,1,vein)
            if stage>=3:
                p.oval(37,89,7,3,'#bb7736');p.rect(38,89,4,1,'#e6a651');p.rect(40,91,2,1,'#8e6230')
        elif species=='radish':
            if stage>=3:p.oval(36,88,9,4,'#ac4e57');p.rect(37,88,5,2,'#d87878');p.rect(38,88,2,1,'#efa89a')
            for i in range(3+stage):
                x=40+round((i-(2+stage)/2)*4*scale);y=91-round((10+(i%3)*4)*scale)
                leaf(40,91,x,y,4,green if i%2 else light,True)
                if stage>=3:
                    leaf(40,89,round((40+x)/2)-3,round((91+y)/2)-2,2,green,True)
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
                    p.line(x-w+2,y-h+3,x-1,y-h+2,'#b7ce7e');p.line(x+2,y-h+3,x+w-1,y-h+4,'#a5c071')
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
    height=round({'mint':32,'tomato':54,'sunflower':68,'calendula':34}[species]*scale)
    top=ground-height
    if species=='sunflower':
        headx=37;heady=top+2
        stem(40,92,41,top+18,3 if stage>=3 else 2)
        stem(41,top+18,headx,heady,3 if stage>=3 else 2)
        for i in range(2+stage):
            y=87-i*max(4,height//(3+stage));side=-1 if i%2 else 1
            reach=round((16-i*.9)*scale);tipx=40+side*reach;tipy=y-4
            stem(40,y,40+side*4,y-3)
            # Broad heart-shaped leaves with pointed tips and branching veins.
            base=40+side*3;w=max(3,round((7-i*.35)*scale))
            p.polygon([(base,y-2),(base+side*3,y-w),(tipx-side*3,y-w),(tipx,tipy),(tipx-side*3,y+3),(base+side*4,y+2)],dark)
            p.polygon([(base+side,y-2),(base+side*4,y-w+1),(tipx-side*3,y-w+1),(tipx-side,tipy),(tipx-side*4,y+1)],green)
            p.line(base,y-2,tipx,tipy,light)
            p.line(base+side*5,y-2,base+side*7,y-w+1,light)
        if stage==3:
            p.oval(headx-5,heady-6,11,12,dark)
            p.oval(headx-4,heady-6,8,9,green)
            for dx in (-3,0,3):p.line(headx,heady+4,headx+dx,heady-4,light)
        if stage==4:
            for i in range(18):
                angle=i*math.tau/18;dx=math.cos(angle);dy=math.sin(angle)*.9
                nx=-math.sin(angle);ny=math.cos(angle)
                def at(r,w=0):return (round(headx+dx*r+nx*w),round(heady+dy*r+ny*w))
                p.polygon([at(5,-2),at(10,-2),at(14),at(10,2),at(5,2)],'#bc7e32')
                p.polygon([at(6,-1),at(10,-1),at(13),at(10,1),at(6,1)],'#edb94e')
                p.line(*at(8),*at(12),'#ffe091')
            p.oval(headx-7,heady-6,15,13,'#654735')
            p.oval(headx-6,heady-5,12,10,'#94683b')
            p.oval(headx-4,heady-3,9,8,'#765237')
            for yy in range(-4,5,2):
                for xx in range(-5,6,2):
                    if xx*xx/36+yy*yy/25<1:
                        p.rect(headx+xx+(yy%3==0),heady+yy,1,1,'#c99b56' if yy<0 else '#aa7b43')
        return p
    # Multiple unequal stems and pinnate/paired leaves replace the generic sprout.
    for j in range(1 if stage==1 else 3):
        tipx=40+(j-1)*round(10*scale);tipy=top+j*3
        stem(40,92,tipx,tipy,2 if species=='tomato' else 1)
        for i in range(2+stage//2):
            t=(i+1)/(3+stage//2);x=round(40+(tipx-40)*t);y=round(92+(tipy-92)*t)
            for side in (-1,1):
                leaf(x,y,x+side*round((8 if species=='tomato' else 6)*scale+2),y-4,2 if species!='tomato' else 3,green if i%2 else light,True)
        if species=='mint' and stage==4:
            for k in range(5):
                p.rect(tipx-1,tipy-k*2,3,1,'#aa93ac');p.rect(tipx,tipy-k*2,1,1,'#d6bfcc')
        elif species=='calendula' and stage>=3:
            if stage==3:p.oval(tipx-2,tipy-3,4,4,green)
            else:flower(tipx,tipy,5,'#e9a34e','#b47b36')
        elif species=='tomato' and stage>=2:
            x=tipx+4;y=tipy+10
            if stage==2:flower(x,y,2,'#e4c467','#cda347')
            else:
                for dx,dy in ((0,0),(-4,7)):
                    p.oval(x+dx-3,y+dy,7,6,'#9b4939' if stage==4 else '#4d7333')
                    p.oval(x+dx-2,y+dy,5,4,'#d47549' if stage==4 else '#8fa652')
                    p.rect(x+dx-1,y+dy+1,2,1,'#f0b16b' if stage==4 else vein)
                    p.line(x+dx-2,y+dy,x+dx+2,y+dy,dark);p.rect(x+dx,y+dy-1,1,2,green)
    return p
