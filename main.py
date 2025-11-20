from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import re
from datetime import datetime

app = FastAPI(title="MemoryWiki API")

# In-memory page storage
PAGES = {}  # {"slug": {"title":..., "content":..., "updated":...}}

# Developer access code
DEV_CODE = "17731"

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


# --------------------------------------------------------
# LIST PAGES
# --------------------------------------------------------
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


# --------------------------------------------------------
# GET PAGE
# --------------------------------------------------------
@app.get("/api/get/{slug}")
def get_page(slug: str):
    if slug not in PAGES:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"ok": True, "page": PAGES[slug]}


# --------------------------------------------------------
# SAVE PAGE
# --------------------------------------------------------
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


# --------------------------------------------------------
# DEV PANEL (HTML)
# --------------------------------------------------------
@app.get("/dev", response_class=HTMLResponse)
def dev_panel(code: str = ""):
    if code != DEV_CODE:
        return """
        <h2>🔒 Developer Access Required</h2>
        <p>Enter code to access /dev:</p>
        <form method="get">
            <input name="code" placeholder="Enter code">
            <button type="submit">Enter</button>
        </form>
        """

    # Build table of pages
    rows = ""
    for slug, info in PAGES.items():
        rows += f"""
        <tr>
            <td>{info['title']}</td>
            <td>{slug}</td>
            <td>{info['updated']}</td>
            <td>
                <form action="/dev/delete" method="post">
                    <input type="hidden" name="code" value="{DEV_CODE}">
                    <input type="hidden" name="slug" value="{slug}">
                    <button style="background:#e11d48; color:white; padding:5px 10px; border:none; border-radius:4px;">
                        Delete
                    </button>
                </form>
            </td>
        </tr>
        """

    return f"""
    <h1>🛠 MemoryWiki Developer Panel</h1>
    <p>Developer code verified.</p>
    <h2>All Pages</h2>

    <table border="1" cellpadding="6" style="border-collapse:collapse;">
        <tr>
            <th>Title</th>
            <th>Slug</th>
            <th>Updated</th>
            <th>Actions</th>
        </tr>
        {rows}
    </table>
    """


# --------------------------------------------------------
# DELETE PAGE (from /dev)
# --------------------------------------------------------
@app.post("/dev/delete")
def dev_delete_page(slug: str = Form(...), code: str = Form(...)):
    if code != DEV_CODE:
        raise HTTPException(status_code=403, detail="Invalid developer code")

    if slug not in PAGES:
        raise HTTPException(status_code=404, detail="Page not found")

    del PAGES[slug]

    return {"ok": True, "message": f"Deleted page '{slug}'"}


# --------------------------------------------------------
# BOOT
# --------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
