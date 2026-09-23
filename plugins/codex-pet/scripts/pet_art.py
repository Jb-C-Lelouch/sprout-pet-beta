"""Hand-authored 64px character contours and eight-pose garden animations."""
import math


def draw_pet(mode,frame,theme,rank=0):
    from pixel_art import Pixels
    p=Pixels(64,64);f=frame%8
    ink='#494535';edge='#8b784f';skin={'苔绿':'#efdbac','樱粉':'#ebc6be','夜色':'#c7d2b1'}[theme]
    cream={'苔绿':'#fff0cb','樱粉':'#ffe4d8','夜色':'#e5ebce'}[theme]
    shade={'苔绿':'#c3a276','樱粉':'#bb8f8b','夜色':'#91a88b'}[theme]
    green='#729447';leaflight='#c3ce78';leafdark='#3f5933'
    body_ramps={
        '苔绿':('#92734c','#b28e5d','#cfaa72','#e4c38d','#f0d6a3','#f8e4b9','#fff0ce'),
        '樱粉':('#95705f','#b08a76','#caa18c','#dfb7a2','#edcbb7','#f6ddca','#ffeadd'),
        '夜色':('#637666','#7f947b','#9eae8b','#b8c7a1','#cfdbb7','#e0e8cb','#eef1dc'),
    }
    def round_volume(points,center,radii):
        # Quantized curved lighting is shared by every pose; never a separate chest patch.
        poly(points,ink)
        mask=[[v for v in row] for row in p.rows]
        cx,cy=center;rx,ry=radii;tones=body_ramps[theme]
        for yy in range(max(0,cy-ry-2+oy),min(p.h,cy+ry+3+oy)):
            for xx in range(max(0,cx-rx-2+ox),min(p.w,cx+rx+3+ox)):
                if mask[yy][xx]!=ink:continue
                inside=all(0<=xx+dx<p.w and 0<=yy+dy<p.h and mask[yy+dy][xx+dx]==ink for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)))
                if not inside:
                    if yy<cy-ry//2+oy and xx<cx+rx//2+ox:p.rect(xx,yy,1,1,edge)
                    continue
                nx=(xx-ox-cx)/rx;ny=(yy-oy-cy)/ry
                nz=math.sqrt(max(0,1-nx*nx-ny*ny))
                illumination=max(0,min(1,.30+nz*.66-nx*.20-ny*.25))
                color=tones[min(6,int(illumination*6.99))]
                p.rect(xx,yy,1,1,color)
    wave=(0,1,2,2,1,0,-1,-1)[f]
    working=mode in ('dig','water','fertilize','harvest','archive')
    bend=(0,1,3,4,4,2,1,0)[f] if mode in ('dig','harvest','archive') else 0
    bob=(0,-1,-2,-1,0,-1,-2,-1)[f] if mode=='walk' else (1 if f in (2,3,4) else 0)
    ox=-bend//2;oy=bob+bend
    def poly(points,color):p.polygon([(x+ox,y+oy) for x,y in points],color)
    def line(x,y,xx,yy,color,width=1):p.line(x+ox,y+oy,xx+ox,yy+oy,color,width)
    def rect(x,y,w,h,color):p.rect(x+ox,y+oy,w,h,color)
    def leaf(points,vein):
        poly(points,leafdark)
        cx=sum(x for x,y in points)/len(points);cy=sum(y for x,y in points)/len(points)
        poly([(round(cx+(x-cx)*.78),round(cy+(y-cy)*.74)) for x,y in points],green)
        line(*vein,leaflight)
        x,y,xx,yy=vein
        for t in (.25,.45,.65,.82):
            vx=round(x+(xx-x)*t);vy=round(y+(yy-y)*t)
            side=-1 if xx<x else 1
            line(vx,vy,vx+side*3,vy-3,'#a2b65c')
            line(vx,vy,vx-side*2,vy+1,'#547735')
        line(x,y,xx,yy,leaflight)
    def crown(offset=0):
        offset+=1 if (f-1)%8 in (2,3,4) and mode=='rest' else 0
        def branch(x,y,xx,yy):line(x,y+offset,xx,yy+offset,leafdark,2)
        def blade(points,veins):leaf([(x,y+offset) for x,y in points],(veins[0],veins[1]+offset,veins[2],veins[3]+offset))
        branch(32,23,33,14)
        if rank<2:
            blade([(32,18),(24,17),(17,12),(15,6),(23,6),(30,10),(34,15)],(32,16,19,9))
            blade([(34,16),(36,8),(43,3),(51,3),(49,10),(42,15)],(35,14,47,6))
            if rank==1:
                blade([(32,21),(22,23),(15,20),(12,15),(21,14),(28,17)],(30,20,16,17))
                blade([(34,21),(41,23),(51,21),(55,15),(47,14),(39,17)],(36,20,51,17))
                for x,y in ((30,8),(33,6),(36,9),(33,12)):rect(x,y+offset,4,4,'#e8acb5')
                rect(33,10+offset,2,2,'#f8d580')
        else:
            branch(33,22,24,13);branch(33,22,44,12);branch(33,20,34,5)
            for x,y,side in ((23,19,-1),(24,13,-1),(35,12,-1),(42,14,1),(43,20,1)):
                blade([(x,y+3),(x+side*10,y+4),(x+side*16,y),(x+side*13,y-6),(x+side*5,y-5)],(x,y+1,x+side*12,y-2))
            if rank==2:
                for x,y in ((20,17),(46,16),(34,6)):rect(x,y+offset,3,3,'#e2bd71')
            else:
                for x,y,r in ((33,8,5),(17,20,3),(51,18,3)):
                    pts=[]
                    for i in range(10):
                        a=-math.pi/2+i*math.pi/5;radius=r if i%2==0 else r*.45
                        pts.append((round(x+math.cos(a)*radius),round(y+offset+math.sin(a)*radius)))
                    poly(pts,'#e9bf59');rect(x,y+offset,1,1,'#fff2bf')
    sleeping=mode=='sleep' or (mode=='rest' and frame>=8)
    if sleeping:
        oy=1 if f in (3,4,5) else 0
        round_volume([(15,46),(19,39),(27,36),(40,37),(49,43),(52,51),(48,56),(21,57),(15,53)],(33,47),(20,12))
        line(23,46,25,48,ink);line(25,48,28,46,ink)
        line(36,46,38,48,ink);line(38,48,41,46,ink)
        rect(30,50,3,1,edge);rect(19,49,4,2,'#dba48d')
        crown(16)
        p.line(52,24-wave,56,24-wave,cream);p.line(56,24-wave,52,28-wave,cream);p.line(52,28-wave,56,28-wave,cream)
        return p
    # A soft round body; short limbs peek out without clothing or chest props.
    swing=(0,2,3,1,0,-2,-3,-1)[f] if mode=='walk' else 0
    poly([(48,37),(53,37+swing),(56,40+swing),(56,44+swing),(53,47+swing),(49,45)],ink)
    poly([(50,39),(53,39+swing),(54,41+swing),(54,44+swing),(52,45+swing),(49,43)],skin)
    for x,dy in ((25,swing),(43,-swing)):
        p.polygon([(x-3,53),(x+3,53),(x+4,57+dy//2),(x+2,59+dy//2),(x-3,59+dy//2),(x-5,57)],ink)
        p.polygon([(x-2,54),(x+2,54),(x+2,57+dy//2),(x,58+dy//2),(x-3,57+dy//2)],shade)
        p.rect(x-2,55+dy//2,3,1,cream)
    round_volume([(28,21),(38,21),(45,24),(51,30),(54,37),(54,44),(51,50),(46,54),(39,57),(28,57),(21,54),(16,49),(13,42),(14,34),(18,28),(23,24)],(34,39),(21,20))
    line(21,29,24,27,cream);rect(20,31,1,3,cream)
    crown()
    if rank>=2:rect(42,27,2,2,'#e9c779');rect(44,29,1,2,cream)
    # Eyelids, eye highlights, cheek freckles and a tiny offset mouth.
    for x in (25,40):
        if mode in ('petting','stretch') or (mode=='eat' and f%3==0) or (mode=='rest' and f==7):line(x,37,x+1,36,ink);line(x+1,36,x+3,37,ink)
        else:
            rect(x,34,3,5,ink);rect(x,34,1,2,'#fff8dd');rect(x+2,38,1,1,edge)
        rect(x-3,40,6,2,'#e4ad91');rect(x-2,39,4,1,'#edc0a2');rect(x-1,41,3,1,'#d89b7d')
    line(31,41,33,42,edge);line(33,42,35,41,edge)
    # Front arm follows the task instead of letting a tool float next to the body.
    handx=15 if working else 16;handy=40+(bend//2 if working else -swing)
    poly([(18,42),(21,45),(handx+5,handy+4),(handx,handy+4),(handx-2,handy),(handx,handy-3)],ink)
    poly([(18,43),(20,44),(handx+4,handy+2),(handx,handy+2),(handx,handy-1)],skin)
    rect(handx,handy-1,3,1,cream)
    if mode=='petting':
        for hx,hy in ((10,18),(53,24)):
            hy-=f//2
            p.polygon([(hx,hy+1),(hx+2,hy-1),(hx+4,hy+1),(hx+6,hy-1),(hx+8,hy+1),(hx+4,hy+6)],'#d9919b')
    elif mode=='stretch':
        for hx in (10,53):
            p.line(hx,37,hx-2,29-wave,ink,3);p.line(hx,36,hx-2,29-wave,skin,2)
    elif mode=='look':
        p.rect(24,34,5,6,skin);p.rect(39,34,5,6,skin)
        for hx in (25,40):
            p.rect(hx+(1 if f<4 else -1),34,3,5,ink);p.rect(hx+(1 if f<4 else -1),34,1,1,cream)
    elif mode=='eat':
        lift=1 if f%2 else 0
        p.polygon([(25,45-lift),(35,43-lift),(40,46-lift),(38,52),(29,54),(24,50)],'#8b613e')
        p.polygon([(26,45-lift),(35,44-lift),(38,46-lift),(35,50),(28,51)],'#dfae67')
        p.oval(22,46,7,5,skin);p.oval(37,45,7,5,skin)
        p.rect(32,42,3,1+f%2,ink)
        if f in (3,4):p.rect(30,54,1,1,'#d8af6e');p.rect(36,56,1,1,'#d8af6e')
    # Tool silhouettes, contents and particles each follow an eight-pose cycle.
    if mode=='dig':
        tilt=(4,2,0,-2,-3,-1,2,4)[f];tipy=52+bend//2
        p.line(15+ox,35+oy,9+tilt,tipy,'#594936',3)
        p.line(16+ox,35+oy,10+tilt,tipy,'#b7925c')
        p.polygon([(6+tilt,tipy-2),(13+tilt,tipy-1),(13+tilt,tipy+3),(9+tilt,tipy+6),(6+tilt,tipy+2)],'#59665b')
        p.line(8+tilt,tipy,10+tilt,tipy+3,'#c4c9aa')
        if f in (4,5,6):
            for x,y in ((4,52),(15,57),(5,58)):p.rect(x, y-(f-4)*2,2,2,'#aa804e')
    elif mode=='water':
        lift=(0,0,1,2,2,2,1,0)[f]
        p.polygon([(8,39-lift),(20,38-lift),(22,49-lift),(18,52-lift),(8,51-lift),(6,46-lift)],'#526655')
        p.polygon([(9,40-lift),(19,40-lift),(20,48-lift),(17,50-lift),(9,49-lift)],'#83a293')
        p.line(11,41-lift,17,41-lift,'#bdd0b0');p.line(18,39-lift,23,35-lift,'#59705b',2)
        p.line(23,35-lift,25,42-lift,'#59705b',2)
        p.polygon([(8,44-lift),(3,40-lift),(1,42-lift),(7,48-lift)],'#7b9683')
        if 2<=f<=6:
            for i in range(3):p.rect(1+i*2,44+(f+i*2)%9,1,3,'#9ed7db');p.rect(1+i*2,44+(f+i*2)%9,1,1,'#e0f0dd')
    elif mode=='fertilize':
        dy=(0,0,-2,-3,-3,-2,0,0)[f]
        p.polygon([(8,39+dy),(16,38+dy),(20,43+dy),(18,52+dy),(7,51+dy),(5,46+dy)],'#806747')
        p.polygon([(9,40+dy),(15,40+dy),(18,44+dy),(16,50+dy),(8,49+dy),(7,46+dy)],'#d2b987')
        p.line(8,42+dy,17,42+dy,'#a58c61');p.rect(11,45+dy,3,3,green)
        if 2<=f<=5:
            for i in range(4):p.rect(3+i*3,51+(f+i)%7,1,1,'#c9b174')
    elif mode in ('harvest','archive'):
        dy=(1,2,3,3,1,-1,-2,0)[f]
        p.line(7,45+dy,8,39+dy,'#876845',2);p.line(8,39+dy,19,39+dy,'#876845',2);p.line(19,39+dy,21,45+dy,'#876845',2)
        if mode=='harvest':
            p.polygon([(9,43+dy),(12,41+dy),(15,44+dy),(13,49+dy)],'#e5a358');p.line(12,43+dy,11,38+dy,green,2)
        else:
            p.rect(13,39+dy,2,8,leafdark);p.rect(10,38+dy,8,3,'#e6b0af');p.rect(12,36+dy,4,7,'#f3c5b5');p.rect(13,39+dy,2,2,'#e7c870')
        p.polygon([(5,44+dy),(23,44+dy),(21,54+dy),(8,54+dy)],'#715238')
        p.polygon([(7,46+dy),(21,46+dy),(19,52+dy),(9,52+dy)],'#ba8c52')
        for y in (47,50):p.line(8,y+dy,20,y+dy,'#e0b16a')
        for x in (10,14,18):p.line(x,46+dy,x,52+dy,'#8b633e')
    return p
