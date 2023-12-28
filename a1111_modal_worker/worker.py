import subprocess
import time

from modal import method

from a1111_modal_worker.setup import image, stub, user_models
from a1111_modal_worker.utils import MODAL_GPU, START_CMD, wait_for_port


@stub.cls(gpu=MODAL_GPU, image=image, volumes={"/models": user_models})
class A1111:
    BASE_URL = "http://127.0.0.1:7860"

    def __enter__(self):
        subprocess.Popen(f"{START_CMD} --api", shell=True)
        wait_for_port(7860)
        time.sleep(15)  # wait for model/embeddings to load

    @method()
    def api_get(self, path: str):
        import httpx
        with httpx.Client() as client:
            r = client.get(self.BASE_URL + path)
            return r.json()

    @method()
    def api_post(self, path: str, data: dict):
        import httpx
        with httpx.Client() as client:
            r = client.post(self.BASE_URL + path, json=data)
            return r.json()
