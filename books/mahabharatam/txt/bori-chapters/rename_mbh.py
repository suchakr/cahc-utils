#%%
'''
Utility to rename file with parva names
files scraped from https://bombay.indology.info/mahabharata/welcome.html
$> for n in `seq -w 0 18`; do wget https://bombay.indology.info/mahabharata/text/UD/MBh$n.txt; done
'''
import re
import os
from glob import glob
mb_parava ={ y[1] : re.sub("parvan","",y[2]).lower() for x in re.split("\n", '''Book 00: General Information	Last updated: Fri Sep 25 2020
Book 01: Ādiparvan	Last updated: Mon Jan 18 2021
Book 02: Sabhāparvan	Last updated: Wed Apr 19 2006
Book 03: Āraṇyakaparvan	Last updated: Mon Jun 22 2020
Book 04: Virāṭaparvan	Last updated: Thu Dec 1 2011
Book 05: Udyogaparvan	Last updated: Tue Dec 22 2020
Book 06: Bhīṣmaparvan	Last updated: Mon Jul 26 2021
Book 07: Droṇaparvan	Last updated: Mon Jun 22 2020
Book 08: Karṇaparvan	Last updated: Mon Jul 29 2019
Book 09: Śalyaparvan	Last updated: Tue Jun 23 2020
Book 10: Sauptikaparvan	Last updated: Thu Feb 26 2009
Book 11: Strīparvan	Last updated: Mon Apr 17 2017
Book 12: Śāntiparvan	Last updated: Wed Jun 16 2021
Book 13: Anuśāsanaparvan	Last updated: Mon Jul 29 2019
Book 14: Āśvamedhikaparvan	Last updated: Mon Jul 29 2019
Book 15: Āśramavāsikaparvan	Last updated: Tue May 15 2007
Book 16: Mausalaparvan	Last updated: Tue May 15 2007
Book 17: Mahāprasthānikaparvan	Last updated: Thu Sep 27 2007
Book 18: Svargārohaṇaparvan	Last updated: Mon Jul 23 2007''') for y in [ re.split("[\s\:]+", x) ] }

for src , dest in [  (f , re.sub( n, f"-{n}-{mb_parava[n]}", f)) 
	for n,f in [ 
		(re.match("^\D+(\d+)\D+", f )[1] ,f ) 
			for f in sorted(glob('MBh??.txt')) 
	]	 ] :
	if not os.path.exists(dest):
		os.rename(src, dest)
		print(dest)
	else:
		print(dest, "already exists")






# %%
