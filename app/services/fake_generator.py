import random

SURNAMES_M = [
    "Смирнов",
    "Иванов",
    "Кузнецов",
    "Попов",
    "Соколов",
    "Лебедев",
    "Козлов",
    "Новиков",
    "Морозов",
    "Волков",
    "Алексеев",
    "Лазарев",
    "Сергеев",
    "Королёв",
    "Степанов",
    "Николаев",
    "Орлов",
    "Андреев",
    "Макаров",
    "Никитин",
    "Захаров",
    "Зайцев",
    "Павлов",
    "Семёнов",
    "Голубев",
    "Виноградов",
    "Богданов",
    "Воробьёв",
    "Фёдоров",
    "Михайлов",
]
SURNAMES_F = [
    "Смирнова",
    "Иванова",
    "Кузнецова",
    "Попова",
    "Соколова",
    "Лебедева",
    "Козлова",
    "Никитина",
    "Морозова",
    "Волкова",
    "Алексеева",
    "Лазарева",
    "Сергеева",
    "Королёва",
    "Степанова",
    "Николаева",
    "Орлова",
    "Андреева",
    "Макарова",
    "Захарова",
    "Зайцева",
    "Павлова",
    "Семёнова",
    "Голубева",
]
FIRST_NAMES_M = [
    "Александр",
    "Дмитрий",
    "Максим",
    "Артём",
    "Илья",
    "Даниил",
    "Кирилл",
    "Антон",
    "Егор",
    "Никита",
    "Арсений",
    "Владислав",
    "Тимофей",
    "Роман",
    "Матвей",
    "Богдан",
    "Денис",
    "Владимир",
    "Павел",
    "Глеб",
    "Ярослав",
    "Марк",
    "Лев",
    "Тимур",
    "Олег",
]
FIRST_NAMES_F = [
    "Анна",
    "Мария",
    "Екатерина",
    "Дарья",
    "Алина",
    "Ольга",
    "Елена",
    "Наталья",
    "Ирина",
    "Татьяна",
    "Светлана",
    "Юлия",
    "Ксения",
    "Виктория",
    "Полина",
    "Вера",
    "Людмила",
    "Валентина",
    "Александра",
    "Марина",
    "Евгения",
    "Кристина",
    "Диана",
    "Надежда",
]
PATRONYMICS_M = [
    "Александрович",
    "Дмитриевич",
    "Сергеевич",
    "Андреевич",
    "Николаевич",
    "Владимирович",
    "Игоревич",
    "Олегович",
    "Евгеньевич",
    "Романович",
    "Викторович",
    "Михайлович",
    "Юрьевич",
    "Петрович",
    "Алексеевич",
    "Иванович",
    "Артёмович",
    "Кириллович",
    "Максимович",
    "Павлович",
]
PATRONYMICS_F = [
    "Александровна",
    "Дмитриевна",
    "Сергеевна",
    "Андреевна",
    "Николаевна",
    "Владимировна",
    "Игоревна",
    "Олеговна",
    "Евгеньевна",
    "Романовна",
    "Викторовна",
    "Михайловна",
    "Юрьевна",
    "Петровна",
    "Алексеевна",
    "Ивановна",
    "Артёмовна",
    "Кирилловна",
    "Максимовна",
    "Павловна",
]

ALL_SURNAMES = set(SURNAMES_M + SURNAMES_F)
ALL_FIRST_NAMES = set(FIRST_NAMES_M + FIRST_NAMES_F)
ALL_PATRONYMICS = set(PATRONYMICS_M + PATRONYMICS_F)

CITIES = [
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Казань",
    "Самара",
    "Омск",
    "Челябинск",
    "Ростов-на-Дону",
    "Уфа",
    "Волгоград",
    "Краснодар",
    "Воронеж",
    "Пермь",
    "Тюмень",
    "Ижевск",
    "Барнаул",
    "Иркутск",
    "Хабаровск",
    "Ярославль",
    "Владивосток",
    "Махачкала",
    "Томск",
    "Оренбург",
    "Кемерово",
    "Новокузнецк",
    "Рязань",
    "Астрахань",
    "Пенза",
    "Липецк",
    "Тула",
    "Киров",
    "Чебоксары",
    "Калининград",
    "Брянск",
    "Курск",
    "Магнитогорск",
    "Ульяновск",
    "Тверь",
    "Ставрополь",
    "Белгород",
    "Сочи",
    "Архангельск",
    "Владимир",
    "Смоленск",
    "Калуга",
    "Чита",
    "Мурманск",
    "Тамбов",
    "Петрозаводск",
    "Кострома",
    "Нижневартовск",
    "Новороссийск",
    "Сургут",
    "Вологда",
    "Череповец",
    "Владикавказ",
    "Орёл",
    "Нальчик",
    "Грозный",
    "Берлин",
    "Париж",
    "Лондон",
    "Рим",
    "Мадрид",
    "Вена",
    "Варшава",
    "Прага",
    "Будапешт",
    "Бухарест",
    "София",
    "Афины",
    "Стокгольм",
    "Осло",
    "Хельсинки",
    "Копенгаген",
    "Брюссель",
    "Амстердам",
    "Лиссабон",
    "Дублин",
    "Цюрих",
    "Женева",
    "Мюнхен",
    "Гамбург",
    "Франкфурт",
    "Барселона",
    "Милан",
    "Неаполь",
    "Турин",
    "Токио",
    "Сеул",
    "Пекин",
    "Шанхай",
    "Гонконг",
    "Сингапур",
    "Бангкок",
    "Манила",
    "Ханой",
    "Дели",
    "Мумбаи",
    "Дубай",
    "Стамбул",
    "Анкара",
    "Каир",
    "Тель-Авив",
    "Торонто",
    "Ванкувер",
    "Монреаль",
    "Сидней",
    "Мельбурн",
    "Киев",
    "Минск",
    "Алматы",
    "Астана",
    "Ташкент",
    "Баку",
    "Ереван",
    "Бишкек",
    "Харьков",
    "Одесса",
    "Днепр",
    "Львов",
    "Запорожье",
    "Николаев",
    "Мариуполь",
    "Винница",
    "Херсон",
    "Полтава",
    "Чернигов",
    "Черкассы",
    "Житомир",
    "Сумы",
    "Ровно",
    "Тернополь",
    "Ужгород",
    "Луцк",
    "Черновцы",
    "Хмельницкий",
    "Кропивницкий",
    "Кременчуг",
    "Бердянск",
    "Мелитополь",
    "Ивано-Франковск",
    "Борисполь",
    "Бровары",
    "Буча",
    "Ирпень",
    "Ялта",
    "Севастополь",
    "Симферополь",
    "Евпатория",
    "Керчь",
]


def _decline_city(base: str, original: str) -> str:
    if base.endswith("ск"):
        if original.endswith("ском"):
            return base + "ом"
        if original.endswith("ска"):
            return base + "а"
        if original.endswith("ску"):
            return base + "у"
        if original.endswith("ске"):
            return base + "е"
        return base
    if base.endswith("бург"):
        if original.endswith("бургом"):
            return base + "ом"
        if original.endswith("бурга"):
            return base + "а"
        if original.endswith("бургу"):
            return base + "у"
        if original.endswith("бурге"):
            return base + "е"
        return base
    if base.endswith("а"):
        if original.endswith("ой"):
            return base[:-1] + "ой"
        if original.endswith("ы"):
            return base[:-1] + "ы"
        if original.endswith("е"):
            return base[:-1] + "е"
        if original.endswith("у"):
            return base[:-1] + "у"
        return base
    if base.endswith("ь"):
        if original.endswith("и"):
            return base[:-1] + "и"
        if original.endswith("ю"):
            return base[:-1] + "ю"
        return base
    return base


EMAIL_DOMAINS = [
    "mail.ru",
    "yandex.ru",
    "gmail.com",
    "inbox.ru",
    "rambler.ru",
    "bk.ru",
    "list.ru",
    "internet.ru",
    "proton.me",
    "outlook.com",
]

WORDS_FOR_EMAIL = [
    "solnce",
    "vetter",
    "listok",
    "moroz",
    "stepnoy",
    "lesnoy",
    "belka",
    "zvezda",
    "morehod",
    "skazochnik",
    "dobry",
    "silach",
    "paley",
    "snegir",
    "zarya",
    "mechta",
    "vecher",
    "utro",
    "blesk",
    "tikhiy",
    "gromkiy",
    "bystryy",
    "yarkiy",
    "sladkiy",
]

M_ENDINGS = (
    "ов",
    "ев",
    "ин",
    "ын",
    "ский",
    "цкий",
    "ий",
    "ый",
    "ов",
    "ев",
    "ич",
    "ук",
    "юк",
    "ун",
    "ён",
)


def _pick(seq):
    return random.choice(seq)


def _detect_gender(word: str) -> str:
    if word.endswith("а") or word.endswith("я"):
        return "f"
    return "m"


def _parse_fio(text: str) -> list[str]:
    parts = text.strip().split()
    result = []
    for p in parts:
        p_stripped = p.strip()
        if p_stripped:
            result.append(p_stripped)
    return result


def _classify_part(word: str) -> str:
    w = word.lower().rstrip(".,:;")
    if w in {s.lower() for s in ALL_PATRONYMICS}:
        return "patronymic"
    if w in {s.lower() for s in ALL_FIRST_NAMES}:
        return "firstname"
    if w in {s.lower() for s in ALL_SURNAMES}:
        return "surname"
    if w.endswith("ич") or w.endswith("на"):
        return "patronymic"
    return "unknown"


def _classify_fio_parts(parts: list[str]) -> list[str]:
    if not parts:
        return []
    classified = [_classify_part(p) for p in parts]
    patronymic_idx = [i for i, c in enumerate(classified) if c == "patronymic"]
    if patronymic_idx:
        pi = patronymic_idx[0]
        for i in range(pi):
            if classified[i] == "unknown":
                classified[i] = "surname" if i == 0 else "firstname"
        return classified

    has_firstname = "firstname" in classified
    has_surname = "surname" in classified

    if len(parts) == 1:
        if classified[0] == "unknown":
            classified[0] = "surname"
    elif len(parts) == 2:
        if has_firstname and not has_surname:
            fi = classified.index("firstname")
            si = 1 - fi
            classified[si] = "surname"
        elif has_surname and not has_firstname:
            si = classified.index("surname")
            fi = 1 - si
            classified[fi] = "firstname"
        else:
            classified[0] = "surname"
            classified[1] = "firstname"
    elif len(parts) >= 3:
        for i, c in enumerate(classified):
            if c == "unknown":
                classified[i] = "surname" if i == 0 else ("firstname" if i == 1 else "patronymic")

    return classified


class FakeGenerator:
    def __init__(self):
        self._surname_map: dict[str, str] = {}
        self._firstname_map: dict[str, str] = {}
        self._patronymic_map: dict[str, str] = {}
        self._per_text_map: dict[str, str] = {}
        self._used_surnames: set[str] = set()
        self._used_firstnames: set[str] = set()
        self._email_map: dict[str, str] = {}
        self._phone_map: dict[str, str] = {}
        self._inn_map: dict[str, str] = {}
        self._snils_map: dict[str, str] = {}
        self._passport_map: dict[str, str] = {}
        self._card_map: dict[str, str] = {}
        self._address_map: dict[str, str] = {}

    def reset(self):
        self.__init__()

    def _gen_unique_surname(self, gender: str) -> str:
        pool = SURNAMES_M if gender == "m" else SURNAMES_F
        available = [s for s in pool if s not in self._used_surnames]
        if not available:
            available = pool
        s = _pick(available)
        self._used_surnames.add(s)
        return s

    def _gen_unique_firstname(self, gender: str) -> str:
        pool = FIRST_NAMES_M if gender == "m" else FIRST_NAMES_F
        available = [s for s in pool if s not in self._used_firstnames]
        if not available:
            available = pool
        s = _pick(available)
        self._used_firstnames.add(s)
        return s

    def _gen_patronymic(self, gender: str) -> str:
        pool = PATRONYMICS_M if gender == "m" else PATRONYMICS_F
        return _pick(pool)

    def replace_per(self, original: str) -> str:
        key = original.strip()
        if key in self._per_text_map:
            return self._per_text_map[key]

        parts = _parse_fio(key)
        classified = _classify_fio_parts(parts)

        if not parts:
            return key

        gender = _detect_gender(parts[-1])

        replacements = []
        for part, ptype in zip(parts, classified):
            if ptype == "surname":
                if part not in self._surname_map:
                    self._surname_map[part] = self._gen_unique_surname(gender)
                replacements.append(self._surname_map[part])
            elif ptype == "firstname":
                if part not in self._firstname_map:
                    self._firstname_map[part] = self._gen_unique_firstname(gender)
                replacements.append(self._firstname_map[part])
            elif ptype == "patronymic":
                if part not in self._patronymic_map:
                    self._patronymic_map[part] = self._gen_patronymic(gender)
                replacements.append(self._patronymic_map[part])
            else:
                if part not in self._surname_map:
                    self._surname_map[part] = self._gen_unique_surname(gender)
                replacements.append(self._surname_map[part])

        result = " ".join(replacements)
        self._per_text_map[key] = result
        return result

    def replace_loc(self, original: str) -> str:
        key = original.strip()
        if key not in self._address_map:
            base = _pick(CITIES)
            declined = _decline_city(base, key)
            self._address_map[key] = declined
        return self._address_map[key]

    def replace_phone(self, original: str) -> str:
        key = original.strip()
        if key not in self._phone_map:
            code = random.randint(900, 999)
            num = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"
            self._phone_map[key] = f"+7 ({code}) {num}"
        return self._phone_map[key]

    def replace_email(self, original: str) -> str:
        key = original.strip()
        if key not in self._email_map:
            prefix = _pick(WORDS_FOR_EMAIL) + str(random.randint(1, 9999))
            self._email_map[key] = f"{prefix}@{_pick(EMAIL_DOMAINS)}"
        return self._email_map[key]

    def replace_inn(self, original: str) -> str:
        key = original.strip()
        if key not in self._inn_map:
            self._inn_map[key] = str(random.randint(1000000000, 9999999999))
        return self._inn_map[key]

    def replace_snils(self, original: str) -> str:
        key = original.strip()
        if key not in self._snils_map:
            self._snils_map[key] = (
                f"{random.randint(100, 999)}-"
                f"{random.randint(100, 999)}-"
                f"{random.randint(100, 999)} "
                f"{random.randint(10, 99)}"
            )
        return self._snils_map[key]

    def replace_passport(self, original: str) -> str:
        key = original.strip()
        if key not in self._passport_map:
            self._passport_map[key] = (
                f"{random.randint(1000, 9999)} {random.randint(100000, 999999)}"
            )
        return self._passport_map[key]

    def replace_card(self, original: str) -> str:
        key = original.strip()
        if key not in self._card_map:
            self._card_map[key] = (
                f"{random.randint(1000, 9999)}-"
                f"{random.randint(1000, 9999)}-"
                f"{random.randint(1000, 9999)}-"
                f"{random.randint(1000, 9999)}"
            )
        return self._card_map[key]

    def replace(self, label: str, original: str) -> str:
        dispatch = {
            "PER": self.replace_per,
            "PERSON": self.replace_per,
            "LOC": self.replace_loc,
            "LOCATION": self.replace_loc,
            "ORG": lambda x: x,
            "ORGANIZATION": lambda x: x,
            "PHONE": self.replace_phone,
            "EMAIL": self.replace_email,
            "INN": self.replace_inn,
            "SNILS": self.replace_snils,
            "PASSPORT": self.replace_passport,
            "CARD": self.replace_card,
            "DATE": lambda x: "01.01.2000",
            "IP": lambda x: (
                f"{random.randint(1, 255)}."
                f"{random.randint(0, 255)}."
                f"{random.randint(0, 255)}."
                f"{random.randint(1, 254)}"
            ),
        }
        fn = dispatch.get(label, lambda x: f"[{label}]")
        return fn(original)


fake_generator = FakeGenerator()
