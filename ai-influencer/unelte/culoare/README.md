# Colorizare video

`applelog_lut.py` scrie un fișier `.cube` pe care ffmpeg îl aplică pe videoclipul original. Imaginea nu e regenerată: rezoluția, cadența și sunetul rămân cele filmate.

## Pași

1. Generezi LUT-ul:

```bash
python applelog_lut.py final.cube -0.95 1.20 1.12 0.03 1.7 0.05 0.32 0.30
```

2. Scoți câteva cadre de probă și te uiți la ele înainte de a randa tot clipul:

```bash
ffmpeg -ss 3.4 -i clip.mov -frames:v 1 -vf "zscale=matrixin=2020_ncl:rangein=limited:matrix=gbr:range=full,format=gbrp16le,lut3d=file=final.cube:interp=tetrahedral,scale=1080:1920:flags=lanczos" proba.png
```

3. Randezi videoclipul:

```bash
ffmpeg -i clip.mov -map 0:v:0 -map 0:a:0 -vf "zscale=matrixin=2020_ncl:rangein=limited:matrix=gbr:range=full,format=gbrp16le,lut3d=file=final.cube:interp=tetrahedral,scale=1080:1920:flags=lanczos,vignette=angle=PI/5.5,noise=alls=4:allf=t,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p" -c:v libx264 -crf 19 -preset slow -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv -c:a aac -b:a 256k -movflags +faststart rezultat.mp4
```

## De știut

- Comenzile sunt pentru material filmat în **Apple Log** (iPhone, ProRes, Rec.2020, nivel video limitat). Pentru alt material se schimbă partea `zscale=matrixin=...:rangein=...`.
- ffmpeg trebuie să aibă filtrele `zscale` și `lut3d`.
- Vigneta și granulația sunt ultimele două filtre de imagine; le scoți dacă nu le vrei.
- Schimbarea culorii unui singur obiect (de exemplu canapeaua) nu se poate face cu un LUT, pentru că LUT-ul schimbă aceeași culoare peste tot. În sesiune s-a făcut separat, cu o selecție după culoare și formă.
