"""
Modal backend for Waterloo Mafia site.

Exposes a simple ASGI web endpoint that returns member data as JSON.
Deploy with:  modal deploy modal_backend.py
Serve locally: modal serve modal_backend.py
"""

import modal

app = modal.App("waterloo-mafia")

MEMBERS = [
    {"name": "kevin", "url": "https://www.kevinjosethomas.com/"},
    {"name": "casper", "url": "https://www.casperdong.com/"},
    {"name": "shayaan", "url": "https://www.shayaanazeem.com/"},
    {"name": "daniel", "url": "https://www.danielcwq.com/"},
    {"name": "chinmay", "url": "https://www.chinmayjindal.com/"},
]


@app.function()
@modal.web_endpoint(method="GET")
def members():
    """Return the list of Waterloo Mafia members as JSON."""
    return {"members": MEMBERS}


@app.function()
@modal.web_endpoint(method="GET")
def health():
    """Health-check endpoint for smoke testing."""
    return {"status": "ok", "service": "waterloo-mafia-backend"}
