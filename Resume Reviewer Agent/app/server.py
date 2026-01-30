from fastapi import FastAPI, UploadFile
from .utils.file import save_to_disk
from .db.collections.files import FileSchema, files_collection

app = FastAPI()


@app.get("/")
def hello():
    return {"status": "healthy"}


@app.post("/upload")
async def upload_file(
    file: UploadFile
):

    db_files = await files_collection.insert_one(
        document=FileSchema(
            name=file.filename,
            status="saving"
        )
    )

    files_collection.insert
    file_path = f"/mnt/uploads/{str(db_files.inserted_id)}/{file.filename}"
    await save_to_disk(file=await file.read(), path=file_path)

    # Mongodb save
    await files_collection.update_one({"_id": (db_files.inserted_id)}, {
        "$set": {
            "status": "queued"
        }
    })

    # push to queue now

    return {"file_id": str(db_files.inserted_id)}
