#!/bin/bash

sudo apt-get install curl ffmpeg
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install -U openai-whisper