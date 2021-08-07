#%%
from urllib.request import urlopen
from urllib.parse import quote
from lxml import html
from glob import glob
import re
import pathlib
import os
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
SCRAPED_RV = './~scraped-rv'
SCRAPED_BHASHYA = './~scraped-bhashya'
SCRAPED_POEM_AND_BHASHYA = './scraped'

MANDALA_SUKTA_COUNT = [
  # (1,191) ,(2,43),  (3,62),  (4,58),  (5,87), 
  (6,75) , (7,104), (8,103) ,(9,114), (10,191) 
]

def scrape_wikisource_for_rv () :
  pathlib.Path(SCRAPED_RV).mkdir(parents=True, exist_ok=True) 
  for mandala, suktas in MANDALA_SUKTA_COUNT:
    for sukta in range(1, suktas+1) :
      fn = f'{SCRAPED_RV}/RV-%02d-%03d.html' % (mandala, sukta )
      if os.path.exists(fn) : 
        print('Skipping existing file: ' + fn)
        continue

      print(f'Fetching file {fn}')
      suktam = ''.join([ M[x] for x in str(sukta)])
      mandalam = ''.join([ M[x] for x in str(mandala)])
      path = quote(f'ऋग्वेदः_सूक्तं_{mandalam}.{suktam}')
      url =  f'https://sa.m.wikisource.org/wiki/{path}'
      html_str = htmlof(url)
      with open(fn, 'w') as fh:
        fh.write(html_str)

# scrape_wikisource_for_rv()

#%%
def scrape_by_text_and_marker():
  pathlib.Path(SCRAPED_BHASHYA).mkdir(parents=True, exist_ok=True) 
  cwd = os.getcwd()
  for filename in sorted(glob(f"{SCRAPED_RV}/*")) :
    # print(filename)
    with open(filename, 'r') as f:
      tree = html.fromstring(f.read())
      texts = tree.xpath('//text()')
      sb_start = False
      sb_end = False
      ans = []
      for x in texts :
        try :
          sb_start = sb_start or re.match("सायणभाष्यम्", x) 
          sb_end = sb_start and ( sb_end or re.match("सम्पाद्यताम्",x) or re.match("मण्डल",x))
          if ( sb_start and not sb_end) :
            ans.append(x)
            # print(x)
        except Exception as e:
          # print(e)
          # print(x)
          pass

      sayana_txt = re.sub(f'{SCRAPED_RV}', f'{SCRAPED_BHASHYA}', filename)
      sayana_txt = re.sub(".html", ".txt", sayana_txt)
      print (sayana_txt, len(ans) , '**********' if len(ans) < 10 else '')
      with open(sayana_txt, 'w') as fh:
        fh.write("\n".join(ans))

# scrape_by_text_and_marker()

#%%
def scrape_by_class_and_nested_text() :
  pathlib.Path(SCRAPED_POEM_AND_BHASHYA).mkdir(parents=True, exist_ok=True) 
  cwd = os.getcwd()
  ms_bhashyas = []
  for filename in sorted(glob(f"{SCRAPED_RV}/*")) :
    ms_mark = re.sub(f'{SCRAPED_RV}', '', filename)
    ms_mark = re.sub(".html", "", ms_mark )
    # print(filename)
    with open(filename, 'r') as f:
      tree = html.fromstring(f.read())
      # texts = tree.xpath("//*[@class='poem' or @class='mw-collapsible-content']//text()")
      suktas = []
      try:
        texts = tree.xpath("//*[@class='poem']//text()")
        for x in texts :
          try :
            suktas.append(x)
          except Exception as e:
            # print(e) # print(x)
            pass
      except Exception as e:
        print (['suktas', ms_mark, e])
        pass


      bhashyas = []
      try :
        texts = tree.xpath("//*[@class='mw-collapsible-content']//text()")
        for x in texts :
          try :
            bhashyas.append(x)
          except Exception as e:
            pass
      except Exception as e:
        print (['bhashyas', ms_mark, e])
        pass

      ms_bhashyas.append(f"## BEGIN {ms_mark} (\n")
      ms_bhashyas.append(f"# begin-sukta  {ms_mark} (\n")
      for t in suktas : ms_bhashyas.append(t)
      ms_bhashyas.append(f"# end-sukta    {ms_mark} )\n")
      ms_bhashyas.append(f"--------------------------------------------\n")
      ms_bhashyas.append(f"# begin-sayana-bhashya {ms_mark}(\n")
      for t in bhashyas : ms_bhashyas.append(t)
      ms_bhashyas.append(f"# end-sayana-bhashya {ms_mark}(\n")
      ms_bhashyas.append(f"## END  {ms_mark} )\n")
      ms_bhashyas.append(f"********************************************\n")
      ms_bhashyas.append(f"\n")
      # sayana_txt = re.sub(f'{SCRAPED_RV}', f'{SCRAPED_POEM_AND_BHASHYA}', filename)
      # sayana_txt = re.sub(".html", ".txt", sayana_txt )
      print (ms_mark, len(suktas) , 'ss===sss===ssss' if len(suktas) < 5 else '', len(ms_bhashyas))
      print (ms_mark, len(bhashyas) , 'bb===bbb===bbbb' if len(bhashyas) < 5 else '' , len(ms_bhashyas))
      print ('')

  rv_all = f'{SCRAPED_POEM_AND_BHASHYA}/rv-with-sayana-from-wiki-source.txt'
  with open(rv_all, 'w') as fh:
    fh.write("".join(ms_bhashyas))
  print (f'Done generating ${rv_all}')

scrape_by_class_and_nested_text()

#%%
scrape_wikisource_for_rv()
scrape_by_class_and_nested_text()

#%%