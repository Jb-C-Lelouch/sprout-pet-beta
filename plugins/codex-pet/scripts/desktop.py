"""Desktop garden shell: preferences, time heartbeat and local growth notices."""
import argparse
from contextlib import closing
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import tempfile
import time
import tkinter as tk
import pet
import desktop_actions
from i18n import tr

THEMES = {
    '苔绿': dict(bg='#f5f4ec',card='#e7ecdf',ink='#253e32',muted='#738174',accent='#628c62',body='#b8d995',leaf='#598958',blush='#e9b7a0'),
    '樱粉': dict(bg='#fcf1ef',card='#f3e0df',ink='#5d3c48',muted='#9a7885',accent='#b77391',body='#edbfd0',leaf='#ab6f93',blush='#e18f99'),
    '夜色': dict(bg='#212a35',card='#2d3947',ink='#edf0dc',muted='#a4b3b3',accent='#a7c88c',body='#aecf9c',leaf='#6c9e7c',blush='#e5b19d'),
}
DEFAULTS = dict(theme='苔绿',topmost=True,compact=False,avatar='',language='zh')


def prepare_display():
    if os.name=='nt':
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()


def read_status(directory):
    path = Path(directory)/'pet.sqlite3'
    if not path.is_file():
        return None
    with closing(sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True,timeout=0.15)) as db:
        db.execute('PRAGMA query_only=ON')
        db.execute('BEGIN')
        return pet.status(db)


def preferences(directory):
    value = dict(DEFAULTS)
    try:
        path = Path(directory)/'desktop.json'
        if path.stat().st_size > 8192: return value
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data,dict): return value
        if data.get('theme') in THEMES: value['theme']=data['theme']
        if data.get('language') in ('zh','en'):value['language']=data['language']
        for key in ('topmost','compact'):
            if type(data.get(key)) is bool: value[key]=data[key]
        from arrangement import clean_decor
        if 'decorations' in data:value['decorations']=clean_decor(data['decorations'])
        if isinstance(data.get('avatar'),str): value['avatar']=data['avatar']
        for key in ('x','y'):
            if type(data.get(key)) is int: value[key]=data[key]
    except (OSError,ValueError,TypeError): pass
    return value


def save_preferences(directory,value):
    directory=Path(directory)
    directory.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=directory,suffix='.tmp',delete=False) as out:
        name=out.name
        json.dump(value,out,ensure_ascii=False,indent=2)
    try: os.replace(name,directory/'desktop.json')
    finally:
        if Path(name).exists(): Path(name).unlink()


class DesktopPet:
    def __init__(self,root,directory):
        self.root=root
        self.directory=Path(directory)
        self.settings=preferences(directory)
        self.data=None
        self.error=''
        self.time_error=''
        self.frame=0
        self.message='一起慢慢长大。'
        self.image=None
        self.drag=None
        self.notices=[]
        self.notice_until=0
        self.spark_until=0
        root.title('小芽 · Codex Pet')
        icon_dir=Path(__file__).resolve().parents[1]/'assets/icons'
        try:
            self.window_icon=tk.PhotoImage(master=root,file=str(icon_dir/'sprout-64.png'))
            root.iconphoto(True,self.window_icon)
            if os.name=='nt':root.iconbitmap(str(icon_dir/'sprout.ico'))
        except (tk.TclError,OSError):pass
        root.overrideredirect(True)
        root.attributes('-topmost',self.settings['topmost'])
        root.protocol('WM_DELETE_WINDOW',self.close)
        root.bind('<Escape>',lambda e:self.close())
        self.canvas=tk.Canvas(root,highlightthickness=0)
        self.canvas.pack(fill='both',expand=True)
        self.canvas.bind('<ButtonPress-1>',self.press)
        self.canvas.bind('<B1-Motion>',self.motion)
        self.canvas.bind('<ButtonRelease-1>',self.release)
        self.canvas.bind('<Button-3>',self.menu)
        self.heartbeat()
        self.load_avatar()
        self.layout()
        self.refresh()
        self.animate()

    @property
    def theme(self): return THEMES[self.settings['theme']]


    def remember(self):
        self.settings.update(x=self.root.winfo_x(),y=self.root.winfo_y())
        try: save_preferences(self.directory,self.settings)
        except OSError:
            self.message='外观设置未能保存'

    def load_avatar(self):
        self.image=None
        path=self.settings.get('avatar')
        if not path: return
        try:
            p=Path(path)
            if p.suffix.lower()!='.png' or p.stat().st_size>2*1024*1024:
                raise ValueError('请使用小于2MB的PNG')
            # Inspect IHDR before letting Tk allocate image pixels.
            with p.open('rb') as f: header=f.read(24)
            if header[:8]!=b'\x89PNG\r\n\x1a\n' or len(header)!=24:
                raise ValueError('PNG格式无效')
            if not all(1<=int.from_bytes(header[i:i+4],'big')<=1024 for i in (16,20)):
                raise ValueError('图片尺寸请控制在1024×1024以内')
            image=tk.PhotoImage(master=self.root,data=p.read_bytes())
            factor=max(1,math.ceil(max(image.width(),image.height())/142))
            self.image=image.subsample(factor)
        except (OSError,ValueError,tk.TclError) as exc:
            self.error='自定义图片不可用，已显示默认小芽'

    def text(self,x,y,value,size=10,color=None,anchor='w',**kwargs):
        return self.canvas.create_text(x,y,text=tr(value,self.settings['language']),font=('Microsoft YaHei UI',size),fill=color or self.theme['ink'],anchor=anchor,**kwargs)


    def heartbeat(self):
        try:
            with closing(pet.connect(self.directory)) as db:
                receipt=pet.tick(db,'heartbeat')
            self.time_error=''
            if receipt['offline_xp']>=.1:
                self.notices.append(f"离线成长 +{receipt['offline_xp']:.1f} 经验")
        except (sqlite3.Error,OSError,ValueError):
            self.time_error='时间结算暂不可用 · 稍后重试'
        self.root.after(15000,self.heartbeat)

    def refresh(self):
        try:
            value=read_status(self.directory)
            self.notices.extend(desktop_actions.growth_events(self.data,value))
            if self.data and value and value['credited_tokens']>self.data['credited_tokens']:
                current=(value.get('energy') or {}).get('current',0)
                if current>(self.data.get('energy') or {}).get('current',0):self.notices.append(f'精力补充到了 {current:.1f} / 100')
            self.data=value
            if not self.settings['avatar']: self.error=''
        except (sqlite3.Error,OSError,KeyError,ValueError):
            self.error='存档暂不可读 · 稍后自动重试'
        self.render()
        self.root.after(3000,self.refresh)


    def motion(self,event):
        if not self.drag:return
        sx,sy,x,y,tags=self.drag
        self.root.geometry(f'+{max(0,x+event.x_root-sx)}+{max(0,y+event.y_root-sy)}')


    def pin(self):
        self.settings['topmost']=not self.settings['topmost']
        self.root.attributes('-topmost',self.settings['topmost'])
        self.remember();self.render()


    def close(self):
        try:
            with closing(pet.connect(self.directory)) as db:pet.tick(db,'close')
        except (sqlite3.Error,OSError,ValueError):pass
        self.remember();self.root.destroy()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--data',type=Path)
    args=parser.parse_args()
    directory=args.data or Path(os.environ.get('CODEX_PET_DATA') or str(Path.home()/'.codex-pet'))
    mutex=None
    if os.name=='nt':
        import ctypes
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.CreateMutexW.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_wchar_p]
        kernel.CreateMutexW.restype=ctypes.c_void_p
        key=hashlib.sha256(str(directory.resolve()).lower().encode()).hexdigest()[:24]
        mutex=kernel.CreateMutexW(None,False,'Local\\CodexPetDesktop-'+key)
        if not mutex:raise OSError('Unable to create desktop instance lock')
        if ctypes.get_last_error()==183:
            kernel.CloseHandle.argtypes=[ctypes.c_void_p];kernel.CloseHandle(mutex)
            return
    try:
        prepare_display()
        root=tk.Tk();root.tk.call('tk','scaling',4/3)
        from desktop_scene import GardenScene
        GardenScene(root,directory);root.mainloop()
    finally:
        if mutex:
            kernel.CloseHandle.argtypes=[ctypes.c_void_p];kernel.CloseHandle(mutex)


if __name__=='__main__':main()
