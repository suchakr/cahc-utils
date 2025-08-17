#%%
## Utility ti scrape skandapurana from sa.wikisource.org - v v kludgy
from urllib.request import urlopen
from urllib.parse import quote, unquote, urlencode
from lxml import html
import re
from time import time

#%%
# sk0 =  "https://sa.wikisource.org/wiki/स्कन्दपुराणम्/खण्डः_१_(माहेश्वरखण्डः)"
def url_encode(s): return quote(s, safe='/:')
def url_decode(s): return unquote(s)

def get_anchors(href, hrefdb, starttime, level = 0) :
  if href in hrefdb : return
  if level > 10: return
  url = f'https://sa.wikisource.org{href}'
  print(" " * level, url)
  page = urlopen(url_encode(url))
  tree = html.fromstring(page.read())
  elems = [ (
    # a.xpath('./@href')
    unquote((a.xpath('./@href') + ['xxx'])[0])
    , unquote((a.xpath('./text()') + ['xxx'])[0])  
  ) for a in tree.xpath('//a') ]
  elems = [ (href,text) for href, text in elems if re.match("^\/wiki\/स्कन्दपुराणम्.*\/", href) ]
  hrefdb.update({ href : (len(elems), tree, page) })
  # num_adhyaya = len([ h for h in hrefdb.keys() if re.match(".*\/अध्यायः_[१२३४५६७८९०]+",h)])
  num_adhyaya = len([ h for h in hrefdb.keys() if re.match(".*\/[१२३४५६७८९०]+",h)])
  for href, text in elems:
    print("%02d %5d %5d %s %s" % (level , num_adhyaya ,  (time() - starttime),  " " * level, text))
    get_anchors(href, hrefdb, starttime, level +1)


#%%
# save text to a file
def save_text_to_file(text, filename):
  with open(filename, 'w') as f:
    f.write(text)

# save a list of strings to a file
def save_list_to_file(l, filename, remove_devnagari_numbers_in_parens=True):
  with open(filename, 'w') as f:
    # remove consecutive newlines
    l = [item for item in l if item.strip()]  # remove empty strings
    l = [item.strip() for item in l]  # strip whitespace
    l = list(dict.fromkeys(l))  # remove duplicates while preserving order
    # l = [item.replace('\n', ' ') for item in l]  # replace newlines with spaces
    # l = [item.replace('\r', '') for item in l]  # remove carriage returns
    # l = [item.replace('\t', ' ') for item in l]  # replace tabs with spaces
    # l = [item for item in l if item]  # remove empty strings again
    # l = [item.strip() for item in l]  # strip whitespace again
    # l = [item for item in l if item]  # remove empty strings again
    # l = [item.replace('  ', ' ') for item in l]  # replace double spaces with single space
    # l = [item for item in l if item]  # remove empty strings again
    l = [re.sub(r'॥\s*$', '॥\n', item) for item in l]  # add newline after each verse
    l = [re.sub(r'।।', '॥', item) for item in l]  # add newline after each verse
    # l = [item.replace('।', '।\n') for item in l]  # add newline after each sentence
    # l = [item.replace('॥\n\n', '॥\n') for item in l]  # remove double newlines after verse
    # l = [item.replace('।\n\n', '।\n') for item in l]  # remove double newlines after sentence
    # l = [item.replace('॥\n॥', '॥\n') for item in l]  # remove double newlines after verse
    # l = [item.replace('।\n।', '।\n') for item in l]  # remove double newlines after sentence
    # l = [item.replace('॥\n॥\n', '॥\n') for item in l]  # remove triple newlines after verse
    # l = [item.replace('।\n।\n', '।\n') for item in l]  # remove triple newlines after sentence
    if remove_devnagari_numbers_in_parens:
      l = [re.sub(r'\(\s*[१२३४५६७८९०]+\s*\)', '', item) for item in l]
    for item in l:
      f.write(item + '\n')

# flatten an array of arrays
def flatten(l):
  return [item for sublist in l for item in sublist]

#%%
## Manually run this for each sk0

# sk0 = "/wiki/स्कन्दपुराणम्"
# sk1 = "/wiki/स्कन्दपुराणम्/प्रभासखण्डः"
# sk2 = "/wiki/स्कन्दपुराणम्/खण्डः_८_(अम्बिकाखण्डः)"

# hrefdb = {}
# starttime = time()
# for sk, cntr in zip ( [ sk0, sk1, sk2 ], range(3)) :
#   get_anchors(sk, hrefdb, starttime=starttime)
#   # [ h for h in hrefdb.keys() if re.match(".*\/अध्यायः_[१२३४५६७८९०]+",h)]
#   print ([ h for h in hrefdb.keys() if re.match(".*\/[१२३४५६७८९०]+",h)])

#   h2 = [ [ [k], 
#     hrefdb[k][1].xpath(
#       "//*[contains(@class,'poem') or contains(@class,'first') ]//text()"
#       )] for k in hrefdb ]

#   save_list_to_file( flatten(flatten(h2)) , f"~sp{cntr}.txt")

#%%

## https://sa.wikisource.org/wiki/नैषधीयचरितम्%E2%80%8C/प्रथमः_सर्गः

# nc0 = "/wiki/नैषधीयचरितम्%E2%80%8C"
nc0 = "/wiki/नैषधीयचरितम्" + unquote("%E2%80%8C")
# nc1 = "/wiki/नैषधीयचरितम्%E2%80%8C/प्रथमः_सर्गः"
nc1 = nc0 + "/प्रथमः_सर्गः"
ncs = [
  "प्रथमः सर्गः",
  "द्वितीयः सर्गः",
  "तृतीयः सर्गः",
  "चतुर्थः सर्गः",
  "पञ्चमः सर्गः",
  "षष्ठः सर्गः",
  "सप्तमः सर्गः",
  "अष्टमः सर्गः",
  "नवमः सर्गः",
  "दशमः सर्गः",
  "एकादशः सर्गः",
  "द्वादशः सर्गः",
  "त्रयोदशः सर्गः",
  "चतुर्दशः सर्गः",
  "पञ्चदशः सर्गः",
  "षोडशः सर्गः",
  "सप्तदशः सर्गः",
  "अष्टादशः सर्गः",
  "एकोनविंश: सर्गः",
  "विंश: सर्गः",
  "एकविंश: सर्गः",
  "द्वाविंश: सर्गः",
]

ncs = [ nc0 + "/" + n for n in ncs ]

hrefdb = {}
starttime = time()
for nc, cntr in zip ( ncs, range(len(ncs) + 1)) :
  get_anchors(nc, hrefdb, starttime=starttime)
  # [ h for h in hrefdb.keys() if re.match(".*\/अध्यायः_[१२३४५६७८९०]+",h)]
  print ([ h for h in hrefdb.keys() if re.match(".*\/[१२३४५६७८९०]+",h)])

  h2 = [ [ [k], 
    hrefdb[k][1].xpath(
      "//*[contains(@class,'poem') or contains(@class,'first') ]//text()"
      )] for k in hrefdb ]

  save_list_to_file( flatten(flatten(h2)) , f"~nc{cntr:03}.txt")

# %%
# मधुरावियजम्

mv0 = "/wiki/पृष्ठम्:मथुराविजयम्.djvu"

def english_to_devanagari_numerals(text):
    english_numerals = "0123456789"
    devanagari_numerals = "०१२३४५६७८९"
    translation_table = str.maketrans(english_numerals, devanagari_numerals)
    return text.translate(translation_table)

mvs = [english_to_devanagari_numerals(str(x)) for x in range(33,78+1)]

# mvs = mvs[:10]  # for testing, limit to first 10

hrefdb = {}
starttime = time()
for mv, cntr in zip ( mvs, range(len(mvs) + 1)) :
  get_anchors(mv0 + "/" + mv, hrefdb, starttime=starttime)
  # [ h for h in hrefdb.keys() if re.match(".*\/अध्यायः_[१२३४५६७८९०]+",h)]
  print ([ h for h in hrefdb.keys() if re.match(".*\/[१२३४५६७८९०]+",h)])

  h2 = [ [ [k], 
    hrefdb[k][1].xpath(
      "//*[contains(@class,'poem') or contains(@class,'first') ]//text()"
      )] for k in hrefdb ]

  # save_list_to_file( flatten(flatten(h2)) , f"~mv{cntr:03}.txt")
  save_list_to_file( flatten(flatten(h2)) , f"~mv{999:03}.txt")
# %%

def do_scrape(work, root_url, chapters, center_tag=None, remove_devnagari_numbers_in_parens=False):
    hrefdb = {}
    starttime = time()
    for chapter, cntr in zip ( chapters, range(len(chapters) + 1)) :
      get_anchors(root_url + "/" + chapter, hrefdb, starttime=starttime)
      # [ h for h in hrefdb.keys() if re.match(".*\/अध्यायः_[१२३४५६७८९०]+",h)]
      print ([ h for h in hrefdb.keys() if re.match(".*\/[१२३४५६७८९०]+",h)])
      # print(f"Chapter {chapter} done, {len(hrefdb)} links found.")
    print(f"Total time taken: {time() - starttime} seconds")

    poems = [ [ [k], 
      hrefdb[k][1].xpath(
        "//*[contains(@class,'poem') or contains(@class,'first') ]//text()" if not center_tag else
        "//*[contains(@class,'poem') or contains(@class,'first') ]//center//text()"
        )] for k in hrefdb ]

    save_list_to_file( flatten(flatten(poems)) , f"~{work}~.txt", remove_devnagari_numbers_in_parens=remove_devnagari_numbers_in_parens)
#%%
mudrarakshasa = [
  "mudrarakshasa",
  "/wiki/मुद्राराक्षसम्",
  ["उपोद्घातः", "प्रथमोऽङ्कः", "द्वितीयोऽङ्कः", "तृतीयोऽङ्कः", "चतुर्थोऽङ्कः", "पञ्चमोऽङ्कः", "षष्ठोऽङ्कः", "सप्तमोऽङ्कः"],
]

do_scrape(*mudrarakshasa)
# %%
kumarasambhava_s =  [ 
  [ f"kumarasambhava_{ix+1:02}",
  "/wiki/कुमारसम्भवम्_-_मल्लिनाथः",
  [c]
  ] for ix, c in enumerate (["प्रथमः_सर्गः", "द्वितीयः_सर्गः", "तृतीयः_सर्गः", "चतुर्थः_सर्गः", "पञ्चमः_सर्गः", "षष्ठः_सर्गः", "सप्तमः_सर्गः", "अष्ठमः_सर्गः",
   "नवमः_सर्गः", "दशमः_सर्गः", "एकादशः_सर्गः", "द्वादशः_सर्गः", "त्रयोदशः_सर्गः", "चतुर्दशः_सर्गः", "पञ्चदशः_सर्गः", "षोडशः_सर्गः", "सप्तदशः_सर्गः", 
  #  "अष्टादशः_सर्गः",
   ])
]

for kumarasambhava_c in kumarasambhava_s:
  do_scrape(*kumarasambhava_c, center_tag=True, remove_devnagari_numbers_in_parens=True)




# %%
