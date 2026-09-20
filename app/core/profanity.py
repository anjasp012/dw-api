import re
from typing import Tuple, List

# Daftar kata-kata kasar / tidak pantas (Indonesian & English profanity words)
PROFANITY_WORDS = {
    # Indonesian vulgar / profanity words
    "anjing", "anjir", "anjay", "asu", "bajingan", "bangsat", "babi", "bedes",
    "bego", "tolol", "goblok", "idiot", "kampret", "kontol", "memek", "itil",
    "jembut", "pepek", "perek", "lonte", "pelacur", "peler", "pantek", "pukimak",
    "tetek", "toket", "ngentot", "ngentod", "kentot", "colok", "coli", "bokep",
    "porno", "bugil", "mesum", "bejad", "silit", "tempik", "bodoh", "setan",
    "iblis", "dajal", "kafir", "pantat", "titit", "buncit", "tai", "taek", "modar",
    "mampus", "bacot", "bacod", "pecun", "jablay", "bencong", "banci", "homo",
    "lesbi", "gay", "sange", "sangean", "cangcut", "vagina", "penis", "sperma",
    
    # English vulgar words
    "fuck", "fucking", "fucked", "fucker", "shit", "bitch", "asshole", "bastard",
    "dick", "cock", "pussy", "cunt", "nigger", "nigga", "slut", "whore", "porn",
    "sex", "boobs", "ass", "motherfucker", "bullshit", "prick", "twat", "wanker"
}

# Mapping leetspeak / variasi angka ke huruf
LEET_MAP = {
    '0': 'o',
    '1': 'i',
    '3': 'e',
    '4': 'a',
    '5': 's',
    '6': 'g',
    '7': 't',
    '8': 'b',
    '@': 'a',
    '$': 's',
    '!': 'i',
    '+': 't'
}

def normalize_text(text: str) -> str:
    """Mengubah leetspeak dan menyederhanakan karakter berulang."""
    t = text.lower()
    for char, replacement in LEET_MAP.items():
        t = t.replace(char, replacement)
    # Hapus karakter non-alfanumerik untuk pengecekan pola rapat
    # Sederhanakan perulangan karakter lebih dari 2x (misal: 'anjiiiiiing' -> 'anjing')
    t_reduced = re.sub(r'(.)\1{2,}', r'\1', t)
    return t_reduced

def contains_profanity(text: str) -> Tuple[bool, List[str]]:
    """
    Memeriksa apakah teks mengandung kata-kata tidak pantas.
    Mengembalikan (True, [daftar_kata]) jika ditemukan, atau (False, []) jika bersih.
    """
    if not text:
        return False, []

    normalized = normalize_text(text)
    # Bersihkan tanda baca untuk tokenisasi kata
    clean_spaced = re.sub(r'[^a-zA-Z0-9\s]', ' ', normalized)
    words = clean_spaced.split()

    detected = []

    # 1. Cek per-kata
    for w in words:
        if w in PROFANITY_WORDS:
            detected.append(w)

    # 2. Cek gabungan tanpa spasi (misal: 'k o n t o l' atau 'k.o.n.t.o.l')
    no_space = re.sub(r'[^a-zA-Z]', '', normalized)
    for bad_word in PROFANITY_WORDS:
        if len(bad_word) >= 4 and bad_word in no_space:
            if bad_word not in detected:
                detected.append(bad_word)

    # 3. Cek regex boundary
    for bad_word in PROFANITY_WORDS:
        pattern = r'\b' + re.escape(bad_word) + r'\b'
        if re.search(pattern, normalized):
            if bad_word not in detected:
                detected.append(bad_word)

    return len(detected) > 0, detected
