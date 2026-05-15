#!/usr/bin/env python3
"""
Tiny example web application for demonstrating the grok-live-web-debug skill.

A simple HTMX-powered item list that is easy to automate and inspect.

Run:
    python app.py

Then use the live debug controller or autonomous tester against http://localhost:5000
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="Grok Live Debug - Simple Example")

# In-memory store
items: list[str] = []


@app.get("/", response_class=HTMLResponse)
def home():
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Simple Web App Demo</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 20px; line-height: 1.5; }
        .item { padding: 10px 12px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; background: #fafafa; }
        button { padding: 6px 14px; cursor: pointer; }
        input { padding: 8px; font-size: 1rem; width: 280px; }
        h1 { margin-bottom: 8px; }
        .status { color: #666; font-size: 0.9rem; margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>Simple Web App</h1>
    <p class="status">This tiny demo is designed for testing the grok-live-web-debug skill.</p>

    <div style="margin-bottom: 20px;">
        <input id="item-input" type="text" placeholder="New item name" />
        <button hx-post="/items" hx-target="#items-list" hx-swap="innerHTML" hx-include="#item-input" hx-on::after-request="document.getElementById('item-input').value=''">
            Add Item
        </button>
    </div>

    <h2>Items</h2>
    <div id="items-list">
        <p>No items yet. Add some above!</p>
    </div>

    <script>
        // Allow Enter key to submit
        document.getElementById('item-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                document.querySelector('button').click();
            }
        });
    </script>
</body>
</html>'''
    return HTMLResponse(html)


@app.post("/items", response_class=HTMLResponse)
async def add_item(request: Request):
    form = await request.form()
    name = form.get("item-input") or form.get("value") or "Unnamed item"
    items.append(str(name))
    return render_items_list()


def render_items_list():
    if not items:
        return HTMLResponse("<p>No items yet. Add some above!</p>")

    html = "<div>"
    for i, item in enumerate(items):
        html += f"""
        <div class="item">
            <span>{item}</span>
            <button hx-delete="/items/{i}" hx-target="#items-list" hx-swap="innerHTML">Delete</button>
        </div>
        """
    html += "</div>"
    return HTMLResponse(html)


@app.delete("/items/{item_id}", response_class=HTMLResponse)
async def delete_item(item_id: int):
    if 0 <= item_id < len(items):
        items.pop(item_id)
    return render_items_list()


if __name__ == "__main__":
    print("Starting Simple Web App demo on http://localhost:5000")
    uvicorn.run(app, host="0.0.0.0", port=5000)
