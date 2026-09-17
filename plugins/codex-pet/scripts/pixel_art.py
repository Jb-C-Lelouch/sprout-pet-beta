"""Small code-native pixel sprites; build once, retain PhotoImages between frames."""
import tkinter as tk
import random
import math
from pathlib import Path
from content_catalog import catalog, resource


class Pixels:
    def __init__(self,w=48,h=48):
        self.w,self.h=w,h;self.rows=[[None]*w for _ in range(h)]

    def rect(self,x,y,w,h,color):
        for yy in range(max(0,y),min(self.h,y+h)):
            for xx in range(max(0,x),min(self.w,x+w)):self.rows[yy][xx]=color

    def oval(self,x,y,w,h,color):
        for yy in range(max(0,y),min(self.h,y+h)):
            for xx in range(max(0,x),min(self.w,x+w)):
                if ((xx+.5-x-w/2)/(w/2))**2+((yy+.5-y-h/2)/(h/2))**2<=1:self.rows[yy][xx]=color

    def photo(self,master,flip=False,scale=2):
        image=tk.PhotoImage(master=master,width=self.w,height=self.h)
        for y,row in enumerate(self.rows):
            if flip:row=row[::-1]
            start=0
            while start<self.w:
                color=row[start];end=start+1
                while end<self.w and row[end]==color:end+=1
                if color:image.put(color,to=(start,y,end,y+1))
                start=end
        return image.zoom(scale)

    def line(self,x1,y1,x2,y2,color,width=1):
        steps=max(abs(x2-x1),abs(y2-y1),1)
        for i in range(steps+1):
            self.rect(round(x1+(x2-x1)*i/steps),round(y1+(y2-y1)*i/steps),width,width,color)

    def polygon(self,points,color):
        for y in range(max(0,min(p[1] for p in points)),min(self.h,max(p[1] for p in points)+1)):
            hits=[]
            for (x1,y1),(x2,y2) in zip(points,points[1:]+points[:1]):
                if min(y1,y2)<=y+.5<max(y1,y2):hits.append(x1+(y+.5-y1)*(x2-x1)/(y2-y1))
            hits.sort()
            for a,b in zip(hits[::2],hits[1::2]):self.rect(math.ceil(a),y,math.ceil(b)-math.ceil(a),1,color)


def pet_pixels(mode,frame,theme,rank=0):
    from pet_art import draw_pet
    return draw_pet(mode,frame,theme,rank)


def plant_pixels(species,stage):
    from plant_art import draw_plant
    visual=catalog().plants[species]['visual']
    if visual['kind']!='procedural':raise ValueError('Use PixelArt.plant for PNG content')
    return draw_plant(visual['variant'],stage)


class PixelArt:
    def __init__(self,master,content=None):
        self.master=master;self.cache={};self.content=content or catalog()
        scene=self.content.scenery['garden'];background=scene['background']
        source=tk.PhotoImage(master=master,data=resource(scene['directory'],background['file']).read_bytes())
        self.background=source.subsample(background['subsample'])
        self.background_position=background['position'];self.field_position=scene['field']['position']
        from plant_art import field_pixels
        self.field=field_pixels().photo(master)

    def pet(self,mode,frame,theme,left=False,rank=0):
        key=('pet',mode,frame,theme,left,rank)
        if key not in self.cache:self.cache[key]=pet_pixels(mode,frame,theme,rank).photo(self.master,flip=not left)
        return self.cache[key]

    def _png(self,pack,filename,visual,flip=False):
        key=('png',str(pack['directory']),filename,visual['scale'],flip)
        if key not in self.cache:
            source=tk.PhotoImage(master=self.master,data=resource(pack['directory'],filename).read_bytes())
            if flip:source=source.subsample(-1,1)
            self.cache[key]=source.zoom(visual['scale'])
        return self.cache[key]

    def pet_frame(self,mode,elapsed,theme,left,level,pet='sprout'):
        pack=self.content.pets[pet];form=self.content.pet_form(level,pet)
        visual=form.get('visual',pack['visual'])
        action='sleep' if mode=='rest' and elapsed>2 else mode
        animation=visual['actions'][action]
        index=int(elapsed*1000/animation['frame_ms'])
        index=index%len(animation['frames']) if animation['loop'] else min(index,len(animation['frames'])-1)
        frame=animation['frames'][index]
        if visual['kind']=='png':
            image=self._png(pack,frame,visual,flip=not left)
        else:
            key=('pet-pack',pet,form['id'],action,frame,theme,left)
            if key not in self.cache:
                self.cache[key]=pet_pixels('rest' if action=='sleep' else action,frame,theme,form['rank']).photo(self.master,flip=not left,scale=visual['scale'])
            image=self.cache[key]
        anchor=list(visual['anchor'])
        if not left:anchor[0]=visual['size'][0]-anchor[0]
        return image,tuple(n*visual['scale'] for n in anchor)

    def plant_anchor(self,species):
        visual=self.content.plants[species]['visual']
        return tuple(n*visual['scale'] for n in visual['anchor'])

    def plant(self,species,progress):
        stage=min(4,int(max(0,progress)*4));key=(species,stage)
        if key not in self.cache:
            pack=self.content.plants[species];visual=pack['visual']
            if visual['kind']=='png':self.cache[key]=self._png(pack,visual['files'][visual['stages'][stage]],visual)
            else:
                from plant_art import draw_plant
                self.cache[key]=draw_plant(visual['variant'],stage).photo(self.master,scale=visual['scale'])
        return self.cache[key]
