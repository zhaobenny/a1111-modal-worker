import os

import httpx
from modal import Image, Stub, Volume

from a1111_modal_worker.utils import UserModels, get_urls

MODELS = "/models"

stub = Stub("a1111")
user_models = Volume.persisted("a1111-user-models")


@stub.function(volumes={MODELS: user_models},
               image=Image.debian_slim(python_version="3.10")
               .pip_install(["httpx"])
               )
def download_all(models: UserModels):
    download_type(models.embeddings_urls, "embeddings")
    download_type(models.loras_urls, "loras")
    download_type(models.checkpoints_urls, "checkpoints")
    download_type(models.vae_urls, "vaes")


def download_type(urls, model_type):
    directory = os.path.join(MODELS, model_type)
    os.makedirs(directory, exist_ok=True)

    if not urls:
        return

    print(f"Downloading {model_type} models...")

    for url in urls:
        try:
            download_to_folder(url, model_type)
        except Exception as e:
            print(f"Failed to download from \"{url}\": {str(e)}")

    user_models.commit()
    print(f"Downloaded all {model_type} models...")


def download_to_folder(url, folder):
    with httpx.Client() as client:
        with client.stream("GET", url, follow_redirects=True, timeout=5) as r:
            headers = r.headers
        filename = extract_filename(url, headers)
        filepath = os.path.join(MODELS, folder, filename)

        if os.path.exists(filepath):
            return print(f"\"{filename}\" already exists in \"{folder}\", skipping...")

        r = client.get(url, follow_redirects=True)
        r.raise_for_status()

        with open(filepath, "wb") as f:
            f.write(r.content)

        print(f"Downloaded \"{url}\" to \"{folder}\" as \"{filename}\"")


def extract_filename(url, headers):
    content_disposition = headers.get("Content-Disposition")

    if content_disposition:
        filename = content_disposition.split("filename=")[1]
    elif url.endswith(".safetensors") or url.endswith(".pt"):
        filename = url.split("/")[-1]
    else:
        raise Exception(f"\"{url}\" does not contain a valid file")

    return filename.strip(";").strip("\"")


@stub.local_entrypoint()
def download_models():
    urls: UserModels = get_urls()
    download_all.remote(urls)
