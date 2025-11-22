from fastapi import FastAPI, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import re
import asyncio
from datetime import datetime

app = FastAPI(title="MemoryWiki API")

PAGES = {}

DEV_CODE = "17731"

# ============================================================
# MASSIVE HASHED CURSE LIST (SAFE)
# YOU WILL MAP THESE TO REAL CURSE WORDS IN YOUR PRIVATE FILE
# ============================================================

CURSE_WORDS_HASHED = {
    # CORE CURSES (original)
    "curse_f1": "sha256:0ff2b210de...",
    "curse_f2": "sha256:11afc123bb...",
    "curse_f3": "sha256:b882dd21af...",
    "curse_f4": "sha256:ac92133fdd...",
    "curse_f5": "sha256:9dc221baef...",
    "curse_f6": "sha256:ba178fcd12...",
    "curse_f7": "sha256:ff9182aa93...",
    "curse_f8": "sha256:12ad8acfee...",
    "curse_f9": "sha256:3aa12df123...",
    "curse_f10": "sha256:9912faab77...",

    # S-WORD FAMILY
    "curse_s1": "sha256:772ab9cc13...",
    "curse_s2": "sha256:a8192cfb11...",
    "curse_s3": "sha256:b91acd983f...",
    "curse_s4": "sha256:13ae99dcb1...",
    "curse_s5": "sha256:221cfe892a...",
    "curse_s6": "sha256:4cff12881d...",
    "curse_s7": "sha256:1188affdb1...",
    "curse_s8": "sha256:88cf29ddbb...",
    "curse_s9": "sha256:aa112cdf89...",
    "curse_s10": "sha256:bcdab199af...",

    # B-WORD FAMILY
    "curse_b1": "sha256:019ad8cfea...",
    "curse_b2": "sha256:a2239cdf1a...",
    "curse_b3": "sha256:cc91a20dba...",
    "curse_b4": "sha256:ff828af111...",
    "curse_b5": "sha256:8ae212ecfe...",
    "curse_b6": "sha256:124accc9bb...",
    "curse_b7": "sha256:88ab229cce...",
    "curse_b8": "sha256:bb223d9f12...",
    "curse_b9": "sha256:aa7c8cd129...",
    "curse_b10": "sha256:119cad899d...",

    # A-WORD FAMILY
    "curse_a1": "sha256:8889ccadfe...",
    "curse_a2": "sha256:129fa93b11...",
    "curse_a3": "sha256:88a19bcdf1...",
    "curse_a4": "sha256:bb9cc381ae...",
    "curse_a5": "sha256:9981723acd...",
    "curse_a6": "sha256:faa2391eb3...",
    "curse_a7": "sha256:abc1289f11...",
    "curse_a8": "sha256:998c22ed77...",
    "curse_a9": "sha256:3abbc112cd...",
    "curse_a10": "sha256:ff1289acdd...",

    # D-WORD FAMILY
    "curse_d1": "sha256:126fabd321...",
    "curse_d2": "sha256:acc19dacbb...",
    "curse_d3": "sha256:9ac29aa1dd...",
    "curse_d4": "sha256:1182acdc29...",
    "curse_d5": "sha256:cc9182dadb...",
    "curse_d6": "sha256:3baaf1aa11...",
    "curse_d7": "sha256:b22cd89c9b...",
    "curse_d8": "sha256:faa2189bbc...",
    "curse_d9": "sha256:ccfa128813...",
    "curse_d10": "sha256:113cd298cb...",

    # P-WORD FAMILY
    "curse_p1": "sha256:9912adbcfe...",
    "curse_p2": "sha256:aa13ce19f1...",
    "curse_p3": "sha256:119ddbad91...",
    "curse_p4": "sha256:abc12ef981...",
    "curse_p5": "sha256:aa98cddc8a...",
    "curse_p6": "sha256:229dfa132f...",
    "curse_p7": "sha256:1bca219aa1...",
    "curse_p8": "sha256:bcc213cfaa...",
    "curse_p9": "sha256:129ddbacfe...",
    "curse_p10": "sha256:faa1289bcf...",

    # C-WORD FAMILY
    "curse_c1": "sha256:129ddab119...",
    "curse_c2": "sha256:221ca8bf12...",
    "curse_c3": "sha256:112cd9da22...",
    "curse_c4": "sha256:aa12bbca99...",
    "curse_c5": "sha256:fea132bb1a...",
    "curse_c6": "sha256:1abfc29ddd...",
    "curse_c7": "sha256:88acdcf1aa...",
    "curse_c8": "sha256:bba19cf991...",
    "curse_c9": "sha256:aa132ddfab...",
    "curse_c10": "sha256:5522bbfe29...",

    # MF-WORD FAMILY
    "curse_mf1": "sha256:1122fa22ff...",
    "curse_mf2": "sha256:2233aa33ee...",
    "curse_mf3": "sha256:3344bb44dd...",
    "curse_mf4": "sha256:4455cc55cc...",
    "curse_mf5": "sha256:5566dd66bb...",
    "curse_mf6": "sha256:6677ee77aa...",
    "curse_mf7": "sha256:7788ff8899...",
    "curse_mf8": "sha256:889900aa33...",
    "curse_mf9": "sha256:9911bbcc44...",
    "curse_mf10": "sha256:aabbccdde1...",

    # CATEGORY MASK SLURS (SAFE)
    "slur_r1": "sha256:r1aa22cc11...",
    "slur_r2": "sha256:r2bb33aa22...",
    "slur_r3": "sha256:r3cc44bb33...",
    "slur_r4": "sha256:r4dd55cc44...",
    "slur_r5": "sha256:r5ee66dd55...",
    "slur_s1": "sha256:s1aa22bb11...",
    "slur_s2": "sha256:s2bb33cc22...",
    "slur_s3": "sha256:s3cc44dd33...",
    "slur_s4": "sha256:s4dd55ee44...",
    "slur_s5": "sha256:s5ee66ff55...",
    "slur_x1": "sha256:x1aa11bb22...",
    "slur_x2": "sha256:x2bb22cc33...",
    "slur_x3": "sha256:x3cc33dd44...",
    "slur_x4": "sha256:x4dd44ee55...",
    "slur_x5": "sha256:x5ee55ff66...",

    # EXTENDED SLUR CATEGORIES (NO REAL WORDS)
    "slur_cat_01": "sha256:caf1b2ac11...",
    "slur_cat_02": "sha256:daa1c3dc22...",
    "slur_cat_03": "sha256:eab2d4ec33...",
    "slur_cat_04": "sha256:fcc3e5fc44...",
    "slur_cat_05": "sha256:1dd4f6ad55...",
    "slur_cat_06": "sha256:2ee5a7be66...",
    "slur_cat_07": "sha256:3ff6b8cf77...",
    "slur_cat_08": "sha256:4aa7c9df88...",
    "slur_cat_09": "sha256:5bb8dade99...",
    "slur_cat_10": "sha256:6cc9ebdfaa..."
}

# ============================================================
# REGEX RECOGNIZER (CATCHES REAL PROFANITY WITHOUT SPELLING IT)
# ============================================================

CURSE_REGEX = [
    r"\bf\W*u\W*c\W*k\b",
    r"\bs\W*h\W*i\W*t\b",
    r"\bb\W*i\W*t\W*c\W*h\b",
    r"\ba\W*s\W*s\b",
    r"\bd\W*a\W*m\W*n\b",
    r"\bh\W*e\W*l\W*l\b",
    r"\bp\W*u\W*s\W*s\W*y\b",
    r"\bm\W*f\b",
    r"\bc\W*u\W*n\W*t\b",
]

# ============================================================
# SEXUAL CONTENT PATTERNS (SAFE)
# ============================================================

SEXUAL_PATTERNS = [
    r"sex", r"sexual", r"sexy", r"xxx",
    r"nsfw", r"18\+", r"explicit",
    r"fetish", r"erotic", r"nude", r"nudity",
    r"onlyfans", r"adult"
]

# ============================================================
# SLUR CATEGORY DETECTION (SAFE)
# ============================================================

SLUR_PATTERNS = [
    r"slur_[a-z]+",
    r"hate_[a-z]+",
    r"\b[a-z]*-slur\b",
    r"\bslurs?\b"
]

# ============================================================
# VIOLENCE / CRIME / DRUG / HARASSMENT LISTS
# ============================================================

VIOLENCE = [
    "abuse", "assault", "attack", "blood", "deadly", "death",
    "destroy", "die", "hurt", "injure", "injury",
    "kill", "killed", "killing", "murder", "stab",
    "shoot", "shooting", "violence", "violent"
]

CRIME = [
    "crime", "criminal", "arson", "extort", "fraud",
    "forgery", "illegal", "illicit", "robbery", "ransom",
    "smuggle", "steal", "terror", "threat"
]

DRUGS = [
    "drug", "drugs", "drunk", "addict"
]

HARASS = [
    "bully", "harass", "insult"
]

DANGER = [
    "dangerous", "hazard", "unsafe", "toxic"
]

PLAIN_BLOCK = VIOLENCE + CRIME + DRUGS + HARASS + DANGER

# ============================================================
# MASTER CHECK FUNCTION
# ============================================================

def contains_blocked(text: str) -> bool:
    t = text.lower()

    # plain words
    for w in PLAIN_BLOCK:
        if w in t:
            return True

    # sexual patterns
    for p in SEXUAL_PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            return True

    # curses
    for pattern in CURSE_REGEX:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    # slur categories
    for pattern in SLUR_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


# ============================================================
# AUTO DELETE 5 SECONDS
# ============================================================

async def auto_delete_page(slug: str):
    await asyncio.sleep(5)
    if slug in PAGES:
        del PAGES[slug]
        print(f"[AUTO DELETE] '{slug}' removed for blocked content.")


def slugify(text: str):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# ============================================================
# ROUTES
# ============================================================

@app.post("/api/save")
def save_page(body: dict, background_tasks: BackgroundTasks):
    title = body.get("title", "").strip()
    content = body.get("content", "")

    if not title:
        raise HTTPException(400, "Title required")

    slug = slugify(title)

    PAGES[slug] = {
        "slug": slug,
        "title": title,
        "content": content,
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    if contains_blocked(title) or contains_blocked(content):
        background_tasks.add_task(auto_delete_page, slug)

    return {"ok": True, "slug": slug}

@app.get("/api/list")
def list_pages():
    return {"ok": True, "pages": list(PAGES.values())}

@app.get("/api/get/{slug}")
def get_page(slug: str):
    if slug not in PAGES:
        raise HTTPException(404, "Not found")
    return {"ok": True, "page": PAGES[slug]}


# ============================================================
# BOOT
# ============================================================

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
