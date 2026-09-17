"""Desktop-only translations. Never translate persisted identifiers."""
import re

from content_catalog import catalog

TEXT = catalog().messages['en']['ui']

PATTERNS=[
 (r'升级啦！(.+)',r'Level up! \1'),
 (r'精力 (.+) / 100',r'Energy \1 / 100'),(r'成长 (.+)',r'Growth \1'),
 (r'储存成长 (.+) 经验',r'Stored growth: \1 XP'),
 (r'花园 (\d+) 株 · 菜畦 (\d+) 株',r'Garden: \1 · Crops: \2'),
 (r'离线成长 \+(.+) 经验',r'Away growth +\1 XP'),
 (r'精力补充到了 (.+) / 100',r'Energy replenished: \1 / 100'),
 (r'打开时的游戏进度：(.+) · (.+)',r'Progress when opened: \1 · \2'),
]


def tr(value,language='zh'):
    if language!='en' or not isinstance(value,str):return value
    if value in TEXT:return TEXT[value]
    if value.endswith(' ✓'):return tr(value[:-2],language)+' ✓'
    if value.endswith(' · 原文'):return value[:-5].split(' · ')[0]+' · Source'
    if value.startswith('长成了'):return 'A new form: '+{catalog().form_name(f['level'], 'zh'):catalog().form_name(f['level'], 'en') for f in catalog().pets['sprout']['forms']}.get(value[3:-1],value[3:-1])+'!'
    if '  ·  花园里的小小伙伴' in value:return 'Your little garden companion'
    for pattern,replacement in PATTERNS:
        if re.fullmatch(pattern,value):return re.sub(pattern,replacement,value)
    return value


def choose(app,zh,en):return en if app.settings.get('language')=='en' else zh
