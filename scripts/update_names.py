import json
import re


def main():
    with open("scripts/russian_names.json", encoding="utf-8") as f:
        names = json.load(f)

    surnames_m = names["surnames_m"]
    surnames_f = names["surnames_f"]
    first_m = names["first_names_m"]
    first_f = names["first_names_f"]

    print(f"Surnames M: {len(surnames_m)}")
    print(f"Surnames F: {len(surnames_f)}")
    print(f"First M: {len(first_m)}")
    print(f"First F: {len(first_f)}")

    with open("app/data/names_gazetteer.py", "r", encoding="utf-8") as f:
        gaz = f.read()

    def replace_list(var_name, new_data):
        pattern = rf"^{var_name} = \[.*?\n\]"
        m = re.search(pattern, gaz, re.MULTILINE | re.DOTALL)
        if not m:
            raise ValueError(f"Cannot find {var_name}")
        lines = [
            f'    "{s.replace(chr(92), chr(92) * 2).replace(chr(34), chr(92) + chr(34))}",'
            for s in new_data
        ]
        block = f"{var_name} = [\n" + "\n".join(lines) + "\n]"
        return gaz[: m.start()] + block + gaz[m.end() :]

    gaz = replace_list("SURNAMES_M", surnames_m)
    gaz = replace_list("SURNAMES_F", surnames_f)
    gaz = replace_list("FIRST_NAMES_M", first_m)
    gaz = replace_list("FIRST_NAMES_F", first_f)

    with open("app/data/names_gazetteer.py", "w", encoding="utf-8") as f:
        f.write(gaz)

    # Also update fake_generator.py
    with open("app/services/fake_generator.py", "r", encoding="utf-8") as f:
        fg = f.read()

    def replace_fg_list(var_name, new_data):
        pattern = rf"^{var_name} = \[.*?\n\]"
        m = re.search(pattern, fg, re.MULTILINE | re.DOTALL)
        if not m:
            raise ValueError(f"Cannot find {var_name}")
        lines = [f'    "{s}",' for s in new_data]
        block = f"{var_name} = [\n" + "\n".join(lines) + "\n]"
        return fg[: m.start()] + block + fg[m.end() :]

    fg = replace_fg_list("SURNAMES_M", surnames_m)
    fg = replace_fg_list("SURNAMES_F", surnames_f)
    fg = replace_fg_list("FIRST_NAMES_M", first_m)
    fg = replace_fg_list("FIRST_NAMES_F", first_f)

    with open("app/services/fake_generator.py", "w", encoding="utf-8") as f:
        f.write(fg)

    print("Done!")


if __name__ == "__main__":
    main()
