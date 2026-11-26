#!/bin/bash
cd /home/kubi/orangepi-iot-telemetry-analytics
cp /mnt/python_skrypty/*.csv dane/
git add dane/*.csv
git commit -m "Auto-update danych CSV: $(date +'%Y-%m-%d %H:%M')"
git push origin main
