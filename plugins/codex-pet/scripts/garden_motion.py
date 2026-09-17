"""Small deterministic motion state machine; does not read/write saves."""
import math

SPOTS={1:(139,248),2:(286,199),3:(487,203),4:(440,250),5:(280,300),6:(200,333),7:(370,335),8:(445,342),9:(516,335)}
WANDER=[(330,272),(449,280),(251,291),(180,277),(471,323),(357,225)]


class Gardener:
    def __init__(self):
        self.x,self.y=345.,288.
        self.mode='rest';self.elapsed=0.;self.plan=None;self.target=(self.x,self.y);self.route=0

    def advance(self,dt,proposal=None):
        dt=max(0,min(dt,.1));self.elapsed+=dt
        if self.mode=='rest' and self.elapsed>=5:
            self.plan=proposal
            if proposal:
                x,y=SPOTS[proposal['plot']];self.target=(x+32,y+8)
            else:self.target=WANDER[self.route%len(WANDER)];self.route+=1
            self.mode='walk';self.elapsed=0
        elif self.mode=='walk':
            dx,dy=self.target[0]-self.x,self.target[1]-self.y;distance=math.hypot(dx,dy)
            step=48*dt
            if distance<=step:
                self.x,self.y=self.target;self.mode=('dig' if self.plan.get('action','plant')=='plant' else self.plan['action']) if self.plan else 'rest';self.elapsed=0
            elif distance:
                self.x+=dx/distance*step;self.y+=dy/distance*step
        elif self.mode=='dig' and self.elapsed>=2:
            self.mode='finish' if 'action' in self.plan else 'water';self.elapsed=0
            return self.plan
        elif self.mode in ('water','fertilize','harvest','archive') and self.elapsed>=2.5 and self.plan and self.plan.get('action') in ('water','fertilize','harvest','archive'):
            self.mode='finish';self.elapsed=0
            return self.plan
        elif self.mode in ('water','finish') and self.elapsed>=2.5:
            self.mode='rest';self.elapsed=0;self.plan=None
        return None

    def cancel_work(self):
        self.plan=None;self.mode='rest';self.elapsed=0
