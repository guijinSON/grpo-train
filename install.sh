#!/bin/bash
# install_dependencies.sh
# A script to install flash-attn, Hugging Face libraries, vLLM, a specific version of TRL from GitHub, 
# and additional packages math_verify, wandb, and langdetect.

set -e  # Exit immediately if a command exits with a non-zero status.

echo "Installing flash-attn..."
pip install flash-attn

echo "Installing Hugging Face libraries..."
pip install --upgrade \
  "transformers==4.48.1" \
  "datasets==3.1.0" \
  "accelerate==1.3.0" \
  "hf-transfer==0.1.9" \
  "deepspeed==0.15.4" \
  "trl==0.14.0"

echo "Installing vLLM..."
pip install "vllm==0.7.0"

echo "Upgrading and reinstalling TRL from GitHub..."
pip install --upgrade --force-reinstall --no-deps git+https://github.com/guijinSON/trl.git

echo "Installing math_verify, wandb, and langdetect..."
pip install math_verify wandb langdetect

echo "All installations completed successfully!"

# accelerate launch --num_processes 3 --config_file deepspeed_zero3.yaml run_grpo.py --config grpo_configs.yaml