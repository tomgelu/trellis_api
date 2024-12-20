# Build stage
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04 as builder

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}
ENV TORCH_CUDA_ARCH_LIST="7.0;7.5;8.0;8.6+PTX"
ENV FORCE_CUDA=1

# Install system dependencies in a single layer and clean up immediately
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 python3.10-dev python3-pip \
    wget git ninja-build build-essential && \
    rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Upgrade pip
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Clone the repository
WORKDIR /workspace
RUN git clone --recurse-submodules https://github.com/microsoft/TRELLIS.git

# Install Python dependencies in one layer, and clean caches to save space
RUN python -m pip install --no-cache-dir \
    torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu118 && \
    python -m pip install --no-cache-dir \
    pillow imageio imageio-ffmpeg tqdm easydict opencv-python-headless \
    scipy ninja rembg onnxruntime trimesh xatlas pyvista pymeshfix \
    igraph transformers && \
    python -m pip install --no-cache-dir \
    git+https://github.com/EasternJournalist/utils3d.git@9a4eb15e4021b67b12c460c7057d642626897ec8 && \
    python -m pip install --no-cache-dir \
    xformers==0.0.27.post2 --index-url https://download.pytorch.org/whl/cu118 && \
    python -m pip install --no-cache-dir flash-attn && \
    python -m pip install --no-cache-dir \
    kaolin -f https://nvidia-kaolin.s3.us-east-2.amazonaws.com/torch-2.4.0_cu121.html && \
    python -m pip install --no-cache-dir spconv-cu118 && \
    python -m pip install --no-cache-dir gradio==4.44.1 gradio_litmodel3d==0.0.1 && \
    python -m pip install --no-cache-dir flask-cors flask requests && \
    rm -rf /root/.cache/*

# Install extensions in one layer, and clean up immediately
RUN mkdir -p /tmp/extensions && \
    git clone https://github.com/NVlabs/nvdiffrast.git /tmp/extensions/nvdiffrast && \
    python -m pip install --no-cache-dir /tmp/extensions/nvdiffrast && \
    git clone --recurse-submodules https://github.com/JeffreyXiang/diffoctreerast.git /tmp/extensions/diffoctreerast && \
    python -m pip install --no-cache-dir /tmp/extensions/diffoctreerast && \
    git clone https://github.com/autonomousvision/mip-splatting.git /tmp/extensions/mip-splatting && \
    python -m pip install --no-cache-dir /tmp/extensions/mip-splatting/submodules/diff-gaussian-rasterization/ && \
    rm -rf /tmp/extensions && \
    rm -rf /root/.cache/*

# Runtime stage
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Copy Python and runtime files from builder
COPY --from=builder /usr/bin/python* /usr/bin/
COPY --from=builder /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=builder /workspace/TRELLIS /workspace/TRELLIS

# Set working directory
WORKDIR /workspace/TRELLIS

# Create input and output directories
RUN mkdir -p /workspace/TRELLIS/input /workspace/TRELLIS/output

# Copy Python scripts
COPY service.py /workspace/TRELLIS/service.py
COPY process.py /workspace/TRELLIS/process.py
COPY initialize.py /workspace/TRELLIS/initialize.py
RUN chmod +x /workspace/TRELLIS/service.py /workspace/TRELLIS/process.py /workspace/TRELLIS/initialize.py

# Expose the port
EXPOSE 5000

# Set entrypoint
CMD ["python", "service.py"]
