import requests
import json
import time
import re

S = requests.Session()
S.headers.update({"User-Agent": "DepersBot/1.0 (research)", "Accept": "application/json"})


def sparql(query):
    for attempt in range(5):
        try:
            r = S.post("https://query.wikidata.org/sparql", data={"query": query}, timeout=300)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                print(f" rate-limited, waiting 60s")
                time.sleep(60)
            elif r.status_code == 504:
                print(f" timeout, retrying")
                time.sleep(30)
            else:
                print(f" HTTP {r.status_code}: {r.text[:200]}")
                return None
        except Exception as e:
            print(f" retry {attempt + 1}: {e}")
            time.sleep(10)
    return None


def get_labels(query):
    data = sparql(query)
    if not data:
        return set()
    return {
        item["label"]["value"]
        for item in data.get("results", {}).get("bindings", [])
        if 2 <= len(item.get("label", {}).get("value", "")) <= 40
    }


def main():
    surnames_m = set()
    surnames_f = set()
    first_m = set()
    first_f = set()

    # --- SURNAMES via P734 (family name) used by Russians ---
    print("=== Surnames ===")
    # Batch by letter to avoid timeouts
    alphabet = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ"
    for letter in alphabet:
        print(f"  Surname {letter}...", end="", flush=True)
        q = f'''SELECT DISTINCT ?label WHERE {{
            ?item wdt:P734 ?sn . ?sn rdfs:label ?label .
            ?item wdt:P27 wd:Q159 .
            FILTER(lang(?label) = "ru")
            FILTER(STRSTARTS(?label, "{letter}"))
            FILTER(STRLEN(?label) > 2 && STRLEN(?label) < 35)
        }} LIMIT 50000'''
        labels = get_labels(q)
        m_endings = (
            "ов",
            "ев",
            "ин",
            "ын",
            "ский",
            "цкий",
            "ый",
            "ий",
            "ко",
            "енко",
            "ук",
            "юк",
            "ун",
            "ёв",
            "ич",
            "ок",
            "ек",
            "ик",
            "н",
            "к",
            "в",
        )
        f_endings = (
            "ова",
            "ева",
            "ина",
            "ына",
            "ская",
            "цкая",
            "ая",
            "яя",
            "ко",
            "енко",
            "ук",
            "юк",
            "на",
            "ва",
        )
        m_new = sum(
            1 for l in labels if any(l.endswith(e) for e in m_endings) and l not in surnames_m
        )
        f_new = sum(
            1 for l in labels if any(l.endswith(e) for e in f_endings) and l not in surnames_f
        )
        for l in labels:
            if any(l.endswith(e) for e in m_endings):
                surnames_m.add(l)
            if any(l.endswith(e) for e in f_endings):
                surnames_f.add(l)
        print(
            f" {len(labels)} found (+{m_new}m, +{f_new}f) total: {len(surnames_m)}m/{len(surnames_f)}f"
        )
        time.sleep(10)

    # --- FIRST NAMES ---
    print("\n=== Male first names ===")
    for letter in alphabet:
        print(f"  Name M {letter}...", end="", flush=True)
        q = f'''SELECT DISTINCT ?label WHERE {{
            ?item wdt:P31/wdt:P279* wd:Q12308941 .
            ?item wdt:P21 wd:Q6581097 .
            ?item rdfs:label ?label .
            FILTER(lang(?label) = "ru")
            FILTER(STRSTARTS(?label, "{letter}"))
            FILTER(STRLEN(?label) > 1 && STRLEN(?label) < 25)
        }} LIMIT 10000'''
        labels = get_labels(q)
        before = len(first_m)
        first_m.update(labels)
        print(f" {len(labels)} (+{len(first_m) - before} new) total: {len(first_m)}")
        time.sleep(10)

    print("\n=== Female first names ===")
    for letter in alphabet:
        print(f"  Name F {letter}...", end="", flush=True)
        q = f'''SELECT DISTINCT ?label WHERE {{
            ?item wdt:P31/wdt:P279* wd:Q12308941 .
            ?item wdt:P21 wd:Q6581072 .
            ?item rdfs:label ?label .
            FILTER(lang(?label) = "ru")
            FILTER(STRSTARTS(?label, "{letter}"))
            FILTER(STRLEN(?label) > 1 && STRLEN(?label) < 25)
        }} LIMIT 10000'''
        labels = get_labels(q)
        before = len(first_f)
        first_f.update(labels)
        print(f" {len(labels)} (+{len(first_f) - before} new) total: {len(first_f)}")
        time.sleep(10)

    # --- Cross-generate male/female surnames ---
    FEM = {
        "ов": "ова",
        "ев": "ева",
        "ин": "ина",
        "ын": "ына",
        "ский": "ская",
        "цкий": "цкая",
        "ый": "ая",
        "ий": "яя",
    }
    MASC = {v: k for k, v in FEM.items()}
    gen_f = set()
    for s in surnames_m:
        for e, fe in sorted(FEM.items(), key=lambda x: -len(x[0])):
            if s.endswith(e) and len(s) > len(e) + 1 and s[: -len(e)] + fe not in surnames_f:
                gen_f.add(s[: -len(e)] + fe)
    surnames_f.update(gen_f)
    gen_m = set()
    for s in surnames_f:
        for e, me in sorted(MASC.items(), key=lambda x: -len(x[0])):
            if s.endswith(e) and len(s) > len(e) + 1 and s[: -len(e)] + me not in surnames_m:
                gen_m.add(s[: -len(e)] + me)
    surnames_m.update(gen_m)
    print(f"\nAfter cross-generate: {len(surnames_m)}m/{len(surnames_f)}f surnames")

    result = {
        "surnames_m": sorted(surnames_m),
        "surnames_f": sorted(surnames_f),
        "first_names_m": sorted(first_m),
        "first_names_f": sorted(first_f),
    }
    with open("scripts/wikidata_names.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to scripts/wikidata_names.json")
    print(f"Surnames M: {len(surnames_m)}")
    print(f"Surnames F: {len(surnames_f)}")
    print(f"First names M: {len(first_m)}")
    print(f"First names F: {len(first_f)}")


if __name__ == "__main__":
    main()
