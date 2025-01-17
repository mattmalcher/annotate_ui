from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mock database - replace with real database in production
class Action(BaseModel):
    id: int
    description: str

class Call(BaseModel):
    id: int
    actions: List[Action]

calls_db = {
    1: Call(
        id=1,
        actions=[
            Action(id=1, description="Updated customer address"),
            Action(id=2, description="Processed refund request"),
            Action(id=3, description="Scheduled follow-up call"),
        ]
    )
}

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    # Redirect to the first call in our database
    first_call_id = min(calls_db.keys())
    return RedirectResponse(url=f"/call/{first_call_id}")

@app.get("/calls", response_class=HTMLResponse)
async def list_calls(request: Request):
    return templates.TemplateResponse(
        "calls_list.html",
        {"request": request, "calls": calls_db.values()}
    )

@app.get("/call/{call_id}", response_class=HTMLResponse)
async def get_call(request: Request, call_id: int):
    call = calls_db.get(call_id)
    if not call:
        return RedirectResponse(url="/calls")
    return templates.TemplateResponse(
        "call.html",
        {"request": request, "call": call}
    )

@app.post("/action/edit/{action_id}")
async def edit_action(action_id: int, description: str = Form(...)):
    # Mock update - replace with database update in production
    for call in calls_db.values():
        for action in call.actions:
            if action.id == action_id:
                action.description = description
                return {"description": description}
    return {"error": "Action not found"}

@app.delete("/action/{action_id}")
async def delete_action(action_id: int):
    # Mock delete - replace with database delete in production
    for call in calls_db.values():
        call.actions = [a for a in call.actions if a.id != action_id]
    return {"success": True}

@app.post("/action/add/{call_id}")
async def add_action(call_id: int, description: str = Form(...)):
    # Mock add - replace with database insert in production
    call = calls_db.get(call_id)
    if call:
        new_id = max([a.id for a in call.actions]) + 1
        new_action = Action(id=new_id, description=description)
        call.actions.append(new_action)
        return {"id": new_id, "description": description}
    return {"error": "Call not found"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)