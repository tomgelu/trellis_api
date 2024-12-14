# START SERVICE

docker stop trellis-service-client
docker rm trellis-service-client

docker build -t trellis-processor .

docker run -d --gpus all -p 5000:5000 \
    -v "/mnt/d/Code/trellis_service/output:/workspace/TRELLIS/output:rw" \
    --name trellis-service-client trellis-processor

docker logs -f trellis-service-client

# START CLIENT

curl -v -X POST http://localhost:5000/initialize

## Test with verbose output
curl -v -X POST -F "image=@input/cherry.webp" http://localhost:5000/process

## Or try with the absolute path
curl -v -X POST -F "image=@/mnt/d/Code/TRELLIS/input/cherry.webp" http://localhost:5000/process






Downloading: "https://github.com/facebookresearch/dinov2/zipball/main" to /root/.cache/torch/hub/main.zip
/root/.cache/torch/hub/facebookresearch_dinov2_main/dinov2/layers/swiglu_ffn.py:43: UserWarning: xFormers is available (SwiGLU)
  warnings.warn("xFormers is available (SwiGLU)")
/root/.cache/torch/hub/facebookresearch_dinov2_main/dinov2/layers/attention.py:27: UserWarning: xFormers is available (Attention)
  warnings.warn("xFormers is available (Attention)")
/root/.cache/torch/hub/facebookresearch_dinov2_main/dinov2/layers/block.py:33: UserWarning: xFormers is available (Block)
  warnings.warn("xFormers is available (Block)")
INFO:dinov2:using MLP layer as FFN
Downloading: "https://dl.fbaipublicfiles.com/dinov2/dinov2_vitl14/dinov2_vitl14_reg4_pretrain.pth" to /root/.cache/torch/hub/checkpoints/dinov2_vitl14_reg4_pretrain.pth
[SPARSE] Backend: spconv, Attention: flash_attn
Warp 1.5.0 initialized:
   CUDA Toolkit 12.6, Driver 12.7
   Devices:
     "cpu"      : "x86_64"
     "cuda:0"   : "NVIDIA GeForce RTX 3090" (24 GiB, sm_86, mempool enabled)
     "cuda:1"   : "NVIDIA GeForce RTX 3070" (8 GiB, sm_86, mempool enabled)
   CUDA peer access:
     Not supported
   Kernel cache:
     /root/.cache/warp/1.5.0
Starting TRELLIS service on port 5000...
Initialize TRELLIS pipeline...
[SPARSE][CONV] spconv algo: auto
[ATTENTION] Using backend: flash_attn
100%|██████████| 1.13G/1.13G [03:40<00:00, 5.53MB/s]]