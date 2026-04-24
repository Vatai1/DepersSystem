import json
import re


def main():
    with open("scripts/final_all_settlements.json", encoding="utf-8") as f:
        all_s = json.load(f)
    with open("scripts/final_single.json", encoding="utf-8") as f:
        single = json.load(f)
    with open("scripts/final_multi.json", encoding="utf-8") as f:
        multi = json.load(f)

    print(f"All: {len(all_s)}, Single: {len(single)}, Multi: {len(multi)}")

    def esc(s):
        return s.replace("\\", "\\\\").replace('"', '\\"')

    # 1. Update app/data/names_gazetteer.py
    with open("app/data/names_gazetteer.py", "r", encoding="utf-8") as f:
        gaz = f.read()

    m = re.search(r"^GEO_STOPWORDS = \{.*?\n\}", gaz, re.MULTILINE | re.DOTALL)
    if not m:
        raise ValueError("Cannot find GEO_STOPWORDS")

    geo_lines = [f'    "{esc(s)}",' for s in all_s]
    new_geo = "GEO_STOPWORDS = {\n" + "\n".join(geo_lines) + "\n}"
    gaz = gaz[: m.start()] + new_geo + gaz[m.end() :]

    gaz = re.sub(r"\n*GEO_REGEX_WORDS = \[.*?\n\]", "", gaz, flags=re.DOTALL)

    regex_lines = [f'    "{esc(s)}",' for s in single]
    new_regex = "\n\nGEO_REGEX_WORDS = [\n" + "\n".join(regex_lines) + "\n]"
    gaz = gaz.rstrip() + new_regex + "\n"

    with open("app/data/names_gazetteer.py", "w", encoding="utf-8") as f:
        f.write(gaz)
    print(f"GEO_STOPWORDS: {len(all_s)}, GEO_REGEX_WORDS: {len(single)}")

    # 2. Update CITIES in fake_generator.py
    with open("app/services/fake_generator.py", "r", encoding="utf-8") as f:
        fg = f.read()

    m = re.search(r"^CITIES = \[.*?\n\]", fg, re.MULTILINE | re.DOTALL)
    if not m:
        raise ValueError("Cannot find CITIES")

    city_lines = [f'    "{esc(s)}",' for s in all_s]
    new_cities = "CITIES = [\n" + "\n".join(city_lines) + "\n]"
    fg = fg[: m.start()] + new_cities + fg[m.end() :]

    with open("app/services/fake_generator.py", "w", encoding="utf-8") as f:
        f.write(fg)
    print(f"CITIES: {len(all_s)}")

    # 3. Update MULTI_WORD_CITIES in patterns.py
    with open("app/core/patterns.py", "r", encoding="utf-8") as f:
        pat = f.read()

    m = re.search(r"^MULTI_WORD_CITIES = \[.*?\n\]", pat, re.MULTILINE | re.DOTALL)
    if not m:
        raise ValueError("Cannot find MULTI_WORD_CITIES")

    multi_lines = [f'    "{esc(s)}",' for s in multi]
    new_multi = "MULTI_WORD_CITIES = [\n" + "\n".join(multi_lines) + "\n]"
    pat = pat[: m.start()] + new_multi + pat[m.end() :]

    with open("app/core/patterns.py", "w", encoding="utf-8") as f:
        f.write(pat)
    print(f"MULTI_WORD_CITIES: {len(multi)}")

    print("Done!")


if __name__ == "__main__":
    main()
