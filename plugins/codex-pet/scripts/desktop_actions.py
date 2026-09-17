"""Display notices for level and form changes."""
def growth_events(previous,current):
    if not previous or not current:return []
    events=[]
    if current['level']>previous['level']:
        events.append(f"升级啦！Lv.{previous['level']} → Lv.{current['level']}")
    if current['form']!=previous['form'] and current['level']>previous['level']:
        events.append('长成了'+current['form']+'！')
    return events
