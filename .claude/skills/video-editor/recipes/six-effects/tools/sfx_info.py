"""Describe SFX files: duration, peak time, attack, decay, spectral centroid, loudness."""
import subprocess, sys, glob, os
import numpy as np
def load(p):
    raw = subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar","48000","-f","f32le","-"],capture_output=True).stdout
    return np.frombuffer(raw,np.float32)
names = dict(l.split("|",1) for l in open(sys.argv[2]).read().strip().splitlines()) if len(sys.argv)>2 else {}
for p in sorted(glob.glob(os.path.join(sys.argv[1],"*.*")), key=lambda x:int(os.path.basename(x).split('.')[0])):
    x = load(p); sr=48000
    if len(x)==0: print(p,"EMPTY"); continue
    env = np.sqrt(np.convolve(x**2, np.ones(480)/480, mode="same"))
    pk = int(np.argmax(env)); pkdb = 20*np.log10(env[pk]+1e-9)
    above = np.where(env > env[pk]*0.1)[0]
    on = above[0]/sr; off = above[-1]/sr
    seg = x[max(0,pk-4800):pk+9600]
    sp = np.abs(np.fft.rfft(seg*np.hanning(len(seg)))); f = np.fft.rfftfreq(len(seg),1/sr)
    cen = (sp*f).sum()/sp.sum()
    # rough low/mid/high energy split
    lo = sp[f<250].sum()/sp.sum(); hi = sp[f>4000].sum()/sp.sum()
    i = os.path.basename(p).split('.')[0]
    print(f"{i:>5} {os.path.splitext(p)[1]:4} dur={len(x)/sr:5.2f}s  on={on:4.2f} peak@{pk/sr:4.2f} ({pkdb:5.1f}dB) tail→{off:4.2f}  cen={cen:5.0f}Hz lo={lo:.2f} hi={hi:.2f}  {names.get(i,'')}")
