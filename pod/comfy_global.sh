#!/bin/bash
# Leagă ComfyUI de pe pod de volumul global, ca tot ce lucrezi să rămână salvat:
# modele, poze generate, poze urcate, workflow-uri, setări și lista de noduri.
# Prima dată:   bash /workspace/comfy_global.sh   (după ce l-ai urcat în Jupyter)
# Apoi, pe fiecare pod nou:   bash /workspace-global/pornire.sh

G="${GLOBAL_DIR:-/workspace-global}"
C="${COMFY_DIR:-/workspace/runpod-slim/ComfyUI}"
BAKED="Civicomfy ComfyUI-KJNodes ComfyUI-Manager ComfyUI-RunpodDirect"

if [ ! -d "$G" ]; then
  echo "❌ Nu găsesc volumul global la $G. Pornește pod-ul cu volumul global la /workspace-global."
  exit 1
fi

# 0. Scriptul se copiază singur pe global și face comanda de pornire
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
[ "$SELF" != "$G/comfy_global.sh" ] && cp "$SELF" "$G/comfy_global.sh"
if [ ! -f "$G/pornire.sh" ]; then
  cat > "$G/pornire.sh" <<'EOF'
#!/bin/bash
# Pornire completă pe un pod nou: ComfyUI legat de global, apoi Ollama și agentul.
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$D/comfy_global.sh"
[ -f "$D/9999.sh" ] && bash "$D/9999.sh"
EOF
fi

echo "Aștept să fie instalat ComfyUI..."
for i in $(seq 1 120); do [ -f "$C/main.py" ] && break; sleep 5; done
[ -f "$C/main.py" ] || { echo "❌ ComfyUI nu e instalat la $C."; exit 1; }
VENV="$(ls -d "$C"/.venv-* 2>/dev/null | head -1)"

# 1. Mută un folder pe global (fără să suprascrie ce e deja acolo) și pune o scurtătură în loc
leaga() {  # leaga <cale locală> <cale pe global>
  local loc="$1" glob="$2"
  [ -L "$loc" ] && return
  mkdir -p "$glob"
  if [ -d "$loc" ]; then
    cp -rn "$loc/." "$glob/" 2>/dev/null
    rm -rf "$loc"
  fi
  mkdir -p "$(dirname "$loc")"
  ln -s "$glob" "$loc"
}
leaga "$C/models"                       "$G/models"
# Pozele generate se scriu întâi pe discul pod-ului (unele noduri, ca MATRIX Metadata Killer,
# folosesc legături de fișiere pe care volumul global nu le suportă), apoi se copiază pe global.
[ -L "$C/output" ] && rm -f "$C/output"
mkdir -p "$C/output" "$G/comfyui/output"
( while sleep 60; do cp -rn "$C/output/." "$G/comfyui/output/" 2>/dev/null; done ) >/dev/null 2>&1 &
leaga "$C/input"                        "$G/comfyui/input"
leaga "$C/user/default/workflows"       "$G/comfyui/workflows"

# Setările ComfyUI (un singur fișier)
S_LOC="$C/user/default/comfy.settings.json"; S_GLOB="$G/comfyui/comfy.settings.json"
if [ ! -L "$S_LOC" ]; then
  mkdir -p "$(dirname "$S_LOC")" "$G/comfyui"
  [ -f "$S_GLOB" ] || { [ -f "$S_LOC" ] && cp "$S_LOC" "$S_GLOB" || echo "{}" > "$S_GLOB"; }
  rm -f "$S_LOC"; ln -s "$S_GLOB" "$S_LOC"
fi
echo "✓ Modele, workflow-uri și setări legate de volumul global; pozele se copiază pe global la fiecare minut."

# 2. Nodurile: lista stă pe global, nodurile se reinstalează pe fiecare pod
LISTA="$G/noduri.txt"
[ -f "$LISTA" ] || echo "https://github.com/artokun/comfyui-mcp-panel" > "$LISTA"
noteaza_noduri() {
  for d in "$C"/custom_nodes/*/; do
    n="$(basename "$d")"
    case " $BAKED " in *" $n "*) continue ;; esac
    [ -e "$d/.git" ] || continue   # doar noduri care sunt ele însele depozite git
    url="$(git -C "$d" remote get-url origin 2>/dev/null)" || continue
    case "$url" in *comfyanonymous/ComfyUI*|*Comfy-Org/ComfyUI.git) continue ;; esac
    grep -qxF "$url" "$LISTA" || echo "$url" >> "$LISTA"
  done
}
noteaza_noduri
while read -r url; do
  case "$url" in ""|\#*|*comfyanonymous/ComfyUI*|*Comfy-Org/ComfyUI.git) continue ;; esac
  n="$(basename "$url" .git)"
  if [ ! -d "$C/custom_nodes/$n" ]; then
    echo "Instalez nodul $n..."
    git clone -q --depth 1 "$url" "$C/custom_nodes/$n"
    if [ -f "$C/custom_nodes/$n/requirements.txt" ] && [ -n "$VENV" ]; then
      "$VENV/bin/python" -m pip install -q -r "$C/custom_nodes/$n/requirements.txt" 2>&1 | grep -E "^ERROR" || true
    fi
  fi
done < "$LISTA"
# La fiecare 10 minute notează nodurile noi instalate din Manager
( while sleep 600; do noteaza_noduri; done ) >/dev/null 2>&1 &
echo "✓ Noduri instalate din lista de pe global."

# 3. Instalări suplimentare de pe global (de ex. workflow-ul MATRIX Krea 2)
for s in "$G"/la_pornire/*.sh; do
  [ -f "$s" ] && { echo "Rulez $(basename "$s")..."; bash "$s"; }
done

# 4. Repornesc ComfyUI ca să vadă totul
[ -n "$NO_RESTART" ] && { echo "(fără repornire)"; exit 0; }
echo "Repornesc ComfyUI..."
pkill -f "python main.py" 2>/dev/null; sleep 3
ARGS="--listen 0.0.0.0 --port 8188 --enable-cors-header $(grep -v '^#' /workspace/runpod-slim/comfyui_args.txt 2>/dev/null | tr '\n' ' ')"
cd "$C" && source "$VENV/bin/activate"
nohup python main.py $ARGS > /workspace/comfyui.log 2>&1 &
for i in $(seq 1 60); do
  curl -s -o /dev/null http://127.0.0.1:8188 && { echo "✅ ComfyUI a pornit. Reîncarcă pagina ComfyUI."; exit 0; }
  sleep 3
done
echo "⚠️ ComfyUI încă pornește. Uită-te în /workspace/comfyui.log dacă durează mult."
