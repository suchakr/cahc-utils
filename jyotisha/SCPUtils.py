'''
Surya Chandra Prajaptin -:- The Astrological Algorithms of SuryaChandra.
'''
#%%
import warnings

from numpy.random import rand; warnings.filterwarnings("ignore")
from IPython.display import display

import NaksUtils
import PlanetPos
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class SCPUtils :
	'''
	Observational data of Sun and Moon transit through Nakshatra
	'''
	def __init__(self, **kwargs) :
		self.nu = NaksUtils.NaksUtils()
		self.df27 = self.nu.df.set_index(['nnid'])
		df28 = self.nu.df28.set_index(['nnid'])
		offsets = df28.scp_muhurta
		angles = ((df28.scp_muhurta.cumsum() - offsets )* 360/df28.scp_muhurta.sum()) # ashvini at 0
		angles = (angles - 8) %360
		angles = [  (lo,hi)  for lo, hi in zip(angles , angles[1:].append(angles[:1])) ]
		df28['scp_lon_lo'] = [ x[0] for x in angles]
		df28['scp_lon_hi'] = [ x[1] for x in angles]
		self.df28 = df28
		
		self.pp = PlanetPos.PlanetPos( slice= ['Moon', 'Sun'])
		self.mdf = self.pp.get_sun_moon_pos_by_years(num_years=100)

		if 'naks_Moon' not in self.mdf.columns :
			print('Adding naks_Moon column to mdf')
			self.mdf['naks_Moon'] = [ self.naksOf(x) for x in self.mdf.elong_Moon ]
			fn = self.pp.sun_moon_df_csv
			print (f"Updating {fn} with naks_Moon")
			self.mdf.to_csv(fn, index='jd')

		if 'naks_Sun' not in self.mdf.columns :
			print('Adding naks_Sun column to mdf')
			self.mdf['naks_Sun'] = [ self.naksOf(x) for x in self.mdf.elong_Sun ]
			fn = self.pp.sun_moon_df_csv
			print (f"Updating {fn} with naks_Sun")
			self.mdf.to_csv(fn, index='jd')

		# self.mdf['naks_Moon'] = self.mdf.apply(lambda row : self.naksOf(row.elong_Moon), axis=1)
		# self.mdf['naks_Sun'] = self.mdf.apply(lambda row : self.naksOf(row.elong_Sun), axis=1)

	def slow_naksOf(self,lon) :
		'''
		lon :longitude
		return : naks N01 to N28 based on SCP spans assuming Abhijit starts at 270
		'''
		df28 = self.df28
		for i, row in df28.iterrows() :
			if row.scp_lon_lo < row.scp_lon_hi :
				if row.scp_lon_lo <= lon <= row.scp_lon_hi :
					return row.nid
			else :
				if row.scp_lon_lo <= lon or lon <= row.scp_lon_hi :
					return row.nid 
		return None

	def naksOf(self,lon) :
		'''
		lon :longitude
		return : naks N01 to N28 based on SCP spans assuming Abhijit starts at 270
		'''
		df28 = self.df28
		for nid, lo, hi in zip( df28.nid, df28.scp_lon_lo, df28.scp_lon_hi ) :
			if lo < hi :
				if lo <= lon <= hi :
					return nid
			else :
				if lo <= lon or lon <= hi :
					return nid 
		return None

	def plot_moon_cycle(self, num_years=1):
		slice = 6*30
		fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(10,10))
		ax.set_theta_zero_location('N', offset=8)
		ax.set_theta_direction(-1)
		# offsets = df28.scp_muhurta 
		# angles = ((df28.scp_muhurta.cumsum() - offsets )* 360/df28.scp_muhurta.sum())
		angles = self.df28.scp_lon_lo
		labels = [ f"{n}\n({(a-8)%360:.0f}°)" for n,a in zip(self.df28.nid , angles)]
		plt.thetagrids(angles, labels=labels)
		# colors = ['r', 'g', 'b', 'orange', 'c', 'm']
		colors = ['r', 'g', 'b', 'brown', 'm', 'black']
		mdf = self.mdf
		slices = range(0, min(slice*12*num_years +slice*2,mdf.shape[0]), slice)
		for slice_idx, slice_start in enumerate(slices) :
			degrees = mdf.iloc[slice_start:slice_start+slice+1].elong_Moon
			radius = mdf.iloc[slice_start:slice_start+slice+1].r_Moon
			phase = mdf.iloc[slice_start:slice_start+slice+1].sun_moon_angle
			ph180 = [ 500 if abs(x-180)<1.2 else 0*abs(x-180)/1000 for x in phase ]
			ph000 = [ 500 if x<2.5 else 0 for x in phase ]

			theta = 2*np.pi*degrees/360

			theta_slice = theta.iloc[:]
			radius_slice = radius.iloc[:]
			# moon_emojis
			# 🌑🌒🌓🌔🌕🌖🌗🌘 ◐◑◒◓◔◕⚫️ # 🌘🌙🌚🌛🌜🌝🌞 # 🌑🌒🌓🌔🌕🌖🌗🌘🌙🌚🌛🌜🌝🌞
			POURNAMI = f'○'
			AMAVASYA = f'●'
			NEW_MOON = f'x'
			SHUKLA_ASHTAMI = f'◑'
			KRISHNA_ASHTAMI = f'◐'
			ax.scatter(
				theta_slice, 
				radius_slice*(1+ 0*np.random.randint(-100,100)/2000), 
				alpha=0.5, color='gray', #colors[(slice_idx//12) % len(colors)],
				marker=f'$({AMAVASYA}{(slice_idx+1):02d})$', s = ph000,
			)
			ax.scatter(
				theta_slice, 
				radius_slice*(1+ 0*np.random.randint(-100,100)/2000), 
				alpha=0.8, color=colors[(slice_idx//12) % len(colors)],
				marker=f'${POURNAMI}{(slice_idx+1):02d}$', s = ph180,
			)
			ax.plot(
				theta_slice, 
				radius_slice*(1+ 0*np.random.randint(-100,100)/2000), 
				# s = np.log(radius)**2,
				# s = (radius - radius.min()+1)**2,
				# s = ph180,
				# 'o', 
				alpha=min(0.3, .5/num_years), 
				# markersize=1, 
				color=colors[(slice_idx//12) % len(colors)]
			)
		ax.set_rmax(radius.max()*1.01)
		ax.set_rmin(radius.min()*0.9)
		# ax.set_rticks([ ])  # Less radial ticks
		# ax.set_rticks([0.5, 1, 1.5])  # Less radial ticks
		# ax.set_rlabel_position(-0)  # Move radial labels away from plotted line
		ax.grid(True, color='#DDE', linestyle='-', linewidth=1)

		ax.set_title(f"Moon plot for {num_years} years of 62, 30 day months from -1000\n poornima in bold , amavasya in gray, each color is a year\n overlaid on unequal nakshatras \n polar plot - angle is longitude, radius is moon distance in earth-moon units ", va='bottom')
		plt.show()



	def plot_moon_hist(self) :
		mdf = self.mdf
		mdf[
			(mdf.sun_moon_angle>0) & (mdf.sun_moon_angle<4)
		].elong_Moon.hist(bins=28 , alpha=0.8, figsize=(10,5), rwidth=0.4)

		pd.DataFrame(mdf.naks_Moon.value_counts().sort_index()).plot.bar(figsize=(20,10))

	def TestSCP() :
		su = SCPUtils()
		su.plot_moon_cycle(num_years=1)
		su.plot_moon_hist()
		display([ (x, su.naksOf(x)) for x in range(230,360,7) ])
		display(su.mdf)


if __name__ == '__main__' :
	# SCPUtils.TestSCP()
	su = SCPUtils()
	su.plot_moon_hist()


#%%
# %%
# plot histogram of mdf

# %%
mdf.iloc[:1000].sun_moon_angle.plot(kind='line', alpha=0.8, figsize=(10,5))


