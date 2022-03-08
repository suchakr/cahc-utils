#%%
from urllib.request import urlopen
from urllib.parse import quote
from lxml import html
from glob import glob
import re
import pathlib
import os
import time
#%%

M = {}
for  s,e in zip(list("१२३४५६७८९०"), list("1234567890")) :
  M[s] , M[e] = e,s

def htmlof(url) :
  page = urlopen(url)
  html_bytes = page.read()
  html_str = html_bytes.decode("utf-8")
  return html_str


#%%
# for mandala, suktas in [ (8,3) ,(9,4), (10,5) ]:
SCRAPED_RAMAYANA = './~scraped-ramayana'

KANDA_SARGA_COUNT = [
  (1,77),
  (2,119),  
  (3,75),  
  (4,67),  
  (5,68), 
  (6,128) 
]

def scrape_iitk_for_ramayana () :
  pathlib.Path(SCRAPED_RAMAYANA).mkdir(parents=True, exist_ok=True) 
  start_time = time.time()
  for kanda, sargas in KANDA_SARGA_COUNT:
    for sarga in range(1, sargas+1) :
      fn = f'{SCRAPED_RAMAYANA}/VR-%02d-%03d.html' % (kanda, sarga )
      if os.path.exists(fn) : 
        print('Skipping existing file: ' + fn)
        continue

      print(f'Fetching file {fn}  - {time.time()-start_time :.2f}')
      # suktam = ''.join([ M[x] for x in str(sarga)])
      # mandalam = ''.join([ M[x] for x in str(kanda)])
      # path = quote(f'ऋग्वेदः_सूक्तं_{mandalam}.{suktam}')
      # url =  f'https://sa.m.wikisource.org/wiki/{path}'
      url = f'https://www.valmiki.iitk.ac.in/sloka?field_kanda_tid={kanda}&language=dv&field_sarga_value={sarga}'
      html_str = htmlof(url)
      with open(fn, 'w') as fh:
        fh.write(html_str)

scrape_iitk_for_ramayana()

#%%
def scrape_text():
  for filename in sorted(glob(f"{SCRAPED_RAMAYANA}/*06*10.html")) :
    ans = []
    with open(filename, 'r') as f:
      tree = html.fromstring(f.read())
      xpaths = [
        "//div[contains(@class,'field')]", "//div" , "//div",
         "//div[starts-with(@class,'views-field views-field-body')]",
         "//div[starts-with(@class,'views-field views-field-field-htetrans')]//div",
         "//div[starts-with(@class,'views-field views-field-field-explanation')]//div",
      ]
      body = tree.xpath(xpaths[0])
      htetrans = tree.xpath(xpaths[1])
      explanation = tree.xpath(xpaths[2])
      print( len(body), len(htetrans), len(explanation))
      for sloka in range(len(body)) :
        ans.append ( "\n\n".join([
          body[sloka].text_content(),
          # htetrans[sloka].text_content() , 
          # explanation[sloka].text_content(),
          "========================="
        ])
        )
    print(ans)
    with open(filename.replace('.html', '.txt'), 'w') as fh:
      if (len(ans) > 0) :
        fh.write('\n'.join(ans))
    print(filename)

scrape_text()

rm #%%

#%%
scrape_iitk_for_ramayana()
# scrape_by_class_and_nested_text()

#%%