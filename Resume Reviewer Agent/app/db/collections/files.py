from pydantic import Field
from typing import TypedDict
from pymongo.asynchronous.collection import AsyncCollection
from ..db import database


class FileSchema(TypedDict):
    name: str = Field(..., description="Name of the file")
    status: str = Field(..., description="Status os the file")


COLLECTION_NAME = "files"
files_collection: AsyncCollection = database[COLLECTION_NAME]
