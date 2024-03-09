#%%
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from lxml import html
from selenium.webdriver.support.ui import Select
import re
import os
import pandas as pd
import requests

#%%

driver = webdriver.Safari()
driver.get('https://insa.nic.in/UI/journaldetails.aspx?AID=Mw==')
sleep(1)
driver.maximize_window()
select_element = Select(driver.find_element(value='ContentPlaceHolder1_ddlvolumeDetails'))
options = select_element.options
opt_vals_map = { option.get_attribute('value') : option.text for option in options }
# print(opt_vals_map)


def get_issue_id(k, val) :
    _,yr, _,vol, _, iss = re.split( r"[\s\,]+", val)
    try :
        z=f'{int(yr):4d}_{int(vol):02d}_{int(iss):02d}'
    except :
        z=f'{int(yr):4d}_{int(vol):02d}_0{iss}'
    z= z.replace(r'and', '-')
    z= z.replace(r'to', '-')
    z= z.replace(r'&', '-')
    z = f'ijhs_{z}'
    return z

excnt = 0
for k in list(opt_vals_map.keys())[:] :
    try :
        issue_id = get_issue_id(k, opt_vals_map[k])
        html_file = f'./scraped/ijhs/html~/{issue_id}~.html'
        # print(f'Scraping {html_file}')
        # skip if html_file exists
        if os.path.exists(html_file) : 
            size_in_bytes = os.path.getsize(html_file)
            size_in_kb = size_in_bytes // (1024)
            if size_in_bytes > 1 :
                # print(f'Skipping. Already scraped {html_file} - {size_in_kb} KB')
                tree = html.parse(html_file)
                papers = [(a.get('href'), a.text, e.getnext().getnext().text 
                    ) for e in tree.xpath('//*[@class="question col-xs-11"]') for a in e.xpath('./a') ]
                if len(papers) > 0 :
                    # print(f'Skipping. Already scraped {html_file} - {size_in_kb} KB')
                    continue
                else :
                    print(f'No Papers - Rescraping {html_file} - {size_in_kb} KB  - no papers found in html file')
            else :
                print(f'Small File - Rescraping {html_file} - {size_in_kb} KB')

        driver.get('https://insa.nic.in/UI/journaldetails.aspx?AID=Mw==')
        sleep(1)
        select_element = Select(driver.find_element(value='ContentPlaceHolder1_ddlvolumeDetails'))
        # print(select_element.options)
        print(k)
        select_element.select_by_value(k)
        # driver.implicitly_wait(3) # seconds
        sleep(2)
        # submit_button = driver.find_element(value='ContentPlaceHolder1_btnsubmit')
        btnid = 'ContentPlaceHolder1_btnsubmit'
        # btnid = 'ctl00$ContentPlaceHolder1$btnsubmit'
        submit_button = driver.find_element(value=btnid)
        form1 = driver.find_element(value='form1')
        submit_button.click()
        # form1.submit()
        wait = WebDriverWait(driver, 1)
        wait.until(EC.url_changes(driver.current_url))
        print(driver.current_url)
        print(html_file)
        # write driver.page_source to file named f'{issue_id}~.html'
        with open(html_file, 'w') as f :
            f.write(driver.page_source)
        # append issue_id, driver.current_url to file named f'log~.html' 
        with open(f'log~.html', 'a') as f :
            f.write(f'{issue_id} {driver.current_url}\n')
        size_in_bytes = os.path.getsize(html_file)
        size_in_kb = size_in_bytes // (1024)
        print(f'Size of {issue_id} is {size_in_kb} KB')
        print("=====================================\n")
    except Exception as e :
        excnt = excnt + 1
        print(f"{excnt}) Exception {e}")
    if excnt > 2 : break
driver.quit()



#%%
from lxml import html
from glob import glob
import pandas as pd

acc = []
nx = 0
# for file in sorted(glob('./scraped/ijhs/html~/ij*58_03*.html')) :
for file in sorted(glob('./scraped/ijhs/html~/ij*.html')) :
    try :
        tree = html.parse(file)
        
        # Perform the XPath queries and manipulate the results
        # papers = [(a.get('href'), a.text, a.getnext().getnext().text) for a in tree.xpath('//*[@class="question col-xs-11"]/a')]
        papers = [(a.get('href'), a.text, e.getnext().getnext().text 
        ) for e in 
        tree.xpath('//*[@class="question col-xs-11"]')
        for a in e.xpath('./a')
        ]
        journal = [td.text for td in tree.xpath('//*[@class="col-xs-8"]//tbody/tr/td')]

        journal = re.sub(r'Indian Journal of History of Science', 'IJHS', '-'.join(journal))
        journal = re.sub(r'\s+', '-', journal)

        # Print the results
        for url, paper, author in papers:
            url = 'https://insa.nic.in/' + url.replace('..', '')
            acc.append((journal, paper, author, url))
        if not len(papers) :
            nx = nx+1
            print(f"{nx} {file} =====================================\n")

    except Exception as e :
        print(f'EEEE {e}')
        continue

insa_df = pd.DataFrame(acc, columns=['journal', 'paper', 'author', 'url'])#.to_csv('ijhs.csv', index=False)    
insa_df.shape
#%%
import requests
def size_in_kb(url) :
    resp = requests.head(url)
    size_in_bytes = int(resp.headers['Content-Length'])
    size_in_kb = size_in_bytes // (1024)
    print(f'{size_in_kb} KB - {url}')
    return size_in_kb
insa_df = insa_df.assign(
    size_in_kb = lambda x : x.url.apply(size_in_kb),
    cum_size_in_kb = lambda x : x.size_in_kb.cumsum()
)#.to_csv('ijhs.csv', index=False)

insa_df.to_csv('scraped/ijhs.tsv', index=False, sep='\t')
insa_df

#%%
insa_df = pd.read_csv('scraped/ijhs.tsv', sep='\t')
insa_df.url.value_counts().sort_values(ascending=False).head(20)
# %%
xdf = insa_df.assign(
    md_url = lambda d : d.url.apply( lambda x: re.sub(r'^.*\/', '/assets/ijhs/', x)),
    year = lambda d : d.journal.apply( lambda x: re.match(r'^.*(\d{4}).*', x).group(1)),
    issue = lambda d : d.journal.apply( lambda x: re.match(r'^.*\-(.*)', x).group(1)),
    md_paper = lambda d : d.apply ( lambda r : f'[{r.paper.strip()}]({r.md_url.strip()})' , axis=1),
)[['year', 'issue', 'author', 'md_paper']]
xdf.index = xdf.index + 1
xdf.to_csv('scraped/ijhs~.md', sep='|', index=True)

# %%
# insa_df[insa_df.journal.str.contains('58-2023-Issue-3')].url.tolist()
# insa_df[insa_df.url.str.contains('Vol49')].sort_values(by='url').style.format({'url': lambda x: f'<a href="{x}">{x}</a>'})  
insa_df.sort_values(by='url')[['url']].to_csv('scraped/ijhs~.urls', index=False)



# %%
xdf.year.value_counts().sort_index().plot(kind='bar', figsize=(20,5))

# %%
