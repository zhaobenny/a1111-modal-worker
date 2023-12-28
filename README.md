# A1111 Stable Diffusion | Modal.com Serverless Worker

Deploys AUTOMATIC1111/stable-diffusion-webui as serverless worker on Modal.com

## Usage
Quickstart:
```
git clone https://github.com/zhaobenny/a1111-modal-worker && cd a1111-modal-worker
pip install modal && modal token new
./deploy.sh
```
Query the Modal endpoint like an normal A1111 endpoint.

To add more models, add your urls to "config.yaml" and run:
```
modal run a1111_modal_worker/download.py
```
(Delete unneeded models using the modal cli or the web dashboard)

## Caveats
- over 50s response time (including for simple requests)
- no extension support yet
- need to add auth to api endpoints
- settings won't get saved if adjusted (use `overwrite` folder)
- very WIP
