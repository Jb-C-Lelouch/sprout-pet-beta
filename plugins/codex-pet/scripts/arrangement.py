"""Direct scene editing: swap existing plots and place cosmetic props."""
from contextlib import closing
import sqlite3
import math
from garden_motion import SPOTS
from i18n import choose
import garden
from garden_ui import rounded

KINDS=('nest','lantern','pot')


def clean_decor(value):
    if not isinstance(value,dict):return {}
    return {k:list(v) for k,v in value.items() if k in KINDS and isinstance(v,(list,tuple)) and len(v)==2 and all(type(n) is int for n in v) and 90<=v[0]<=660 and 170<=v[1]<=310}


class Arrangement:
    def toggle_arrange(self):
        if self.settings.get('compact'):self.toggle_compact()
        self.arranging=not self.arranging;self.arrange_selected=None;self.card_open=False
        self.brain.cancel_work();self.proposal=None
        for panel in (self.journal,self.plant_window,self.snack_panel):
            if panel and panel.window.winfo_exists():panel.window.destroy()
        self.render()

    def draw_decorations(self):
        from decor_art import draw_decor
        for kind,(x,y) in sorted(self.settings.get('decorations',{}).items(),key=lambda kv:kv[1][1]):
            if kind not in self.decor_images:self.decor_images[kind]=draw_decor(kind).photo(self.root,scale=1)
            self.canvas.create_image(x-24,y-44,image=self.decor_images[kind],anchor='nw',tags='decor-'+kind)

    def draw_arrange(self):
        c=self.canvas
        for plot,(x,y) in SPOTS.items():
            color='#e8ca83' if self.arrange_selected==('plant',plot) else '#a0b578'
            c.create_oval(x-17,y-6,x+17,y+7,outline=color,width=2,tags=('layout','slot-'+str(plot)))
        rounded(c,110,12,540,42,self.theme['bg'],12,'layout')
        names=[('nest',choose(self,'小窝','Nest')),('lantern',choose(self,'石灯','Lantern')),('pot',choose(self,'花盆','Planter')),('remove',choose(self,'收起装饰','Store prop')),('done',choose(self,'完成','Done'))]
        for i,(key,label) in enumerate(names):
            rounded(c,118+i*105,18,98,30,self.theme['card'],8,('layout','layout-'+key))
            c.create_text(167+i*105,33,text=label,font=('Microsoft YaHei UI',9),fill=self.theme['ink'],tags=('layout','layout-'+key))
        rounded(c,120,365,520,30,self.theme['bg'],10,'layout')
        text=self.arrange_note or (choose(self,'已选装饰：点击空草地摆放，或点「收起装饰」。','Prop selected: click open lawn, or Store prop.') if self.arrange_selected and self.arrange_selected[0]=='decor' else '') or choose(self,'点植物，再点同区落点交换；点装饰，再点草地摆放。','Select a plant, then a plot to swap; select a prop, then grass.')
        c.create_text(380,380,text=text,font=('Microsoft YaHei UI',9),fill=self.theme['ink'],tags='layout')
        c.tag_raise('layout')

    def arrange_click(self,event,tags):
        self.arrange_note=''
        for tag in tags:
            if tag=='layout-done':self.toggle_arrange();return
            if tag=='layout-remove':
                if self.arrange_selected and self.arrange_selected[0]=='decor':
                    self.settings.get('decorations',{}).pop(self.arrange_selected[1],None);self.remember()
                self.arrange_selected=None;self.render();return
            if tag.startswith('layout-') and tag[7:] in KINDS:
                self.arrange_selected=('decor',tag[7:]);self.render();return
        selected=self.arrange_selected
        if selected and selected[0]=='decor':
            x,y=round(event.x),round(event.y)
            # Keep props on the inner lawn and clear of plots and the crop bed.
            if 90<=x<=660 and 170<=y<=310 and all(math.hypot(x-px,y-py)>38 for px,py in SPOTS.values()) and not (325<=x<=585 and y>=290) and all(k==selected[1] or math.hypot(x-pos[0],y-pos[1])>45 for k,pos in self.settings.get('decorations',{}).items()):
                self.settings.setdefault('decorations',{})[selected[1]]=[x,y];self.remember();self.arrange_selected=None
            else:self.arrange_note=choose(self,'请选择空草地，避开植物与菜畦。','Choose open lawn, clear of plants and crops.')
            self.render();return
        plot=next((int(t.split('-')[1]) for t in tags if t.startswith('slot-')),None)
        if plot is None:plot=next((int(t[5:]) for t in tags if t.startswith('plant') and t[5:].isdigit()),None)
        if plot is not None:
            if selected and selected[0]=='plant' and selected[1]!=plot:
                try:
                    with closing(sqlite3.connect((self.directory/'pet.sqlite3').resolve().as_uri()+'?mode=rw',uri=True,timeout=.2)) as db:
                        garden.edit(db,'move',selected[1],destination=plot,expected=self.scene['revision']);self.scene=garden.snapshot(db)
                    self.arrange_selected=None
                except (sqlite3.Error,ValueError):self.arrange_note=choose(self,'请在同区交换；布局变化时请重新进入。','Swap within one area; reopen if the layout changed.')
            elif any(p['plot']==plot and p['species'] for p in self.scene['plots']):self.arrange_selected=('plant',plot)
        else:
            decor=next((t[6:] for t in tags if t.startswith('decor-')),None)
            self.arrange_selected=('decor',decor) if decor else None
        self.render()
