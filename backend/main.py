from typing import Any, Union

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    context: dict[str, Any] = {
        "request": request,
    }
    return templates.TemplateResponse("views/home.html", context)


@app.get("/order/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
