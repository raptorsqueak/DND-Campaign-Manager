#!/usr/bin/env bash
# Turn a session recording into a name-corrected transcript.
#
#   bin/transcribe.sh recording.m4a
#   bin/transcribe.sh recording.wav --campaign example-campaign --date 2026-05-01
#   bin/transcribe.sh recording.m4a --model medium.en
#
# Pipeline: ffmpeg normalize -> glossary -> whisper.cpp -> fuzzy name correction.
# Output lands in campaigns/{slug}/.transcript-working/{date}.txt, which is
# git-ignored working state -- not an archive. It is deleted once the session log
# has been written from it.
#
# The source audio is NEVER touched by this script. Deleting it is a separate,
# explicit step that happens only after a log write succeeds.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WHISPER_DIR="${WHISPER_DIR:-$HOME/.local/share/whisper.cpp}"

AUDIO=""
CAMPAIGN=""
MODEL="small.en"
DATE=""
KEEP_RAW=0

while [ $# -gt 0 ]; do
    case "$1" in
        --campaign) CAMPAIGN="$2"; shift 2 ;;
        --model)    MODEL="$2";    shift 2 ;;
        --date)     DATE="$2";     shift 2 ;;
        --keep-raw) KEEP_RAW=1;    shift ;;
        -h|--help)  sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        -*)         echo "error: unknown option $1" >&2; exit 1 ;;
        *)          AUDIO="$1";    shift ;;
    esac
done

[ -n "$AUDIO" ] || { echo "usage: bin/transcribe.sh <audio-file> [--campaign SLUG] [--model NAME] [--date YYYY-MM-DD]" >&2; exit 1; }
[ -f "$AUDIO" ] || { echo "error: no such audio file: $AUDIO" >&2; exit 1; }

command -v ffmpeg >/dev/null 2>&1 || { echo "error: ffmpeg is required" >&2; exit 1; }

CLI="$WHISPER_DIR/build/bin/whisper-cli"
MODEL_FILE="$WHISPER_DIR/models/ggml-$MODEL.bin"
if [ ! -x "$CLI" ] || [ ! -f "$MODEL_FILE" ]; then
    echo "error: whisper.cpp not installed (looked in $WHISPER_DIR)" >&2
    echo "       run: bin/install-whisper.sh $MODEL" >&2
    exit 1
fi

# Resolve the campaign, mirroring build-glossary.py's auto-detect.
if [ -z "$CAMPAIGN" ]; then
    mapfile -t FOUND < <(find "$REPO/campaigns" -mindepth 2 -maxdepth 2 -name campaign.json -printf '%h\n' | sort)
    [ "${#FOUND[@]}" -eq 1 ] || { echo "error: pass --campaign (found ${#FOUND[@]} campaigns)" >&2; exit 1; }
    CAMPAIGN="$(basename "${FOUND[0]}")"
fi
CAMPAIGN_DIR="$REPO/campaigns/$CAMPAIGN"
[ -d "$CAMPAIGN_DIR" ] || { echo "error: no such campaign: $CAMPAIGN" >&2; exit 1; }

# Date the transcript by the recording's own mtime, not by today -- transcription
# often runs the morning after, and the file should carry the session's date.
[ -n "$DATE" ] || DATE="$(date -r "$AUDIO" +%Y-%m-%d)"

WORK="$CAMPAIGN_DIR/.transcript-working"
mkdir -p "$WORK"
WAV="$WORK/.$DATE.16k.wav"
OUT_BASE="$WORK/$DATE"

echo "==> [1/4] normalizing audio to 16 kHz mono"
ffmpeg -nostdin -loglevel error -y -i "$AUDIO" -ar 16000 -ac 1 -c:a pcm_s16le "$WAV"
printf '    %s (%s)\n' "$(basename "$WAV")" "$(du -h "$WAV" | cut -f1)"

echo "==> [2/4] building name glossary"
python3 "$REPO/bin/build-glossary.py" --campaign "$CAMPAIGN" | sed 's/^/    /'
PROMPT_FILE="$WORK/glossary/decode-prompt.txt"
ROSTER="$WORK/glossary/roster.json"

# --max-context 0 is not optional. Carrying decoded text between segments makes the
# model wedge in a repetition loop on quiet or crosstalk-heavy stretches -- it emitted
# the same sentence for four straight minutes of real table audio, and the fallback
# retries dragged it below realtime. Dropping cross-segment context fixed both.
echo "==> [3/4] transcribing with $MODEL (roughly 8 min per hour of audio on 8 cores)"
"$CLI" \
    --model "$MODEL_FILE" \
    --file "$WAV" \
    --prompt "$(cat "$PROMPT_FILE")" \
    --max-context 0 \
    --threads "$(nproc)" \
    --output-txt \
    --output-file "$OUT_BASE" \
    --print-progress

TRANSCRIPT="$OUT_BASE.txt"
[ -f "$TRANSCRIPT" ] || { echo "error: whisper produced no transcript at $TRANSCRIPT" >&2; exit 1; }

echo "==> [4/4] correcting proper nouns against the full roster"
python3 "$REPO/bin/correct-names.py" "$TRANSCRIPT" --roster "$ROSTER" | sed 's/^/    /'

[ "$KEEP_RAW" -eq 1 ] || rm -f "$WAV"

WORDS="$(wc -w < "$TRANSCRIPT")"
cat <<EOF

done.
  transcript : $TRANSCRIPT  (~$WORDS words)
  source audio left untouched at: $AUDIO

Read it, then draft the session log from it. Delete the transcript and the source
audio only once that log is written.
EOF
