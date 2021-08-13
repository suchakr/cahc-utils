# Distribution of eclipse frequency
#%%
rom numpy.lib.index_tricks import ndenumerate
from numpy.random import sample
import pandas as pd
import numpy as np
import re
from astropy.time import Time
from IPython.display import display
from time import time
# %%
# Ts =  [ Time('0000-01-01') , Time('0001-01-01') , Time('0002-01-01') ]
# Jds = pd.Series([ t.jd1 for t in Ts])
# JD0 = Jds[0]
JD0= Time('0000-01-01').jd1
JD2000= Time('2000-01-01 12:00:00').jd1
(JD0, JD2000)
#%%
def j01(x,debugL=None) :
	M = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(" ")
	for m,ix in zip(M , range(1,len(M)+1)) :
		x = re.sub(m,'%02d'%ix,x)
	neg = x[0] == '-'
	inx = x
	x = re.sub("^\-","",x)
	try :
		y,m,d,_,_ =  [ int(z) for z in re.split(r'[\s\-\:]+',x)]
	except ValueError as e:
		# print('e1 ' + str(e) + ' -- '+ x)
		try:
			y,m,d =  [ int(z) for z in x.split("-")]
		except ValueError as e2:
			print([e2, str(e2), x, inx, debugL])
			raise e2
	y = -y if neg else y
	fmt = '%06d-%02d-%02d' if y < 0 else '%04d-%02d-%02d'
	x = fmt % (y,m,d)
	# return x
	try :
		# print(x, Time(x).jd1)
		return {'jd': Time(x).jd1, 'dt': x }
	except Exception as e:
		try:
			x = re.sub("02-29","02-28", x)  # some Time(feb/29) fail so fix it forcefully
			return {'jd': Time(x).jd1, 'dt': x }
		except Exception as e:
			print([x,'L2', e])
			raise e
# [ j01('-0200 Feb 29 23:19') ,j01('-0198 Jan 8 10:22') ,j01('-0200 Feb 29 23:19') ]
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


#%%

def plot_eclipse_freq_histogram(sedf, ledf) :
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

def plot_eclipse_scatter(sedf, ledf) :
	sldf= gen_sldf(sedf, ledf)
	lsl = sldf.EclSeq.apply( lambda x: bool(re.match(r"L.S.L.",x)))
	sldf = sldf[lsl][ 'Date EclSeq DaysSince DaysSince2 MagSeq Mag jd'.split(" ") ]
	sldf

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
# %%
#%%
def plot_eclipse_charts():
	sedf = read_edf(
		"../datasets/jaipur-solar-eclipses.csv",
		"../datasets/jaipur-solar-eclipses-cooked.csv", 'S')

	ledf = read_edf(
		"../datasets/jaipur-lunar-eclipses.csv",
		"../datasets/jaipur-lunar-eclipses-cooked.csv", 'L')
	# display(sedf.head(), ledf.head(), sedf.shape, ledf.shape)
	plot_eclipse_freq_histogram(sedf, ledf)
	plot_eclipse_scatter(sedf, ledf)
	# return (sedf, ledf)
#
plot_eclipse_charts()

# sldf[sldf.DaysSince <=30].EclSeq.value_counts()

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
#%%
def get_moon_phases_df(raw_fn = "../datasets/moon-phases-scrape.txt"):
	cooked_csv = re.sub(".txt","-cooked.csv",raw_fn)
	try:
		df = pd.read_csv(cooked_csv)
		return df
	except Exception as e:
		print(e)
		print("Reading raw data from %s" % raw_fn)
		pass

	rxs = [  "".join(
				# [ '^(?\S*)' ] + 
				[ '^(.....)' ] + 
				[ '\s*(.*?:\d\d).(\S?)' ] * n 
			)
			for n in range(1,5) 
		]
	rxs = [ re.compile(x) for x in rxs ]

	lines = []
	with open(raw_fn) as f: lines = [ line for line in f]
	yr = None
	moon_phases = []
	start_time = time()
	lines_ = lines[:]
	nl_ = len(lines_)	
	for l,nl in zip(lines_, range(nl_)):
		nd = len([x for x in l if x ==':'])
		matches = re.match(rxs[nd-1],l).groups()
		# print("==========")
		# print(nd, len(l), l)
		# print(len(matches), matches )
		# print(matches)
		patches = (None,) * (9 - len(matches))
		matches = matches  + patches
		# print(len(matches), matches )
		(y,amavas,sgr,s8,_,poorni,cgr,k8,_) = matches 
		y = y.strip()	
		if y: yr = y 
		(amavas,s8,poorni,k8) = ( f"{yr} {x}" if x else '' for x in (amavas,s8,poorni,k8) )	
		(jamavas,js8,jpoorni,jk8) = ( j01(x, l)['jd'] if x else '' for x in (amavas,s8,poorni,k8) )	
		mp = [x for x in [
			[amavas, 0.0,jamavas, sgr],
			[s8    , 0.5,js8,      ''],
			[poorni, 1.0,jpoorni, cgr],
			[k8    ,-0.5,jk8,      ''],
		] if bool(x[0])]
		for x in mp: moon_phases = moon_phases + [x]
		if ( nl % 100 == 0 ): print (f"{nl:03d} of {nl_: 6d} - {100.0*nl/(1.0*nl_) : 3.2f}% -  {time() - start_time:.3f}")


	moon_phases_df = pd.DataFrame(moon_phases, columns=['dt','phase','astro_jd','gr'])
	stel_df = pd.DataFrame(moon_phases_df.dt.apply(xform).tolist(), columns=['dt', 'stel_dt', 'astro_jd', 'stel_jd'])
	moon_phases_df['stel_dt'] = stel_df['stel_dt']	
	moon_phases_df['stel_jd'] = 0 # placeholder
	moon_phases_df = moon_phases_df[['dt', 'stel_dt', 'phase', 'astro_jd', 'stel_jd', 'gr']]
	moon_phases_df.sort_values(by=['astro_jd'], inplace=True)
	moon_phases_df.to_csv(cooked_csv, index=False)
	return moon_phases_df

#%%
moon_phases_df = get_moon_phases_df()
zz=moon_phases_df[['stel_dt', 'phase', 'gr']].apply(
	lambda x: f"['{x.stel_dt}',{x.phase:>3},\'{x.gr if len(str(x.gr))==1 else '-'}\']",
	axis=1)
s=",\n".join(zz)
with open('../datasets/moon-phases-js-array.ssc', 'w') as f: f.write(f"[{s}]")


# xx = moon_phases_df
# ww = xx.dt.apply(xform)
# display(xx, pd.DataFrame(ww.tolist()))
#%%

#moon_phases_df.shape

# %%
def xform(x) :
	j = j01(x)
	return [x 
		 ,j['dt'] + f'T{re.match(".*(..:..).*",x)[1] + ":00"}'
		,j['jd']
		,0
	]  

#%%

class FitAstroStelJD :
	def samples_for_stellarium(moon_phases_df) :
		sample_df = moon_phases_df.iloc[[0] + list(range(1,moon_phases_df.shape[0],5000))  +[-1]]
		samples = sample_df.dt.apply(xform).tolist()
		return samples
	#ans=samples_for_stellarium(moon_phases_df)
	#print(ans) and feed this to stellarium .. which stellarium patches

	def patched_samples_from_stellarium() :
		patched = [ 
			#dt                   astro_dt             astro_jd     stel_dt              stel_jd  
			["-1999 Jan  7  00:24", "-01999-01-07T00:24:00", 990946, "-1999-01-07T00:24:02", 990929.3011597223, ],
			["-1999 Jan 15  05:26", "-01999-01-15T05:26:00", 990954, "-1999-01-15T05:26:02", 990937.5108819444, ],
			["-1898 Feb  6  21:33", "-01898-02-06T21:33:00", 1027866, "-1898-02-06T21:33:02", 1027850.1824097222, ],
			["-1797 Mar  2  20:05", "-01797-03-02T20:05:00", 1064778, "-1797-03-02T20:05:02", 1064764.1212986112, ],
			["-1696 Mar 24  17:53", "-01696-03-24T17:53:00", 1101690, "-1696-03-24T17:53:02", 1101677.0296319446, ],
			["-1595 Apr 16  15:44", "-01595-04-16T15:44:00", 1138604, "-1595-04-16T15:44:02", 1138589.9400486113, ],
			["-1494 May 10  12:52", "-01494-05-10T12:52:00", 1175516, "-1494-05-10T12:52:02", 1175503.8206041667, ],
			["-1393 Jun  2  02:06", "-01393-06-02T02:06:00", 1212428, "-1393-06-02T02:06:02", 1212416.3719930556, ],
			["-1292 Jun 24  09:10", "-01292-06-24T09:10:00", 1249340, "-1292-06-24T09:10:02", 1249329.6664375002, ],
			["-1191 Jul 18  02:15", "-01191-07-18T02:15:00", 1286254, "-1191-07-18T02:15:02", 1286243.3782430557, ],
			["-1090 Aug  9  13:09", "-01090-08-09T13:09:00", 1323166, "-1090-08-09T13:09:02", 1323155.8324097223, ],
			["-0989 Sep  2  05:42", "-00989-09-02T05:42:00", 1360078, "-0989-09-02T05:42:02", 1360069.5219930557, ],
			["-0888 Sep 24  17:10", "-00888-09-24T17:10:00", 1396990, "-0888-09-24T17:10:02", 1396982.9997708334, ],
			["-0787 Oct 17  07:44", "-00787-10-17T07:44:00", 1433904, "-0787-10-17T07:44:02", 1433895.6067152778, ],
			["-0686 Nov 10  06:32", "-00686-11-10T06:32:00", 1470816, "-0686-11-10T06:32:02", 1470809.556715278, ],
			["-0585 Dec  3  11:02", "-00585-12-03T11:02:00", 1507728, "-0585-12-03T11:02:02", 1507722.744215278, ],
			["-0484 Dec 25  07:31", "-00484-12-25T07:31:00", 1544640, "-0484-12-25T07:31:02", 1544635.5976875, ],
			["-0382 Jan 18  07:44", "-00382-01-18T07:44:00", 1581554, "-0382-01-18T07:44:02", 1581549.6067152778, ],
			["-0281 Feb 10  03:36", "-00281-02-10T03:36:00", 1618466, "-0281-02-10T03:36:02", 1618462.4344930556, ],
			["-0180 Mar  4  06:15", "-00180-03-04T06:15:00", 1655378, "-0180-03-04T06:15:02", 1655375.5449097224, ],
			["0021 Mar 31  22:18", "0021-03-31T22:18:00", 1728820, "0021-03-31T22:18:02", 1728818.2136597224, ],
			["0122 Apr 24  00:53", "0122-04-24T00:53:00", 1765732, "0122-04-24T00:53:02", 1765731.3212986111, ],
			["0223 May 17  20:17", "0223-05-17T20:17:00", 1802644, "0223-05-17T20:17:02", 1802645.1296319445, ],
			["0324 Jun  8  07:16", "0324-06-08T07:16:00", 1839556, "0324-06-08T07:16:02", 1839557.5872708336, ],
			["0425 Jul  1  18:16", "0425-07-01T18:16:00", 1876470, "0425-07-01T18:16:02", 1876471.0456041668, ],
			["0526 Jul 25  07:53", "0526-07-25T07:53:00", 1913382, "0526-07-25T07:53:02", 1913384.6129652779, ],
			["0627 Aug 16  18:52", "0627-08-16T18:52:00", 1950294, "0627-08-16T18:52:02", 1950297.0706041667, ],
			["0728 Sep  8  13:42", "0728-09-08T13:42:00", 1987206, "0728-09-08T13:42:02", 1987210.855326389, ],
			["0829 Oct  1  20:50", "0829-10-01T20:50:00", 2024120, "0829-10-01T20:50:02", 2024124.1525486112, ],
			["0930 Oct 24  13:23", "0930-10-24T13:23:00", 2061032, "0930-10-24T13:23:02", 2061036.8421319446, ],
			["1031 Nov 17  12:52", "1031-11-17T12:52:00", 2097944, "1031-11-17T12:52:02", 2097950.820604167, ],
			["1132 Dec  9  13:22", "1132-12-09T13:22:00", 2134856, "1132-12-09T13:22:02", 2134863.8414375, ],
			["1234 Jan  1  13:03", "1234-01-01T13:03:00", 2171770, "1234-01-01T13:03:02", 2171776.828243056, ],
			["1335 Jan 25  12:41", "1335-01-25T12:41:00", 2208682, "1335-01-25T12:41:02", 2208690.812965278, ],
			["1436 Feb 17  05:56", "1436-02-17T05:56:00", 2245594, "1436-02-17T05:56:02", 2245603.531715278, ],
			["1537 Mar 11  12:03", "1537-03-11T12:03:00", 2282506, "1537-03-11T12:03:02", 2282516.786576389, ],
			["1638 Apr 14  07:28", "1638-04-14T07:28:00", 2319430, "1638-04-14T07:28:02", 2319430.595604167, ],
			["1739 May  7  18:46", "1739-05-07T18:46:00", 2356342, "1739-05-07T18:46:02", 2356343.0664375, ],
			["1840 May 31  07:15", "1840-05-31T07:15:00", 2393256, "1840-05-31T07:15:02", 2393256.586576389, ],
			# ["1941 Jun 24  19:22", "1941-06-24T19:22:00", 2430170, "1941-06-24T19:41:40", 2430170.0914375, ],
			# ["2042 Jul 17  05:52", "2042-07-17T05:52:00", 2467082, "2042-07-17T06:11:40", 2467082.5289375, ],
			# ["2100 Dec 30  23:58", "2100-12-30T23:58:00", 2488432, "2100-12-31T00:17:40", 2488433.283104167, ],
		]
		ans = pd.DataFrame( 
			patched, 
			columns=["dt", "astro_dt" , "astro_jd", "stel_dt", "stel_jd"]
		)
		return ans[ans.astro_jd <=2393265 ]  # beyond this, astro_dt and stel_dt are by 20 minutes 


	def fit_astro_to_stel_poly():
		pdf = patched_samples_from_stellarium()
		# display(pdf)
		coeff = np.polyfit(pdf.astro_jd, pdf.stel_jd,8)
		polyfn = np.poly1d(coeff)
		return (coeff, polyfn)

	def test():
		coeff, fn = fit_astro_to_stel_poly()
		pdf = patched_samples_from_stellarium()
		for a, s , d in zip(pdf.astro_jd,pdf.stel_jd, pdf.dt):
			s1 = fn(a)
			print(f"{d}, {a}, {s:.2f}, {s1:.2f}, {s-s1:.2f}")

FitAstroStelJD.test()
# display(fn(2393256) , f"{patched_samples_from_stellarium().tail(1).stel_jd}")
# display(fn(2356342) , f"{patched_samples_from_stellarium().tail(1).stel_jd}")


#%% 
class FullMoon():
	def __init__(self):
		self.df = pd.read_csv(f"../datasets/moon-phases-lat-lon-01.tsv", sep="\t")
		self.df.columns = ["astro_dt", "stel_dt", "astro_jd", "lon", "lat", "ra", "dec", "phase", "ill", "ph", "gr"]
		self.df['_londiff'] = self.df.lon.diff().fillna(0)
		self.df = self.df[self.df._londiff !=0]

	def fit_date_to_ecl_poly(self):
		self.coeff = np.polyfit(self.df.astro_jd, self.df.dec,3)
		self.fn = np.poly1d(self.coeff)
		pass

	def test(self):
		self.fit_date_to_ecl_poly()
		for a, s, d in zip(self.df.astro_jd,self.df.dec, self.df.astro_dt):
			s1 = self.fn(a)
			print(f"{d}, {a}, {s:.2f}, {s1:.2f}, {s-s1:.2f}")
		


FullMoon().test()




# %%
