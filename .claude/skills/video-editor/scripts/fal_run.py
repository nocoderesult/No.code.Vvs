#!/usr/bin/env python3
"""Call fal.ai models from the skill: price, estimate, schema, upload, submit (queue) and resume.

The key is FAL_KEY from the environment, or from the git-ignored `.env` at the repository root (fal's agent-connect
flow writes it there, see reference/fal.md). It is never printed, logged, put in a URL or on a command line.

Submitting is billable, so `submit` is a dry run unless `--yes` is given. Every submitted job is appended to
`<out>/fal_jobs.jsonl` (time, endpoint, request id) before the script waits on it. If the wait is cut off, fetch the
same job with `resume`: submitting again starts a second, separately billed job.

Examples:
  fal_run.py price kling/v4/image-to-video google/gemini-omni-flash/v1.2/image-to-video
  fal_run.py estimate kling/v4/image-to-video=3 fal-ai/nano-banana-pro/edit=2
  fal_run.py schema kling/v4/image-to-video
  fal_run.py upload frame.png
  fal_run.py submit kling/v4/image-to-video --args job.json --file start_image_url=frame.png --out fal_out
  fal_run.py submit kling/v4/image-to-video --args job.json --file start_image_url=frame.png --out fal_out --yes
  fal_run.py resume kling/v4/image-to-video 0a1b2c3d-... --out fal_out
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import time
import urllib.parse

import httpx

API = "https://api.fal.ai/v1"
CREDITS_URL = "https://fal.ai/dashboard/usage-billing/credits"
FAL_SUFFIXES = (".fal.run", ".fal.ai", ".fal.media")


def die(msg: str, code: int = 1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def is_fal_origin(url: str) -> bool:
    u = urllib.parse.urlparse(url)
    host = (u.hostname or "").lower()
    return u.scheme == "https" and (host in ("fal.run", "fal.ai", "fal.media") or host.endswith(FAL_SUFFIXES))


def load_key() -> str:
    """FAL_KEY from the environment, else from the first .env with a FAL_KEY line, walking up from the cwd and from
    this script (the repository root holds it). The value never leaves this process."""
    key = os.environ.get("FAL_KEY", "").strip()
    if key:
        return key
    seen = set()
    for start in (pathlib.Path.cwd(), pathlib.Path(__file__).resolve().parent):
        for d in (start, *start.parents):
            env = d / ".env"
            if env in seen or not env.is_file():
                continue
            seen.add(env)
            try:
                for line in env.read_text().splitlines():
                    if line.strip().startswith("FAL_KEY="):
                        value = line.split("=", 1)[1].strip().strip("'\"")
                        if value:
                            return value
            except OSError:
                die(f"FAL_KEY: {env} is not readable (state unknown, the key was not replaced).")
    die("FAL_KEY is absent. Connect the project first: reference/fal.md (fal's agent-connect, the user approves "
        "in the browser).")


def http(key: str | None = None) -> httpx.Client:
    # trust_env (default) keeps the session's HTTPS proxy and CA bundle; TLS verification stays on.
    headers = {"Authorization": f"Key {key}"} if key else {}
    return httpx.Client(timeout=60, headers=headers, follow_redirects=True)


def explain_http_error(status: int, body: str):
    print(f"fal answered HTTP {status}: {body[:400]}", file=sys.stderr)
    if status == 403:
        if "exhausted balance" in body.lower():
            print(f"The integration works; the account needs credits: {CREDITS_URL}", file=sys.stderr)
        else:
            print("The account is locked for the reason above; credits do not lift other locks. Not retrying.",
                  file=sys.stderr)


# ---------------------------------------------------------------- read-only commands (not billed)

def cmd_price(a):
    key = load_key()
    with http(key) as c:
        r = c.get(f"{API}/models/pricing", params=[("endpoint_id", e) for e in a.endpoints])
        if r.status_code != 200:
            explain_http_error(r.status_code, r.text)
            sys.exit(1)
        for p in r.json().get("prices", []):
            print(f"{p['endpoint_id']}: base {p['unit_price']} {p['currency']} per {p['unit']}")
        with http() as pub:
            for e in a.endpoints:
                doc = pub.get(f"https://fal.ai/models/{e}/llms.txt")
                m = re.search(r"## Pricing\s*\n(.*?)(?:\n## |\nFor more details)", doc.text, re.S) if doc.status_code == 200 else None
                if m:
                    print(f"  {e} (model page): {' '.join(m.group(1).split())}")


def cmd_estimate(a):
    key = load_key()
    endpoints = {}
    for item in a.items:
        ep, _, qty = item.rpartition("=")
        if not ep:
            die(f"estimate takes endpoint=units, got {item!r}")
        endpoints[ep] = {"unit_quantity": float(qty)}
    with http(key) as c:
        r = c.post(f"{API}/models/pricing/estimate", json={"estimate_type": "unit_price", "endpoints": endpoints})
        if r.status_code != 200:
            explain_http_error(r.status_code, r.text)
            sys.exit(1)
        d = r.json()
        print(f"estimated total: {d['total_cost']} {d['currency']} (base unit prices; see `price` for resolution tiers)")


def cmd_schema(a):
    with http() as c:
        r = c.get(f"{API}/models", params={"endpoint_id": a.endpoint, "expand": "openapi-3.0"})
        r.raise_for_status()
        models = r.json().get("models") or die(f"unknown endpoint {a.endpoint}")
    m = models[0]
    md, spec = m["metadata"], m.get("openapi") or {}
    comps = spec.get("components", {}).get("schemas", {})

    def deref(node, depth=0):
        while isinstance(node, dict) and "$ref" in node and depth < 6:
            node = comps.get(node["$ref"].split("/")[-1], {})
            depth += 1
        return node

    def show(title, schema):
        schema = deref(schema)
        req = set(schema.get("required", []))
        print(title)
        for name, prop in schema.get("properties", {}).items():
            prop = deref(prop)
            enum = prop.get("enum") or next((deref(x).get("enum") for x in prop.get("anyOf", []) if deref(x).get("enum")), None)
            bits = [prop.get("type") or "/".join(deref(x).get("type", "?") for x in prop.get("anyOf", []))]
            for k, v in (("enum", enum), ("default", prop.get("default")), ("min", prop.get("minimum")), ("max", prop.get("maximum"))):
                if v not in (None, []):
                    bits.append(f"{k}={v}")
            desc = " ".join((prop.get("description") or "").split())[:140]
            print(f"  {name}{' (required)' if name in req else ''}: {' '.join(map(str, bits))}  {desc}")

    print(f"{a.endpoint}: {md['display_name']} [{md['category']}] {md.get('status')}; retires: {m.get('retires_at')}")
    for path, ops in spec.get("paths", {}).items():
        post = ops.get("post") or {}
        body = post.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")
        if body and "{request_id}" not in path:
            show("input:", body)
    for path, ops in spec.get("paths", {}).items():
        get = ops.get("get") or {}
        out = get.get("responses", {}).get("200", {}).get("content", {}).get("application/json", {}).get("schema")
        if out and path.endswith("{request_id}"):
            show("output:", out)


# ---------------------------------------------------------------- uploads and jobs

def client(key: str):
    import fal_client
    return fal_client.SyncClient(key=key, default_timeout=120.0)


def upload(fc, path: str) -> str:
    """Upload to fal storage; on an HTTP error print fal's reason (the SDK raises before showing it) and stop."""
    import fal_client
    try:
        return fc.upload_file(pathlib.Path(path))
    except httpx.HTTPStatusError as e:
        explain_http_error(e.response.status_code, e.response.text)
    except fal_client.FalClientHTTPError as e:
        explain_http_error(e.status_code, str(e))
    die(f"upload of {path} failed; nothing was submitted.")


def cmd_upload(a):
    print(upload(client(load_key()), a.path))


def media_urls(node, path=""):
    if isinstance(node, dict):
        if isinstance(node.get("url"), str) and node["url"].startswith("http"):
            yield path or "file", node["url"], node.get("file_name")
        for k, v in node.items():
            if k != "url":
                yield from media_urls(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from media_urls(v, f"{path}[{i}]")


def save_result(out: pathlib.Path, request_id: str, result) -> list[pathlib.Path]:
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{request_id}.json").write_text(json.dumps(result, indent=1, ensure_ascii=False))
    saved = []
    with http() as c:
        for where, url, name in media_urls(result):
            if not is_fal_origin(url):
                print(f"skipped {where}: {url} is not on a fal origin", file=sys.stderr)
                continue
            ext = pathlib.Path(urllib.parse.urlparse(url).path).suffix or pathlib.Path(name or "").suffix or ".bin"
            dest = out / f"{request_id[:8]}_{re.sub(r'[^A-Za-z0-9]+', '_', where).strip('_')}{ext}"
            with c.stream("GET", url) as r:
                r.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in r.iter_bytes():
                        f.write(chunk)
            saved.append(dest)
            print(f"saved {dest} ({dest.stat().st_size / 1e6:.1f} MB)")
    return saved


def wait(handle, endpoint: str, out: pathlib.Path):
    import fal_client
    for url in (handle.status_url, handle.response_url):
        if not is_fal_origin(url):
            die(f"queue returned a non-fal URL ({urllib.parse.urlparse(url).hostname}); not polling it. "
                f"request id {handle.request_id}")
    last = None
    t0 = time.time()
    try:
        for st in handle.iter_events(with_logs=False, interval=2.0):
            label = type(st).__name__ + (f" (position {st.position})" if isinstance(st, fal_client.Queued) else "")
            if label != last:
                print(f"[{time.time() - t0:5.0f}s] {label}")
                last = label
        result = handle.get()
    except fal_client.FalClientHTTPError as e:
        explain_http_error(e.status_code, str(e))
        die(f"request id {handle.request_id}: fetch it later with `resume {endpoint} {handle.request_id}`")
    except (fal_client.FalClientTimeoutError, httpx.TimeoutException, KeyboardInterrupt):
        die(f"stopped waiting; the job keeps running. Fetch it with `resume {endpoint} {handle.request_id}` "
            f"(do not submit again).")
    save_result(out, handle.request_id, result)


def cmd_submit(a):
    args = json.loads(pathlib.Path(a.args).read_text()) if a.args else {}
    for item in a.file:
        name, _, path = item.partition("=")
        if not path:
            die(f"--file takes name=path, got {item!r}")
        if not pathlib.Path(path).is_file():
            die(f"--file {name}: {path} not found")
    print(f"endpoint: {a.endpoint}")
    print("arguments (files are uploaded on --yes):")
    print(json.dumps({**args, **{i.partition('=')[0]: f"<upload {i.partition('=')[2]}>" for i in a.file}},
                     indent=1, ensure_ascii=False))
    if not a.yes:
        print("dry run: nothing uploaded or billed. Check the price (`price`), then add --yes to submit.")
        return
    key = load_key()
    fc = client(key)
    for item in a.file:
        name, _, path = item.partition("=")
        url = upload(fc, path)
        if name.endswith("[]"):
            args.setdefault(name[:-2], []).append(url)
        else:
            args[name] = url
    import fal_client
    try:
        handle = fc.submit(a.endpoint, arguments=args)
    except fal_client.FalClientHTTPError as e:
        explain_http_error(e.status_code, str(e))
        sys.exit(1)
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "fal_jobs.jsonl", "a") as f:
        f.write(json.dumps({"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "endpoint": a.endpoint,
                            "request_id": handle.request_id, "arguments": args}, ensure_ascii=False) + "\n")
    print(f"submitted: request id {handle.request_id} (logged in {out / 'fal_jobs.jsonl'})")
    wait(handle, a.endpoint, out)


def cmd_resume(a):
    handle = client(load_key()).get_handle(a.endpoint, a.request_id)
    wait(handle, a.endpoint, pathlib.Path(a.out))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("price", help="unit price per endpoint (authenticated read, not billed)")
    p.add_argument("endpoints", nargs="+")
    p.set_defaults(fn=cmd_price)
    p = sub.add_parser("estimate", help="estimated total for endpoint=units pairs (not billed)")
    p.add_argument("items", nargs="+")
    p.set_defaults(fn=cmd_estimate)
    p = sub.add_parser("schema", help="input and output schema of an endpoint (public)")
    p.add_argument("endpoint")
    p.set_defaults(fn=cmd_schema)
    p = sub.add_parser("upload", help="upload a local file to fal storage, print its URL")
    p.add_argument("path")
    p.set_defaults(fn=cmd_upload)
    p = sub.add_parser("submit", help="queue a job (billable: dry run unless --yes)")
    p.add_argument("endpoint")
    p.add_argument("--args", help="JSON file with the model arguments")
    p.add_argument("--file", action="append", default=[], help="name=path: upload path, pass its URL as name "
                   "(name[]=path appends to a list)")
    p.add_argument("--out", default="fal_out")
    p.add_argument("--yes", action="store_true", help="really submit (billed)")
    p.set_defaults(fn=cmd_submit)
    p = sub.add_parser("resume", help="wait for / fetch a job already submitted (never resubmits)")
    p.add_argument("endpoint")
    p.add_argument("request_id")
    p.add_argument("--out", default="fal_out")
    p.set_defaults(fn=cmd_resume)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
