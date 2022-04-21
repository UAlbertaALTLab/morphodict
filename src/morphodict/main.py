import os
from fastapi import FastAPI
from http.client import HTTPException
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
description = """
The defender of the server. Long live they that defend the server. 
"""

app = FastAPI(description=description)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/local/")
async def root():
    description="hello"
    return {"message": "TESTING 00x01"}

@app.get("/local/search/{word}")
async def search(word: str):
    clean = word.encode("utf-8")
    reqString = "\"{}\" : \"{}\"".format("name", clean.decode())
    reqString = "{" + reqString + "}"
    resHandler = "curl -X POST localhost:8000/api/search/ -H \'Content-Type: application/json' -d '{}'".format(reqString)
    jsonRes = os.popen(resHandler).read()
    jsonRes = jsonable_encoder(jsonRes)
    return JSONResponse(content = jsonRes)

@app.get("/local/word/{word}")
async def get_word(word: str):
    clean = word.encode("utf-8").decode()
    word = "curl localhost:8000/api/word/{}/ -H \"Accept: application/json\"".format(clean)
    jsonRes = os.popen(word).read()
    jsonRes = jsonable_encoder(jsonRes)
    return JSONResponse(content = jsonRes)


@app.get("/local/word_type/{word}")
async def get_word_type(word: str, type="ling"):
    print(type) 
    clean = word.encode("utf-8").decode()
    word = "curl localhost:8000/api/word/{}/ -H \"Accept: application/json\"".format(clean)
    jsonRes = os.popen(word).read()
    jsonRes = jsonable_encoder(jsonRes)
    return JSONResponse(content = jsonRes)

