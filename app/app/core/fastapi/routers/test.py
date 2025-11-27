from fastapi import APIRouter, Response, Depends, HTTPException, Request
from starlette.status import HTTP_401_UNAUTHORIZED
from opentelemetry.propagate import inject
import httpx
from typing import Optional
import logging, time 
import random, os
from app.core.zitadel.auth import get_current_user
from app.core.zitadel.access_control import authorize_access

router = APIRouter()

TARGET_ONE_HOST = os.environ.get("TARGET_ONE_HOST", "app-b")

@router.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    logging.error("items")
    return {"item_id": item_id, "q": q}


@router.get("/io_task")
async def io_task():
    time.sleep(1)
    logging.error("io task")
    return "IO bound task finish!"


@router.get("/cpu_task")
async def cpu_task():
    for i in range(1000):
        n = i*i*i
    logging.error("cpu task")
    return "CPU bound task finish!"


@router.get("/random_status")
async def random_status(request: Request, authorization: bool = Depends(get_current_user)):
    if authorization is not True:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=authorization)
    request.status_code = random.choice([200, 200, 300, 400, 500])
    logging.error("random status")
    return {"path": "/random_status"}

# TODO authorization function should come from Depends
@router.get("/random_sleep")
async def random_sleep(request: Request, authorization: bool = Depends(get_current_user)):
    if authorization is not True:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=authorization)
    time.sleep(random.randint(0, 5))
    logging.error("random sleep")
    return {"path": "/random_sleep"}


@router.get("/error_test")
async def error_test(request: Request, authorization: bool = Depends(get_current_user)):
    if authorization is not True:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=authorization)
    logging.error("got error!!!!")
    return {"message": "ERROR!!!!!!!!!!!"}

@router.get("/chain")
async def chain(response: Response):

    headers = {}
    inject(headers)  # inject trace info to header
    logging.critical(headers)

    async with httpx.AsyncClient() as client:
        await client.get("http://localhost:8000/", headers=headers,)
    async with httpx.AsyncClient() as client:
        await client.get(f"http://{TARGET_ONE_HOST}:8000/io_task", headers=headers,)
    async with httpx.AsyncClient() as client:
        await client.get(f"http://{TARGET_ONE_HOST}:8000/cpu_task", headers=headers,)
    async with httpx.AsyncClient() as client:
        await client.get(f"http://app-a:8000/io_task", headers=headers,)
    logging.info("Chain Finished")
    return {"path": "/chain"}