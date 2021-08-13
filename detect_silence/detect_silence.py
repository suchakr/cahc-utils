from pydub import AudioSegment
from pydub.playback import play
from pydub.silence import detect_silence
sound = AudioSegment.from_file("Amit-27Feb-कुम्भा.ogg", format="ogg")
print (detect_silence(sound, min_silence_len=25))
play(sound)
