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

def get_anchors(href, hrefdb, starttime, level = 0) :
  if href in hrefdb : return
  if level > 10: return
  url = f'https://sa.wikisource.org{href}'
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
def save_list_to_file(l, filename):
  with open(filename, 'w') as f:
    for item in l:
      f.write(item + '\n')

# flatten an array of arrays
def flatten(l):
  return [item for sublist in l for item in sublist]

#%%
## Manually run this for each sk0

sk0 = "/wiki/स्कन्दपुराणम्"
sk1 = "/wiki/स्कन्दपुराणम्/प्रभासखण्डः"
sk2 = "/wiki/स्कन्दपुराणम्/खण्डः_८_(अम्बिकाखण्डः)"

hrefdb = {}
starttime = time()
for sk, cntr in zip ( [ sk0, sk1, sk2 ], range(3)) :
  get_anchors(sk, hrefdb, starttime=starttime)
  # [ h for h in hrefdb.keys() if re.match(".*\/अध्यायः_[१२३४५६७८९०]+",h)]
  print ([ h for h in hrefdb.keys() if re.match(".*\/[१२३४५६७८९०]+",h)])

  h2 = [ [ [k], 
    hrefdb[k][1].xpath(
      "//*[contains(@class,'poem') or contains(@class,'first') ]//text()"
      )] for k in hrefdb ]

  save_list_to_file( flatten(flatten(h2)) , f"~sp{cntr}.txt")
