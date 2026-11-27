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
pip install -q "pyarrow<18" "numpy<2"
mkdir -p myvoice
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -in assets/myvoice/ref.enc -out myvoice/ref.wav -pass env:MYVOICE_KEY
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -in assets/myvoice/ref_text.enc -out myvoice/ref_text.txt -pass env:MYVOICE_KEY
if [ -d assets/myvoice/emo ]; then      # one reference clip per mood (hook, calm, suspense, twist, question, sad, success, end)
  mkdir -p myvoice/emo
  for f in assets/myvoice/emo/*.enc; do b=$(basename "$f" .enc); [ "$b" = texts ] && o=myvoice/emo/texts.json || o=myvoice/emo/$b.wav
    openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -in "$f" -out "$o" -pass env:MYVOICE_KEY; done
fi
echo "my voice ready"
