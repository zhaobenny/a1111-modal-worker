from fastapi import FastAPI
from modal import asgi_app

from a1111_modal_worker.setup import stub
from a1111_modal_worker.worker import A1111

web_app = FastAPI()


@web_app.get("{path:path}")
def forward_get(path: str):
    return A1111.api_get.remote(path)


@web_app.post("{path:path}")
def forward_post(path: str, body: dict):
    return A1111.api_post.remote(path, body)


@stub.function()
@asgi_app()
def webui():
    return web_app
