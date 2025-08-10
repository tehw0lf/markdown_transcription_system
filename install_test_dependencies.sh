#!/bin/bash

sudo apt-get update
sudo apt-get install curl ffmpeg
sudo pip install -U openai-whisper
curl -LsSf https://astral.sh/uv/install.sh | sh