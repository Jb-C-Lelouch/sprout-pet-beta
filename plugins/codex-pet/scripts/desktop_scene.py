"""The main UI is a living garden. Click its pet for a contextual attribute card."""
from contextlib import closing
import math
import os
import random
import sqlite3
import time
import tkinter as tk
from desktop import DesktopPet
import garden
import botany
from i18n import tr,choose
from garden_motion import Gardener,SPOTS
from pixel_art import PixelArt
from arrangement import Arrangement
from garden_ui import rounded,GardenPanel,GardenMenu


class GardenScene(Arrangement,DesktopPet):
    def __init__(self,root,directory):
        self.arranging=False;self.arrange_selected=None;self.arrange_note='';self.decor_images={}
        self.interaction=None;self.interaction_start=0.;self.interaction_until=0.;self.next_idle=time.monotonic()+15;self.idle_turn=0;self.snack_panel=None
        self.brain=Gardener();self.scene=None;self.proposal=None;self.auto_enabled=True
        self.card_open=False;self.last_frame=time.monotonic();self.small_image=None;self.image_source=None
        self.scene_error='';self.hint_until=time.monotonic()+14
        self.journal=None;self.menu_window=None;self.plant_window=None
        self.pixel_art=PixelArt(root)
        super().__init__(root,directory)
        root.title('小芽 · 桌面花园')
        root.unbind('<Escape>');root.bind('<Escape>',self.escape)

    def layout(self):
        self.width,self.height=(180,150) if self.settings.get('compact') else (760,420)
        x=max(0,min(self.settings.get('x',self.root.winfo_screenwidth()-790),self.root.winfo_screenwidth()-self.width))
        y=max(0,min(self.settings.get('y',self.root.winfo_screenheight()-465),self.root.winfo_screenheight()-self.height))
        self.root.geometry(f'{self.width}x{self.height}+{x}+{y}')
        if os.name=='nt':self.root.attributes('-transparentcolor','#364523')
        self.render()

    def refresh(self):
        try:
            with closing(sqlite3.connect((self.directory/'pet.sqlite3').resolve().as_uri()+'?mode=ro',uri=True,timeout=.15)) as db:
                db.execute('BEGIN')
                self.scene=garden.snapshot(db);self.proposal=garden.work_plan(db)
                self.auto_enabled=bool(db.execute('SELECT enabled FROM garden_autonomy WHERE id=1').fetchone()[0])
            self.scene_error=''
        except (sqlite3.Error,OSError,ValueError,KeyError):self.scene_error='花园暂不可读，正在重试'
        super().refresh()

    def colors(self):
        return {'苔绿':('#c4d5a4','#a4bd83','#719460','#e5d3aa','#9dcac4'),
                '樱粉':('#d9d9b4','#bbc391','#849f71','#eddbbb','#abd1cd'),
                '夜色':('#566e60','#435d50','#314b43','#9b927b','#588a91')}[self.settings['theme']]

    def render(self):
        if self.root.state() in ('withdrawn','iconic'):return
        c=self.canvas;c.delete('all')
        c.configure(bg='#364523' if os.name=='nt' else self.theme['bg'])
        if self.settings.get('compact'):
            self.draw_pet();return
        c.create_image(*self.pixel_art.background_position,image=self.pixel_art.background,anchor='nw',tags='landscape')
        c.create_image(*self.pixel_art.field_position,image=self.pixel_art.field,anchor='nw',tags='landscape')
        for x,y,title in [(123,166,'花园'),(402,294,'菜畦')]:
            c.create_rectangle(x-26,y-9,x+26,y+9,fill='#82623e',outline='#51462d',tags='landscape')
            c.create_text(x,y,text=tr(title,self.settings['language']),font=('Microsoft YaHei UI',9),fill='#ffedc8',tags='landscape')
        self.draw_decorations()
        if self.scene:
            for plant in sorted(self.scene['plots'],key=lambda p:SPOTS[p['plot']][1]):
                if plant['species']:self.draw_plant(plant)
        self.draw_pet()
        if self.card_open:self.draw_card()
        if self.arranging:self.draw_arrange()

    def draw_plant(self,p):
        x,y=SPOTS[p['plot']]
        image=self.pixel_art.plant(p['species'],p['progress'])
        ax,ay=self.pixel_art.plant_anchor(p['species'])
        self.canvas.create_image(x-ax,y-ay,image=image,anchor='nw',tags='plant'+str(p['plot']))

    def draw_pet(self):
        c=self.canvas;c.delete('avatar');c.delete('visitors');c.delete('bubble')
        if not hasattr(self,'settings'):return
        compact=self.settings.get('compact',False)
        x,y=(90,112) if compact else (self.brain.x,self.brain.y)
        active=self.interaction if time.monotonic()<self.interaction_until else None
        mode=active or self.brain.mode
        if mode=='finish':mode='rest'
        bob=math.sin(self.frame/(2 if mode=='walk' else 10))*(2 if mode=='walk' else 1)
        c.create_oval(x-21,y-4,x+21,y+6,fill=self.colors()[1],outline='',tags='avatar')
        py=y-27+bob
        if self.image:
            if self.image_source is not self.image:
                self.image_source=self.image;self.small_image=self.image.subsample(2)
            c.create_image(x,py-5,image=self.small_image,tags='avatar')
        else:
            left=self.brain.target[0]<x if mode=='walk' else True
            level=self.data['level'] if self.data else 1
            sprite,(ax,ay)=self.pixel_art.pet_frame(mode,time.monotonic()-self.interaction_start if active else self.brain.elapsed,self.settings['theme'],left,level)
            c.create_image(round(x/2)*2-ax,round(y/2)*2-ay,image=sprite,anchor='nw',tags='avatar')
        if self.scene and not compact:
            for p in self.scene['plots']:
                if p['species'] and SPOTS[p['plot']][1]>y:c.tag_raise('plant'+str(p['plot']))
            unlocked={v['id'] for v in self.scene['visitors'] if v['discovered']}
            if 'butterfly' in unlocked:
                bx=250+math.sin(self.frame/75)*125
                by=160+math.cos(self.frame/38)*16+math.sin(self.frame/9)*2
                c.create_image(round(bx),round(by),image=self.pixel_art.butterfly(self.frame//2),tags='visitors')
            if 'sparrow' in unlocked:
                sx=537+math.sin(self.frame/120)*18
                c.create_image(round(sx),328,image=self.pixel_art.sparrow(self.frame//5),tags='visitors')
        if compact:
            c.create_text(90,132,text=choose(self,'右键：花园 / 投喂','Right-click: garden / snack'),font=('Microsoft YaHei UI',8),fill=self.theme['ink'],tags='bubble')
            return
        hint=self.scene_error or self.time_error or (self.message if self.notice_until>time.monotonic() else '')
        if not hint and mode in ('dig','water','fertilize','harvest','archive'):
            hint={'dig':'正在播种','water':'正在浇水','fertilize':'正在施肥','harvest':'正在收获','archive':'正在收藏'}[mode]
        if not hint and time.monotonic()<self.hint_until:hint='点点小芽，看看它的成长'
        if hint and not self.card_open and not self.arranging:
            rounded(c,x-118,py-120,236,38,self.theme['bg'],12,'bubble')
            c.create_text(x,py-101,text=tr(hint,self.settings['language']),width=224,font=('Microsoft YaHei UI',9),fill=self.theme['ink'],tags='bubble')
        c.tag_raise('card')
        if self.arranging:c.tag_raise('layout')

    def draw_card(self):
        c=self.canvas;c.delete('card')
        x=max(18,min(self.brain.x+40,460));y=max(12,min(self.brain.y-245,154));w=280
        rounded(c,x+3,y+5,w,255,self.theme['card'],22,'card')
        rounded(c,x,y,w,255,self.theme['bg'],22,'card')
        def label(dy,text,size=10):self.text(x+20,y+dy,text,size,tags=('card',))
        if self.data:
            d=self.data;g=d.get('growth') or {};exact=g.get('total_xp',d['experience'])-5*d['level']*(d['level']-1)
            label(29,'小芽',21)
            rounded(c,x+196,y+17,64,27,self.theme['card'],12,'card')
            self.text(x+228,y+30,f"Lv.{d['level']}",10,anchor='center',tags='card')
            label(58,d['form']+'  ·  花园里的小小伙伴',9)
            label(81,f"储存成长 {exact:,.1f} 经验" if d['at_level_cap'] else f"成长 {exact:.1f} / {d['next_level_cost']}",10)
            rounded(c,x+20,y+97,240,6,self.theme['card'],3,'card')
            ratio=1 if d['at_level_cap'] else min(1,exact/d['next_level_cost'])
            if ratio>0:rounded(c,x+20,y+97,max(2,240*ratio),6,self.theme['accent'],3,'card')
            energy=d.get('energy') or {'current':0,'cap':100}
            label(126,f"精力 {energy['current']:.1f} / 100",12)
            label(152,'有精力就照料，休息时也在成长。',9)
            plots=(self.scene or {}).get('plots',[])
            label(178,f"花园 {sum(bool(p['species']) for p in plots if p['plot']<=6)} 株 · 菜畦 {sum(bool(p['species']) for p in plots if p['plot']>6)} 株",9)
        else:label(35,'正在读取小芽的成长…')
        for dx,caption,tag in [(20,'花园装扮','card-style'),(146,'成长足迹','card-growth')]:
            rounded(c,x+dx,y+198,114,31,self.theme['card'],11,('card',tag))
            self.text(x+dx+57,y+213,caption,9,anchor='center',tags=('card',tag))
        label(241,'点击草地收起 · 右键装扮花园',8)

    def animate(self):
        now=time.monotonic();dt=now-self.last_frame;self.last_frame=now;self.frame+=1
        inspecting=(self.plant_window and self.plant_window.window.winfo_exists()) or (self.journal and self.journal.window.winfo_exists())
        inspecting=self.arranging or inspecting or (self.snack_panel and self.snack_panel.window.winfo_exists())
        interacting=now<self.interaction_until
        if not interacting and not inspecting and not self.card_open and self.brain.mode=='rest' and now>=self.next_idle and (self.settings.get('compact') or not (self.proposal and self.auto_enabled)):
            action=('look','stretch','sleep')[self.idle_turn%3];self.idle_turn+=1
            self.react(action,8 if action=='sleep' else 3);interacting=True
        if not self.card_open and not inspecting and not interacting and not self.settings.get('compact'):
            plan=self.brain.advance(dt,self.proposal if self.auto_enabled else None)
            if plan:
                try:
                    with closing(sqlite3.connect((self.directory/'pet.sqlite3').resolve().as_uri()+'?mode=rw',uri=True,timeout=.15)) as db:
                        planted=garden.perform_work(db,plan)
                    if not planted:self.brain.cancel_work()
                    else:
                        self.proposal=None
                        with closing(sqlite3.connect((self.directory/'pet.sqlite3').resolve().as_uri()+'?mode=ro',uri=True)) as db:self.scene=garden.snapshot(db)
                        event=self.scene['events'][0]
                        if event['action'] in ('plant','harvest','archive'):
                            name=botany.name(event['species'],self.settings['language'])
                            prefix={'plant':choose(self,'种下了：','Sown: '),'harvest':choose(self,'收获了：','Harvested: '),'archive':choose(self,'已收藏：','Collected: ')}[event['action']]
                            self.notices.append(prefix+name)
                        self.render()
                except (sqlite3.Error,OSError,ValueError):self.brain.cancel_work();self.scene_error='暂时无法照料，等一会儿再试'
        if self.notices and now>=self.notice_until:
            self.message=self.notices.pop(0);self.notice_until=now+5
        if self.root.winfo_viewable():self.draw_pet()
        self.root.after(100,self.animate)

    def press(self,event):
        # Tk image hit boxes include transparent padding. Only painted sprite
        # pixels may cover another plant or the pet underneath.
        tags=()
        for item in reversed(self.canvas.find_overlapping(event.x,event.y,event.x,event.y)):
            if self.canvas.type(item)=='image':
                box=self.canvas.bbox(item);name=self.canvas.itemcget(item,'image')
                if self.root.tk.call(name,'transparency','get',int(event.x-box[0]),int(event.y-box[1])):continue
            tags=self.canvas.gettags(item);break
        self.drag=(event.x_root,event.y_root,self.root.winfo_x(),self.root.winfo_y(),tags)

    def release(self,event):
        if not self.drag:return
        sx,sy,x,y,tags=self.drag;self.drag=None
        if self.arranging:
            if abs(event.x_root-sx)+abs(event.y_root-sy)<=5:self.arrange_click(event,tags)
            return
        if abs(event.x_root-sx)+abs(event.y_root-sy)>5:self.remember();return
        if 'card-style' in tags:self.settings_dialog();return
        if 'card-growth' in tags:self.growth_details();return
        if 'card' in tags:return
        for tag in tags:
            if tag.startswith('plant') and tag[5:].isdigit():
                self.show_plant(int(tag[5:]));return
        if 'avatar' in tags:
            self.react('petting',2.5)
            if self.settings.get('compact'):self.render();return
        self.card_open=not self.card_open if 'avatar' in tags else False
        self.render()

    def motion(self,event):
        if not self.arranging:super().motion(event)

    def escape(self,event=None):
        if self.arranging:self.toggle_arrange();return
        self.card_open=False;self.render()

    def toggle_auto(self):
        try:
            with closing(sqlite3.connect((self.directory/'pet.sqlite3').resolve().as_uri()+'?mode=rw',uri=True,timeout=.2)) as db:
                garden.set_autonomy(db,not self.auto_enabled)
            self.auto_enabled=not self.auto_enabled
            if not self.auto_enabled:self.brain.cancel_work();self.proposal=None
        except (sqlite3.Error,OSError):self.scene_error='设置暂未保存'

    def menu(self,event):
        if self.menu_window and self.menu_window.window.winfo_exists():self.menu_window.window.destroy()
        self.menu_window=GardenMenu(self,event.x_root,event.y_root)

    def panel(self,page):
        if self.journal and self.journal.window.winfo_exists():
            self.journal.tab(page);self.journal.window.lift();return
        self.journal=GardenPanel(self,page)

    def growth_details(self):self.panel('growth')

    def settings_dialog(self):self.panel('style')

    def show_card(self):
        if self.settings.get('compact'):self.toggle_compact()
        self.card_open=True;self.render()

    def open_garden(self):self.root.deiconify();self.root.lift()

    def show_plant(self,plot):
        plant=next((p for p in (self.scene or {}).get('plots',[]) if p['plot']==plot and p['species']),None)
        if not plant:return
        from plant_card import PlantCard
        if self.plant_window and self.plant_window.window.winfo_exists():self.plant_window.window.destroy()
        self.card_open=False;self.plant_window=PlantCard(self,plant);self.render()

    def react(self,action,duration):
        if self.interaction=='eat' and time.monotonic()<self.interaction_until:return
        self.interaction=action;self.interaction_start=time.monotonic()
        self.interaction_until=self.interaction_start+duration;self.next_idle=self.interaction_until+18

    def toggle_compact(self):
        self.arranging=False;self.arrange_selected=None
        self.settings['compact']=not self.settings.get('compact',False)
        self.card_open=False
        self.brain.cancel_work();self.proposal=None
        for panel in (self.journal,self.plant_window,self.snack_panel):
            if panel and panel.window.winfo_exists():panel.window.destroy()
        self.layout();self.remember()

    def feed_menu(self):
        from garden_ui import SnackPanel
        if self.snack_panel and self.snack_panel.window.winfo_exists():self.snack_panel.window.lift();return
        self.snack_panel=SnackPanel(self)

    def feed_snack(self,species):
        if time.monotonic()<self.interaction_until and self.interaction=='eat':return False
        try:
            with closing(sqlite3.connect((self.directory/'pet.sqlite3').resolve().as_uri()+'?mode=rw',uri=True,timeout=.2)) as db:
                if not garden.feed(db,species):return False
                self.scene=garden.snapshot(db)
        except (sqlite3.Error,OSError,ValueError):return False
        self.card_open=False;self.react('eat',4);self.render();return True
