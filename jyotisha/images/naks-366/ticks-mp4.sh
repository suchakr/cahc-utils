#!/bin/bash
ls ticks*jpg | perl -lne '$l=$_;$q=chr(39);print qq(file $q$l$q) for 1..60' > x.stt
ffmpeg -y -f concat -i ./x.stt -c:v copy  -pix_fmt yuv420p x.mp4
HandBrakeCLI -i x.mp4 -o ticks.mp4
rm x.stt x.mp4

ls noticks*jpg | perl -lne '$l=$_;$q=chr(39);print qq(file $q$l$q) for 1..60' > x.stt
ffmpeg -y -f concat -i ./x.stt -c:v copy  -pix_fmt yuv420p x.mp4
HandBrakeCLI -i x.mp4 -o noticks.mp4
rm x.stt x.mp4

ls -hal
open ticks.mp4
open noticks.mp4
