#!/bin/bash

# Make script work regardless of where it is run from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}/.."

PYTHON="python3"
if [ -x "$HOME/nhlsb-venv/bin/python3" ]; then
  PYTHON="$HOME/nhlsb-venv/bin/python3"
fi

MODEL=""
if [ -r /proc/device-tree/model ]; then
  MODEL=$(tr -d '\0' < /proc/device-tree/model)
fi

# Original Pi Zero / Zero W / Pi 1. Zero 2 W contains "Zero 2" and keeps the faster flags.
if echo "$MODEL" | grep -qi 'raspberry pi zero' && ! echo "$MODEL" | grep -qi 'zero 2'; then
  sudo "$PYTHON" src/main.py \
    --led-gpio-mapping=adafruit-hat-pwm \
    --led-rows=32 \
    --led-cols=64 \
    --led-brightness=60
elif echo "$MODEL" | grep -qi 'raspberry pi model '; then
  sudo "$PYTHON" src/main.py \
    --led-gpio-mapping=adafruit-hat-pwm \
    --led-rows=32 \
    --led-cols=64 \
    --led-brightness=60
else
  sudo "$PYTHON" src/main.py --led-gpio-mapping=adafruit-hat-pwm --led-slowdown-gpio=3
fi
