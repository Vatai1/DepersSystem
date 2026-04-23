import re
import json
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse

HEADERS = {"User-Agent": "DepersBot/1.0 (research; educational project)"}


def fetch_page(title):
    url = f"https://ru.wikipedia.org/wiki/{urllib.parse.quote(title)}"
    print(f"  Fetching: {title}")
    resp = requests.get(url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def fetch_api_category(category, cmcontinue=None, limit=500):
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category,
        "cmlimit": limit,
        "format": "json",
    }
    if cmcontinue:
        params["cmcontinue"] = cmcontinue
    resp = requests.get(
        "https://ru.wikipedia.org/w/api.php",
        params=params,
        headers=HEADERS,
        timeout=60,
    )
    return resp.json()


def extract_table_cities(soup):
    cities = []
    for table in soup.find_all("table", {"class": ["wikitable", "standard", "sortable"]}):
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            if not cells:
                continue
            for cell in cells:
                link = cell.find("a")
                if link and link.text.strip():
                    text = link.text.strip()
                    if 2 < len(text) < 60 and not any(c in text for c in "0123456789"):
                        cities.append(text)
    return cities


def extract_list_items(soup):
    items = []
    for li in soup.find_all("li"):
        link = li.find("a")
        if link:
            text = link.get("title") or link.text.strip()
            if text:
                text = text.strip()
                if 2 < len(text) < 60:
                    items.append(text)
    return items


def clean_name(name):
    name = name.strip()
    name = re.sub(r"\s*\(.*?\)\s*$", "", name)
    name = re.sub(r"\s*\[.*?\]\s*$", "", name)
    name = name.strip(" *")
    return name


def is_valid(name):
    if len(name) < 2 or re.match(r"^\d", name):
        return False
    skip = {
        "Россия",
        "Список",
        "Население",
        "Город",
        "Область",
        "Край",
        "Республика",
        "Район",
        "Федеральный",
        "Округ",
        "Населённые",
        "Содержание",
        "Навигация",
        "Поиск",
        "Википедия",
        "Обсуждение",
        "Категория",
        "Шаблон",
        "Участник",
        "Файл",
        "Портал",
        "поселение",
        "посёлок",
        "село",
        "деревня",
        "хутор",
        "станица",
        "сельсовет",
        "муниципальный",
        "Столица",
        "Страна",
    }
    words = name.split()
    if any(w in skip for w in words):
        return False
    if re.match(r"^[a-zA-Z]", name):
        return False
    return True


def main():
    all_settlements = []
    seen = set()

    def add(name):
        name = clean_name(name)
        key = name.lower()
        if is_valid(name) and key not in seen:
            seen.add(key)
            all_settlements.append(name)

    print("=== 1. Cities from table ===")
    soup = fetch_page("Список_городов_России")
    for c in extract_table_cities(soup):
        add(c)
    print(f"  Total so far: {len(all_settlements)}")

    print("\n=== 2. PGTs from category ===")
    cmcontinue = None
    pgt_count = 0
    while True:
        data = fetch_api_category("Категория:Посёлки городского типа России", cmcontinue)
        members = data.get("query", {}).get("categorymembers", [])
        for m in members:
            title = m.get("title", "")
            if not title.startswith("Категория:"):
                add(title)
                pgt_count += 1
        cmcontinue = data.get("continue", {}).get("cmcontinue")
        if not cmcontinue:
            break
        time.sleep(0.5)
    print(f"  PGTs via API: {pgt_count}, Total: {len(all_settlements)}")

    print("\n=== 3. Large villages (>3000 pop) from category ===")
    for cat in [
        "Категория:Населённые пункты России с населением более 5000 человек",
        "Категория:Населённые пункты по алфавиту",
    ]:
        try:
            cmcontinue = None
            count = 0
            while count < 10000:
                data = fetch_api_category(cat, cmcontinue, limit=500)
                members = data.get("query", {}).get("categorymembers", [])
                if not members:
                    break
                for m in members:
                    title = m.get("title", "")
                    if title.startswith("Категория:"):
                        continue
                    add(title)
                    count += 1
                cmcontinue = data.get("continue", {}).get("cmcontinue")
                if not cmcontinue:
                    break
                time.sleep(0.3)
            print(f"  From {cat}: {count}, Total: {len(all_settlements)}")
        except Exception as e:
            print(f"  Error: {e}")

    print("\n=== 4. Regional settlement lists ===")
    region_pages = {
        "Населённые_пункты_Московской_области": "Московская область",
        "Населённые_пункты_Ленинградской_области": "Ленинградская область",
        "Населённые_пункты_Краснодарского_края": "Краснодарский край",
        "Населённые_пункты_Свердловской_области": "Свердловская область",
        "Населённые_пункты_Республики_Татарстан": "Татарстан",
        "Населённые_пункты_Нижегородской_области": "Нижегородская область",
        "Населённые_пункты_Самарской_области": "Самарская область",
        "Населённые_пункты_Челябинской_области": "Челябинская область",
        "Населённые_пункты_Ростовской_области": "Ростовская область",
        "Населённые_пункты_Республики_Башкортостан": "Башкортостан",
        "Населённые_пункты_Красноярского_края": "Красноярский край",
        "Населённые_пункты_Пермского_края": "Пермский край",
        "Населённые_пункты_Ставропольского_края": "Ставропольский край",
        "Населённые_пункты_Волгоградской_области": "Волгоградская область",
        "Населённые_пункты_Воронежской_области": "Воронежская область",
        "Населённые_пункты_Кемеровской_области": "Кемеровская область",
        "Населённые_пункты_Новосибирской_области": "Новосибирская область",
        "Населённые_пункты_Омской_области": "Омская область",
        "Населённые_пункты_Тюменской_области": "Тюменская область",
        "Населённые_пункты_Хабаровского_края": "Хабаровский край",
        "Населённые_пункты_Иркутской_области": "Иркутская область",
        "Населённые_пункты_Приморского_края": "Приморский край",
        "Населённые_пункты_Забайкальского_края": "Забайкальский край",
        "Населённые_пункты_Алтайского_края": "Алтайский край",
        "Населённые_пункты_Тульской_области": "Тульская область",
        "Населённые_пункты_Ярославской_области": "Ярославская область",
        "Населённые_пункты_Владимирской_области": "Владимирская область",
        "Населённые_пункты_Рязанской_области": "Рязанская область",
        "Населённые_пункты_Тверской_области": "Тверская область",
        "Населённые_пункты_Калужской_области": "Калужская область",
        "Населённые_пункты_Смоленской_области": "Смоленская область",
        "Населённые_пункты_Костромской_области": "Костромская область",
        "Населённые_пункты_Ивановской_области": "Ивановская область",
        "Населённые_пункты_Брянской_области": "Брянская область",
        "Населённые_пункты_Курской_области": "Курская область",
        "Населённые_пункты_Орловской_области": "Орловская область",
        "Населённые_пункты_Липецкой_области": "Липецкая область",
        "Населённые_пункты_Пензенской_области": "Пензенская область",
        "Населённые_пункты_Тамбовской_области": "Тамбовская область",
        "Населённые_пункты_Ульяновской_области": "Ульяновская область",
        "Населённые_пункты_Кировской_области": "Кировская область",
        "Населённые_пункты_Астраханской_области": "Астраханская область",
        "Населённые_пункты_Оренбургской_области": "Оренбургская область",
        "Населённые_пункты_Саратовской_области": "Саратовская область",
        "Населённые_пункты_Удмуртской_Республики": "Удмуртия",
        "Населённые_пункты_Республики_Дагестан": "Дагестан",
        "Населённые_пункты_Чеченской_Республики": "Чечня",
        "Населённые_пункты_Республики_Северная_Осетия — Алания": "Северная Осетия",
        "Населённые_пункты_Кабардино-Балкарской_Республики": "Кабардино-Балкария",
        "Населённые_пункты_Карачаево-Черкесской_Республики": "Карачаево-Черкесия",
        "Населённые_пункты_Республики_Ингушетия": "Ингушетия",
        "Населённые_пункты_Республики_Калмыкия": "Калмыкия",
        "Населённые_пункты_Адыгеи": "Адыгея",
        "Населённые_пункты_Мурманской_области": "Мурманская область",
        "Населённые_пункты_Архангельской_области": "Архангельская область",
        "Населённые_пункты_Вологодской_области": "Вологодская область",
        "Населённые_пункты_Республики_Карелия": "Карелия",
        "Населённые_пункты_Республики_Коми": "Коми",
        "Населённые_пункты_Новгородской_области": "Новгородская область",
        "Населённые_пункты_Псковской_области": "Псковская область",
        "Населённые_пункты_Калининградской_области": "Калининградская область",
        "Населённые_пункты_Мариий_Эл": "Марий Эл",
        "Населённые_пункты_Республики_Мордовия": "Мордовия",
        "Населённые_пункты_Чувашской_Республики": "Чувашия",
        "Населённые_пункты_Республики_Хакасия": "Хакасия",
        "Населённые_пункты_Республики_Алтай": "Республика Алтай",
        "Населённые_пункты_Республики_Тыва": "Тыва",
        "Населённые_пункты_Республики_Бурятия": "Бурятия",
        "Населённые_пункты_Амурской_области": "Амурская область",
        "Населённые_пункты_Сахалинской_области": "Сахалинская область",
        "Населённые_пункты_Магаданской_области": "Магаданская область",
        "Населённые_пункты_Камчатского_края": "Камчатский край",
        "Населённые_пункты_Чукотского_автономного_округа": "Чукотка",
        "Населённые_пункты_Ненецкого_автономного_округа": "НАО",
        "Населённые_пункты_Ханты-Мансийского_автономного_округа — Югры": "ХМАО",
        "Населённые_пункты_Ямало-Ненецкого_автономного_округа": "ЯНАО",
        "Населённые_пункты_Еврейской_автономной_области": "ЕАО",
    }

    for page, region_name in region_pages.items():
        try:
            s = fetch_page(page)
            before = len(all_settlements)
            for c in extract_table_cities(s):
                add(c)
            for c in extract_list_items(s):
                add(c)
            print(f"  +{len(all_settlements) - before} from {region_name}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  Error ({region_name}): {e}")

    all_settlements.sort(key=lambda x: (len(x.split()), x.lower()))
    print(f"\n=== Total: {len(all_settlements)} ===")

    single_word = [s for s in all_settlements if " " not in s and "-" not in s]
    multi_word = [s for s in all_settlements if " " in s or "-" in s]
    print(f"Single-word: {len(single_word)}")
    print(f"Multi-word: {len(multi_word)}")

    with open("scripts/russian_settlements.json", "w", encoding="utf-8") as f:
        json.dump(all_settlements, f, ensure_ascii=False, indent=2)
    with open("scripts/single_word_settlements.json", "w", encoding="utf-8") as f:
        json.dump(single_word, f, ensure_ascii=False, indent=2)
    with open("scripts/multi_word_settlements.json", "w", encoding="utf-8") as f:
        json.dump(multi_word, f, ensure_ascii=False, indent=2)

    print("Done!")


if __name__ == "__main__":
    main()
