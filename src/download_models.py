"""
Download embedding and reranker models into data/models/ so they are
part of the project and not dependent on the user-level HuggingFace cache.

Run once: python src/download_models.py
"""

from pathlib import Path
from sentence_transformers import SentenceTransformer, CrossEncoder

MODEL_DIR = Path(__file__).parent.parent / "data" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODELS = [
    ("embedding", SentenceTransformer, "intfloat/multilingual-e5-base"),
    ("reranker",  CrossEncoder,        "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"),
]

for label, cls, name in MODELS:
    dest = MODEL_DIR / name.replace("/", "--")
    if dest.exists():
        print(f"  {label} already exists at {dest}, skipping.")
        continue
    print(f"  Downloading {label} ({name})...")
    model = cls(name)
    model.save(str(dest))
    print(f"  Saved to {dest}")

print("\nDone. Models are now stored in data/models/.")
