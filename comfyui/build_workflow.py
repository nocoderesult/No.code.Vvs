"""Generates realism_krea2_nova.json - a ComfyUI workflow modelled on the
"REALISM KREA 2 NOVA v2" control-menu layout.

Node settings come from the official ComfyUI templates (Krea-2 Turbo,
Z-Image-Turbo, Z-Image 2K upscaler) and from the FaceDetailer screenshot.
Run: python3 build_workflow.py
"""
import json
import random
random.seed(7)

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
PURPLE = "#8A2BE2"
GREY = "#444444"

# ---------------------------------------------------------------- Main Meniu
group("Main Meniu", -460, -40, 420, 900, PURPLE)
add("Fast Groups Bypasser (rgthree)", (-440, 20), size=(380, 820), title="Control Menu",
    widgets=[],
    color=("#2a1a3a", "#3a2350"))
nodes[-1]["properties"].update({"matchColors": "", "matchTitle": "", "showNav": True,
                                "sort": "position", "customSortAlphabet": "",
                                "toggleRestriction": "default"})

# ---------------------------------------------------------- CONTROL NET GROUP
group("CONTROL NET GROUP", 0, -40, 420, 260, GREY)
add("Note", (20, 20), size=(380, 180), widgets=[
    "ControlNet (poza / ipostaza) - se adauga in sesiunea dedicata.\n"
    "Modelul: Z-Image-Turbo-Fun-Controlnet-Union (folder model_patches).\n"
    "Grupul ramane OPRIT pana atunci."])

# -------------------------------------------------------------- Prompt builder
group("Prompt builder", 0, 260, 420, 600)
p_char = add("PrimitiveStringMultiline", (20, 320), size=(380, 200), title="Personaj (fix)",
             widgets=["a 28-year-old woman, [descrierea fixa a personajului: par, ochi, ten, semn distinctiv, tinuta]"],
             outputs=[("STRING", "STRING")])
p_scene = add("PrimitiveStringMultiline", (20, 540), size=(380, 160), title="Scena (se schimba)",
              widgets=["candid smartphone photo, standing in a bright cafe, natural window light, relaxed smile"],
              outputs=[("STRING", "STRING")])
p_join = add("StringConcatenate", (20, 720), size=(380, 110), widgets=["", "", ", "],
             inputs=[("string_a", "STRING", "string_a"), ("string_b", "STRING", "string_b")],
             outputs=[("STRING", "STRING")])
link(p_char, 0, p_join, "string_a")
link(p_scene, 0, p_join, "string_b")

# ------------------------------------------------------------- Prompt guidance
group("Prompt guidance", 0, 900, 420, 260, GREY)
add("Note", (20, 960), size=(380, 180), widgets=[
    "Structura prompt: [personaj fix], [actiune], [loc], [incadrare camera], [lumina], "
    "candid smartphone photo.\nPersonajul NU se modifica intre poze - schimbi doar scena.\n"
    "Cand ai LoRA-ul personajului, pune cuvantul-declansator la inceputul descrierii."])

# ----------------------------------------------------------- LOAD KREA MODELS
group("LOAD KREA MODELS", 460, -40, 420, 700)
k_unet = add("UNETLoader", (480, 20), widgets=["krea2_turbo_fp8_scaled.safetensors", "default"],
             outputs=[("MODEL", "MODEL")], size=(380, 90),
             models=[model("krea2_turbo_fp8_scaled.safetensors", f"{HF_KREA}/diffusion_models/krea2_turbo_fp8_scaled.safetensors", "diffusion_models")])
k_lora = add("LoraLoaderModelOnly", (480, 130), widgets=["personaj_lora.safetensors", 1.0],
             inputs=[("model", "MODEL")], outputs=[("MODEL", "MODEL")], size=(380, 90),
             title="LoRA personaj (porneste-l cand ai LoRA)", mode=4)
k_clip = add("CLIPLoader", (480, 240), widgets=["qwen3vl_4b_fp8_scaled.safetensors", "krea2", "default"],
             outputs=[("CLIP", "CLIP")], size=(380, 110),
             models=[model("qwen3vl_4b_fp8_scaled.safetensors", f"{HF_KREA}/text_encoders/qwen3vl_4b_fp8_scaled.safetensors", "text_encoders")])
k_vae = add("VAELoader", (480, 370), widgets=["qwen_image_vae.safetensors"], outputs=[("VAE", "VAE")],
            size=(380, 60),
            models=[model("qwen_image_vae.safetensors", f"{HF_KREA}/vae/qwen_image_vae.safetensors", "vae")])
k_pos = add("CLIPTextEncode", (480, 450), widgets=[""], inputs=[("clip", "CLIP"), ("text", "STRING", "text")],
            outputs=[("CONDITIONING", "CONDITIONING")], size=(380, 90), title="Prompt Krea")
k_neg = add("ConditioningZeroOut", (480, 570), inputs=[("conditioning", "CONDITIONING")],
            outputs=[("CONDITIONING", "CONDITIONING")], size=(380, 50))
link(k_unet, 0, k_lora, "model")
link(k_clip, 0, k_pos, "clip")
link(p_join, 0, k_pos, "text")
link(k_pos, 0, k_neg, "conditioning")

# --------------------------------------------------------- LOAD Z IMAGE MODELS
group("LOAD Z IMAGE MODELS", 460, 700, 420, 700)
z_unet = add("UNETLoader", (480, 760), widgets=["z_image_turbo_bf16.safetensors", "default"],
             outputs=[("MODEL", "MODEL")], size=(380, 90),
             models=[model("z_image_turbo_bf16.safetensors", f"{HF_Z}/diffusion_models/z_image_turbo_bf16.safetensors", "diffusion_models")])
z_shift = add("ModelSamplingAuraFlow", (480, 870), widgets=[3], inputs=[("model", "MODEL")],
              outputs=[("MODEL", "MODEL")], size=(380, 60))
z_clip = add("CLIPLoader", (480, 950), widgets=["qwen_3_4b.safetensors", "lumina2", "default"],
             outputs=[("CLIP", "CLIP")], size=(380, 110),
             models=[model("qwen_3_4b.safetensors", f"{HF_Z}/text_encoders/qwen_3_4b.safetensors", "text_encoders")])
z_vae = add("VAELoader", (480, 1080), widgets=["ae.safetensors"], outputs=[("VAE", "VAE")], size=(380, 60),
            models=[model("ae.safetensors", f"{HF_Z}/vae/ae.safetensors", "vae")])
z_pos = add("CLIPTextEncode", (480, 1160), widgets=[""], inputs=[("clip", "CLIP"), ("text", "STRING", "text")],
            outputs=[("CONDITIONING", "CONDITIONING")], size=(380, 90), title="Prompt Z-Image")
z_neg = add("ConditioningZeroOut", (480, 1280), inputs=[("conditioning", "CONDITIONING")],
            outputs=[("CONDITIONING", "CONDITIONING")], size=(380, 50))
link(z_unet, 0, z_shift, "model")
link(z_clip, 0, z_pos, "clip")
link(p_join, 0, z_pos, "text")
link(z_pos, 0, z_neg, "conditioning")

# ------------------------------------------------------------------ Image size
group("Image size", 920, -40, 380, 200)
latent = add("EmptyLatentImage", (940, 20), widgets=[896, 1152, 1],
             outputs=[("LATENT", "LATENT")], size=(340, 110), title="Marime (896x1152 = 4:5)")

# ------------------------------------------------- KREA 2 .TWO PASS SAMPLING
group("KREA 2 .TWO PASS SAMPLING", 920, 200, 380, 760)
ks1 = add("KSampler", (940, 260), widgets=[seed(), "randomize", 8, 1, "euler", "simple", 1],
          inputs=[("model", "MODEL"), ("positive", "CONDITIONING"), ("negative", "CONDITIONING"),
                  ("latent_image", "LATENT")],
          outputs=[("LATENT", "LATENT")], size=(340, 270), title="Krea pas 1")
up_lat = add("LatentUpscaleBy", (940, 550), widgets=["nearest-exact", 1.5], inputs=[("samples", "LATENT")],
             outputs=[("LATENT", "LATENT")], size=(340, 90))
ks2 = add("KSampler", (940, 660), widgets=[seed(), "randomize", 8, 1, "euler", "simple", 0.45],
          inputs=[("model", "MODEL"), ("positive", "CONDITIONING"), ("negative", "CONDITIONING"),
                  ("latent_image", "LATENT")],
          outputs=[("LATENT", "LATENT")], size=(340, 270), title="Krea pas 2")
for ks in (ks1, ks2):
    link(k_lora, 0, ks, "model")
    link(k_pos, 0, ks, "positive")
    link(k_neg, 0, ks, "negative")
link(latent, 0, ks1, "latent_image")
link(ks1, 0, up_lat, "samples")
link(up_lat, 0, ks2, "latent_image")
k_dec = add("VAEDecode", (940, 1000), inputs=[("samples", "LATENT"), ("vae", "VAE")], outputs=IMG,
            size=(340, 50), title="Imagine Krea")
link(ks2, 0, k_dec, "samples")
link(k_vae, 0, k_dec, "vae")

# --------------------------------------------------- Preview first generation
group("Preview first generation", 1340, -40, 420, 520, GREY)
prev_dec = add("VAEDecode", (1360, 20), inputs=[("samples", "LATENT"), ("vae", "VAE")], outputs=IMG,
               size=(380, 50))
link(ks1, 0, prev_dec, "samples")
link(k_vae, 0, prev_dec, "vae")
prev1 = add("PreviewImage", (1360, 90), inputs=[("images", "IMAGE")], size=(380, 360))
link(prev_dec, 0, prev1, "images")

# ------------------------------------------------------ Z image Upscale mode
group("Z image Upscale mode", 1340, 520, 420, 400)
up_model = add("UpscaleModelLoader", (1360, 670), widgets=["RealESRGAN_x4plus.safetensors"],
               outputs=[("UPSCALE_MODEL", "UPSCALE_MODEL")], size=(380, 60),
               models=[model("RealESRGAN_x4plus.safetensors", f"{HF_ESRGAN}/RealESRGAN_x4plus.safetensors", "upscale_models")])
up_img = add("ImageUpscaleWithModel", (1360, 750), inputs=[("upscale_model", "UPSCALE_MODEL"), ("image", "IMAGE")],
             outputs=IMG, size=(380, 50))
up_scale = add("ImageScaleBy", (1360, 820), widgets=["lanczos", 0.5], inputs=[("image", "IMAGE")], outputs=IMG,
               size=(380, 80), title="x4 -> x2")
norm = add("ImageScaleToTotalPixels", (1360, 580), widgets=["lanczos", 1, 1], inputs=[("image", "IMAGE")],
            outputs=IMG, size=(380, 80), title="Normalizare la 1 MP")
link(k_dec, 0, norm, "image")
link(up_model, 0, up_img, "upscale_model")
link(norm, 0, up_img, "image")
link(up_img, 0, up_scale, "image")

# ------------------------------------------------- Z IMAGE SAMPLER REFINER
group("Z IMAGE SAMPLER REFINER", 1340, 920, 420, 520)
z_enc = add("VAEEncode", (1360, 980), inputs=[("pixels", "IMAGE"), ("vae", "VAE")],
            outputs=[("LATENT", "LATENT")], size=(380, 50))
z_ks = add("KSampler", (1360, 1050), widgets=[seed(), "randomize", 5, 1, "dpmpp_2m_sde", "beta", 0.33],
           inputs=[("model", "MODEL"), ("positive", "CONDITIONING"), ("negative", "CONDITIONING"),
                   ("latent_image", "LATENT")],
           outputs=[("LATENT", "LATENT")], size=(380, 270), title="Rafinare piele (denoise 0.33)")
z_dec = add("VAEDecode", (1360, 1340), inputs=[("samples", "LATENT"), ("vae", "VAE")], outputs=IMG,
            size=(380, 50))
link(up_scale, 0, z_enc, "pixels")
link(z_vae, 0, z_enc, "vae")
link(z_shift, 0, z_ks, "model")
link(z_pos, 0, z_ks, "positive")
link(z_neg, 0, z_ks, "negative")
link(z_enc, 0, z_ks, "latent_image")
link(z_ks, 0, z_dec, "samples")
link(z_vae, 0, z_dec, "vae")

# ------------------------------------------------------- Z IMAGE DETAILERS
group("Z IMAGE DETAILERS", 1800, -40, 440, 1000)
face_det = add("UltralyticsDetectorProvider", (1820, 20), widgets=["bbox/face_yolov8m.pt"],
               outputs=[("BBOX_DETECTOR", "BBOX_DETECTOR"), ("SEGM_DETECTOR", "SEGM_DETECTOR")],
               size=(400, 80), title="Detector fata")
sam = add("SAMLoader", (1820, 120), widgets=["sam_vit_b_01ec64.pth", "AUTO"],
          outputs=[("SAM_MODEL", "SAM_MODEL")], size=(400, 80))

DETAILER_INPUTS = [("image", "IMAGE"), ("model", "MODEL"), ("clip", "CLIP"), ("vae", "VAE"),
                   ("positive", "CONDITIONING"), ("negative", "CONDITIONING"),
                   ("bbox_detector", "BBOX_DETECTOR"), ("sam_model_opt", "SAM_MODEL"),
                   ("segm_detector_opt", "SEGM_DETECTOR"), ("detailer_hook", "DETAILER_HOOK"),
                   ("scheduler_func_opt", "SCHEDULER_FUNC")]
DETAILER_OUTPUTS = [("image", "IMAGE"), ("cropped_refined", "IMAGE"), ("cropped_enhanced_alpha", "IMAGE"),
                    ("mask", "MASK"), ("detailer_pipe", "DETAILER_PIPE"), ("cnet_images", "IMAGE")]


def detailer_widgets(denoise, seed_value):
    # Order = FaceDetailer.INPUT_TYPES widgets; values copied from the screenshot.
    return [512, True, 1024, seed_value, "fixed", 4, 1.0, "euler", "normal", denoise, 5, True, True,
            0.40, 10, 3.0, "center-1", 0, 0.80, 0, 0.70, "False", 10, "", 1, False, 100, False, False]


face = add("FaceDetailer", (1820, 220), widgets=detailer_widgets(0.30, 137053700462745),
           inputs=DETAILER_INPUTS, outputs=DETAILER_OUTPUTS, size=(400, 720), title="FaceDetailer (fata)")
for n in (face,):
    link(z_dec, 0, n, "image")

# --------------------------------------------------- Detailer boost options
group("Detailer boost options", 2280, -40, 440, 1000, GREY)
hand_det = add("UltralyticsDetectorProvider", (2300, 20), widgets=["bbox/hand_yolov8s.pt"],
               outputs=[("BBOX_DETECTOR", "BBOX_DETECTOR"), ("SEGM_DETECTOR", "SEGM_DETECTOR")],
               size=(400, 80), title="Detector maini")
hands = add("FaceDetailer", (2300, 120), widgets=detailer_widgets(0.35, 137053700462746),
            inputs=DETAILER_INPUTS, outputs=DETAILER_OUTPUTS, size=(400, 720), title="Detailer maini")
link(face, 0, hands, "image")
for n, det in ((face, face_det), (hands, hand_det)):
    link(z_shift, 0, n, "model")
    link(z_clip, 0, n, "clip")
    link(z_vae, 0, n, "vae")
    link(z_pos, 0, n, "positive")
    link(z_neg, 0, n, "negative")
    link(det, 0, n, "bbox_detector")
    link(sam, 0, n, "sam_model_opt")

# ------------------------------------------------------- Z IMAGE RESULTS
group("Z IMAGE RESULTS", 2760, -40, 420, 520, GREY)
z_prev = add("PreviewImage", (2780, 20), inputs=[("images", "IMAGE")], size=(380, 440))
link(hands, 0, z_prev, "images")

# -------------------------------------------------- AUTHENTICITY PROFILE
group("AUTHENTICITY PROFILE", 2760, 520, 420, 560)
vign = add("ProPostVignette", (2780, 580), widgets=[0.15, 0.5, 0.5], inputs=[("image", "IMAGE")], outputs=IMG,
           size=(380, 110), title="Lentila: vigneta")
grain = add("ProPostFilmGrain", (2780, 710), widgets=[False, "Fine", 0.3, 0.25, 0.15, 0.10, 1.0, 0, 1.0, 1, "fixed"],
            inputs=[("image", "IMAGE")], outputs=IMG, size=(380, 330), title="Granulatie senzor")
link(hands, 0, vign, "image")
link(vign, 0, grain, "image")

# --------------------------------------------------------- NOVA IMAGE FILTER
group("NOVA IMAGE FILTER", 3220, -40, 420, 260)
radial = add("ProPostRadialBlur", (3240, 20), widgets=[6.0, 0.5, 0.5, 2.0, 5], inputs=[("image", "IMAGE")],
             outputs=IMG, size=(380, 170), title="Margini usor moi (lentila telefon)")
link(grain, 0, radial, "image")

# ----------------------------------------------------- NOVA POST-PROCESOR
group("NOVA POST-PROCESOR", 3220, 260, 420, 200)
sharp = add("ImageSharpen", (3240, 320), widgets=[1, 0.6, 0.25], inputs=[("image", "IMAGE")], outputs=IMG,
            size=(380, 110), title="Claritate finala")
link(radial, 0, sharp, "image")

# --------------------------------------------------------- NOVA TEXT FILTER
group("NOVA TEXT FILTER", 3220, 500, 420, 200, GREY)
add("Note", (3240, 560), size=(380, 120), widgets=[
    "Rezervat. In original, grupul filtreaza textul promptului. Ramane OPRIT."])

# ---------------------------------------------------- SAVE WITH METADATA
group("SAVE WITH METADATA", 3680, -40, 420, 520)
save = add("SaveImage", (3700, 20), widgets=["personaj/img"], inputs=[("images", "IMAGE")], size=(380, 440),
           title="Salvare (promptul si setarile raman in PNG)")
link(sharp, 0, save, "images")

# ------------------------------------------------------------- Final result
group("Final result", 3680, 520, 420, 520)
final = add("PreviewImage", (3700, 580), inputs=[("images", "IMAGE")], size=(380, 440))
link(sharp, 0, final, "images")

# ------------------------------------------------ NSFW rows (left empty, OFF)
group("NSFW CONTENT GROUP", 4140, -40, 300, 120, GREY)
group("NSFW DETAILERS PREVIEW", 4140, 120, 300, 120, GREY)

workflow = {
    "last_node_id": _nid[0],
    "last_link_id": _lid[0],
    "nodes": nodes,
    "links": links,
    "groups": groups,
    "config": {},
    "extra": {"ds": {"scale": 0.45, "offset": [500, 100]}},
    "version": 0.4,
}

if __name__ == "__main__":
    with open("realism_krea2_nova.json", "w") as f:
        json.dump(workflow, f, indent=1)
    print(f"{len(nodes)} nodes, {len(links)} links, {len(groups)} groups")
