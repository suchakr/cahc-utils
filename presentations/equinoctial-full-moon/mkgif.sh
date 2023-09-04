#!/bin/bash
mv ../../jyotisha/images/ndial_kuru*.png .
ls ndial_kuru*png | perl -lne 'print qq(file $_)' > x.txt
cat x.txt
rm ndial_1.mp4 ; rm ndial_1.gif ; rm output.gif
ffmpeg -r .5 -f concat -safe 0 -i x.txt ndial_1.mp4
rm x.txt
HandBrakeCLI -i ndial_1.mp4  -o 2.mp4 ; mv 2.mp4 ndial_1.mp4 ; rm 2.mp4
ffmpeg -i ndial_1.mp4 -r 3 -s 1250x625 ndial_1.gif
ls -hal ndial_1.*
echo ffplay ndial_1.gif
