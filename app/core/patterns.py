import re

from app.data.names_gazetteer import GEO_STOPWORDS

PHONE = re.compile(r"(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}")
EMAIL = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
INN = re.compile(r"\b(\d{10}|\d{12})\b")
SNILS = re.compile(r"\b\d{3}[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{2}\b")
PASSPORT = re.compile(r"\b\d{4}\s\d{6}\b")
CARD = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")
DATE_RU = re.compile(r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b")
IP_ADDRESS = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")

_GEO_PATTERN = re.compile(
    r"(?:г\.?\s*|город\s*)("
    + "|".join(re.escape(c) for c in sorted(GEO_STOPWORDS, key=len, reverse=True))
    + r")\b",
    re.IGNORECASE,
)

MULTI_WORD_CITIES = [
    "Нижний Новгород",
    "Набережные Челны",
    "Старый Оскол",
    "Великий Устюг",
    "Нижний Тагил",
    "Новый Уренгой",
    "Комсомольск-на-Амуре",
    "Ростов-на-Дону",
    "Каменск-Уральский",
    "Каменск-Шахтинский",
    "Усть-Илимск",
    "Усть-Кут",
    "Йошкар-Ола",
    "Южно-Сахалинск",
    "Рио-де-Жанейро",
    "Сан-Франциско",
    "Сан-Диего",
    "Сан-Хосе",
    "Сан-Паулу",
    "Сантьяго",
    "Лос-Анджелес",
    "Нью-Йорк",
    "Нью-Орлеан",
    "Буэнос-Айрес",
    "Франкфурт-на-Майне",
    "Форт-Уэрт",
    "Сан-Антонио",
    "Колорадо-Спрингс",
    "Вирджиния-Бич",
    "Оклахома-Сити",
    "Канзас-Сити",
    "Нави-Мумбаи",
    "Пимпри-Чинчвад",
    "Сан-Паулу",
    "Сан-Себастьян",
    "Крайстчёрч",
    "Куала-Лумпур",
    "Бандар-Сери-Бегаван",
    "Куала-Лумпур",
    "Куала-Белайт",
    "Кота-Кинабалу",
    "Куала-Тренггалану",
    "Алор-Сетар",
    "Порт-Диксон",
    "Пуэрто-Принсеса",
    "Кесон-Сити",
    "Кагаян-де-Оро",
    "Лапу-Лапу",
    "Генерал-Сантос",
    "Санта-Ана",
    "Сан-Франциско",
    "Клуж-Напока",
    "Аддис-Абеба",
    "Дар-эс-Салам",
    "Эль-Пасо",
    "Корпус-Кристи",
    "Пемброк-Пайнс",
    "Форт-Лодердейл",
    "Сент-Питерсберг",
    "Западный Палм-Бич",
    "Палм-Бей",
    "Саут-Бенд",
    "Форт-Уэйн",
    "Де-Мойн",
    "Батон-Руж",
    "Уэст-Палм-Бич",
    "Кейп-Корал",
    "Клируотер",
    "Джорджтаун",
    "Петалинг-Джая",
    "Субанг-Джая",
    "Нью-Бедфорд",
    "Фейетвилл",
    "Уинстон-Сейлем",
    "Хафр-эль-Батин",
    "Эль-Вакра",
    "Эль-Хор",
    "Эль-Райян",
    "Эль-Джахра",
    "Эль-Ахмади",
    "Мубарак-эль-Кебир",
    "Ришон-ле-Цион",
    "Петах-Тиква",
    "Бней-Брак",
    "Рамат-Ган",
    "Бат-Ям",
    "Кфар-Сава",
    "Нацрат-Иллит",
    "Бейт-Шеан",
    "Кирьят-Гат",
    "Кирьят-Малахи",
    "Мицпе-Рамон",
    "Камышлы",
    "Баальбек",
    "Дейр-эз-Зор",
    "Эс-Сувейда",
    "Эль-Кут",
    "Эль-Камышлы",
    "Бендер-Аббас",
    "Элязыг",
    "Афьонкарахисар",
    "Невшаер",
    "Балыкесир",
    "Чанаккале",
    "Зонгулдак",
    "Карабюк",
    "Кыркларели",
    "Текирдаг",
    "Кыршехир",
    "Хафр-эль-Батин",
    "Джафельна",
    "Эль-Хубар",
    "Эль-Катиф",
    "Эль-Айн",
    "Рас-эль-Хайма",
    "Умм-эль-Кайвайн",
    "Шрнак",
    "Тунджели",
    "Гюмюшхане",
    "Кастамону",
    "Бандар-Аббас",
    "Порт-Харкорт",
    "Абумаджан",
    "Кривой Рог",
    "Белая Церковь",
    "Каменец-Подольский",
    "Могилёв-Подольский",
    "Переяслав-Хмельницкий",
    "Рава-Русская",
    "Владимир-Волынский",
    "Каменка-Бугская",
    "Каменка-Днепровская",
    "Новая Каховка",
    "Великие Мосты",
    "Жёлтые Воды",
    "Боково-Платово",
    "Брошнев-Осада",
    "Пуща-Водица",
    "Вита-Почтовая",
    "Ивано-Франковск",
]

_MULTI_WORD_CITY_PATTERN = re.compile(
    r"(?:г\.?\s*|город\s*)("
    + "|".join(re.escape(c) for c in sorted(MULTI_WORD_CITIES, key=len, reverse=True))
    + r")",
    re.IGNORECASE,
)

ALL_PATTERNS = {
    "PHONE": PHONE,
    "EMAIL": EMAIL,
    "INN": INN,
    "SNILS": SNILS,
    "PASSPORT": PASSPORT,
    "CARD": CARD,
    "DATE": DATE_RU,
    "IP": IP_ADDRESS,
}


def scan_geo(text: str) -> list[dict]:
    entities = []
    seen = set()
    for m in _MULTI_WORD_CITY_PATTERN.finditer(text):
        span = (m.start(1), m.end(1))
        if span not in seen:
            seen.add(span)
            entities.append(
                {
                    "text": m.group(1),
                    "label": "LOC",
                    "start": m.start(1),
                    "end": m.end(1),
                    "score": 1.0,
                    "source": "geo_pattern",
                }
            )
    for m in _GEO_PATTERN.finditer(text):
        span = (m.start(1), m.end(1))
        dominated = any(s <= span[0] < e or s < span[1] <= e for s, e in seen)
        if not dominated and span not in seen:
            seen.add(span)
            entities.append(
                {
                    "text": m.group(1),
                    "label": "LOC",
                    "start": m.start(1),
                    "end": m.end(1),
                    "score": 1.0,
                    "source": "geo_pattern",
                }
            )
    return entities


REPLACEMENTS = {
    "PHONE": "+7 (XXX) XXX-XX-XX",
    "EMAIL": "[EMAIL]",
    "INN": "[ИНН]",
    "SNILS": "[СНИЛС]",
    "PASSPORT": "[ПАСПОРТ]",
    "CARD": "[XXXX-XXXX-XXXX-XXXX]",
    "DATE": "[ДАТА]",
    "IP": "[IP]",
}

MASK_CHARS = {
    "PHONE": lambda m: re.sub(r"\d", "X", m.group()),
    "EMAIL": lambda m: (
        re.sub(
            r"[a-zA-Z0-9]", "*", m.group(), count=len(m.group()) - len(m.group().split("@")[1]) - 1
        )
        if "@" in m.group()
        else m.group()
    ),
    "INN": lambda m: re.sub(r"\d", "X", m.group()),
    "SNILS": lambda m: re.sub(r"\d", "X", m.group()),
    "PASSPORT": lambda m: re.sub(r"\d", "X", m.group()),
    "CARD": lambda m: re.sub(r"\d", "X", m.group()),
    "DATE": lambda m: re.sub(r"\d", "X", m.group()),
    "IP": lambda m: re.sub(r"\d", "X", m.group()),
}
