export hf_model_path=./weights/DotsOCR  # Path to your downloaded model weights, Please use a directory name without periods (e.g., `DotsOCR` instead of `dots.ocr`) for the model save path. This is a temporary workaround pending our integration with Transformers.
export PYTHONPATH=$(dirname "$hf_model_path"):$PYTHONPATH
# Use the model's built-in chat template instead of overriding it
CUDA_VISIBLE_DEVICES=0 vllm serve "$hf_model_path" \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.85 \
  --served-model-name model \
  --trust-remote-code \
  --compilation-config '{"level": 0, "use_inductor": false, "use_cudagraph": true, "cudagraph_num_of_warmups": 2}' \
  --max-model-len 90000 \
  --block-size 32 \
  --swap-space 12 