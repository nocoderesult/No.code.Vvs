# Bundled models (small, offline-safe)

| File | Used by | Source | License |
|---|---|---|---|
| `face_detection_yunet_2023mar.onnx` (232 KB) | `reframe.py` face tracking | [OpenCV Zoo, YuNet](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet) | MIT |
| `rnnoise_sh.rnnn` (298 KB) | `audio_master.py`, `transcribe.py`, `plan_cuts.py` (ffmpeg `arnndn` denoise) | [GregorR/rnnoise-models](https://github.com/GregorR/rnnoise-models), `somnolent-hogwash-2018-09-01/sh.rnnn` | The repo README says the models are "not subject to copyright" |

If a file is missing, `vcommon.model_path()` downloads it from the URLs in `vcommon.MODELS` and checks its sha256:

- YuNet: `8f2383e4…2552fa4`
- RNNoise: `70bb6685…f3fdec0`

If the download fails too, the scripts fall back to:

- **Faces:** the OpenCV Haar cascade.
- **Denoise:** `afftdn`.
