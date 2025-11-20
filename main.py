from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import re
from datetime import datetime

app = FastAPI(title="MemoryWiki API")

# In-memory page storage
PAGES = {}  # {"slug": {"title":..., "content":..., "updated":...}}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


@app.get("/")
def root():
    return {"message": "MemoryWiki API online"}


@app.get("/api/list")
def list_pages():
    result = [
        {
            "slug": slug,
            "title": data["title"],
            "updated": data["updated"]
        }
        for slug, data in PAGES.items()
    ]

    result.sort(key=lambda x: x["title"].lower())
    return {"ok": True, "pages": result}


@app.get("/api/get/{slug}")
def get_page(slug: str):
    if slug not in PAGES:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"ok": True, "page": PAGES[slug]}


@app.post("/api/save")
def save_page(body: dict):
    title = body.get("title", "").strip()
    content = body.get("content", "")

    if title == "":
        raise HTTPException(status_code=400, detail="Title required")

    slug = slugify(title)

    PAGES[slug] = {
        "slug": slug,
        "title": title,
        "content": content,
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    return {"ok": True, "slug": slug}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
