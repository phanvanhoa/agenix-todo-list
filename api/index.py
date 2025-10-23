from fastapi import FastAPI, Request
import os
from supabase import create_client, Client
from fastapi.middleware.cors import CORSMiddleware

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/todos")
async def get_todos():
    response = supabase.table("todos").select("*").execute()
    items = []
    for item in response.data:
        items.append({
            "type": "Note",
            "id": item["id"],
            "published": item["created_at"],
            "content": item["title"],
            "completed": item["is_complete"]
        })
    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Collection",
        "items": items
    }

@app.post("/api/todos")
async def create_todo(request: Request):
    body = await request.json()
    title = body.get("title")
    data = supabase.table("todos").insert({"title": title}).execute()
    item = data.data[0]
    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Create",
        "object": {
            "type": "Note",
            "id": item["id"],
            "published": item["created_at"],
            "content": item["title"],
            "completed": item["is_complete"]
        }
    }

@app.patch("/api/todos/{todo_id}")
async def update_todo(todo_id: int, request: Request):
    body = await request.json()
    is_complete = body.get("is_complete")
    updated = supabase.table("todos").update({"is_complete": is_complete}).eq("id", todo_id).execute()
    item = updated.data[0]
    return {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Update",
        "object": {
            "type": "Note",
            "id": item["id"],
            "published": item["created_at"],
            "content": item["title"],
            "completed": item["is_complete"]
        }
    }
