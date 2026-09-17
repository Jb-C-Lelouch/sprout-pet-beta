"""Small code-native pixel sprites; build once, retain PhotoImages between frames."""
import tkinter as tk
import random
import math
from pathlib import Path


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

    def photo(self,master,flip=False):
        image=tk.PhotoImage(master=master,width=self.w,height=self.h)
        for y,row in enumerate(self.rows):
            if flip:row=row[::-1]
            start=0
            while start<self.w:
                color=row[start];end=start+1
                while end<self.w and row[end]==color:end+=1
                if color:image.put(color,to=(start,y,end,y+1))
                start=end
        return image.zoom(2)

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
    return draw_plant(species,stage)


class PixelArt:
    def __init__(self,master):
        self.master=master;self.cache={}
        source=tk.PhotoImage(master=master,data=(Path(__file__).parent.parent/'assets/pixel/garden.png').read_bytes())
        self.background=source.subsample(2)
        from plant_art import field_pixels
        self.field=field_pixels().photo(master)

    def pet(self,mode,frame,theme,left=False,rank=0):
        key=('pet',mode,frame,theme,left,rank)
        if key not in self.cache:self.cache[key]=pet_pixels(mode,frame,theme,rank).photo(self.master,flip=not left)
        return self.cache[key]

    def plant(self,species,progress):
        stage=min(4,int(max(0,progress)*4));key=(species,stage)
        if key not in self.cache:self.cache[key]=plant_pixels(species,stage).photo(self.master)
        return self.cache[key]
