#!/usr/bin/env python3
"""Generate Flux keyframes for the SALT demo film.

Reads payload/shots.json and renders each shot's first frame with Flux,
then derives each last frame from the first frame with Flux Kontext so
both frames share the same world (light, grade, lens) — the property
Wan 2.2 FLF2V needs to interpolate cleanly.

Backends (auto-detected from environment):
  FAL_KEY      -> fal.ai   (fal-ai/flux-pro/v1.1 + fal-ai/flux-pro/kontext)
  BFL_API_KEY  -> bfl.ai   (flux-pro-1.1 + flux-kontext-pro)

Usage:
  python payload/generate_keyframes.py             # render everything
  python payload/generate_keyframes.py --dry-run   # print the prompt plan
  python payload/generate_keyframes.py --shot 4    # render one shot
Stdlib only. Output: payload/keyframes/shotNN_A.png / shotNN_B.png
"""
import argparse
import base64
import json
import os
import ssl
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "keyframes")

CA_BUNDLE = os.environ.get("REQUESTS_CA_BUNDLE") or (
    "/root/.ccr/ca-bundle.crt" if os.path.exists("/root/.ccr/ca-bundle.crt") else None
)
SSL_CTX = ssl.create_default_context(cafile=CA_BUNDLE)


def http_json(url, payload=None, headers=None, method=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method or ("POST" if data else "GET"))
    req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=300) as resp:
        return json.loads(resp.read())


def http_download(url, path):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=300) as resp:
        with open(path, "wb") as f:
            f.write(resp.read())


def img_to_data_uri(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


class FalBackend:
    """fal.ai — synchronous fal.run endpoints."""

    name = "fal.ai"

    def __init__(self, key):
        self.headers = {"Authorization": f"Key {key}"}

    def generate(self, prompt, width, height, seed):
        body = {
            "prompt": prompt,
            "image_size": {"width": width, "height": height},
            "seed": seed,
            "num_images": 1,
            "safety_tolerance": "2",
        }
        out = http_json("https://fal.run/fal-ai/flux-pro/v1.1", body, self.headers)
        return out["images"][0]["url"]

    def kontext(self, prompt, image_path, seed):
        body = {
            "prompt": prompt,
            "image_url": img_to_data_uri(image_path),
            "seed": seed,
            "num_images": 1,
        }
        out = http_json("https://fal.run/fal-ai/flux-pro/kontext", body, self.headers)
        return out["images"][0]["url"]


class BflBackend:
    """Black Forest Labs direct API — submit then poll."""

    name = "bfl.ai"

    def __init__(self, key):
        self.headers = {"x-key": key}

    def _poll(self, submit):
        poll_url = submit["polling_url"]
        for _ in range(120):
            time.sleep(2)
            status = http_json(poll_url, headers=self.headers, method="GET")
            if status["status"] == "Ready":
                return status["result"]["sample"]
            if status["status"] not in ("Pending", "Queued", "Processing"):
                raise RuntimeError(f"BFL generation failed: {status}")
        raise TimeoutError("BFL polling timed out")

    def generate(self, prompt, width, height, seed):
        body = {"prompt": prompt, "width": width, "height": height, "seed": seed}
        return self._poll(http_json("https://api.bfl.ai/v1/flux-pro-1.1", body, self.headers))

    def kontext(self, prompt, image_path, seed):
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        body = {"prompt": prompt, "input_image": b64, "seed": seed, "aspect_ratio": "16:9"}
        return self._poll(http_json("https://api.bfl.ai/v1/flux-kontext-pro", body, self.headers))


def pick_backend():
    if os.environ.get("FAL_KEY"):
        return FalBackend(os.environ["FAL_KEY"])
    if os.environ.get("BFL_API_KEY"):
        return BflBackend(os.environ["BFL_API_KEY"])
    return None


def kontext_prompt(shot):
    # Kontext edits the first frame; the instruction is the delta plus hard
    # keep-constraints so lighting/grade/identity survive the edit.
    return (
        f"{shot['last_frame']}. Keep the exact same lighting, color grade, "
        "film grain, lens character, environment and framing as the input image."
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print the plan, render nothing")
    ap.add_argument("--shot", type=int, help="render only this shot id")
    ap.add_argument("--only", choices=["A", "B"], help="render only first (A) or last (B) frames")
    args = ap.parse_args()

    with open(os.path.join(ROOT, "shots.json")) as f:
        spec = json.load(f)

    shots = [s for s in spec["shots"] if args.shot is None or s["id"] == args.shot]
    if not shots:
        sys.exit(f"No shot with id {args.shot}")
    w, h = spec["render"]["width"], spec["render"]["height"]

    if args.dry_run:
        for s in shots:
            print(f"\n=== Shot {s['id']:02d} — {s['name']} ({s['type']}, {s['duration_s']}s, seed {s['seed']})")
            print(f"  A (Flux):    {s['first_frame']}, {spec['style_suffix']}")
            if s["last_frame"]:
                print(f"  B (Kontext): {kontext_prompt(s)}")
            print(f"  Wan motion:  {s['motion_prompt']}")
        return

    backend = pick_backend()
    if backend is None:
        sys.exit(
            "No image API key found. Set FAL_KEY (https://fal.ai/dashboard/keys) "
            "or BFL_API_KEY (https://api.bfl.ai), then re-run."
        )
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Backend: {backend.name} — rendering {len(shots)} shot(s) at {w}x{h}")

    for s in shots:
        a_path = os.path.join(OUT_DIR, f"shot{s['id']:02d}_A.png")
        if args.only != "B":
            prompt = f"{s['first_frame']}, {spec['style_suffix']}"
            print(f"[shot {s['id']:02d}] first frame …", flush=True)
            http_download(backend.generate(prompt, w, h, s["seed"]), a_path)
            print(f"  -> {a_path}")
        if s["last_frame"] and args.only != "A":
            if not os.path.exists(a_path):
                sys.exit(f"shot {s['id']:02d}: first frame missing — render A before B")
            b_path = os.path.join(OUT_DIR, f"shot{s['id']:02d}_B.png")
            print(f"[shot {s['id']:02d}] last frame (Kontext) …", flush=True)
            http_download(backend.kontext(kontext_prompt(s), a_path, s["seed"]), b_path)
            print(f"  -> {b_path}")

    print("\nDone. Review pairs side-by-side (curation gate) before Wan 2.2 FLF2V.")


if __name__ == "__main__":
    main()
