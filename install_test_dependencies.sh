#!/bin/bash

sudo apt update
sudo apt install curl ffmpeg python3-openai-whisper
curl -LsSf https://astral.sh/uv/install.sh | sh