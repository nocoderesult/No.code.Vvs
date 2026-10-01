"""Generates krea2_studio.json - Krea 2 + Z-Image realism workflow, rebuilt from scratch.

Two modes (text2img / img2img from a reference photo) picked with an rgthree
Fast Groups Muter and joined by an Any Switch, 5-slot LoRA stack, hires fix,
Z-Image upscale + skin refine, face/hand detailers, phone look, save.
Run: python3 build_studio.py
"""
import json
import random
random.seed(11)

HF_KREA = "https://huggingface.co/Comfy-Org/Krea-2/resolve/main"
HF_Z = "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files"
HF_ESRGAN = "https://huggingface.co/Comfy-Org/Real-ESRGAN_repackaged/resolve/main"

nodes, links, groups = [], [], []
_nid = [0]
_lid = [0]


def model(name, url, directory):
    return {"name": name, "url": url, "directory": directory}


def add(type_, pos, widgets=None, inputs=None, outputs=None, size=(320, 120),
        title=None, mode=0, models=None, color=None):
    """inputs: list of (name, type) or (name, type, widget_name)."""
    _nid[0] += 1
    node = {
        "id": _nid[0],
        "type": type_,
        "pos": list(pos),
        "size": list(size),
        "flags": {},
        "order": _nid[0],
        "mode": mode,
        "inputs": [],
        "outputs": [],
        "properties": {"Node name for S&R": type_},
        "widgets_values": widgets if widgets is not None else [],
    }
    for inp in inputs or []:
        entry = {"name": inp[0], "type": inp[1], "link": None}
        if len(inp) > 2:
            entry["widget"] = {"name": inp[2]}
        node["inputs"].append(entry)
    for i, (oname, otype) in enumerate(outputs or []):
        node["outputs"].append({"name": oname, "type": otype, "links": [], "slot_index": i})
    if title:
        node["title"] = title
    if models:
        node["properties"]["models"] = models
    if color:
        node["color"], node["bgcolor"] = color
    nodes.append(node)
    return node


def link(src, src_slot, dst, dst_name):
    _lid[0] += 1
    lid = _lid[0]
    out = src["outputs"][src_slot]
    out["links"].append(lid)
    slot = next(i for i, inp in enumerate(dst["inputs"]) if inp["name"] == dst_name)
    dst["inputs"][slot]["link"] = lid
    links.append([lid, src["id"], src_slot, dst["id"], slot, out["type"]])


def group(title, x, y, w, h, color="#3f789e"):
    groups.append({"id": len(groups) + 1, "title": title, "bounding": [x, y, w, h],
                   "color": color, "font_size": 24, "flags": {}})


def seed():
    return random.randint(1, 2**48)



IMG = [("IMAGE", "IMAGE")]
NODE = ("#3d1a5c", "#6a2fa0")      # noduri mov
G = "#a1309b"                       # grupuri mov
G2 = "#6a2fa0"
KS_IN = [("model", "MODEL"), ("positive", "CONDITIONING"), ("negative", "CONDITIONING"),
         ("latent_image", "LATENT")]
LAT = [("LATENT", "LATENT")]


def n(*a, **k):
    k.setdefault("color", NODE)
    return add(*a, **k)


# ============================== RAND 1 ======================================
# ---------------------------------------------------------- PANOU CONTROL
group("PANOU CONTROL", 0, 0, 420, 1180, G)
mut = n("Fast Groups Muter (rgthree)", (20, 60), size=(380, 200), title="ALEGE MODUL (porneste doar unul)")
mut["properties"].update({"matchColors": "", "matchTitle": "^MOD", "showNav": True,
                          "sort": "position", "customSortAlphabet": "", "toggleRestriction": "max one"})
byp = n("Fast Groups Bypasser (rgthree)", (20, 290), size=(380, 860), title="PORNESTE / OPRESTE GRUPURI")
byp["properties"].update({"matchColors": "", "matchTitle": "^(?!MOD|PANOU|MODELE|PROMPT)",
                          "showNav": True, "sort": "position", "customSortAlphabet": "",
                          "toggleRestriction": "default"})

# --------------------------------------------------------------- PROMPT
group("PROMPT", 460, 0, 440, 760, G)
p_char = n("PrimitiveStringMultiline", (480, 60), size=(400, 240), title="Personaj (fix)",
           widgets=["a 26-year-old Eastern European woman with fair skin and warm undertones, visible pores "
                    "and fine natural skin texture, faint freckles on the nose, a tiny scar on the left eyebrow, "
                    "light brown shoulder-length hair with darker roots, slightly messy with loose strands, "
                    "grey-blue eyes, natural unshaped eyebrows, little makeup, small silver stud earrings"],
           outputs=[("STRING", "STRING")])
p_scene = n("PrimitiveStringMultiline", (480, 320), size=(400, 240), title="Scena (se schimba)",
            widgets=["taking a mirror selfie in a bright bedroom in the late morning, wearing a fitted black "
                     "ribbed crop top and high-waisted jeans, relaxed confident expression, unmade bed behind "
                     "her, soft daylight from a side window, real smartphone mirror selfie, natural colors"],
            outputs=[("STRING", "STRING")])
p_join = n("StringConcatenate", (480, 580), size=(400, 120), widgets=["", "", ", "],
           inputs=[("string_a", "STRING", "string_a"), ("string_b", "STRING", "string_b")],
           outputs=[("STRING", "STRING")], title="Prompt final")
link(p_char, 0, p_join, "string_a")
link(p_scene, 0, p_join, "string_b")

# ------------------------------------------------------------ LORA STACK
group("LORA STACK (Ctrl+B pe fiecare LoRA)", 940, 0, 420, 760, G2)
k_unet = n("UNETLoader", (960, 60), widgets=["krea2_turbo_fp8_scaled.safetensors", "default"],
           outputs=[("MODEL", "MODEL")], size=(380, 90), title="Model Krea 2 Turbo",
           models=[model("krea2_turbo_fp8_scaled.safetensors",
                         f"{HF_KREA}/diffusion_models/krea2_turbo_fp8_scaled.safetensors", "diffusion_models")])
prev_model = k_unet
lora_titles = ["LoRA 1 - personaj", "LoRA 2 - piele / realism", "LoRA 3 - stil telefon",
               "LoRA 4 - liber", "LoRA 5 - liber"]
for i, t in enumerate(lora_titles):
    lo = n("LoraLoaderModelOnly", (960, 170 + i * 110), widgets=[f"lora_{i + 1}.safetensors", 0.8],
           inputs=[("model", "MODEL")], outputs=[("MODEL", "MODEL")], size=(380, 90), title=t, mode=4)
    link(prev_model, 0, lo, "model")
    prev_model = lo
k_model = prev_model

# ------------------------------------------------------- MODELE KREA
group("MODELE KREA", 1400, 0, 420, 520, G)
k_clip = n("CLIPLoader", (1420, 60), widgets=["qwen3vl_4b_fp8_scaled.safetensors", "krea2", "default"],
           outputs=[("CLIP", "CLIP")], size=(380, 110),
           models=[model("qwen3vl_4b_fp8_scaled.safetensors",
                         f"{HF_KREA}/text_encoders/qwen3vl_4b_fp8_scaled.safetensors", "text_encoders")])
k_vae = n("VAELoader", (1420, 190), widgets=["qwen_image_vae.safetensors"], outputs=[("VAE", "VAE")],
          size=(380, 60), models=[model("qwen_image_vae.safetensors", f"{HF_KREA}/vae/qwen_image_vae.safetensors", "vae")])
k_pos = n("CLIPTextEncode", (1420, 270), widgets=[""], inputs=[("clip", "CLIP"), ("text", "STRING", "text")],
          outputs=[("CONDITIONING", "CONDITIONING")], size=(380, 100), title="Prompt Krea")
k_neg = n("ConditioningZeroOut", (1420, 400), inputs=[("conditioning", "CONDITIONING")],
          outputs=[("CONDITIONING", "CONDITIONING")], size=(380, 50))
link(k_clip, 0, k_pos, "clip")
link(p_join, 0, k_pos, "text")
link(k_pos, 0, k_neg, "conditioning")


def krea_sampler(pos, title, denoise, steps=8):
    ks = n("KSampler", pos, widgets=[seed(), "randomize", steps, 1, "euler", "simple", denoise],
           inputs=KS_IN, outputs=LAT, size=(380, 270), title=title)
    link(k_model, 0, ks, "model")
    link(k_pos, 0, ks, "positive")
    link(k_neg, 0, ks, "negative")
    return ks


# ------------------------------------------------------- MOD TEXT2IMG
group("MOD 1 - TEXT2IMG (din prompt)", 1860, 0, 420, 520, G)
latent = n("EmptyLatentImage", (1880, 60), widgets=[896, 1152, 1], outputs=LAT, size=(380, 110),
           title="Marime 896x1152 (4:5) / batch")
t2i = krea_sampler((1880, 200), "Generare din prompt", 1.0)
link(latent, 0, t2i, "latent_image")

# ------------------------------------------------------- MOD IMG2IMG
group("MOD 2 - IMG2IMG (din poza de referinta)", 2320, 0, 420, 800, G2)
ref = n("LoadImage", (2340, 60), widgets=["example.png", "image"], outputs=[("IMAGE", "IMAGE"), ("MASK", "MASK")],
        size=(380, 260), title="Poza de referinta")
ref_norm = n("ImageScaleToTotalPixels", (2340, 340), widgets=["lanczos", 1, 1], inputs=[("image", "IMAGE")],
             outputs=IMG, size=(380, 80), title="Referinta la 1 MP")
ref_enc = n("VAEEncode", (2340, 440), inputs=[("pixels", "IMAGE"), ("vae", "VAE")], outputs=LAT, size=(380, 50))
link(ref, 0, ref_norm, "image")
link(ref_norm, 0, ref_enc, "pixels")
link(k_vae, 0, ref_enc, "vae")
i2i = krea_sampler((2340, 510), "Generare din poza (denoise 0.6)", 0.6)
link(ref_enc, 0, i2i, "latent_image")
for nd in (ref, ref_norm, ref_enc, i2i):
    nd["mode"] = 2          # pornit din PANOU CONTROL

# ------------------------------------------------------- HIRES FIX
group("HIRES FIX KREA", 2780, 0, 420, 760, G)
sw = n("Any Switch (rgthree)", (2800, 60), size=(380, 110), title="Mod activ",
       inputs=[("any_01", "*"), ("any_02", "*"), ("any_03", "*")], outputs=[("*", "*")])
link(i2i, 0, sw, "any_01")
link(t2i, 0, sw, "any_02")
up_lat = n("LatentUpscaleBy", (2800, 190), widgets=["nearest-exact", 1.5], inputs=[("samples", "LATENT")],
           outputs=LAT, size=(380, 90))
link(sw, 0, up_lat, "samples")
ks2 = krea_sampler((2800, 300), "Pas 2 detalii (denoise 0.45)", 0.45)
link(up_lat, 0, ks2, "latent_image")
k_dec = n("VAEDecode", (2800, 590), inputs=[("samples", "LATENT"), ("vae", "VAE")], outputs=IMG, size=(380, 50),
          title="Imagine Krea")
link(ks2, 0, k_dec, "samples")
link(k_vae, 0, k_dec, "vae")

# ------------------------------------------------------- PREVIEW
group("PREVIEW KREA", 3240, 0, 520, 760, G2)
prev1 = n("PreviewImage", (3260, 60), inputs=[("images", "IMAGE")], size=(480, 680))
link(k_dec, 0, prev1, "images")

# ============================== RAND 2 ======================================
Y = 860
# ------------------------------------------------------- MODELE Z
group("MODELE Z-IMAGE", 460, Y, 440, 620, G)
z_unet = n("UNETLoader", (480, Y + 60), widgets=["z_image_turbo_bf16.safetensors", "default"],
           outputs=[("MODEL", "MODEL")], size=(400, 90),
           models=[model("z_image_turbo_bf16.safetensors", f"{HF_Z}/diffusion_models/z_image_turbo_bf16.safetensors", "diffusion_models")])
z_shift = n("ModelSamplingAuraFlow", (480, Y + 170), widgets=[3], inputs=[("model", "MODEL")],
            outputs=[("MODEL", "MODEL")], size=(400, 60))
z_clip = n("CLIPLoader", (480, Y + 250), widgets=["qwen_3_4b.safetensors", "lumina2", "default"],
           outputs=[("CLIP", "CLIP")], size=(400, 110),
           models=[model("qwen_3_4b.safetensors", f"{HF_Z}/text_encoders/qwen_3_4b.safetensors", "text_encoders")])
z_vae = n("VAELoader", (480, Y + 380), widgets=["ae.safetensors"], outputs=[("VAE", "VAE")], size=(400, 60),
          models=[model("ae.safetensors", f"{HF_Z}/vae/ae.safetensors", "vae")])
z_pos = n("CLIPTextEncode", (480, Y + 460), widgets=[""], inputs=[("clip", "CLIP"), ("text", "STRING", "text")],
          outputs=[("CONDITIONING", "CONDITIONING")], size=(400, 80), title="Prompt Z-Image")
z_neg = n("ConditioningZeroOut", (480, Y + 560), inputs=[("conditioning", "CONDITIONING")],
          outputs=[("CONDITIONING", "CONDITIONING")], size=(400, 50))
link(z_unet, 0, z_shift, "model")
link(z_clip, 0, z_pos, "clip")
link(p_join, 0, z_pos, "text")
link(z_pos, 0, z_neg, "conditioning")

# ------------------------------------------------------- UPSCALE + REFINE
group("UPSCALE + REFINE PIELE (Z-IMAGE)", 940, Y, 880, 620, G2)
norm = n("ImageScaleToTotalPixels", (960, Y + 60), widgets=["lanczos", 1, 1], inputs=[("image", "IMAGE")],
         outputs=IMG, size=(380, 80), title="Normalizare 1 MP")
up_model = n("UpscaleModelLoader", (960, Y + 160), widgets=["RealESRGAN_x4plus.safetensors"],
             outputs=[("UPSCALE_MODEL", "UPSCALE_MODEL")], size=(380, 60),
             models=[model("RealESRGAN_x4plus.safetensors", f"{HF_ESRGAN}/RealESRGAN_x4plus.safetensors", "upscale_models")])
up_img = n("ImageUpscaleWithModel", (960, Y + 240), inputs=[("upscale_model", "UPSCALE_MODEL"), ("image", "IMAGE")],
           outputs=IMG, size=(380, 50))
up_scale = n("ImageScaleBy", (960, Y + 310), widgets=["lanczos", 0.5], inputs=[("image", "IMAGE")], outputs=IMG,
             size=(380, 80), title="x4 -> x2")
link(k_dec, 0, norm, "image")
link(up_model, 0, up_img, "upscale_model")
link(norm, 0, up_img, "image")
link(up_img, 0, up_scale, "image")
z_enc = n("VAEEncode", (1420, Y + 60), inputs=[("pixels", "IMAGE"), ("vae", "VAE")], outputs=LAT, size=(380, 50))
z_ks = n("KSampler", (1420, Y + 130), widgets=[seed(), "randomize", 5, 1, "dpmpp_2m_sde", "beta", 0.33],
         inputs=KS_IN, outputs=LAT, size=(380, 270), title="Refine piele (denoise 0.33)")
z_dec = n("VAEDecode", (1420, Y + 420), inputs=[("samples", "LATENT"), ("vae", "VAE")], outputs=IMG,
          size=(380, 50))
link(up_scale, 0, z_enc, "pixels")
link(z_vae, 0, z_enc, "vae")
link(z_shift, 0, z_ks, "model")
link(z_pos, 0, z_ks, "positive")
link(z_neg, 0, z_ks, "negative")
link(z_enc, 0, z_ks, "latent_image")
link(z_ks, 0, z_dec, "samples")
link(z_vae, 0, z_dec, "vae")

# ------------------------------------------------------- DETAILERS
DETAILER_INPUTS = [("image", "IMAGE"), ("model", "MODEL"), ("clip", "CLIP"), ("vae", "VAE"),
                   ("positive", "CONDITIONING"), ("negative", "CONDITIONING"),
                   ("bbox_detector", "BBOX_DETECTOR"), ("sam_model_opt", "SAM_MODEL"),
                   ("segm_detector_opt", "SEGM_DETECTOR"), ("detailer_hook", "DETAILER_HOOK"),
                   ("scheduler_func_opt", "SCHEDULER_FUNC")]
DETAILER_OUTPUTS = [("image", "IMAGE"), ("cropped_refined", "IMAGE"), ("cropped_enhanced_alpha", "IMAGE"),
                    ("mask", "MASK"), ("detailer_pipe", "DETAILER_PIPE"), ("cnet_images", "IMAGE")]


def detailer_widgets(denoise):
    return [512, True, 1024, seed(), "fixed", 4, 1.0, "euler", "normal", denoise, 5, True, True,
            0.40, 10, 3.0, "center-1", 0, 0.80, 0, 0.70, "False", 10, "", 1, False, 100, False, False]


group("DETAILER FATA", 1860, Y, 420, 960, G)
face_det = n("UltralyticsDetectorProvider", (1880, Y + 60), widgets=["bbox/face_yolov8m.pt"],
             outputs=[("BBOX_DETECTOR", "BBOX_DETECTOR"), ("SEGM_DETECTOR", "SEGM_DETECTOR")],
             size=(380, 80), title="Detector fata")
sam = n("SAMLoader", (1880, Y + 160), widgets=["sam_vit_b_01ec64.pth", "AUTO"],
        outputs=[("SAM_MODEL", "SAM_MODEL")], size=(380, 80))
face = n("FaceDetailer", (1880, Y + 260), widgets=detailer_widgets(0.30), inputs=DETAILER_INPUTS,
         outputs=DETAILER_OUTPUTS, size=(380, 680), title="Detailer fata")
link(z_dec, 0, face, "image")

group("DETAILER MAINI", 2320, Y, 420, 960, G2)
hand_det = n("UltralyticsDetectorProvider", (2340, Y + 60), widgets=["bbox/hand_yolov8s.pt"],
             outputs=[("BBOX_DETECTOR", "BBOX_DETECTOR"), ("SEGM_DETECTOR", "SEGM_DETECTOR")],
             size=(380, 80), title="Detector maini")
hands = n("FaceDetailer", (2340, Y + 160), widgets=detailer_widgets(0.35), inputs=DETAILER_INPUTS,
          outputs=DETAILER_OUTPUTS, size=(380, 680), title="Detailer maini")
link(face, 0, hands, "image")
for d, det in ((face, face_det), (hands, hand_det)):
    link(z_shift, 0, d, "model")
    link(z_clip, 0, d, "clip")
    link(z_vae, 0, d, "vae")
    link(z_pos, 0, d, "positive")
    link(z_neg, 0, d, "negative")
    link(det, 0, d, "bbox_detector")
    link(sam, 0, d, "sam_model_opt")

# ------------------------------------------------------- LOOK TELEFON
group("LOOK TELEFON (vigneta, grain, claritate)", 2780, Y, 420, 700, G)
vign = n("ProPostVignette", (2800, Y + 60), widgets=[0.15, 0.5, 0.5], inputs=[("image", "IMAGE")], outputs=IMG,
         size=(380, 110), title="Vigneta lentila")
grain = n("ProPostFilmGrain", (2800, Y + 190), widgets=[False, "Fine", 0.3, 0.25, 0.15, 0.10, 1.0, 0, 1.0, 1, "fixed"],
          inputs=[("image", "IMAGE")], outputs=IMG, size=(380, 330), title="Granulatie senzor")
sharp = n("ImageSharpen", (2800, Y + 540), widgets=[1, 0.6, 0.25], inputs=[("image", "IMAGE")], outputs=IMG,
          size=(380, 110), title="Claritate finala")
link(hands, 0, vign, "image")
link(vign, 0, grain, "image")
link(grain, 0, sharp, "image")

# ------------------------------------------------------- REZULTAT
group("REZULTAT FINAL + SALVARE", 3240, Y, 520, 960, G2)
final = n("PreviewImage", (3260, Y + 60), inputs=[("images", "IMAGE")], size=(480, 560), title="Rezultat final")
save = n("SaveImage", (3260, Y + 640), widgets=["personaj/img"], inputs=[("images", "IMAGE")], size=(480, 300),
         title="Salvare")
link(sharp, 0, final, "images")
link(sharp, 0, save, "images")

# ------------------------------------------------------- GHID
group("GHID", 0, 1220, 420, 560, G2)
n("Note", (20, 1280), size=(380, 480), widgets=[
    "CUM FOLOSESTI\n"
    "1. ALEGE MODUL: TEXT2IMG (din prompt) sau IMG2IMG (din poza). Doar unul pornit.\n"
    "2. Scrii personajul o data in 'Personaj (fix)'. Schimbi doar 'Scena'.\n"
    "3. Run. Prima imagine apare in PREVIEW KREA, cea finala in REZULTAT FINAL.\n\n"
    "GRUPURI OPTIONALE (Panou control): Upscale, Detailer fata/maini, Look telefon.\n"
    "Opresti un grup = imaginea trece mai departe neschimbata.\n\n"
    "LORA: pune fisierul in models/loras, alege-l in nodul LoRA si apasa Ctrl+B pe nod ca sa-l pornesti.\n\n"
    "BATCH: in 'Marime' schimbi ultimul numar din 1 in 4 = 4 variante odata.\n"
    "ACEEASI FATA, ALTA SCENA: pe 'Generare din prompt' pune control_after_generate pe 'fixed'."])

workflow = {
    "last_node_id": _nid[0],
    "last_link_id": _lid[0],
    "nodes": nodes,
    "links": links,
    "groups": groups,
    "config": {},
    "extra": {"ds": {"scale": 0.35, "offset": [100, 100]}},
    "version": 0.4,
}

if __name__ == "__main__":
    with open("krea2_studio.json", "w") as f:
        json.dump(workflow, f, indent=1)
    print(f"{len(nodes)} nodes, {len(links)} links, {len(groups)} groups")
