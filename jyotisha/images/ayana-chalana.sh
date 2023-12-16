#!/bin/bash
cd naks-366
rm list.txt
ls *deg* | cat | perl -lne '$f=$_; print qq(file $f) for 1 .. 1' | tail -r  >> list.txt
ls *deg* | cat | perl -lne '$f=$_; print qq(file $f) for 1 .. 1' >> list.txt
wc -l list.txt
ffmpeg  -f concat -i 'list.txt' -vf 'fps=600' o.gif
rm list.txt
ls *deg* | cat | perl -lne '$f=$_; print qq(file $f) for 1 .. 50' | tail -r  >> list.txt
ls *deg* | cat | perl -lne '$f=$_; print qq(file $f) for 1 .. 50' >> list.txt
wc -l list.txt
ffmpeg  -f concat -i 'list.txt' -vf 'fps=60' o.mp4
ls -hal o.gif o.mp4
cd ..
