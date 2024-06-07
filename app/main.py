from typing import Union, Annotated
from fastapi import FastAPI, UploadFile, File, Query, Path
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from PIL import Image
import uuid
import models
from database import engine
import schemas
from routers import posts, users, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)

item_1 = schemas.Item(id=1, slug=uuid.uuid4().hex, name="Item 1", price=9.99)

items = {
    item_1.id: item_1
}

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/fake_items")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

@app.get("/items")
def read_items(q: Annotated[str | None, Query(max_length=50)] = None):
    if q:
        return {"items": items, "q": q}
    return items

@app.get("/testing/")
async def testing(q: Annotated[str | None, Query(alias="item-query", deprecated=True, include_in_schema=False)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

@app.get("/items_list/")
async def read_items_list(q: Annotated[list[int] | None, Query()] = None):
    if q:
        return [items[i] if i in items  else {i: "Not Avilable"} for i in q]
    return items

@app.get("/items/{item_id}")
def read_item(item_id: Annotated[int, Path(title="The ID of the item to get")], q: str | None = None, short: bool = False):
    result = {}
    if item_id in items:
        result['item_id'] = items[item_id]
        if q:
            result['q'] = q
        if short:
            result["short"] = "This is short"
    return result
    

@app.post("/items")
def create_item(item_data: dict):
    next_id = len(items) + 1
    item_slug = uuid.uuid4().hex
    item_data["id"] = next_id
    item_data["slug"] = item_slug
    item = schemas.Item(**item_data)
    items[item.id] = item
    return items[item.id]

@app.put("/items/{item_id}")
def update_item(item_id: int, item_data: dict):
    item = items[item_id]
    item.name = item_data["name"]
    item.price = item_data["price"]
    item.description = item_data["description"]
    return item

@app.get("/models/{model_name}")
def get_model(model_name: schemas.ModelName):
    if model_name == schemas.ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    with open(file_path) as file:
        content = file.read()
    return {"file_path": file_path, "content": content}

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/convert-image/")
def convert_image(file: UploadFile = File(...)):
    if file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        image = Image.open(file.file)
        image = image.convert('RGB')
        pdf_name = f"{file.filename.split('.')[0]}.pdf"
        image.save(pdf_name, "PDF", resolution=100.0, save_all=True)
        return FileResponse(pdf_name, media_type='application/pdf', filename=pdf_name)
    else:
        return {"message": "Only JPEG and PNG images are allowed"}

if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")