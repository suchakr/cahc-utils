# Distribution of eclipse frequency
#%%
from numpy.lib.index_tricks import ndenumerate
import pandas as pd
import numpy as np
import re
from astropy.time import Time
from IPython.display import display

# %%
Ts =  [ Time('0000-01-01') , Time('0001-01-01') , Time('0002-01-01') ]
Jds = pd.Series([ t.jd1 for t in Ts])
# t = Time('-01982-01-22')
JD0 = Jds[0]
#%%
M = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(" ")
def j01(x) :
	for m,ix in zip(M , range(1,len(M)+1)) :
		x = re.sub(m,'%02d'%ix,x)
	neg = x[0] == '-'
	x = re.sub("^\-","",x)
	try :
		y,m,d,_,_ =  [ int(z) for z in re.split(r'[\s\-\:]+',x)]
	except ValueError as e:
		print('e1 ' + str(e) + ' -- '+ x)
		try:
			y,m,d =  [ int(z) for z in x.split("-")]
		except ValueError as e2:
			print('e2 ' + str(e2))
			raise e2
	y = -y if neg else y
	fmt = '%06d-%02d-%02d' if y < 0 else '%04d-%02d-%02d'
	x = fmt % (y,m,d)
	# return x
	try :
		# print(x, Time(x).jd1)
		return {'jd': Time(x).jd1, 'dt': x }
	except Exception as e:
		print([x, e])
		raise e

j01('-0198 Jan 8 10:22')
j01('0198 Jan 8 10:22')
j01('-0199 Jan 4 10:22')
# %%
# COLS=['pSameEcl', 'Date' , 'jd', 'Ecl', 'EclType', 'Mag', 'pDate' , 'pEclType', 'pMag' ]

def read_edf(ecsv, cooked, tag) :
	# Date,EclType,ParBegin,ParBAlt,ATBegin,MaxEcl,MaxAlt,MaxAzi,ATEnd,ParEnd,ParEAlt,EclMag,EclObs,ATDur
	edf = pd.read_csv(ecsv)
	edf = edf.drop_duplicates()
	edf['jd'] = edf.Date.apply( lambda x : j01(x)['jd']) 
	edf = edf.sort_values(by = ['jd'], ascending=True)
	# edf['jdiff'] = edf.jd.diff()
	# edf['pDate'] = edf.Date.shift(1)
	# edf['pEclType'] = edf.EclType.shift(1)
	# edf['pMag'] = edf.Mag.shift(1)
	edf['DaysSince'] = edf.jd.diff()
	edf['Body'] = tag 
	edf = edf[1:] # First row has NaN jdiff -- drop that
	edf.DaysSince = [ int(x) for x in edf.DaysSince ]
	COLS=['DaysSince', 'Date' , 'jd', 'Body', 'EclType' , 'Mag']
	edf[COLS].to_csv(cooked, index=None)
	return edf[COLS]

sedf = read_edf(
	"../datasets/jaipur-solar-eclipses.csv",
	"../datasets/jaipur-solar-eclipses-cooked.csv", 'S')

ledf = read_edf(
	"../datasets/jaipur-lunar-eclipses.csv",
	"../datasets/jaipur-lunar-eclipses-cooked.csv", 'L')
#%%
# display(sedf.head(), ledf.head(), sedf.shape, ledf.shape)
ledf.head()
#%%
for ecl, edf in zip( ['Lunar', 'Solar'], [ledf, sedf] ) :
	bdf = edf[edf.jd <=JD0]
	dist = pd.DataFrame(bdf.DaysSince.value_counts().sort_index())
	ax = dist.plot.bar( logy=not True, grid=True, rot=60, figsize=(10,5),
		legend=False,
		title=f"{ecl} - Eclipse Count by Days Since Last Eclipse"
			+ f"\nJaipur from {bdf.Date.tolist()[0]} to {bdf.Date.tolist()[-1]}" 
			# + f"\nConsidering Total, Partial and Penumbral > 0.8"
			+ f"\nConsidering Total, Partial and Penumbral"
			)
	ax.set_xlabel("Days Since Last Eclipse")
	ax.set_ylabel("Eclipse Count")
	ax.set_xticklabels([ re.sub("\.0","",x.get_text()) for x in ax.get_xticklabels()])
	for d, i in zip( dist.DaysSince, range(dist.shape[0]+1)) :
		ax.annotate( str(d), [i, d+25] , color='red', rotation=0)
#%%
# sldf['EclSeq'] = sldf.Ecl.shift(0) + sldf.Ecl.shift(-1) + sldf.Ecl.shift(-2) 
def gen_sldf(sedf, ledf):
	sldf = pd.concat ([sedf[sedf.jd <=JD0], ledf[ledf.jd <=JD0]]).sort_values(by=['jd'])
	sldf['DaysSince2'] = sldf.jd.diff()
	sldf = sldf[1:].reset_index(drop=True)
	sldf.DaysSince2 = [ int(x) for x in sldf.DaysSince2 ]


	sldf['EclSeq'] = [ str(x) for x in (
		sldf.Body.shift(0) + sldf.EclType.shift(0).apply( lambda x : str(x).lower()) +  ''
		+ sldf.Body.shift(1) + sldf.EclType.shift(1).apply( lambda x : str(x).lower()) +  ''
		+ sldf.Body.shift(2) + sldf.EclType.shift(2).apply( lambda x : str(x).lower()) +  ''
	)]

	sldf['MagSeq'] = [  [x,y,z] for x,y,z in zip(
		sldf.Mag.shift(0)
		, sldf.Mag.shift(1)
		, sldf.Mag.shift(2) 
	)]
	sldf = sldf[2:]
	sldf.MagSeq = [( 
		 '%.2f'%float(re.sub("[^\d\.]","",str(x[0])))
		 , '%.2f'%float(re.sub("[^\d\.]","",str(x[1])))
		 , '%.2f'%float(re.sub("[^\d\.]","",str(x[2])))
		)
		for x in sldf.MagSeq 
	]
	return sldf
#%%

sldf= gen_sldf(sedf, ledf)
lsl = sldf.EclSeq.apply( lambda x: bool(re.match(r"L.S.L.",x)))
sldf = sldf[lsl][ 'Date EclSeq DaysSince DaysSince2 MagSeq Mag jd'.split(" ") ]
sldf

# %%
ax = sldf.plot.scatter(
	x='jd', y='DaysSince', grid=True, rot=90, figsize=(25,5)
	# ,s=[ int(x) for x in sldf.Mag*100]
	# ,s=sldf.apply(lambda x: int(100*max(float(x.MagSeq[0]),float(x.MagSeq[2]) )) if x.DaysSince<=30 else 10, axis=1)
	,s=sldf.apply(lambda x: int(300*max(float(x.MagSeq[0]),float(x.MagSeq[2]) )) 
		if ( x.DaysSince<=30 and (re.match(r"L[pt]",x.EclSeq))  ) else 8, 
		axis=1)
	,c=sldf.apply(lambda x: 'blue'
		if ( x.DaysSince<=30 and (re.match(r"L",x.EclSeq))  ) else 'gray', 
		axis=1
	)
)
ax.set_xlabel("")
ax.set_ylabel("Days Since Last Lunar Eclipse")
ax.set_title("Solar Eclipse between Two Lunar Eclipses in Jaipur")
# ax.set_xticklabels([ re.sub("\.0","",x.get_text()) for x in ax.get_xticklabels()])
# ax.set_xticklabels([ re.sub("\.0","",x.get_text()) for x in ax.get_xticklabels()])
# ax.set_xlim( [ sldf.jd.min(), sldf.jd.max() ] )
# ax.set_xticks( [ x for x,i in zip(sldf.jd, range(sldf.shape[0])) if i%20 == 0]  )
# ax.set_xticklabels( [ x for x,i in zip(sldf.Date, range(sldf.shape[0])) if i%20 == 0]  )
ax.set_xticks( [ x for x,d,i in zip(sldf.jd, sldf.DaysSince, range(sldf.shape[0])) if d<=30]  )
ax.set_xticklabels( [ x for x,d,i in zip(sldf.Date, sldf.DaysSince, range(sldf.shape[0])) if d<=30])

sldf.shape
# %%
sldf[sldf.DaysSince <=30].EclSeq.value_counts()

# %%
# Read a textfile line by line
# -0199   Jan  4  10:22     Jan 11  15:00     Jan 19  19:11     Jan 27  04:48    
#         Feb  2  21:32     Feb 10  10:58     Feb 18  10:32     Feb 25  11:45    
#         Mar  4  09:31 P   Mar 12  06:34     Mar 19  22:57 t   Mar 26  17:23    
#         Apr  2  22:30     Apr 11  00:30     Apr 18  08:35     Apr 24  23:10    
#         May  2  12:23     May 10  16:01     May 17  16:08     May 24  06:27    
#         Jun  1  02:55     Jun  9  04:50     Jun 15  22:40     Jun 22  16:17    
#         Jun 30  17:55     Jul  8  15:00     Jul 15  05:27     Jul 22  05:17    
#         Jul 30  09:06     Aug  6  23:00     Aug 13  13:41     Aug 20  21:32    
#         Aug 29  00:03 P   Sep  5  05:43     Sep 12  00:20 t   Sep 19  16:39    
#         Sep 27  14:14     Oct  4  12:22     Oct 11  13:49     Oct 19  13:33    
#         Oct 27  03:16     Nov  2  20:14     Nov 10  06:02     Nov 18  10:26    
#         Nov 25  15:04     Dec  2  06:19     Dec 10  00:21     Dec 18  05:13    
#         Dec 25  01:55     Dec 31  19:02                                        
# -0198                                       Jan  8  19:39     Jan 16  20:17    
#         Jan 23  12:11     Jan 30  10:09     Feb  7  14:22     Feb 15  07:14    
#         Feb 21  22:09 T   Mar  1  03:02     Mar  9  06:58 n   Mar 16  14:46    
def read_data(filename):
	data = []
	with open(filename) as f:
		data = [ line for line in f]
	return data
#%%
rxs = [  "".join(
			[ '^(\S*)' ] + 
			[ '\s*(.*?:\d\d).(\S?)' ] * n 
		)
		for n in range(1,5) 
	]
rxs = [ re.compile(x) for x in rxs ]
rxs
#%%
lines = read_data("../datasets/moon-phases-scrape-raw.txt")
yr = None
# .........1.........2.........3.........4.........5.........6.........7.........8.........9.........0 
# -0199...Jan  4  10:22.X...Jan 11  15:00.....Jan 19  19:11.X...Jan 27  04:48    
# (-0199)...(Jan  4  10:22).(X)...(Jan 11  15:00).....(Jan 19  19:11).(X)...(Jan 27  04:48)    
# (.....)...(.............).(.)...(.............).....(.............).(.)...(.............)    
# -0199   Jan  4  10:22     Jan 11  15:00     Jan 19  19:11     Jan 27  04:48    
# rx = re.compile(r'(.....)...(.............).(.)...(.............).....(.............).(.)...(.............).*')
rx = re.compile(
	r'''
	(.....)...                 # yr
	(.............).(.)...     # m0 SE
	(.............).....       # s8
	(.............).(.)...     # m1 le
	(.............).*          # k8
	''', re.VERBOSE
)
for l in lines[:]:
	matches = re.match(rx,l).groups()
	(y,m0,SE,s8,m1,le,k8) = [ re.sub("\s*$","",re.sub("^\s*","",x)) for x in matches]
	if y: yr=y
	(m0,s8,m1,k8) = ( f"{yr} {x}" if x else '' for x in (m0,s8,m1,k8) )
	print(l)
	print(f"{m0} {SE} {s8} {m1} {le} {k8}")
	(jm0,js8,jm1,jk8) = ( j01(x)['jd'] if x else '' for x in (m0,s8,m1,k8) )
	# print(f"{jm0} {SE} {js8} {jm1} {le} {jk8}")
	# print(f"{m0} {SE} {s8} {m1} {le} {k8}")
	# m0 = f"{yr} {m0}"
	# s8 = f"{yr} {s8}"
	# m1 = f"{yr} {m1}"
	# k8 = f"{yr} {k8}"
#%%
for l in lines[0:20]:
	nd = len([x for x in l if x ==':'])
	matches = re.match(rxs[nd-1],l).groups()
	print("==========")
	print(nd)
	print(l)
	# print(matches)
	(y,amavas,sgr,s8,_,poorni,cgr,k8,_) = matches
	if y: yr = y 
	print(y,amavas,sgr,s8,poorni,cgr,k8)



#%%
## Multi line regex
import regex
rx = re.compile(r'''
	^(\S*)
	\s*(.*?:\d\d).(\S?)
	\s*(.*?:\d\d).(\S?)
	\s*(.*?:\d\d).(\S?)
	\s*(.*?:\d\d).(\S?)
	\s*
	''', re.VERBOSE)

rxs = [ re.compile( "".join(
			[ r'^(\S*)\s*' ] + 
			[ r'\s*(.*?:\d\d).(\S?)' ] * n 
			)
		, re.VERBOSE)
		for n in range(1,4) 
	]



xx1 = '-0199   Jan  4  10:22     Jan 11  15:00     Jan 19  19:11     Jan 27  04:48    '
xx2 = '        Mar  4  09:31 P   Mar 12  06:34     Mar 19  22:57 t   Mar 26  17:23    '
xx3 = '-0198                                       Jan  8  19:39     Jan 16  20:17    '
#re.match(rx,xx1).groups(), re.match(rx,xx2).groups() 
#e.match(rx,xx3).groups()

# %%
