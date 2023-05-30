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
fn = './scraped/vishnu-purana-scrape.txt'

if  os.path.exists(fn) :
    base = "https://sa.wikisource.org"
    root_url =  base + quote("/wiki/विष्णुपुराणम्")
    root_str = htmlof(root_url)
    tree = html.fromstring(root_str)
    amshas = tree.xpath('//*[@id="mw-content-text"]/*/ul/*/a/text()')
    hrefs = tree.xpath('//*[@id="mw-content-text"]/*/ul/*/a/@href')
    # print(tree.xpath('//a/@href'))
    acc = []
    dict(zip(amshas,hrefs))
    for amsha_cnt, amsha, href in zip(range(1,len(amshas)+1), amshas,hrefs) :
        url = base + href
        str = htmlof(url)
        tree = html.fromstring(str) 
        adhyayas = tree.xpath('//*[@id="mw-content-text"]/*/ul/*/a/text()')
        adhyaya_hrefs = tree.xpath('//*[@id="mw-content-text"]/*/ul/*/a/@href')
        print(amsha, adhyayas)
        # print(adhyaya_hrefs)
        for adhyaya_cnt, adhyaya, adhyaya_href in zip( range(1,len(adhyayas)+1) , adhyayas, adhyaya_hrefs) :
            url = base + adhyaya_href
            str = htmlof(url)
            tree = html.fromstring(str)
            # suktas = tree.xpath('//*[@id="mw-content-text"]/*/ul/*/a/text()')
            suktas = tree.xpath('//*[@class="poem"]/*/text()')
            ttl = f'## {amsha} {adhyaya} {amsha_cnt}.{adhyaya_cnt:02d}'
            acc.append(ttl + "\n")
            acc.extend(suktas)
            print(f'{ttl} {len(suktas)}')

    print( "Writing to file: " + fn)
    with open(fn, 'w') as fh:
        fh.write("".join(acc))

# %%
