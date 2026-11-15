#!/usr/bin/env python3
"""Build a game ladder or a directory from independent public GitHub repos."""
from __future__ import annotations
import datetime as dt
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.github.com"
PROTO = "openrank/1"
SLUG = re.compile(r"[a-z0-9][a-z0-9-]{0,62}\Z")
REPO = re.compile(r"[A-Za-z0-9-]{1,39}/[A-Za-z0-9_.-]{1,100}\Z")


def get_json(url, token=""):
    headers = {"User-Agent": "openrank-portal/1", "Accept": "application/vnd.github+json"}
    if url.startswith(API):
        headers["X-GitHub-Api-Version"] = "2022-11-28"
        if token:
            headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=18) as res:
                body = res.read(1_000_001)
                if len(body) > 1_000_000:
                    return None
                return json.loads(body)
        except urllib.error.HTTPError as e:
            if e.code in (404, 403, 422):
                print("skip", url.split("?")[0], e.code)
                return None
            if e.code not in (429, 502, 503, 504):
                print("skip", e)
                return None
        except (TimeoutError, urllib.error.URLError, ValueError) as e:
            print("fetch failed", str(e))
        if attempt < 2:
            time.sleep(attempt + 1)
    return None


def discover(topic, token="", max_pages=10, fetch=get_json):
    found = {}
    for page in range(1, max_pages + 1):
        q = urllib.parse.urlencode({"q": f"topic:{topic} archived:false is:public", "sort": "updated", "order": "desc", "per_page": 100, "page": page})
        result = fetch(API + "/search/repositories?" + q, token)
        if not isinstance(result, dict):
            break
        items = result.get("items", [])
        for repo in items:
            full = repo.get("full_name", "")
            if REPO.fullmatch(full):
                found[full.lower()] = (full, repo.get("default_branch", "main"))
        if len(items) < 100:
            break
    return list(found.values())


def repo_json(full, branch, path, fetch=get_json):
    if not REPO.fullmatch(full):
        return None
    # Raw file URLs do not consume REST API requests, but are still rate/traffic limited.
    segments = [urllib.parse.quote(part, safe="") for part in full.split("/")]
    return fetch(f"https://raw.githubusercontent.com/{segments[0]}/{segments[1]}/{urllib.parse.quote(branch, safe='')}/{path}")


def page_url(full):
    owner, name = full.split("/", 1)
    if name.lower() == owner.lower() + ".github.io":
        return f"https://{name.lower()}/"
    return f"https://{owner.lower()}.github.io/{name}/"


def valid_player(value, full):
    if not isinstance(value, dict) or value.get("protocol") != PROTO or value.get("type") != "player":
        return None
    if str(value.get("repository", "")).lower() != full.lower() or not isinstance(value.get("games"), dict):
        return None
    games = {}
    for id_, g in value["games"].items():
        if not isinstance(id_, str) or not SLUG.fullmatch(id_) or not isinstance(g, dict):
            continue
        rp, wins, losses = g.get("rp"), g.get("wins"), g.get("losses")
        if not all(type(v) is int and v >= 0 for v in (rp, wins, losses)) or rp > 100_000:
            continue
        genre, name = g.get("genre"), g.get("name")
        if not isinstance(genre, str) or not SLUG.fullmatch(genre):
            continue
        if not isinstance(name, str) or not 0 < len(name) <= 100:
            continue
        games[id_] = {"id": id_, "name": name, "genre": genre, "rp": rp,
                      "wins": wins, "losses": losses,
                      "win_rate": round(wins/(wins+losses)*100, 2) if (wins+losses) else 0}
    return {"repository": full, "display_name": str(value.get("display_name") or full.split("/")[0])[:80],
            "page_url": page_url(full), "games": games}


def valid_portal(value, full):
    if not isinstance(value, dict) or value.get("protocol") != PROTO or value.get("mode") != "game":
        return None
    game_id = value.get("game_id")
    if not isinstance(game_id, str) or not SLUG.fullmatch(game_id):
        return None
    if not isinstance(value.get("title"), str) or not 0 < len(value["title"]) <= 100:
        return None
    genre = value.get("genre", "other")
    if not isinstance(genre, str) or not SLUG.fullmatch(genre):
        return None
    return {"repository": full, "game_id": game_id, "title": value["title"],
            "genre": genre, "page_url": page_url(full)}


def build_catalog(config, token="", discover_fn=discover, repo_fn=repo_json):
    if config.get("protocol") != PROTO or config.get("mode") not in ("game", "directory"):
        raise ValueError("portal.json protocol/mode invalid")
    mode = config["mode"]
    game_id = config.get("game_id", "")
    if mode == "game" and (not isinstance(game_id, str) or not SLUG.fullmatch(game_id)):
        raise ValueError("invalid game_id")
    result = {"protocol": PROTO, "mode": mode, "title": config.get("title", "OpenRank"),
              "game_id": game_id if mode == "game" else None,
              "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    if mode == "game":
        players=[]
        for full, branch in discover_fn("openrank-player", token):
            info = valid_player(repo_fn(full, branch, "manifest.json"), full)
            if not info or game_id not in info["games"]:
                continue
            game = info["games"][game_id]
            players.append({"repository": full, "name": info["display_name"], "page_url": info["page_url"], **game})
        players.sort(key=lambda p: (-p["rp"], -p["wins"], p["repository"].lower()))
        result["players"] = players
    else:
        portals=[]
        for full, branch in discover_fn("openrank-portal", token):
            info = valid_portal(repo_fn(full, branch, "portal.json"), full)
            if info:
                portals.append(info)
        result["portals"] = sorted(portals, key=lambda p: (p["genre"], p["title"].lower(), p["repository"].lower()))
    return result


def main():
    config = json.loads(Path("portal.json").read_text(encoding="utf-8"))
    result = build_catalog(config, os.environ.get("GITHUB_TOKEN", ""))
    out = Path("data/catalog.json");out.parent.mkdir(exist_ok=True)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    old = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    # Avoid daily empty commits if the source content is identical.
    old_cmp, new_cmp = dict(old), dict(result)
    old_cmp.pop("generated_at", None);new_cmp.pop("generated_at", None)
    if old_cmp == new_cmp:
        print("Catalog unchanged")
    else:
        out.write_text(text, encoding="utf-8")
        print("Catalog updated:", len(result.get("players", result.get("portals", []))))


if __name__ == "__main__":
    main()
