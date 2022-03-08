'''
Look for candidate yugaadi as specified in lvj
For the yugaadi tabulate the position of sun and moon 
- for each jd for 5 years
- for each thithi for 5 years
'''
#%%
# import sys
# import os
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
#%%
from IPython.display import display
import math
import pandas as pd
import numpy as np
from astropy.time import Time
from pandas.core.reshape.tile import cut
import PlanetPos as PP
from JdUtils import stelJD
from time import time
import re
import NaksUtils
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")
# %%
from maasa import get_moon_planet_pos
#%%
class SunMoonQuadrants: 
	'''
	Find  dates for amavasya/poornima/shukla/krishna ashtami at uttarayan/daskshinayana
	Useful for finding the candidate yugaadi of lagadha vedanga jyotisha and other vedangas events
	'''
	PHASE_AMASVASYA = 0
	PHASE_POORNIMA = 1
	PHASE_SHUKLA_ASHTAMI = 0.5
	PHASE_KRISHNA_ASHTAMI = -0.5
	def TestUsage():
		smq = SunMoonQuadrants()
		display(smq.amavasya_at_uttarayan())
		 
	def __init__(self) :
		df = get_moon_planet_pos(force=False)
		pvt_elong = pd.pivot_table(df, 
			index=['jd', 'date'], 
			columns='planet', 
			values='elong',
			)
		pvt_elong = pvt_elong[['Moon', 'Sun']].rename(
				columns={'Moon' : "moon_lon", "Sun" : "sun_lon"}
			)
		pvt_r = pd.pivot_table(df, 
			index=['jd', 'date'], 
			columns='planet', 
			values='r'
			)
		pvt_r = pvt_r[['Moon']].rename(columns={'Moon' : "moon_r"})

		pvt_phase = pd.pivot_table(df, index=['jd', 'date'], values='phase')
		pvt_gr = pd.pivot_table(
			df[['jd','date','gr']].fillna('-')
			,index=['jd', 'date']
			,values='gr'
			,aggfunc=lambda x: x[0]
			)
		
		bce_sunmoon_lon_phase_dist_by_date = pd.merge( pvt_elong, 
		pd.merge (
			pvt_phase, pvt_gr 
			, on=['jd','date']
		)
			, on=['jd','date']
		)

		# amavasya_at_uttarayan_loose = bce_sunmoon_lon_phase_dist_by_date[ 
		# 	 bce_sunmoon_lon_phase_dist_by_date.apply( lambda x: 
		# 	 	(x.phase == 0) 
		# 		and (x.sun_lon > 265) 
		# 		and (x.sun_lon < 275)
		# 		, axis=1)  ]

		self.bce_sunmoon_lon_phase_dist_by_date_df = bce_sunmoon_lon_phase_dist_by_date

	def phase_at_lon( self, phase=PHASE_AMASVASYA, lon=270) : # defaults are amava
		tol = 1
		df = self.bce_sunmoon_lon_phase_dist_by_date_df
		ans = df[
			df.apply( lambda x: 
				(x.phase == phase) 
				and (x.sun_lon > lon-tol) and (x.sun_lon < lon+tol)
				and (x.moon_lon > lon-tol) and (x.moon_lon < lon+tol)
				, axis=1)  ]
		return ans
	
		# pandas set display float format
		# pd.options.display.float_format = '{:.3f}'.format
		amavasya_at_uttarayan_dict = [ x for x in ans.reset_index().apply( lambda x: x.to_dict(), axis=1)]

	def amavasya_at_uttarayana(self) : return self.phase_at_lon(self.PHASE_AMASVASYA)
	def amavasya_at_daskshinayana(self) : return self.phase_at_lon(self.PHASE_AMASVASYA, lon=90)
	def poornima_at_uttarayana(self) : return self.phase_at_lon(self.PHASE_POORNIMA)
	def poornima_at_daskshinayana(self) : return self.phase_at_lon(self.PHASE_POORNIMA, lon=90)
	def shukla_ashtami_at_uttarayana(self) : return self.phase_at_lon(self.PHASE_SHUKLA_ASHTAMI)
	def shukla_ashtami_at_daskshinayana(self) : return self.phase_at_lon(self.PHASE_SHUKLA_ASHTAMI, lon=90)	
	def krishna_ashtami_at_uttarayana(self) : return self.phase_at_lon(self.PHASE_KRISHNA_ASHTAMI)
	def krishna_ashtami_at_daskshinayana(self) : return self.phase_at_lon(self.PHASE_KRISHNA_ASHTAMI, lon=90)

# %%
# tt = Time("-01610-01-04T22:09:00")
# (tt.jd1 , tt.jd2, tt.jd , stelAltJD(-1610,1,4,22,9))

# %%
# SunMoonQuadrants.TestUsage()


# %%
smq = SunMoonQuadrants()
lvj_zero_jd, lvj_zero_dt  = smq.amavasya_at_uttarayana().index[2]
#%%
tz=Time(lvj_zero_dt)
lvj_zero_jd, lvj_zero_dt , tz.jd , stelJD(-1238,1,2,1,0)
#%%
bce600 = stelJD(-600,1,1,0,0)
pp = PP.PlanetPos()
t0 = time()
mdf = pd.DataFrame()
step=365
for y in range(0,100*step,step) :
	ydf = pd.concat([ pp.get_planet_pos(bce600 + x ).loc[['Mars'],['jd', 'date', 'elong']] for x in range(y,y+step) ])
	mdf = pd.concat([mdf,ydf])
	print (f'{y//365 :4d} -- {y:6d} {y+step:6d} -- {time()-t0 :.2f}  -- {ydf.shape} {mdf.shape}')
	if (y//365)%10 == 0 :display(mdf.head(2), mdf.tail(2))

mdf.to_csv("../datasets/~mars-600bce-to-500bce-daily.csv")
display(mdf.head(), mdf.tail())

#%%
tol=.8
m1 = mdf[ [ (213.6-tol) < x < (213.6+tol) for x in mdf.elong ] ]
m1['jdiff'] = m1.jd.diff().fillna(1)
m1 = m1[m1.jdiff>100].reset_index()
m1['jdiff'] = m1.jd.diff().fillna(1)
m1 = m1.loc[1:,]
m1['year'] = m1.date.apply(lambda x: int(re.sub("......T.*","",x)))
ax=m1[m1.jdiff>1].plot(x='jd', y='jdiff', marker='o', rot=60, grid=True, figsize=(15,6), legend=None)
ax.set_xticks(m1.jd)
ax.set_xlabel('year')
ax.set_ylabel('days since \n last mangal vakra near guru', fontsize=15)
ax.set_xticklabels( [ -600+int(x-m1.jd[1])//365 for x in m1.jd] )
ax.set_title('Days between Mangal Vakra near Guru', fontsize=15)

''


# %%
