FROM nvidia/cuda:12.4.0-devel-ubuntu22.04
WORKDIR /content
ENV PATH="/home/camenduru/.local/bin:${PATH}"
RUN adduser --disabled-password --gecos '' camenduru && \
    adduser camenduru sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    chown -R camenduru:camenduru /content && \
    chmod -R 777 /content && \
    chown -R camenduru:camenduru /home && \
    chmod -R 777 /home

RUN apt update -y && apt install software-properties-common -y && add-apt-repository -y ppa:git-core/ppa && apt update -y && apt install -y aria2 git git-lfs unzip ffmpeg python3-pip python-is-python3

USER camenduru

RUN pip install -q opencv-python imageio imageio-ffmpeg ffmpeg-python av runpod \
    torch==2.1.0+cu121 torchvision==0.16.0+cu121 torchaudio==2.1.0+cu121 torchtext==0.16.0 torchdata==0.7.0 --extra-index-url https://download.pytorch.org/whl/cu121 \
    https://download.pytorch.org/whl/cu121/xformers-0.0.22.post7-cp310-cp310-manylinux2014_x86_64.whl \
    https://github.com/camenduru/wheels/releases/download/colab/mmcv-2.0.1-cp310-cp310-linux_x86_64.whl \
    moviepy av diffusers==0.24.0 einops omegaconf transformers==4.33.1 accelerate==0.29.3 mmdet mmpose

RUN git clone https://github.com/TMElyralab/MusePose /content/MusePose

RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/MusePose/resolve/main/MusePose/denoising_unet.pth -d /content/MusePose/pretrained_weights/MusePose -o denoising_unet.pth
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/MusePose/resolve/main/MusePose/motion_module.pth -d /content/MusePose/pretrained_weights/MusePose -o motion_module.pth
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/MusePose/resolve/main/MusePose/pose_guider.pth -d /content/MusePose/pretrained_weights/MusePose -o pose_guider.pth
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/MusePose/resolve/main/MusePose/reference_unet.pth -d /content/MusePose/pretrained_weights/MusePose -o reference_unet.pth
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/MusePose/resolve/main/dwpose/dw-ll_ucoco_384.pth -d /content/MusePose/pretrained_weights/dwpose -o dw-ll_ucoco_384.pth
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/MusePose/resolve/main/dwpose/yolox_l_8x8_300e_coco.pth -d /content/MusePose/pretrained_weights/dwpose -o yolox_l_8x8_300e_coco.pth
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/MusePose/resolve/main/image_encoder/pytorch_model.bin -d /content/MusePose/pretrained_weights/image_encoder -o pytorch_model.bin
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/MusePose/raw/main/image_encoder/config.json -d /content/MusePose/pretrained_weights/image_encoder -o config.json
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/MusePose/resolve/main/sd-image-variations-diffusers/diffusion_pytorch_model.bin -d /content/MusePose/pretrained_weights/sd-image-variations-diffusers/unet -o diffusion_pytorch_model.bin
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/MusePose/raw/main/sd-image-variations-diffusers/config.json -d /content/MusePose/pretrained_weights/sd-image-variations-diffusers/unet -o config.json
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/MusePose/resolve/main/sd-vae-ft-mse/diffusion_pytorch_model.bin -d /content/MusePose/pretrained_weights/sd-vae-ft-mse -o diffusion_pytorch_model.bin
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/camenduru/MusePose/raw/main/sd-vae-ft-mse/config.json -d /content/MusePose/pretrained_weights/sd-vae-ft-mse -o config.json

COPY ./worker_runpod.py /content/MusePose/worker_runpod.py
WORKDIR /content/MusePose
CMD python worker_runpod.py
