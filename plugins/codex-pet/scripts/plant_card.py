"""Offline botanical field note for the actual planted species."""
import webbrowser
from garden_ui import Surface,rounded
import botany
from content_catalog import catalog
from i18n import choose
from contextlib import closing
import sqlite3
import garden


class PlantCard(Surface):
    def __init__(self,app,plant):
        super().__init__(app,520,660,'植物观察手记')
        self.plant=dict(plant);self.revision=app.scene['revision'];self.profile=botany.profile(plant['species'],app.settings['language']);self.note='';self.render()

    def render(self):
        self.base();plant=self.plant;self.profile=botany.profile(plant['species'],self.app.settings['language']);p=self.profile
        self.text(26,28,'植物观察手记',10,self.p['muted'])
        self.text(26,61,p['name'],20)
        self.button(461,19,29,'×',self.window.destroy,h=29)
        self.text(28,94,p['latin'],12)
        self.text(28,121,p['family']+' · '+p['life'],10,self.p['muted'])
        rounded(self.c,26,143,458,58,self.p['soft'],12)
        stage=choose(self.app,plant['stage'],'Ready' if plant['progress']>=1 else 'Growing' if plant['progress']>=.25 else 'Sprouting')
        self.text(42,160,f"打开时的游戏进度：{plant['progress']:.0%} · {stage}",10)
        self.text(42,184,'品种已固定，查看和重启不会重新抽取。',9,self.p['muted'])
        y=218
        for title,key in [('认识它','intro'),('观察线索','observe'),('真实生长习性','habitat'),('一个小知识','fact')]:
            self.text(28,y,title,11)
            self.text(28,y+19,p[key],10,self.p['muted'],anchor='nw',width=458)
            y+=76
        self.text(28,532,catalog().game_note(self.app.settings['language']),9,self.p['muted'],anchor='nw',width=458)
        if p.get('extra_url'):
            self.button(26,570,226,'主要资料 · 打开原文',lambda:webbrowser.open(p['url']))
            self.button(264,570,220,'生命周期 · 打开原文',lambda:webbrowser.open(p['extra_url']))
        else:self.button(26,570,458,p['source']+' · 原文',lambda:webbrowser.open(p['url']))
        if self.note:self.text(28,628,self.note,9,self.p['muted'],width=452)
        elif plant['plot']<=6 and plant['progress']>=1:self.button(26,610,458,'收藏并腾出位置',self.collect,True)
        else:self.text(28,628,'成熟后可以收藏换种' if plant['plot']<=6 else '菜畦成熟后由小芽收获，再随机补种。',9,self.p['muted'],width=452)

    def collect(self):
        try:
            with closing(sqlite3.connect((self.app.directory/'pet.sqlite3').resolve().as_uri()+'?mode=rw',uri=True,timeout=.2)) as db:
                garden.archive_plant(db,self.plant['plot'],self.revision)
                self.app.scene=garden.snapshot(db)
            self.app.brain.cancel_work();self.app.proposal=None;self.app.notices.append('已收藏，可以补种新植物了。')
            self.window.destroy();self.app.render()
            self.app.panel('collection')
        except ValueError as exc:self.note=str(exc);self.render()
        except (sqlite3.Error,OSError):self.note='操作暂未完成，请稍后重试。';self.render()
