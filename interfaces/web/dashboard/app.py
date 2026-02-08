"""
Web Dashboard - Interface web para OpenClaw MCP
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI(title="OpenClaw Dashboard")

# Templates
templates = Jinja2Templates(directory="interfaces/web/dashboard/templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard principal"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/stats")
async def get_stats():
    """Estatísticas do sistema"""
    return {
        "total_tasks": 0,
        "active_skills": 11,
        "uptime": "0h 0m"
    }

if __name__ == "__main__":
    print("🦞 OpenClaw Web Dashboard")
    print("=" * 50)
    print("Starting server on http://127.0.0.1:8080")
    print("=" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=8080)
