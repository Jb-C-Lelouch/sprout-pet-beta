"""A non-consuming garden driven by XP earned after planting."""
import growth
import energy
import time
import secrets
import botany
import rules

from content_catalog import catalog

PLANTS = catalog().plant_rules()

VISITORS={'butterfly':dict(name='蝴蝶',species=1),'sparrow':dict(name='麻雀',species=3)}


def initialize(db):
    db.executescript('''CREATE TABLE IF NOT EXISTS garden_plots(
        plot INTEGER PRIMARY KEY CHECK(plot BETWEEN 1 AND 9),species TEXT NOT NULL,planted_xp INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS garden_collection(kind TEXT NOT NULL,item TEXT NOT NULL,PRIMARY KEY(kind,item));
        CREATE TABLE IF NOT EXISTS garden_meta(id INTEGER PRIMARY KEY CHECK(id=1),revision INTEGER NOT NULL);
        INSERT OR IGNORE INTO garden_meta VALUES(1,0);
        CREATE TABLE IF NOT EXISTS garden_autonomy(id INTEGER PRIMARY KEY CHECK(id=1),enabled INTEGER NOT NULL,next_xp INTEGER NOT NULL);''')
    schema=db.execute("SELECT sql FROM sqlite_master WHERE name='garden_plots'").fetchone()[0]
    if 'BETWEEN 1 AND 6' in schema:
        with db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('CREATE TABLE garden_plots_v2(plot INTEGER PRIMARY KEY CHECK(plot BETWEEN 1 AND 9),species TEXT NOT NULL,planted_xp INTEGER NOT NULL)')
            db.execute('INSERT INTO garden_plots_v2 SELECT * FROM garden_plots')
            db.execute('DROP TABLE garden_plots')
            db.execute('ALTER TABLE garden_plots_v2 RENAME TO garden_plots')
    db.executescript("""CREATE TABLE IF NOT EXISTS garden_care(plot INTEGER PRIMARY KEY,bonus INTEGER NOT NULL DEFAULT 0,fertilized INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS garden_work(id INTEGER PRIMARY KEY CHECK(id=1),next_wall INTEGER NOT NULL,action TEXT NOT NULL);
        INSERT OR IGNORE INTO garden_work VALUES(1,0,'');
        CREATE TABLE IF NOT EXISTS garden_inventory(species TEXT PRIMARY KEY,amount INTEGER NOT NULL);""")
    db.executescript('''CREATE TABLE IF NOT EXISTS garden_rotation(id INTEGER PRIMARY KEY CHECK(id=1),enabled INTEGER NOT NULL);
        INSERT OR IGNORE INTO garden_rotation VALUES(1,0);
        CREATE TABLE IF NOT EXISTS garden_display(plot INTEGER PRIMARY KEY,since_online INTEGER NOT NULL,pinned INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS garden_archive(id INTEGER PRIMARY KEY AUTOINCREMENT,species TEXT NOT NULL,age INTEGER NOT NULL,bonus INTEGER NOT NULL,fertilized INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS garden_events(id INTEGER PRIMARY KEY AUTOINCREMENT,action TEXT NOT NULL,species TEXT NOT NULL);''')
    import memories
    memories.initialize(db)
    with db:
        db.execute('INSERT OR IGNORE INTO garden_autonomy VALUES(1,1,?)',(growth.total_units(db),))


def sync(db):
    xp=growth.total_units(db)
    online=db.execute('SELECT online_seconds FROM growth_state WHERE id=1').fetchone()[0]
    for plot,species,start,bonus in db.execute('SELECT plot,species,planted_xp,coalesce(bonus,0) FROM garden_plots LEFT JOIN garden_care USING(plot)'):
        if plot<=6 and xp-start+bonus>=PLANTS[species]['xp']*growth.UNIT:
            db.execute('INSERT OR IGNORE INTO garden_display VALUES(?,?,0)',(plot,online))
    for species,start in db.execute('SELECT species,planted_xp-coalesce(bonus,0) FROM garden_plots LEFT JOIN garden_care USING(plot)'):
        if species in PLANTS and xp-start>=PLANTS[species]['xp']*growth.UNIT:
            db.execute("INSERT OR IGNORE INTO garden_collection VALUES('plant',?)",(species,))
            import memories
            memories.record(db,'mature',species)
    count=db.execute("SELECT count(*) FROM garden_collection WHERE kind='plant'").fetchone()[0]
    for key,visitor in VISITORS.items():
        if count>=visitor['species']:
            db.execute("INSERT OR IGNORE INTO garden_collection VALUES('visitor',?)",(key,))
            import memories
            memories.record(db,'visitor',key)


def snapshot(db):
    xp=growth.total_units(db);level=rules.progress_for_db(db)['level']
    planted={p:(s,x) for p,s,x in db.execute('SELECT plot,species,planted_xp-coalesce(bonus,0) FROM garden_plots LEFT JOIN garden_care USING(plot)')}
    collection=list(db.execute('SELECT kind,item FROM garden_collection ORDER BY kind,item'))
    plots=[]
    for p in range(1,10):
        if p not in planted:
            plots.append(dict(plot=p,species=None));continue
        species,start=planted[p];plant=PLANTS[species]
        earned=max(0,xp-start)/growth.UNIT
        ratio=min(1,earned/plant['xp'])
        plots.append(dict(plot=p,species=species,name=plant['name'],earned_xp=earned,needed_xp=plant['xp'],
                          progress=ratio,stage='成熟' if ratio>=1 else '生长中' if ratio>=.25 else '萌芽'))
    return dict(level=level,rotation=bool(db.execute('SELECT enabled FROM garden_rotation').fetchone()[0]),archive=[dict(id=i,species=s) for i,s in db.execute('SELECT id,species FROM garden_archive ORDER BY id DESC')],events=[dict(id=i,action=a,species=s) for i,a,s in db.execute('SELECT id,action,species FROM garden_events ORDER BY id DESC LIMIT 5')],energy=energy.summary(db),inventory=dict(db.execute('SELECT species,amount FROM garden_inventory')),work=dict(zip(('next_wall','action'),db.execute('SELECT next_wall,action FROM garden_work WHERE id=1').fetchone())),revision=db.execute('SELECT revision FROM garden_meta WHERE id=1').fetchone()[0],plots=plots,
                catalog=[dict(id=k,**v,botanical_name=catalog().profile(k)['latin'],unlocked=level>=v['level'],discovered=('plant',k) in collection) for k,v in PLANTS.items()],
                visitors=[dict(id=k,**v,discovered=('visitor',k) in collection) for k,v in VISITORS.items()])


def edit(db,action,plot,species=None,destination=None,expected=None):
    if type(plot) is not int or not 1<=plot<=9:raise ValueError('请选择1至9号种植位置')
    with db:
        db.execute('BEGIN IMMEDIATE')
        revision=db.execute('SELECT revision FROM garden_meta WHERE id=1').fetchone()[0]
        if expected is not None and revision!=expected:raise ValueError('花园布局已在其他窗口改变，请刷新后再操作')
        sync(db)
        row=db.execute('SELECT species,planted_xp FROM garden_plots WHERE plot=?',(plot,)).fetchone()
        if action=='plant':
            if species in (None,'random'):species=draw_species(db,plot)
            if not isinstance(species,str) or species not in PLANTS:raise ValueError('未知植物')
            if rules.progress_for_db(db)['level']<PLANTS[species]['level']:raise ValueError('尚未解锁这株植物')
            if row:raise ValueError('这块地已经种植，请先移动或移除原植物')
            if (plot>6)!=(catalog().plants[species]['zone']=='crops'):raise ValueError('请把农作物种在菜畦，观赏植物种在花园')
            db.execute('INSERT INTO garden_plots VALUES(?,?,?)',(plot,species,growth.total_units(db)))
        elif action=='remove':
            if not row:raise ValueError('这是一块空地')
            db.execute('DELETE FROM garden_plots WHERE plot=?',(plot,))
            db.execute('DELETE FROM garden_care WHERE plot=?',(plot,))
            db.execute('DELETE FROM garden_display WHERE plot=?',(plot,))
        elif action=='move':
            if type(destination) is not int or not 1<=destination<=9 or destination==plot:raise ValueError('请选择另一块地')
            if not row:raise ValueError('这是一块空地')
            if (destination>6)!=(plot>6):raise ValueError('请在同一区域内移动植物')
            display=list(db.execute('SELECT plot,since_online,pinned FROM garden_display WHERE plot IN (?,?)',(plot,destination)))
            db.execute('DELETE FROM garden_display WHERE plot IN (?,?)',(plot,destination))
            for old,since,pinned in display:db.execute('INSERT INTO garden_display VALUES(?,?,?)',(destination if old==plot else plot,since,pinned))
            care=list(db.execute('SELECT plot,bonus,fertilized FROM garden_care WHERE plot IN (?,?)',(plot,destination)))
            db.execute('DELETE FROM garden_care WHERE plot IN (?,?)',(plot,destination))
            for old,bonus,fert in care:db.execute('INSERT INTO garden_care VALUES(?,?,?)',(destination if old==plot else plot,bonus,fert))
            other=db.execute('SELECT species,planted_xp FROM garden_plots WHERE plot=?',(destination,)).fetchone()
            db.execute('DELETE FROM garden_plots WHERE plot IN (?,?)',(plot,destination))
            db.execute('INSERT INTO garden_plots VALUES(?,?,?)',(destination,*row))
            if other:db.execute('INSERT INTO garden_plots VALUES(?,?,?)',(plot,*other))
        else:raise ValueError('未知花园操作')
        db.execute('UPDATE garden_meta SET revision=revision+1 WHERE id=1')


def auto_plan(db):
    enabled,next_xp=db.execute('SELECT enabled,next_xp FROM garden_autonomy WHERE id=1').fetchone()
    if not enabled or growth.total_units(db)<next_xp:return None
    state=snapshot(db)
    free=next((p['plot'] for p in state['plots'] if not p['species']),None)
    if free is None:return None
    return dict(plot=free,species=None,revision=state['revision'])


def auto_plant(db,plan):
    """Commit only after the pet's digging animation; stale/paused plans do nothing."""
    with db:
        db.execute('BEGIN IMMEDIATE')
        current=auto_plan(db)
        if not current or current!=plan:return False
        xp=growth.total_units(db)
        db.execute('INSERT INTO garden_plots VALUES(?,?,?)',(plan['plot'],draw_species(db,plan['plot']),xp))
        db.execute('UPDATE garden_autonomy SET next_xp=? WHERE id=1',(xp+6*growth.UNIT,))
        db.execute('UPDATE garden_meta SET revision=revision+1 WHERE id=1')
    return True


def set_autonomy(db,enabled):
    with db:db.execute('UPDATE garden_autonomy SET enabled=? WHERE id=1',(int(bool(enabled)),))


WORK_COST={'plant':6,'water':4,'fertilize':10,'harvest':4,'archive':4}
WORK_INTERVAL=60


def work_plan(db,now=None):
    now=int(time.time() if now is None else now)
    if not db.execute('SELECT enabled FROM garden_autonomy WHERE id=1').fetchone()[0]:return None
    if now<db.execute('SELECT next_wall FROM garden_work WHERE id=1').fetchone()[0]:return None
    units=db.execute('SELECT units FROM pet_energy WHERE id=1').fetchone()[0]
    state=snapshot(db)
    def task(action,p):return dict(action=action,plot=p['plot'],species=p['species'],revision=state['revision'])
    # Preserve crops until the harvest animation completes.
    for p in state['plots']:
        if p['species'] and p['plot']>6 and p['progress']>=1 and units>=WORK_COST['harvest']*energy.UNIT:return task('harvest',p)
    if state['rotation'] and units>=WORK_COST['archive']*energy.UNIT:
        online=db.execute('SELECT online_seconds FROM growth_state').fetchone()[0]
        for p in state['plots']:
            display=db.execute('SELECT since_online,pinned FROM garden_display WHERE plot=?',(p['plot'],)).fetchone()
            if p['species'] and p['plot']<=6 and p['progress']>=1 and display and not display[1] and online-display[0]>=3600:return task('archive',p)
    seed=auto_plan(db)
    if seed and units>=WORK_COST['plant']*energy.UNIT:return dict(action='plant',**seed)
    # Fill the new vegetable area even while old garden planting is waiting for XP.
    free=next((p['plot'] for p in state['plots'] if p['plot']>6 and not p['species']),None)
    if free and units>=WORK_COST['plant']*energy.UNIT:
        return dict(action='plant',plot=free,species=None,revision=state['revision'])
    for p in sorted((p for p in state['plots'] if p['species'] and p['progress']<1),key=lambda p:p['progress']):
        bonus,fertilized=db.execute('SELECT bonus,fertilized FROM garden_care WHERE plot=?',(p['plot'],)).fetchone() or (0,0)
        cap=PLANTS[p['species']]['xp']*growth.UNIT//2
        if bonus>=cap:continue
        action='fertilize' if bonus>=growth.UNIT and not fertilized else 'water'
        if units>=WORK_COST[action]*energy.UNIT:return task(action,p)
        if action=='fertilize' and units>=WORK_COST['water']*energy.UNIT:return task('water',p)
    return None


def perform_work(db,plan,now=None):
    """Energy debit and plant benefit commit together, once, after the animation."""
    now=int(time.time() if now is None else now)
    with db:
        db.execute('BEGIN IMMEDIATE')
        current=work_plan(db,now)
        if not current or current!=plan:return False
        action=plan['action'];plot=plan['plot'];species=plan['species'];xp=growth.total_units(db)
        db.execute('UPDATE pet_energy SET units=units-? WHERE id=1',(WORK_COST[action]*energy.UNIT,))
        if action=='plant':
            species=draw_species(db,plot)
            db.execute('INSERT INTO garden_plots VALUES(?,?,?)',(plot,species,xp))
            db.execute('UPDATE garden_autonomy SET next_xp=? WHERE id=1',(xp+6*growth.UNIT,))
        elif action=='archive':
            _archive(db,plot)
        elif action=='harvest':
            sync(db)
            db.execute('INSERT INTO garden_inventory VALUES(?,1) ON CONFLICT(species) DO UPDATE SET amount=amount+1',(species,))
            db.execute('DELETE FROM garden_plots WHERE plot=?',(plot,));db.execute('DELETE FROM garden_care WHERE plot=?',(plot,))
        else:
            amount=(3 if action=='fertilize' else 1)*growth.UNIT
            db.execute('INSERT OR IGNORE INTO garden_care VALUES(?,0,0)',(plot,))
            # A cycle can receive at most half its required growth from care.
            cap=PLANTS[species]['xp']*growth.UNIT//2
            db.execute('UPDATE garden_care SET bonus=min(?,bonus+?),fertilized=max(fertilized,?) WHERE plot=?',(cap,amount,int(action=='fertilize'),plot))
        db.execute('UPDATE garden_work SET next_wall=?,action=? WHERE id=1',(now+WORK_INTERVAL,action))
        db.execute('UPDATE garden_meta SET revision=revision+1 WHERE id=1');sync(db)
        log_event(db,action,species)
    return True


def seed_pool(db,plot):
    level=rules.progress_for_db(db)['level']
    return [s for s in PLANTS if (plot>6)==(catalog().plants[s]['zone']=='crops') and level>=PLANTS[s]['level']]


def draw_species(db,plot):
    # Called only by committing plant operations, never by previews or reads.
    return secrets.choice(seed_pool(db,plot))


def log_event(db,action,species):
    if action in ('harvest','feed'):
        import memories
        memories.record(db,action,species)
    db.execute('INSERT INTO garden_events(action,species) VALUES(?,?)',(action,species))
    db.execute('DELETE FROM garden_events WHERE id<=(SELECT max(id)-20 FROM garden_events)')


def set_rotation(db,enabled):
    with db:db.execute('UPDATE garden_rotation SET enabled=?',(int(bool(enabled)),))


def _archive(db,plot):
    row=db.execute('SELECT species,planted_xp FROM garden_plots WHERE plot=?',(plot,)).fetchone()
    if not row or plot>6:raise ValueError('只能收藏花园植物')
    species,start=row;bonus,fertilized=db.execute('SELECT bonus,fertilized FROM garden_care WHERE plot=?',(plot,)).fetchone() or (0,0)
    age=max(0,growth.total_units(db)-start)
    if age+bonus<PLANTS[species]['xp']*growth.UNIT:raise ValueError('植物成熟后才能收藏')
    db.execute('INSERT INTO garden_archive(species,age,bonus,fertilized) VALUES(?,?,?,?)',(species,age,bonus,fertilized))
    for table in ('garden_plots','garden_care','garden_display'):db.execute('DELETE FROM '+table+' WHERE plot=?',(plot,))
    db.execute('UPDATE garden_autonomy SET next_xp=?',(growth.total_units(db),))
    return species


def archive_plant(db,plot,expected):
    if type(plot) is not int or not 1<=plot<=6:raise ValueError('只能收藏花园植物')
    with db:
        db.execute('BEGIN IMMEDIATE')
        if db.execute('SELECT revision FROM garden_meta').fetchone()[0]!=expected:raise ValueError('花园已改变，请重新打开植物卡')
        sync(db);species=_archive(db,plot)
        log_event(db,'archive',species);db.execute('UPDATE garden_meta SET revision=revision+1')


def restore_plant(db,identity):
    with db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT species,age,bonus,fertilized FROM garden_archive WHERE id=?',(identity,)).fetchone()
        if not row:raise ValueError('这株植物已经摆回花园')
        occupied={r[0] for r in db.execute('SELECT plot FROM garden_plots')}
        plot=next((n for n in range(1,7) if n not in occupied),None)
        if plot is None:raise ValueError('花园已满，请先收藏一株植物')
        species,age,bonus,fertilized=row
        db.execute('INSERT INTO garden_plots VALUES(?,?,?)',(plot,species,growth.total_units(db)-age))
        db.execute('INSERT INTO garden_care VALUES(?,?,?)',(plot,bonus,fertilized))
        # A deliberately restored favorite stays put, even with rotation enabled.
        online=db.execute('SELECT online_seconds FROM growth_state').fetchone()[0]
        db.execute('INSERT INTO garden_display VALUES(?,?,1)',(plot,online))
        db.execute('DELETE FROM garden_archive WHERE id=?',(identity,));log_event(db,'restore',species)
        db.execute('UPDATE garden_meta SET revision=revision+1')
        return plot


def feed(db,species):
    """Consume one harvested crop atomically; feeding never creates XP or energy."""
    if species not in PLANTS or catalog().plants[species]['zone']!='crops':
        raise ValueError('Choose a harvested crop')
    with db:
        result=db.execute('UPDATE garden_inventory SET amount=amount-1 WHERE species=? AND amount>0',(species,))
        if result.rowcount!=1:return False
        log_event(db,'feed',species)
    return True
