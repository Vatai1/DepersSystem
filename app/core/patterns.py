import re

PHONE = re.compile(r"(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}")
EMAIL = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
INN = re.compile(r"\b\d{10,12}\b")
SNILS = re.compile(r"\b\d{3}[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{2}\b")
PASSPORT = re.compile(r"\b\d{4}\s?\d{6}\b")
CARD = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")
DATE_RU = re.compile(r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b")
IP_ADDRESS = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")

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
