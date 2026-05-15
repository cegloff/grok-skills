#!/usr/bin/env python3
"""
Tiny example web application for demonstrating the grok-live-web-debug skill.

Run with:
    python app.py

Then connect using the live debug controller.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import uvicorn

app = FastAPI(title="Simple Web App Example")

# In-memory "database"
items = []


@app.get("/", response_class=HTMLResponse)
def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Web App</title>
        <script src="https://unpkg.com/htmx.org@1.9.10"></script>
        <style>
            body { font-family: system-ui; max-width: 800px; margin: 40px auto; padding: 0 20px; }
            .item { padding: 8px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }
            button { margin-left: 8px; }
        </style>
    </head>
    <body>
        <h1>Simple Web App</h1>
        <p>This is a tiny example app for testing the live debug controller.</p>

        <div>
            <input id="item-input" type="text" placeholder="New item name" />
            <button hx-post="/items" hx-target="#items-list" hx-swap="innerHTML" hx-include="#item-input">
                Add Item
            </button>
        </div>

        <h2>Items</h2>
        <div id="items-list">
            <!-- Populated by HTMX -->
        </div>

        <script>
            // Optional: allow Enter key
            document.getElementById('item-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    htmx.trigger('#item-input', 'htmx:trigger', {});
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html)


@app.post("/items", response_class=HTMLResponse)
async def add_item(request: Request):
    form = await request.form()
    name = form.get("item-input", "Unnamed")
    items.append(name)
    return render_items_list()


def render_items_list():
    if not items:
        return "<p>No items yet.</p>"

    html = "<ul>"
    for i, item in enumerate(items):
        html += f"""
        <li class="item">
            {item}
            <button hx-delete="/items/{i}" hx-target="#items-list" hx-swap="innerHTML">Delete</button>
        </li>
        """
    html += "</ul>"
    return HTMLResponse(html)


@app.delete("/items/{item_id}", response_class=HTMLResponse)
async def delete_item(item_id: int):
    if 0 <= item_id < len(items):
        items.pop(item_id)
    return render_items_list()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
