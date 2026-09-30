#!/usr/bin/env python3
"""Baut Kartenkatalog + Cardmarket-Preise für den Pokémon Karten-Tracker.

Quellen: TCGdex-Kartendatenbank (GitHub, geklont) für Karten, Sets und
Cardmarket-Produkt-IDs, dazu der öffentliche Cardmarket-Preisguide.

Aufruf: python3 build.py <tcgdex-repo> <ausgabe-ordner> [<ordner-mit-karten-json>]
Erzeugt catalog-intl.json und catalog-asia.json. Wird ein Karten-Ordner
(ArtifactData list mit out_dir) angegeben, entsteht zusätzlich snapshot.json
mit den Preisen der Karten aus der Sammlung.
"""
import datetime
import glob
import json
import os
import re
import sys
import urllib.request

SERIES = {"Pedang & Perisai": "Sword & Shield", "その他": "Sonstige", "サン＆ムーン": "Sun & Moon", "ポケットモンスターカードゲーム": "Classic",
          "ポケモンカードe": "e-Card", "ポケモンカード★neo": "Neo", "ポケモンカードゲーム MEGA": "Mega", "Grund": "Grundset", "Miscellaneous": "Sonstige", "Trainer kits": "Trainer-Kits"}
PRICE_URL = "https://downloads.s3.cardmarket.com/productCatalog/priceGuide/price_guide_6.json"
STR = r'"((?:[^"\\]|\\.)*)"|\'((?:[^\'\\]|\\.)*)\''


def block(text, key, start=0):
    m = re.compile(r'(?m)^(?:\t| {1,4})["\']?' + re.escape(key) + r'["\']?\s*:\s*\{').search(text, start)
    if not m:
        return None
    i, depth = m.end(), 1
    while i < len(text) and depth:
        ch = text[i]
        if ch in "\"'":
            q = ch
            i += 1
            while i < len(text) and text[i] != q:
                i += 2 if text[i] == "\\" else 1
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        i += 1
    return text[m.end():i - 1]


def strings(body):
    out = {}
    if not body:
        return out
    for m in re.finditer(r'["\']?([\w-]+)["\']?\s*:\s*(?:' + STR + ')', body):
        v = m.group(2) if m.group(2) is not None else m.group(3)
        out.setdefault(m.group(1), v.replace('\\"', '"').replace("\\'", "'"))
    return out


def scalar(text, key):
    m = re.search(r'(?m)^\s*' + re.escape(key) + r'\s*:\s*(?:' + STR + ')', text)
    return (m.group(1) if m.group(1) is not None else m.group(2)) if m else None


def pick(d, order):
    for k in order:
        if d.get(k):
            return d[k]
    return next(iter(d.values()), "")


def load_prices():
    with urllib.request.urlopen(PRICE_URL, timeout=120) as r:
        data = json.load(r)
    out = {}
    for p in data.get("priceGuides", []):
        def g(k):
            v = p.get(k)
            return round(float(v), 2) if isinstance(v, (int, float)) and v > 0 else None
        v = g("avg7") if g("avg7") is not None else g("trend")
        vr = g("avg7-holo") if g("avg7-holo") is not None else g("trend-holo")
        out[p["idProduct"]] = (v, vr)
    return out, (data.get("createdAt") or "")[:10]


def build(root, cat, name_order, set_name_order, prices):
    sets = []
    for serie_file in sorted(glob.glob(os.path.join(root, "*.ts"))):
        serie_dir = serie_file[:-3]
        stxt = open(serie_file, encoding="utf-8").read()
        serie_name = pick(strings(block(stxt, "name")), set_name_order)
        serie_name = SERIES.get(serie_name, serie_name)
        serie_id = scalar(stxt, "id") or ""
        if "pocket" in serie_name.lower() or "pocket" in os.path.basename(serie_dir).lower():
            continue
        for set_file in sorted(glob.glob(os.path.join(serie_dir, "*.ts"))):
            t = open(set_file, encoding="utf-8").read()
            sid = scalar(t, "id")
            card_dir = set_file[:-3]
            if not sid or not os.path.isdir(card_dir):
                continue
            rd = scalar(t, "releaseDate") or pick(strings(block(t, "releaseDate")), ["ja", "zh-tw", "ko", "en"])
            cc = block(t, "cardCount") or ""
            mo = re.search(r"official\s*:\s*(\d+)", cc)
            ab = strings(block(t, "abbreviations"))
            cards = []
            for cf in glob.glob(os.path.join(card_dir, "*.ts")):
                ct = open(cf, encoding="utf-8").read()
                lid = os.path.basename(cf)[:-3]
                nm = pick(strings(block(ct, "name")), name_order)
                m = re.search(r"cardmarket\s*:\s*(\d+)", ct[ct.find("variants"):] if "variants" in ct else "")
                v = vr = None
                if m and int(m.group(1)) in prices:
                    v, vr = prices[int(m.group(1))]
                row = [lid, nm]
                if v is not None or vr is not None:
                    row += [v, vr] if vr is not None else [v]
                cards.append(row)
            if not cards:
                continue
            cards.sort(key=lambda r: (int(re.sub(r"\D", "", r[0]) or 0), r[0]))
            sets.append({"id": sid, "n": pick(strings(block(t, "name")), set_name_order), "s": serie_name, "sr": serie_id,
                         "d": rd or "", "o": int(mo.group(1)) if mo else 0, "a": ab.get("official", ""), "c": cards})
    sets.sort(key=lambda s: s["d"] or "0000", reverse=True)
    return sets


def main():
    repo, out = sys.argv[1], sys.argv[2]
    cards_dir = sys.argv[3] if len(sys.argv) > 3 else None
    os.makedirs(out, exist_ok=True)
    prices, pdate = load_prices()
    cats = {
        "intl": build(os.path.join(repo, "data"), "intl", ["de", "en", "fr", "es", "it"], ["de", "en", "fr"], prices),
        "asia": build(os.path.join(repo, "data-asia"), "asia", ["en", "id", "ja", "zh-tw", "ko", "zh-cn"], ["en", "id", "ja", "zh-tw", "ko"], prices),
    }
    for k, sets in cats.items():
        with open(os.path.join(out, f"catalog-{k}.json"), "w", encoding="utf-8") as fh:
            json.dump({"u": pdate, "sets": sets}, fh, ensure_ascii=False, separators=(",", ":"))
        n = sum(len(s["c"]) for s in sets)
        np = sum(1 for s in sets for c in s["c"] if len(c) > 2)
        print(f"{k}: {len(sets)} Sets, {n} Karten, {np} mit Preis")
    if cards_dir:
        idx = {f"{k}:{s['id']}/{c[0]}": c for k, sets in cats.items() for s in sets for c in s["c"]}
        snap = {}
        for f in glob.glob(os.path.join(cards_dir, "**", "*.json"), recursive=True):
            try:
                c = json.load(open(f, encoding="utf-8"))
            except Exception:  # noqa: BLE001
                continue
            key = c.get("key") if isinstance(c, dict) else None
            row = idx.get(key)
            if row and len(row) > 2:
                snap[key] = row[2:]
        try:
            from zoneinfo import ZoneInfo
            now = datetime.datetime.now(ZoneInfo("Europe/Berlin"))
        except Exception:  # noqa: BLE001
            now = datetime.datetime.now()
        doc = {"d": now.strftime("%Y-%m-%d"), "n": len(snap), "p": snap}
        with open(os.path.join(out, "snapshot.json"), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
        print(f"Snapshot: {len(snap)} Karten mit Preis, Dokument-ID s-{doc['d']}")


if __name__ == "__main__":
    main()
