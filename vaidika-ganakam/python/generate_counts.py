#@title MTR - countMantras(mantra)
import sys

debuglevel = 0

def warn(*args, **kwargs): 
  print(*args, file=sys.stderr, **kwargs)

debuglevel = 0
if (len(sys.argv) > 1) and (sys.argv[1].isnumeric()):
  debuglevel = int(sys.argv[1])
  
sv = ['अ', 'इ', 'उ', 'ऋ' ]
lv = ['आ', 'ई', 'ऊ', 'ए', 'ऐ', 'ओ','औ' ]
sm = ['कि', 'कु', 'कृ', 'कॢ']
lm = ['का', 'की', 'कू', 'के', 'कै', 'को', 'कौ', 'कं', 'तॄ']
visarga = ['कः']
aconst = ['क', 'ख', 'ग', 'घ', 'ङ',
          'च', 'छ', 'ज', 'झ', 'ञ',
          'ट', 'ठ', 'ड', 'ढ', 'ण',
          'त', 'थ', 'द', 'ध', 'न',
          'प', 'फ', 'ब', 'भ', 'म',
          'य', 'र', 'ल', 'ळ', 'व', 'श', 'ष', 'स', 'ह', 'ङ' ]
lp = ['॒']
hp = ['॑']
halant = ['्']
danda = ['।','॥']
numerals = ['१','२','३','४','५','६','७','८','९']
wsp = [' ', '\t', '\n','ऽ', '-', u"\u200D", '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
ignoredMatras = ['कँ']
transformToAnusvara = ['न्','ङ्','ञ्','ण्','म्']
ksha = 'क्ष'
sample = "अ॒ग्निमी॑ळे पु॒रोहि॑तं य॒ज्ञस्य॑ दे॒वमृ॒त्विज॑म् ।"
tokenmap = {}
for c in sv:
  tokenmap[ord(c[-1])] = "sv"
for c in lv:
  tokenmap[ord(c[-1])] = "lv"
for c in sm:
  tokenmap[ord(c[-1])] = "sm"
for c in lm:
  tokenmap[ord(c[-1])] = "lm"
for c in aconst:
  tokenmap[ord(c[-1])] = "aconst"
for c in lp:
  tokenmap[ord(c[-1])] = "lp"
for c in hp:
  tokenmap[ord(c[-1])] = "hp"
for c in danda:
  tokenmap[ord(c[-1])] = "danda"
for c in wsp:
  tokenmap[ord(c[-1])] = "wsp"
for c in halant:
  tokenmap[ord(c[-1])] = "halant"
for i in range(len(numerals)):
  tokenmap[ord(numerals[i])] = str(i + 1)
for c in ignoredMatras:
  tokenmap[ord(c[-1])] = "ignored"
for c in visarga:
  tokenmap[ord(c[-1])] = "visarga"

few_rv_mantras ='''
अ॒ग्निमी॑ळे पु॒रोहि॑तं य॒ज्ञस्य॑ दे॒वमृ॒त्विज॑म् । होता॑रं रत्न॒धात॑मम् ॥
अ॒ग्निः पूर्वे॑भि॒रृषि॑भि॒रीड्यो॒ नूत॑नैरु॒त । स दे॒वाँ एह व॑क्षति ॥
अ॒ग्निना॑ र॒यिम॑श्नव॒त्पोष॑मे॒व दि॒वेदि॑वे । य॒शसं॑ वी॒रव॑त्तमम् ॥ 
अग्ने॒ यं य॒ज्ञम॑ध्व॒रं वि॒श्वत॑ः परि॒भूरसि॑ । स इद्दे॒वेषु॑ गच्छति ॥
अ॒ग्निर्होता॑ क॒विक्र॑तुः स॒त्यश्चि॒त्रश्र॑वस्तमः । दे॒वो दे॒वेभि॒रा ग॑मत् ॥ 
यद॒ङ्ग दा॒शुषे॒ त्वमग्ने॑ भ॒द्रं क॑रि॒ष्यसि॑ । तवेत्तत्स॒त्यम॑ङ्गिरः ॥
उप॑ त्वाग्ने दि॒वेदि॑वे॒ दोषा॑वस्तर्धि॒या व॒यम् । नमो॒ भर॑न्त॒ एम॑सि ॥ 
राज॑न्तमध्व॒राणां॑ गो॒पामृ॒तस्य॒ दीदि॑विम् । वर्ध॑मानं॒ स्वे दमे॑ ॥
स न॑ः पि॒तेव॑ सू॒नवेऽग्ने॑ सूपाय॒नो भ॑व । सच॑स्वा नः स्व॒स्तये॑ ॥ 
वाय॒वा या॑हि दर्शते॒मे सोमा॒ अरं॑कृताः । तेषां॑ पाहि श्रु॒धी हव॑म् ॥
वाय॑ उ॒क्थेभि॑र्जरन्ते॒ त्वामच्छा॑ जरि॒तार॑ः । सु॒तसो॑मा अह॒र्विद॑ः ॥ 
वायो॒ तव॑ प्रपृञ्च॒ती धेना॑ जिगाति दा॒शुषे॑ । उ॒रू॒ची सोम॑पीतये ॥
इन्द्र॑वायू इ॒मे सु॒ता उप॒ प्रयो॑भि॒रा ग॑तम् । इन्द॑वो वामु॒शन्ति॒ हि ॥ 
वाय॒विन्द्र॑श्च चेतथः सु॒तानां॑ वाजिनीवसू । तावा या॑त॒मुप॑ द्र॒वत् ॥
वाय॒विन्द्र॑श्च सुन्व॒त आ या॑त॒मुप॑ निष्कृ॒तम् । म॒क्ष्वि१॒॑त्था धि॒या न॑रा ॥ 
मि॒त्रं हु॑वे पू॒तद॑क्षं॒ वरु॑णं च रि॒शाद॑सम् । धियं॑ घृ॒ताचीं॒ साध॑न्ता ॥
ऋ॒तेन॑ मित्रावरुणावृतावृधावृतस्पृशा । क्रतुं॑ बृ॒हन्त॑माशाथे ॥ 
क॒वी नो॑ मि॒त्रावरु॑णा तुविजा॒ता उ॑रु॒क्षया॑ । दक्षं॑ दधाते अ॒पस॑म् ॥
अश्वि॑ना॒ यज्व॑री॒रिषो॒ द्रव॑त्पाणी॒ शुभ॑स्पती । पुरु॑भुजा चन॒स्यत॑म् ॥ 
अश्वि॑ना॒ पुरु॑दंससा॒ नरा॒ शवी॑रया धि॒या । धिष्ण्या॒ वन॑तं॒ गिर॑ः ॥
अ॒श्व॒युर्ग॒व्यू र॑थ॒युर्व॑सू॒युरिंद्र॒ इद्रा॒यः क्ष॑यति प्रयं॒ता ॥
''';

def warnList(lst, items=10):
  lines = []
  for i in range(0, len(lst), items):
    chunk = lst[i:i + items]
    line = ", ".join("{!r}".format(x) for x in chunk)
    lines.append(line)
  return "[" + ",\n".join(lines) + "]"

def mapToToken(curr, n):
  if debuglevel > 2:
    warn("mapping", curr, hex(ord(curr)), n, hex(ord(n)), end = ": ")
  if (not ord(curr) in tokenmap):
    return ["err"]
  if debuglevel > 3:
    warn(tokenmap[ord(curr)], tokenmap[ord(n)])
  if (tokenmap[ord(curr)] != "aconst") or (not ord(n) in tokenmap):
    return [tokenmap[ord(curr)]]
  if (tokenmap[ord(n)] == "halant"):
    return ["const"]
  if ((tokenmap[ord(n)] == "sm") or (tokenmap[ord(n)] == "lm")):
    return ["const", tokenmap[ord(n)]]
  return ["aconst"] 

def firstPass(mantra):
  mantra = mantra + "    "
  mappedTokens = []
  i = 0
  while (i < (len(mantra)-1)):
    if debuglevel > 2:
      warn(i, hex(ord(mantra[i])))
      warn (mantra[i], mantra[i+1], end=' '), 
    for anusvara in transformToAnusvara:
      if (len(mappedTokens) > 1 and mantra[i] == anusvara[0] and mantra[i+1] == anusvara[1] and mappedTokens[-1] != "const"):
        mappedTokens.append("lm")
        i = i + 2
    if (len(mappedTokens) > 1 and mappedTokens[-1] == "visarga" and mantra[i] == ksha[0] and mantra[i+1] == ksha[1] and mantra[i+2] == ksha[2]):
      mappedTokens.append("ksh")
      i = i + 3
      lookahead = mapToToken(mantra[i], mantra[i+1])
      if (lookahead != "halant" and lookahead != "sm" and lookahead != "lm"):
        # For the implied short a
        mappedTokens.append("sm")
    mappedToken = mapToToken(mantra[i], mantra[i+1])
    if (mappedToken[0] == "const"):
      mappedTokens.extend(mappedToken)
      i = i + 2
    elif ((mappedToken[0] == "err") or (mappedToken[0] == "halant")):
      warn (mantra[i], mantra[i+1])
      mappedTokens.extend(mappedToken)
      i = i + 1
    elif (mappedToken[0] in ["lp", "wsp"]):
      # ignore these
      i = i + 1
    elif (mappedToken[0] == "aconst"):
      mappedTokens.append("const")
      mappedTokens.append("sm")
      i = i + 1    
    else:
      mappedTokens.extend(mappedToken)
      # warn(mappedToken)
      i = i + 1
  return mappedTokens

def computeDurations(mappedTokens, verse):
  j = 0
  mappedTokens.append("wsp")
  mappedTokens.append("wsp")
  mappedTokens.append("wsp")
  mappedTokens.append("wsp")
  mappedTokens.append("wsp")
  durations = []
  while (j < len(mappedTokens) - 5):
    oldj = j
    if debuglevel > 1:
      warn ("\t", j, mappedTokens[j], mappedTokens[j+1], mappedTokens[j+2], mappedTokens[j+3])
    if (mappedTokens[j] == "hp" or mappedTokens[j] == "wsp"):
      j = j + 1
    elif (mappedTokens[j] == "sv"):
      if (mappedTokens[j+1] == "const" and mappedTokens[j+2] == "const"):
        durations.append(2)
        j = j + 2
      elif (mappedTokens[j+1] == "lm"):
        durations.append(2)
        j = j + 2
      elif (mappedTokens[j+1] == "hp" and mappedTokens[j+2] == "lm"):
        durations.append(2)
        j = j + 3
      else:
        durations.append(1)
        j = j + 1
    elif (mappedTokens[j] == "lv"):
      if (mappedTokens[j+1] == "hp"):
        durations.append(4)
        j = j + 2
      elif (mappedTokens[j+1] == "lm"):
        durations.append(2)
        j = j + 2
      else:
        durations.append(2)
        j = j + 1
    elif (mappedTokens[j] == "const"):
      if (mappedTokens[j+1] == "const"):
        j = j + 1
      elif (mappedTokens[j+1] == "danda"):
        j = j + 1
        durations.append(1)
      else:
        smfound = 0
        lmfound = 0
        hpfound = 0
        visargafound = 0
        k = j + 1
        while ((mappedTokens[k] == "sm") or (mappedTokens[k] == "lm")
               or (mappedTokens[k] == "hp") or (mappedTokens[k] == "visarga")):
          if (mappedTokens[k] == "sm"):
            smfound = smfound + 1
          elif (mappedTokens[k] == "lm"):
            lmfound = lmfound + 1
          elif (mappedTokens[k] == "visarga"):
            visargafound = visargafound + 1
          else:
            hpfound = hpfound + 1
          k = k + 1
        j = j + 1 + lmfound + hpfound + smfound + visargafound
        if debuglevel > 2:
          warn(mappedTokens[j], lmfound, hpfound, smfound, visargafound)
        if (lmfound > 0 and hpfound > 0):
          durations.append(4)
          #elif (lmfound > 0 and mappedTokens[j] == "const" and mappedTokens[j+1] == "const"):
          #  durations.append(2.5)
          #  j = j + 1
        elif (lmfound > 0):
          durations.append(2)
        elif (smfound > 0 and mappedTokens[j] == "const" and mappedTokens[j+1] == "const"):
          durations.append(2)
          j = j + 1
        elif (smfound > 0 and visargafound > 0 and hpfound > 0 and mappedTokens[j] == "danda"):
          durations.append(3)
        elif (smfound > 0 and hpfound > 0 and mappedTokens[j] == "danda"):
          durations.append(2)
        elif (visargafound > 0):
          if mappedTokens[j] == "ksh":
            # Hack! : Replace ksh with a consonant so that the rest of the mantra does not need to check for ksh explicitly
            mappedTokens[j] = "const"
            durations.append(2.5)
          else:
            durations.append(2)
        elif (smfound > 0):
          durations.append(1)
        elif (mappedTokens[j+1] == "danda"):
          j = j + 1
        else:
          warn(j, mappedTokens[j], mappedTokens[j+1], " unmapped", verse)
          raise Exception("Unmapped " + verse)
          j = j + 1
    elif (mappedTokens[j] == "danda"):
      durations.append(2)
      durations.append("|")
      j = j + 1
    elif (mappedTokens[j] == "ignored"):
      j = j + 1
    elif (mappedTokens[j].isnumeric()):
      durations.append(int(mappedTokens[j]) + 1)
      j = j + 1
    else:
      warn(j, mappedTokens[j], " unknown", verse)
      raise Exception("unknown " + verse)
      j = j + 1
    if debuglevel > 1 and len(durations) > 0:
      warn (durations[-1], "tokens consumed", j - oldj)
  return durations    

# warn(sample)
# firstPassTokens = firstPass(sample)
# warn(warnList(firstPassTokens, 10))

#for i in range(len(firstPassTokens)):
#  if (firstPassTokens[i] == "err" or firstPassTokens[i] == "halant"):
#    warn(i, sample[i-10:i+10])

# warn(warnList(firstPassTokens, 5))
# warn(warnList(computeDurations(firstPassTokens, sample), 20))

def splitStringAtViramas(input):
  returnValue = input.split('॥')
  return [x + '॥' for x in returnValue if x != ""]

def countMatrasVerbose(input_mantra = few_rv_mantras):
  for verse in splitStringAtViramas(input_mantra):
    warn(verse)
    if debuglevel > 0:
      warn(warnList([hex(ord(x)) for x in verse], 10))
      warn()
    fpt = firstPass(verse)
    if debuglevel > 0:
      warn(warnList(fpt, 10))
    warn(warnList(computeDurations(fpt, verse), 30))
    warn()
    
def countMatras(input_mantra = few_rv_mantras):
  ans = []
  try:
    for verse in splitStringAtViramas(input_mantra):
      fpt = firstPass(verse)
      fpt = [x for x in fpt if x != "err"]
      ans.append(computeDurations(fpt, verse))
    return ans
  except:
    return [[-1]]

def summmarizeMatras( aan ):
  duration = 0 
  count = 0
  for an in aan :
    for n in an:
      if ( type(n) == type(1)) :
        duration = duration + n
        count = count +1
  return ( count, duration )

