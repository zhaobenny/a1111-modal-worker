import inspect
import shutil
import socket
import time
from dataclasses import dataclass, field
from typing import List

MODAL_GPU = "A10G"
START_CMD = "bash /webui.sh -f --lora-dir '/models/loras' --embeddings-dir '/models/embeddings' --ckpt-dir '/models/checkpoints/' --vae-dir '/models/vaes/' --xformers"
ALWAYS_GET_LATEST_A1111 = True


def wait_for_port(port: int):
    while True:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=5.0):
                break
        except OSError:
            time.sleep(0.1)


@dataclass(frozen=True)
class UserModels:
    checkpoints_urls: List[str] = field(default_factory=list)
    vae_urls: List[str] = field(default_factory=list)
    loras_urls: List[str] = field(default_factory=list)
    embeddings_urls: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, env):
        return cls(**{
            k: v for k, v in env.items()
            if k in inspect.signature(cls).parameters
        })


def get_urls():
    """ should only be ran locally """
    import yaml

    try:
        with open("./config.yaml") as f:
            try:
                config = yaml.safe_load(f)
                return UserModels.from_dict(config)
            except yaml.YAMLError as exc:
                print(exc)
    except FileNotFoundError:
        shutil.copyfile("./config.example.yaml", "./config.yaml")
    return UserModels()
