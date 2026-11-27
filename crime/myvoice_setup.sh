#!/usr/bin/env bash
# Owner's own AI voice (IndicF5 clone) for the crime channel: install the voice tools and unlock the reference recording.
# The recording and its words are kept AES-256 encrypted in assets/myvoice/ (this repo is public); key = MYVOICE_KEY secret.
set -euo pipefail
[ -n "${MYVOICE_KEY:-}" ] || { echo "MYVOICE_KEY secret is missing - add it in Settings > Secrets > Actions"; exit 1; }
pip install -q numpy soundfile gradio_client
# slow CPU fallback (only used when the free Hugging Face GPU is busy or its daily quota is used up)
pip install -q torch torchaudio torchcodec --index-url https://download.pytorch.org/whl/cpu
pip install -q git+https://github.com/ai4bharat/IndicF5.git
pip install -q "transformers==4.50.0" "datasets==3.6.0" soundfile numpy gradio_client
mkdir -p myvoice
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -in assets/myvoice/ref.enc -out myvoice/ref.wav -pass env:MYVOICE_KEY
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -in assets/myvoice/ref_text.enc -out myvoice/ref_text.txt -pass env:MYVOICE_KEY
echo "my voice ready"
