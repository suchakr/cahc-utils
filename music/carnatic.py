#%%
import pandas as pd
import numpy as np
import re
import time
import random
from synthesizer import Player, Synthesizer, Waveform

#%%
#================================================================
# Frequency ratios of 12 notes
# sa r1 r2 r3 g3 m1 m2 pa d1 d2 d3 n3 Sa
#       g1 g2                n1 n2
#
NOTES = {
     's0'  : 01.0/01.0 , 's'  : 01.0/01.0
    ,'r1'  : 16.0/15.0 
    ,'r2'  : 09.0/08.0 ,'g1'  : 09.0/08.0 
    ,'r3'  : 06.0/05.0 ,'g2'  : 06.0/05.0 
    ,'g3'  : 05.0/04.0
    ,'m1'  : 04.0/03.0 
    ,'m2'  : 17.0/12.0
    ,'p'   : 03.0/02.0
    ,'p0'  : 03.0/02.0
    ,'d1'  : 08.0/05.0 
    ,'d2'  : 05.0/03.0 ,'n1'  : 05.0/03.0 
    ,'d3'  : 09.0/05.0 ,'n2'  : 09.0/05.0 
    ,'n3'  : 15.0/08.0
}
NOTES.update({n.upper() : 2*NOTES[n] for n in NOTES })

#%%
#===================================================================
# some typical notes strings
SARGAM  = list('srgmpdn') 
SARGAMS = list('srgmpdnS') 
SPS     = list('spS')  

#===================================================================
# For a given melakarta num (mk between 1 and 72 ) 
#   find the stanas (positions )  r g , m, and d n 
#   s p are fixed for all 72 mk
# 
def _stanas(mk) :
    stanas = {  
        'lo' : [   [ 'r%d'%  (x//10) , 'g%d' %  (x%10)  ] for x in ( 11, 12, 13, 22, 23, 33 )],  
        'hi' : [   [ 'd%d'%  (x//10) , 'n%d' %  (x%10)  ] for x in ( 11, 12, 13, 22, 23, 33 )] 
    }
    rg = stanas['lo'][((mk-1)%36)//6]
    m  = ['m'+str(1+(mk-1) //36)]
    nd = stanas['hi'][((mk-1)%36)%6]
    ans = [ 's0'] + rg + m + ['p0'] + nd
    #ans = ans + [ x.upper() for x in ans ] 
    return ans

STANAS_AA = [ _stanas(x) for x in range(1,73)]  # array of arrays
STANAS_AH = [ { x[0]: x for  x in  xs } for xs in STANAS_AA ] # array of hashes
STANAS_DF = pd.DataFrame(STANAS_AH)[SARGAM] # data frame

#%%
#================================================================
# This plays a note
_player = Player()
_player.open_stream()
_synthesizer = Synthesizer(osc1_waveform=Waveform.sawtooth, osc1_volume=0.1, use_osc2=False, osc2_volume=0.05)


WNOTE ='cCdDefFgGaAb'
#WNFF  = Western Note Freq Factor
WNFF  = { x:-1+2.0**1+WNOTE.index(x)/12 for x in list(WNOTE) }

def wnote_norm(x)  :  return (0,x[0]) if x[0]  not in '0123456789' else (int(x[0]), x[1])
def wnote_to_onf(x) :  o,n = wnote_norm(x); return (o, n, (2**o) * WNFF[n])

def wnote_to_next_onf (wn):
    o,n = wnote_norm(x)
    ix = WNOTE.index(n)
    next_ix = ix + 1
    next_o = n + nix // len(WNOTE)
    next_n = WNOTE[ (ix+1) % len(WNOTE)] 
    (next_o, next_n, (2**next_o) * WNFF[next_n])

def wnote_play (wnotes=[list('FaFd')], base=220, speed=0.3, verbose=False):
    chord= [  base*wnote_to_onf(wn)[-1] for wn in wnotes ]
    _player.play_wave(_synthesizer.generate_chord(chord, speed))


'''

In [50]: zs = [  [ x for x in re.split( r"(..)", x)  if len(x)>0]   for x in '1b 1b 1a 1G 1e 1F0a0F0d'.split(" ")]
In [64]: zs = [  [ x for x in re.split( r"(..)", x)  if len(x)>0]   for x in '1b 1b 1a 1a 1G 1G 1e 1e 1F0a0F0d 1F0a0F0d 1F0a0F0d 1F0a0F0d 1F
    ...:  1F 1F 1F 1b 1b 1b 1b 1a 1a 1a 1a 1G0b0G0e 1G0b0G0e 1G0b0G0e 1G0b0G0e 1G 1G 1G 1G 1b 1b 1b 1b'.split(" ")]

In [51]: _=[wnote_play(x) for x in zs]

Astromania - Coffin Dance https://pianoletternotes.blogspot.com/2020/04/coffin-dance-meme.html?m=1
RH:5|--------------C-----------|
RH:4|b-a-G-e-F---F---b---a---G-|
LH:3|--------a---------------b-|
LH:3|--------F---------------G-|
LH:3|--------d---------------e-|

RH:5|--------------------a-G-a-|
RH:4|--G-G-b---a-G-F---F-------|
LH:3|--------------a-----------|
LH:3|--------------F-----------|
LH:3|--------------C-----------|

RH:5|G-a-------a-G-a-G-a-------|
RH:4|----F---F-----------F---F-|
LH:3|----a---------------a-----|
LH:3|----F---------------F-----|
LH:3|----C---------------d-----|

RH:5|C-------------------------|
RH:4|--b---a---G---G-G-b---a-G-|:
LH:3|----------b---------------|
LH:3|----------G---------------|
LH:3|----------e---------------|

RH:5|------a-G-a-G-a-------a-G-|
RH:4|F---F-----------F---F-----|
LH:3|a---------------a---------|
LH:3|F---------------F---------|
LH:3|C---------------C---------|

RH:5|a-G-a---------------------|

srgmpdn
cdefgab



'''


def play_note (note='s0', octave=0, base=220, speed=0.3, verbose=False):
    base = base*NOTES[note]*(2**octave)
    chord= [ base*(1+r/10)  for r in range( 0,1) ]
    _player.play_wave(_synthesizer.generate_chord(chord, speed))


#================================================================
# Given a string of notes and a mk returns a dataframe where each row
#  - represents has note,octave, duration, freq mutiplier and some debug info
#  - for s,,, patterns the , are treated as duration extenders
#  - the sss patterns are treated as repeats 
#  -  when note is repeated it beomes two notes - the note for 85% time and next_note for 15% time
# 
# Note Notation is $octave$note where
#  - $octave is optional , it optionally has one of +- , followed by digits
#    $octave represents the power of 2 by which the $note is scaled
#  - $note is one of srgmpdn
#  - SRGPMDN are short from of 1s 1r so on
#
def song_to_notes_df (song = 'spSSps', mk=29, clip_on_repeat=0.85 ):
    # convert S P to 1s 1r ..
    song = re.sub('([SRGMPDN])', lambda x: '1'+x[0].lower(),song)  

    # split the song into $octave$note strings  ignore spaces and non-note like things
    zz = [ x for x in re.split(r'(([+-]?\d+)?.)', song) if x and len(x) and  re.match('^.*?[srgmpdn,]$',x) ]

    # if note have no octave , assuime base ocatve => plain s becomes 0s
    zz1 = [  '0'+x if len(x) == 1 else x for x in zz]

    # add + for octave without explicit sign 
    zz2 = [  '+'+x if x[0] in '0123456789' else x for x in zz1]

    # split +1s to ( '+1', 's') from 
    zz3 = [  [ x2 for x2 in re.split('([+-]\d+)(.)',x) if len(x2)] for x in zz2]

    # pad a dummy note at the beginning of tuple note list
    zz3 = [(0, '_z')] + zz3

    # provision an ans with a dummy first entry - lets call the note array
    ans = [ ('_z') ]

    # transform the tuple note list to an note array like [ note, octave, duration_factor, freq_factor, debug info]
    # handles extended s,, and repeat sss note patterns
    for i, e in enumerate( zz3[1:] )  :
        prev_e = zz3[i]
        octave = int(e[0])
        note = e[1]
        note_extends = note == ','
        note_repeats = not note_extends  and note == prev_e[1]

        if ( note_extends ) :
            octave = ans[-1][1]
            note = ans[-1][0][0]

        mk_note = STANAS_DF.loc[mk-1,note]
        clip =  clip_on_repeat if note_repeats else 1
        freq = NOTES[mk_note]*(2**octave)
        elem = [ mk_note, octave, clip, freq, mk, note, note_repeats, note_extends ]
        ans.append(elem)
       
        if note_repeats :
            note_index = SARGAM.index(note)
            octave = octave + (note_index+1) // len(SARGAM)
            note_index = (note_index+1) % len(SARGAM)
            note = SARGAM[note_index]
            mk_note = STANAS_DF.loc[mk-1, note]
            clip = 1 - clip_on_repeat
            freq = NOTES[mk_note]*(2**octave)
            elem = [ mk_note, octave, clip, freq, mk, note, note_repeats, note_extends ]
            ans.append(elem)

    # make data frame of the note array ignoreing the first dummy entry
    ans_df = pd.DataFrame ( ans[1:], columns= [ 'note', 'octave' , 'duration', 'freq', '_mk', '_note' , '_repeats', '_extends' ] )

    return ans_df

def play_note_row (x, base=220, speed=0.3, verbose=False) :
    if verbose :
        try:
            display(pd.DataFrame(x).T.round({'freq':3}) )
        except:
            print(pd.DataFrame(x).T.round({'freq':3}) )
    play_note(x.note, int(x.octave), speed =speed*x.duration)

def play_song_df(song_df, mk=15, base=220, speed=0.3, jitter_speed=0, verbose=False):
    prec = pd.get_option("display.precision")
    pd.set_option("display.precision", 2)
    song_df.duration = [s + ((random.randrange(-jitter_speed,jitter_speed)/1000) if jitter_speed>0 else 0 ) for s in song_df.duration]
    _ = song_df.apply ( lambda x : play_note_row(x, base=base, speed=speed, verbose=verbose) , axis=1 )
    pd.set_option("display.precision", prec)
    time.sleep(2)

def play_song(song= 'spSSps', mk=15, base=220, speed=0.3, jitter_speed=0, verbose=False):
    song_df = song_to_notes_df(song)
    play_song_df(song_df, mk, base, speed, jitter_speed, verbose)

#================================================================
SONGS = [
    [ # geetham 2
        'kundagowra'  
        ,15
        , ''' 
            dp mgrs rm pdmp
            dR RSdp dp mgrs
            s, r,r, dp mgrs
            sr m,gr sr grs,

            dp mgrs rm pdmp
            dR RSdp dp mgrs
            s, r,r, dp mgrs
            sr m,gr sr grs,

            dp mgrs rm pdmp
            dR RSdp dp mgrs
            s, r,r, dp mgrs
            sr m,gr sr grs,
            '''
    ],

    [ # geetham 3
        'kereya'  
        ,15
        , ''' 
            dSS dp mp ddp mm p,
            ddS dp mp ddp mg rs
            srr sr sr ddp mg rs
            dpd S, dp ddp mg rs
            srr sr sr ddp mg rs

            dSS dp mp ddp mm p,
            ddS dp mp ddp mg rs
            srr sr sr ddp mg rs
            dpd S, dp ddp mg rs
            srr sr sr ddp mg rs
            
            '''
    ],

    [ # geetham 5
        'aanalekara'
        ,29
        ,'''
            RMR RS dS SSS dp mp
            ddS d, dp pmr dd dp
            ppp dd dp ppp mp dp
            pmr sr sr pmp sr sr
            ppd pp mr rsr m, m,

            dpd S, S, RRS dp mp
            ddS d, dp pmr dd dp
            p,p dd dp p,p mp dp
            pmr sr sr pmp sr sr
            ppd pp mr rsr mm mm

            dpd S, S,
            '''
    ],

    [ # varnam 2
        'ninnukori'
        ,28
        ,'''
            g,g, r,,, ssrr ggrr
            srgr srsd srgp grsr

            gpgg rsrg rrs-1d srgr
            gpgp dpdS ddpg dpgr

            g,g, p,,, ggpp ddp,
            dSdd pgdp dgdp grsr
            
            ggpp dpdS dSRS GR.S
            dSRS ,dpd Sd,p grsr

            g,rg rsr, srsg rgsr
            s-1dsr grgp gpd, p,,,

            gpdp dSRS R,GS ,Rd,
            Sp,d SRGS ,dp, grsr
            
            g,g, r,,, ssrr ggrr
            s,,, ,,,, s,,, ,,,,

            g,g, g,,, rgpg p,p,
            ggdd p,gd dpgp grsr

            g,,, r,s, r,,, d,,,
            r,d, s,,, r,,, g,r,
            
            g,g, g,,, rgpg p,p,
            ggdd p,gd dpgp grsr
            
            g,gr grsr g,g-1p -1d-1dsr
            g,gg dpgr g,gS dpgr
            
            g,g, g,,, rgpg p,p,
            ggdd p,gd dpgp grsr
            
            p,dd p,gr s,rg r,s-1d
            s,rg p.d, SS,d p,gr
            
            g,g, g,,, rgpg p,p,
            ggdd p,gd dpgp grsr

            S,RG RSRS dSdp grsr
            s,,, ,,ss rrgg ppdd

            SRGR GRdS RSRS pdSd
            Sdgp dpdp RSdp grsr
            
            g,g, g,,, rgpg p,p,
            ggdd p,gd dpgp grsr
            
            g,g, r,,, s,,, ,,,,
            '''
    ],
]
SONG_COLS = [ 'name', 'mk', 'song' ]
SONGS_DF=pd.DataFrame (SONGS, columns=SONG_COLS)

#==============================

def do_improvise(speed=.2, jitter_speed=50) :
    _ = SONGS_DF.apply ( lambda x: play_song( ''.join(random.choices(list(x.song),k=1*len(x.song))), mk=x.mk, speed=.2, jitter_speed=jitter_speed ) , axis=1)
    _ = SONGS_DF.apply ( lambda x: play_song( ''.join(random.sample(list(x.song),len(x.song))), mk=x.mk, speed=.2, jitter_speed=jitter_speed ) , axis=1)

def do_play_all_songs() :
    _ = SONGS_DF.apply ( lambda x: play_song( x.song, mk=x.mk, speed=.4 ) , axis=1)

def do_jittered_play_all_songs() :
    _ = SONGS_DF.apply ( lambda x: play_song( x.song, mk=x.mk, speed=.4 , jitter_speed=120) , axis=1)

def do_play_named_songs ( names ) :
    filt = [pd.Series([x2 in x for x2 in names]).any() for x in  SONGS_DF.name]
    print(SONGS_DF[ filt ].name)
    song_df = SONGS_DF[ filt ]
    _ = song_df.apply ( lambda x: play_song( x.song, mk=x.mk, speed=.3 ) , axis=1)


def do_chamattu_play (verbose=False) :
    #print ("29 स रे ग म प द नी स")
    #play_song('srgmpdnS', mk=29, speed=0.4, verbose=verbose)
    #play_song('Sndpmgrs', mk=29, speed=0.4, verbose=verbose)
    #print ("===================")

    print ("15 Kereya")
    play_song(SONGS[1][2], mk=15, speed=0.4, verbose=verbose)
    print ("===================")

    print ("29 Ānalekara")
    play_song(SONGS[2][2], mk=29, speed=0.4, verbose=verbose)
    print ("===================")

    print ("15 Kundagowra")
    play_song(SONGS[0][2], mk=15, speed=0.4, verbose=verbose)
    print ("===================")

#%%
if __name__ == '__main__' :
    time.sleep(2)  # to start recording utility
    #do_play_all_songs()
    #do_jittered_play_all_songs()
    #do_improvise()
    do_play_named_songs(['kereya', 'ninnu'])
