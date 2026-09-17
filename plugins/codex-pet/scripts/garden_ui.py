"""Canvas garden stationery: shared rounded surfaces, panels and context menu."""
import tkinter as tk
from tkinter import filedialog
import sqlite3
from contextlib import closing
import garden
import botany
from i18n import tr,choose


def rounded(c,x,y,w,h,fill,r=14,tags=()):
    r=min(r,w/2,h/2)
    return c.create_polygon(x+r,y,x+w-r,y,x+w,y,x+w,y+r,x+w,y+h-r,x+w,y+h,x+w-r,y+h,x+r,y+h,x,y+h,x,y+h-r,x,y+r,x,y,smooth=True,splinesteps=20,fill=fill,outline='',tags=tags)


def palette(app):
    t=app.theme
    return dict(bg=t['bg'],surface='#fffdf5' if app.settings['theme']!='夜色' else '#344251',soft=t['card'],ink=t['ink'],muted=t['muted'],accent=t['accent'],leaf=t['leaf'])


class Surface:
    def __init__(self,app,width,height,title):
        self.app=app;self.width=width;self.height=height;self.actions={}
        self.window=tk.Toplevel(app.root);self.window.title(title);self.window.overrideredirect(True)
        self.window.attributes('-topmost',app.settings['topmost'])
        self.window.configure(bg='#ff00ff')
        import os
        if os.name=='nt':self.window.attributes('-transparentcolor','#ff00ff')
        x=max(0,min(app.root.winfo_x()+80,self.window.winfo_screenwidth()-width))
        y=max(0,min(app.root.winfo_y()-100,self.window.winfo_screenheight()-height))
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        self.c=tk.Canvas(self.window,width=width,height=height,bg='#ff00ff',highlightthickness=0);self.c.pack()
        self.c.bind('<ButtonPress-1>',self.press);self.c.bind('<B1-Motion>',self.drag);self.c.bind('<ButtonRelease-1>',self.release)
        self.window.bind('<Escape>',lambda e:self.window.destroy())
        self.window.protocol('WM_DELETE_WINDOW',self.window.destroy)
        self.start=None

    def press(self,e):
        self.start=(e.x_root,e.y_root,self.window.winfo_x(),self.window.winfo_y(),e.y)

    def drag(self,e):
        if self.start and self.start[4]<75:
            sx,sy,x,y,_=self.start;self.window.geometry(f'+{max(0,x+e.x_root-sx)}+{max(0,y+e.y_root-sy)}')

    def release(self,e):
        if not self.start:return
        sx,sy,*_=self.start;self.start=None
        if abs(e.x_root-sx)+abs(e.y_root-sy)>5:return
        current=self.c.find_withtag('current')
        for tag in self.c.gettags(current[0]) if current else ():
            if tag in self.actions:self.actions[tag]();return

    def text(self,x,y,text,size=10,color=None,anchor='w',tags=(),**kwargs):
        self.c.create_text(x,y,text=tr(text,self.app.settings.get('language','zh')),font=('Microsoft YaHei UI',size),fill=color or self.p['ink'],anchor=anchor,tags=tags,**kwargs)

    def button(self,x,y,w,text,fn,primary=False,h=35):
        tag='action'+str(len(self.actions));self.actions[tag]=fn
        rounded(self.c,x,y,w,h,self.p['accent'] if primary else self.p['soft'],10,tag)
        color=('#294333' if self.app.settings['theme']=='夜色' else '#ffffff') if primary else self.p['ink']
        self.text(x+w/2,y+h/2,text,10,color,'center',tag)

    def base(self):
        self.p=palette(self.app);self.actions={};self.c.delete('all')
        rounded(self.c,4,6,self.width-8,self.height-10,self.p['soft'],24)
        rounded(self.c,0,0,self.width-8,self.height-10,self.p['bg'],24)


class GardenPanel(Surface):
    def __init__(self,app,page='growth'):
        super().__init__(app,520,620,'小芽 · 花园手记')
        self.page=page;self.note='';self.data=None;self.collection_page=0;self.garden=None
        self.reload();self.render()

    def reload(self):
        from desktop import read_status
        try:
            self.data=read_status(self.app.directory)
            with closing(sqlite3.connect((self.app.directory/'pet.sqlite3').resolve().as_uri()+'?mode=ro',uri=True)) as db:self.garden=garden.snapshot(db)
        except (sqlite3.Error,OSError,ValueError):self.note='暂时读不到记录，请稍后重新打开。'

    def tab(self,page):self.page=page;self.note='';self.reload();self.render()

    def render(self):
        self.base()
        self.text(26,28,'GARDEN JOURNAL',9,self.p['muted'])
        self.text(26,58,'小芽的花园手记',20)
        self.button(461,19,29,'×',self.window.destroy,h=29)
        self.c.create_oval(396,34,417,47,fill=self.p['leaf'],outline='')
        self.c.create_oval(416,23,433,40,fill=self.p['accent'],outline='')
        for i,(key,title) in enumerate([('growth','成长足迹'),('collection','植物收藏'),('style','花园装扮')]):
            self.button(26+i*156,85,144,title,lambda k=key:self.tab(k),self.page==key)
        if self.page=='style':self.style_page()
        elif not self.data:self.text(28,165,self.note or '还没有可显示的记录。')
        elif self.page=='growth':self.growth_page()
        elif self.page=='collection':self.collection_view()
        if self.note:self.text(28,589,self.note,9,self.p['muted'],width=458)

    def growth_page(self):
        g=self.data.get('growth') or {}
        self.text(28,150,'每一点陪伴，都在慢慢生长。',12)
        rows=[('累计成长',g.get('total_xp',0),'经验'),('当前精力',(self.data.get('energy') or {}).get('current',0),'/ 100'),('桌面陪伴',g.get('online_seconds',0)/3600,'小时'),('离线陪伴',g.get('offline_seconds',0)/3600,'小时')]
        for i,(title,value,unit) in enumerate(rows):
            x=26+(i%2)*234;y=178+(i//2)*118
            rounded(self.c,x,y,220,103,self.p['surface'],16)
            self.text(x+17,y+23,title,10,self.p['muted'])
            self.text(x+17,y+61,f'{value:,.2f}',21)
            self.text(x+199,y+84,unit,9,self.p['muted'],'e')
        rounded(self.c,26,433,454,127,self.p['soft'],16)
        for i,line in enumerate(['陪伴 +6经验/小时 · 离线 +3经验/小时，最多12小时','每1000 token补充1精力，上限100；不再直接加经验','浇水4精力 · 施肥10精力，单株最多加速半程','播种6精力 · 收获4精力，照料间隔至少1分钟']):self.text(44,453+i*24,line,9)
        total=sum((self.garden or {}).get('inventory',{}).values())
        self.text(44,549,choose(self.app,f'累计收获 {total} 株 · 明细见植物收藏',f'Total harvested: {total} · Details in Collection'),9)

    def style_page(self):
        self.text(28,151,'为小芽和花园手记，换一种配色。',12)
        for i,(name,leaf,soil) in enumerate([('苔绿','#85a371','#e4e7ce'),('樱粉','#c695ad','#f3e2df'),('夜色','#9db797','#435b52')]):
            x=26+i*156;rounded(self.c,x,177,144,151,self.p['surface'],15)
            self.c.create_oval(x+18,205,x+126,260,fill=soil,outline='')
            self.c.create_line(x+73,246,x+73,212,fill=leaf,width=4)
            self.c.create_oval(x+44,207,x+73,224,fill=leaf,outline='')
            self.c.create_oval(x+72,199,x+101,216,fill=leaf,outline='')
            self.button(x+10,279,124,name+(' ✓' if name==self.app.settings['theme'] else ''),lambda n=name:self.set_theme(n),name==self.app.settings['theme'])
        rounded(self.c,26,352,458,184,self.p['surface'],17)
        self.text(44,379,'小芽的专属模样',14)
        self.text(44,410,'使用透明背景 PNG，让它成为你的独家伙伴。',10,self.p['muted'])
        self.text(44,437,'推荐256×256，最大1024×1024、小于2MB。',9,self.p['muted'])
        self.button(44,469,195,'选择宠物图片',self.choose_image,True)
        self.button(254,469,208,'恢复默认小芽',self.reset_image)
        self.button(26,546,222,'简体中文',lambda:self.set_language('zh'),self.app.settings['language']=='zh')
        self.button(260,546,222,'English',lambda:self.set_language('en'),self.app.settings['language']=='en')

    def set_language(self,language):
        self.app.settings['language']=language;self.app.remember();self.app.render();self.render()
        card=self.app.plant_window
        if card and card.window.winfo_exists():card.render()

    def collection_view(self):
        state=self.garden or {};enabled=state.get('rotation',False)
        self.button(26,140,458,'轮换：开启 · 成熟后展示1小时' if enabled else '轮换：关闭 · 保留现有植物',lambda:self.mutate(lambda db:garden.set_rotation(db,not enabled)),enabled)
        self.text(28,189,'按桌面陪伴时间计时；小芽花4精力收藏，再花6精力补种。',9,self.p['muted'],anchor='nw',width=452)
        self.text(28,231,'手动收藏和摆回不耗精力。摆回的植物不会自动轮换。',9,self.p['muted'],anchor='nw',width=452)
        items=state.get('archive',[]);pages=max(1,(len(items)+3)//4);self.collection_page=min(self.collection_page,pages-1)
        for i,item in enumerate(items[self.collection_page*4:self.collection_page*4+4]):
            y=279+i*49;rounded(self.c,26,y,458,43,self.p['surface'],10)
            self.text(40,y+21,botany.name(item['species'],self.app.settings['language']),10)
            self.button(372,y+5,98,'摆回花园',lambda n=item['id']:self.mutate(lambda db:garden.restore_plant(db,n),'已摆回花园，会一直保留。'),h=32)
        if not items:self.text(28,306,'还没有收藏。点击成熟的花园植物，即可收藏。',10,self.p['muted'],anchor='nw',width=440)
        self.button(26,484,118,'上一页',lambda:self.turn_collection(-1))
        self.text(255,502,f'{self.collection_page+1} / {pages}',10,anchor='center')
        self.button(365,484,118,'下一页',lambda:self.turn_collection(1))
        stock=state.get('inventory',{})
        names={'carrot':('胡萝卜','Carrot'),'tomato':('番茄','Tomato'),'radish':('小萝卜','Radish'),'lettuce':('生菜','Lettuce')}
        line=' · '.join(choose(self.app,*names[s])+f' {stock.get(s,0)}' for s in names)
        self.text(28,538,line,9,self.p['muted'],anchor='nw',width=450)

    def turn_collection(self,delta):
        pages=max(1,(len((self.garden or {}).get('archive',[]))+3)//4)
        self.collection_page=max(0,min(pages-1,self.collection_page+delta));self.render()

    def mutate(self,action,note=''):
        try:
            with closing(sqlite3.connect((self.app.directory/'pet.sqlite3').resolve().as_uri()+'?mode=rw',uri=True,timeout=.2)) as db:action(db)
            self.note=note;self.app.brain.cancel_work();self.app.proposal=None
        except ValueError as exc:self.note=str(exc)
        except (sqlite3.Error,OSError):self.note='操作暂未完成，请稍后重试。'
        self.reload();self.app.scene=self.garden;self.app.render();self.render()

    def set_theme(self,name):
        self.app.settings['theme']=name;self.app.layout();self.app.remember();self.render()

    def choose_image(self):
        path=filedialog.askopenfilename(parent=self.window,title='选择小芽的透明PNG',filetypes=[('PNG 图片','*.png')])
        if path:
            self.app.settings['avatar']=path;self.app.error='';self.app.load_avatar();self.app.render();self.app.remember()
            self.note=self.app.error or '新模样已保存。';self.render()

    def reset_image(self):
        self.app.settings['avatar']='';self.app.image=None;self.app.error='';self.app.render();self.app.remember();self.note='已恢复默认小芽。';self.render()


class GardenMenu(Surface):
    def __init__(self,app,x,y):
        super().__init__(app,236,342,'小芽 · 花园菜单');self.base()
        self.window.geometry(f'236x342+{max(0,min(x,self.window.winfo_screenwidth()-236))}+{max(0,min(y,self.window.winfo_screenheight()-342))}')
        self.text(20,27,'花园里的小事',12)
        rows=[('看看小芽',app.show_card),('成长足迹',app.growth_details),('花园装扮',app.settings_dialog),('暂停自动照料' if app.auto_enabled else '恢复自动照料',app.toggle_auto),('取消置顶' if app.settings['topmost'] else '置顶花园',app.pin),('退出花园',app.close)]
        for i,(name,fn) in enumerate(rows):self.button(16,53+i*44,196,name,lambda f=fn:self.call(f))
        self.window.focus_force();self.window.bind('<FocusOut>',lambda e:self.window.destroy() if self.window.winfo_exists() else None)

    def call(self,fn):self.window.destroy();fn()
