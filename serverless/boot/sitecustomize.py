"""Pornire MATRIX pe worker-ul oficial runpod/worker-comfyui, fără imagine proprie.

Endpoint-ul are PYTHONPATH=/runpod-volume/boot, așa că Python importă acest fișier
la fiecare pornire. Doar procesul ComfyUI (/comfyui/main.py) rulează pregătirea:
nodurile MATRIX + rgthree, pachetele pentru piele/ochi și căile modelelor de pe volum.
Handler-ul worker-ului așteaptă cât timp procesul ComfyUI trăiește, deci pauza e sigură.
"""
import os
import subprocess

try:
    with open("/proc/self/cmdline", "rb") as f:
        _cmd = f.read().split(b"\0")
except OSError:
    _cmd = []

if any(part.endswith(b"/comfyui/main.py") for part in _cmd) and not os.path.exists("/tmp/.boot_matrix_done"):
    _script = "/runpod-volume/boot_matrix.sh"
    if os.path.exists(_script):
        subprocess.run(["bash", _script], check=False)
    open("/tmp/.boot_matrix_done", "w").close()
