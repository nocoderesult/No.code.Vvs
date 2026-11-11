#!/usr/bin/env python3
"""Generează un LUT 3D (.cube) pentru colorizare: Apple Log (Rec.2020) -> Rec.709, plus un look de film.

Folosit în sesiune pe un clip 4K ProRes filmat cu iPhone în Apple Log. Cere numpy.

  python applelog_lut.py look.cube EV CONTRAST SAT CALD SPLIT NEGRU ALB CALD_LUMINI

  EV           expunere în trepte (ex. -0.95 = aproape o treaptă mai jos)
  CONTRAST     contrast în jurul griului mediu (1.0 = neutru; folosit 1.20)
  SAT          saturație (1.0 = neutru; folosit 1.12)
  CALD         balans de alb spre cald (0 = neutru; folosit 0.03)
  SPLIT        tentă: umbre reci, lumini calde (0 = fără; folosit 1.7)
  NEGRU        coborârea punctului de negru (0 = fără; folosit 0.05)
  ALB          ridicarea luminilor puternice (0 = fără; folosit 0.32)
  CALD_LUMINI  cât din tenta caldă rămâne în lumini (1 = toată; folosit 0.30)

Valorile din sesiune:  python applelog_lut.py final.cube -0.95 1.20 1.12 0.03 1.7 0.05 0.32 0.30
Conversie neutră:      python applelog_lut.py neutru.cube 0 1.0 1.0 0 0 0 0 1
"""
import numpy as np, sys
out=sys.argv[1]; ev=float(sys.argv[2]); con=float(sys.argv[3]); sat=float(sys.argv[4]); warm=float(sys.argv[5]); split=float(sys.argv[6]); bp=float(sys.argv[7]); wk=float(sys.argv[8]); hiwarm=float(sys.argv[9])
N=65
g=np.linspace(0,1,N)
# .cube order: R fastest
B,G,R=np.meshgrid(g,g,g,indexing='ij')
P=np.stack([R,G,B],-1).reshape(-1,3)
# Apple Log -> scene linear
R0,Rt,c,beta,gamma,delta=-0.05641088,0.01,47.28711236,0.00964052,0.08550479,0.69336945
Pt=c*(Rt-R0)**2
lin=np.where(P>=Pt, 2.0**((P-delta)/gamma)-beta, np.sqrt(np.maximum(P,0)/c)+R0)
# Rec.2020 -> Rec.709
M=np.array([[1.6605,-0.5876,-0.0728],[-0.1246,1.1329,-0.0083],[-0.0182,-0.1006,1.1187]])
lin=lin@M.T
lin=np.maximum(lin,0)
# exposure + white balance (scene linear)
lin*=2.0**ev
lin*=np.array([1+warm,1.0,1-warm*1.3])
# contrast around mid grey
lin=0.18*(lin/0.18)**con
# filmic tone map (ACES fit)
x=lin*0.6
tm=np.clip((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14),0,1)
# display encode
d=tm**(1/2.4)
Y=(d*np.array([0.2126,0.7152,0.0722])).sum(-1,keepdims=True)
# saturation: less in deep shadows and in highlights (film-like)
w=np.clip(Y/0.25,0,1)**0.7*(1-0.35*np.clip((Y-0.75)/0.25,0,1))
d=Y+(d-Y)*(sat*(0.75+0.25*w))
# split toning: cool teal shadows, warm amber highlights
sh=(1-np.clip(Y/0.45,0,1))**1.5; hi=np.clip((Y-0.45)/0.55,0,1)**1.2
d=d+split*sh*np.array([-0.030,0.004,0.028])*np.clip(Y/0.06,0,1)+split*hiwarm*hi*np.array([0.030,0.008,-0.034])
d=np.clip(d,0,1)
# deeper blacks: move black point, keep mids
d=np.clip((d-bp)/(1-bp),0,1); d=d**(1+0.6*bp*4*(1-d))
# brighter, cleaner whites: gain weighted to highlights with soft shoulder
Y2=(d*np.array([0.2126,0.7152,0.0722])).sum(-1,keepdims=True)
t=np.clip((Y2-0.52)/0.40,0,1); t=t*t*(3-2*t)
d=d*(1+wk*t); d=np.where(d>0.85,0.85+0.15*np.tanh((d-0.85)/0.15),d)
d=np.clip(d,0,1)
with open(out,'w') as f:
    f.write('LUT_3D_SIZE %d\n'%N)
    np.savetxt(f,d,fmt='%.6f')
