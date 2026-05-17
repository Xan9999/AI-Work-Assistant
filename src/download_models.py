"""
Download embedding and reranker models into data/models/ so they are
part of the project and not dependent on the user-level HuggingFace cache.

Run once: python src/download_models.py
"""

from pathlib import Path
from huggingface_hub import snapshot_download

MODEL_DIR = Path(__file__).parent.parent / "data" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODELS = [
    ("embedding", "intfloat/multilingual-e5-base"),
    ("reranker",  "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"),
]

# Exclude safetensors — forces PyTorch to load pytorch_model.bin instead,
# which avoids a silent crash in the safetensors C extension on some Windows setups.
IGNORE = ["*.safetensors", "*.msgpack", "flax_model*", "tf_model*", "rust_model*", "onnx/*", "openvino/*", "*.onnx"]

for label, name in MODELS:
    dest = MODEL_DIR / name.replace("/", "--")
    if dest.exists() and any(dest.iterdir()):
        print(f"  {label} already exists at {dest}, skipping.")
        continue
    print(f"  Downloading {label} ({name})...")
    snapshot_download(
        repo_id=name,
        local_dir=str(dest),
        local_dir_use_symlinks=False,  # copy files directly, no HF cache involvement
        ignore_patterns=IGNORE,
    )
    print(f"  Saved to {dest}")

print("\nDone. Models are now stored in data/models/.")
