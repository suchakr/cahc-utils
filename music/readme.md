# Utility to play carnatic music

Given a sequence of notes and melakarta number, this utility will play the sequence.

## Conventions for notes
  Prefix octave to go high or low as  +1s and -1s 
  s0 is same as +0s or -0s.

  The general pattern in [octave]note or **,** where
    **octave** is [+-]number 
    **note** is one s r g m p d n 
    **,** implies repeat of prev note

  The uppper case versions are shortcuts  as the next higher octave


## Notes of ffmpeg usage to record the songs
### list devices
 ffmpeg -f avfoundation -list_devices true -i ""

### capture  - set o/p to multi using MIDI
  ffmpeg -f avfoundation -i ":0" kg.mp3

### cut
  ffmpeg -ss 00:00:01 -t 00:04:00 -i input.mp3 output.mp3

### minify
  ffmpeg -i kg.mp3 -map 0:a:0 -b:a 33k kg.smallish.mp3

### play
  ffplay -nodisp -autoexit -loglevel quiet kg.smallish.mp3 

### change volume
  ffmpeg -i kg.smallish.mp3 -af 'volume=0.5' loud.mp3

### add text to jpg 
 ifmpeg -i kovida.jpg -vf "drawtext=text='10':fontcolor=blue:fontsize=150:x=950:y=200:" k10.jpg

### picture + sound 
  ffmpeg -i ep1.png -i ep1.wav ep1.flv
  ffmpeg -loop 1 -framerate 1 -i k3.jpg -i क_03.mp3 -c:a copy -c:v libx264 -shortest ./mp4/x3.mp4

### concat mp3
  ffmpeg -f concat -safe 0 -i ./filelist -c copy all-filesdeepika.mp3
  where file list is
    file './file_01.mp3'
    file './file_02.mp3' ...

### Trim all silence encountered from beginning to end where there is more than 1 second of silence in audio:
    https://ffmpeg.org/ffmpeg-filters.html#silenceremove
  ffmpeg -i in.mp3 -af silenceremove=stop_periods=-1:stop_duration=1:stop_threshold=-90dB out.mp3

### Add mp3 to mp4 with reduced volume
ffmpeg -i agm-2020.mp4 -i veena.mp3 -filter_complex "[1:a]volume=0.15,apad[A];[0:a][A]amerge[out]" -c:v copy -map 0:v -map [out] -y x.mp4
