# adapted from https://modal.com/docs/examples/a1111_webui#stable-diffusion-a1111

import subprocess
import time
import webbrowser

from modal import App, Image, Volume, forward

from a1111_modal_worker.utils import (ALWAYS_GET_LATEST_A1111, MODAL_GPU,
                                      START_CMD, wait_for_port)

app = App("a1111")
user_models = Volume.from_name("a1111-user-models", create_if_missing=True)


def initialize_webui():
    subprocess.Popen("bash /webui.sh -f --no-download-sd-model", shell=True)
    wait_for_port(7860)


image = (
    Image.debian_slim(python_version="3.10").apt_install(
        "wget",
        "git",
        "python3",
        "python3-pip",
        "python3-venv",
        "libgl1",
        "libglib2.0-0",
        "google-perftools",
    ).env(
        {"LD_PRELOAD": "/usr/lib/x86_64-linux-gnu/libtcmalloc.so.4"}
    ).run_commands(
        "pip3 install httpx",
        "pip3 install pyyaml",
        "pip3 install fastapi",
    ).run_commands(
        "pip3 install xformers",
        gpu=MODAL_GPU
    ).run_commands(
        "wget -q https://raw.githubusercontent.com/AUTOMATIC1111/stable-diffusion-webui/master/webui.sh",
        "chmod +x webui.sh",
    ).run_function(
        initialize_webui,
        gpu=MODAL_GPU,
        force_build=ALWAYS_GET_LATEST_A1111,
    )
    .add_local_dir(
        "./overwrite/", "/stable-diffusion-webui"
    )
    .add_local_python_source("a1111_modal_worker")
)


@app.function(gpu=MODAL_GPU, image=image, volumes={"/models/": user_models})
def web_instance():
    with forward(7860) as tunnel:
        p = subprocess.Popen(f"{START_CMD} --listen", shell=True)
        wait_for_port(7860)
        webbrowser.open(tunnel.url)
        time.sleep(10)  # pause to allow models to load
        print("######################")
        print("######################")
        print("URL")
        print("Accepting connections at", tunnel.url)
        print("WARNING: None of your settings will be saved on this instance")
        print("Press Ctrl+C to quit or be timed out in 1 hour")
        print("######################")
        print("######################")
        p.wait(3600)


@app.local_entrypoint()
def start_web_instance():
    web_instance.remote()
