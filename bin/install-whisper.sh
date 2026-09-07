#!/usr/bin/env bash
# Build whisper.cpp and fetch a transcription model.
#
# Everything lands outside the repo (default ~/.local/share/whisper.cpp) -- the build
# tree and the model weights are not campaign data and must never be committed.
#
#   bin/install-whisper.sh                # small.en, the default for table audio
#   bin/install-whisper.sh medium.en      # slower, better; overnight runs only
#   WHISPER_DIR=/opt/whisper bin/install-whisper.sh
#
# On 8 cores with no GPU, expect roughly: base.en ~25 min, small.en ~60 min,
# medium.en 3h+ for a 2.5-hour session.

set -euo pipefail

MODEL="${1:-small.en}"
WHISPER_DIR="${WHISPER_DIR:-$HOME/.local/share/whisper.cpp}"
REPO_URL="https://github.com/ggml-org/whisper.cpp.git"

for tool in git cmake make g++; do
    command -v "$tool" >/dev/null 2>&1 || { echo "error: $tool is required but not installed" >&2; exit 1; }
done

if [ -d "$WHISPER_DIR/.git" ]; then
    echo "==> updating $WHISPER_DIR"
    git -C "$WHISPER_DIR" pull --ff-only
else
    echo "==> cloning whisper.cpp into $WHISPER_DIR"
    mkdir -p "$(dirname "$WHISPER_DIR")"
    git clone --depth 1 "$REPO_URL" "$WHISPER_DIR"
fi

echo "==> building (this takes a few minutes)"
cmake -S "$WHISPER_DIR" -B "$WHISPER_DIR/build" -DCMAKE_BUILD_TYPE=Release >/dev/null
cmake --build "$WHISPER_DIR/build" --config Release -j "$(nproc)"

# Upstream renamed the CLI: ./main is deprecated in favour of build/bin/whisper-cli.
CLI="$WHISPER_DIR/build/bin/whisper-cli"
if [ ! -x "$CLI" ]; then
    CLI="$(find "$WHISPER_DIR/build" -maxdepth 3 -type f -name 'whisper-cli' -perm -u+x | head -1 || true)"
fi
[ -n "$CLI" ] && [ -x "$CLI" ] || { echo "error: build finished but no whisper-cli binary found" >&2; exit 1; }

echo "==> fetching model: $MODEL"
"$WHISPER_DIR/models/download-ggml-model.sh" "$MODEL"

MODEL_FILE="$WHISPER_DIR/models/ggml-$MODEL.bin"
[ -f "$MODEL_FILE" ] || { echo "error: model not found at $MODEL_FILE" >&2; exit 1; }

cat <<EOF

done.
  binary : $CLI
  model  : $MODEL_FILE

Transcribe a session with:
  bin/transcribe.sh /path/to/recording.m4a
EOF
