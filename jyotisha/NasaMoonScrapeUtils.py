"""Explore why only certain nakshatras name the maasas"""
#%%
from IPython.display import display
import math
import pandas as pd
import numpy as np
from astropy.time import Time
import PlanetPos as PP
from JdUtils import toStelJD
from time import time
import re
import NaksUtils
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")

#%%
def get_full_moon_planet_pos(force=False) -> pd.DataFrame:
	"""
	Get the planet positions/distance for all planets at full moon for years from -1999 to -100
		planet	jd		date			elong	elati	r	geo_r	geoc_x	geoc_y	geoc_z
	0	Jupiter	990952.05	-01999-01-29T13:17:00	294.55	-1.04	4.99	5.99	2.49	-5.44	-0.11
	1	Mars	990952.05	-01999-01-29T13:17:00	273.96	-1.00	1.39	2.29	0.16	-2.28	-0.04
	2	Mercury	990952.05	-01999-01-29T13:17:00	311.29	1.66	0.32	0.92	0.61	-0.69	0.03
	3	Moon	990952.05	-01999-01-29T13:17:00	107.52	3.16	57.15	57.15	-18.19	54.08	3.27
	4	Saturn	990952.05	-01999-01-29T13:17:00	88.36	0.62	9.35	8.44	0.24	8.44	0.09
	5	Sun	990952.05	-01999-01-29T13:17:00	292.96	-0.00	1.00	1.00	0.39	-0.92	-0.00
	6	Venus	990952.05	-01999-01-29T13:17:00	338.88	1.37	0.72	0.74	0.69	-0.27	0.02
	"""
	try :
		if force : raise FileNotFoundError
		return pd.read_csv('../datasets/full-moon-planet-pos-bce2000-to-bce0100.csv')
	except Exception as e: # FileNotFoundError:
		print(e , "Trying to regenerate")
		pp = PP.PlanetPos()
		moon_df = pd.read_csv('../datasets/moon-phases-scrape-cooked.csv')
		# moon_df = moon_df[  [ bool(re.match("^.199[89]",x)) for x in moon_df.dt] ] 
		moon_df.stel_jd = moon_df.stel_dt.apply(toStelJD)
		bce_full_moons_df = moon_df[
			(moon_df.phase > 0.5) & 
			(moon_df.astro_jd < (PP.JD_2000 - 2000*365.25)) 
			].sort_values(by='stel_jd')
		nelems = bce_full_moons_df.shape[0]
		slices = [(x, min(x+1000,nelems)) for x in range(0,nelems,1000)]
		ts = time()
		acc=[]
		rows = 0
		for i, (start, stop) in enumerate(slices):
			ans = pd.concat([
				pp.get_planet_pos(jd, dt) 
				for jd, dt , phase in zip(
					bce_full_moons_df.stel_jd[start:stop]
					, bce_full_moons_df.stel_dt[start:stop]
					, bce_full_moons_df.phase[start:stop]
					) 
			])
			acc.append(ans)
			rows += ans.shape[0]
			print(f'{i}/{len(slices)} - {rows} - {time()-ts : .3f}')
			#
		acc_df = pd.concat(acc)
		acc_df.to_csv('../datasets/full-moon-planet-pos-bce2000-to-bce0100.csv')
		return acc_df

#%%

def get_moon_planet_pos(force=False) -> pd.DataFrame:
	"""
	Get the planet positions/distance for all planets at full moon for years from -1999 to -100
		jd		date			elong		elati		r		geo_r		geoc_x		geoc_y		geoc_z		phase  gr
	Jupiter	9.909295e+05	-01999-01-07T00:24:00	289.178995	-1.028499	4.993017	5.919687	1.944425	-5.590225	-0.106257	-0.5  
	Mars	9.909295e+05	-01999-01-07T00:24:00	256.276168	-0.826578	1.391493	2.329699	-0.552646	-2.262952	-0.033608	-0.5
	Mercury	9.909295e+05	-01999-01-07T00:24:00	272.915735	-1.900560	0.378695	1.362881	0.069288	-1.360368	-0.045200	-0.5
	Moon	9.909295e+05	-01999-01-07T00:24:00	177.319963	5.041963	60.099824	60.099824	-59.727728	4.203308	5.188405	-0.5
	Saturn	9.909295e+05	-01999-01-07T00:24:00	90.081351	0.583402	9.345761	8.356267	-0.011864	8.355825	0.085084	-0.5
	"""
	try :
		if force : raise FileNotFoundError
		return pd.read_csv('../datasets/moon-planet-pos-bce2000-to-bce0100.csv')
	except Exception as e: # FileNotFoundError:
		print(e , "Trying to Regenerate")
		pp = PP.PlanetPos()
		moon_df = pd.read_csv('../datasets/moon-phases-scrape-cooked.csv')
		# moon_df = moon_df[  [ bool(re.match("^.199[89]",x)) for x in moon_df.dt] ] 
		moon_df.stel_jd = moon_df.stel_dt.apply(toStelJD)
		bce_moons_df = moon_df[
			# (moon_df.phase > 0.5) & 
			(moon_df.astro_jd < (PP.JD_2000 - 2000*365.25)) 
			].sort_values(by='stel_jd')
		nelems = bce_moons_df.shape[0]
		slices = [(x, min(x+1000,nelems)) for x in range(0,nelems,1000)]
		ts = time()
		acc=[]
		rows = 0
		def ppx(jd,dt,phase,gr) :
			df = pp.get_planet_pos(jd, dt)
			df['phase'] = phase
			df['gr'] = gr
			return df

		for i, (start, stop) in enumerate(slices[:]):
			ans = pd.concat([
				ppx(jd, dt, phase, gr)
				# pp.get_planet_pos(jd, dt)
				for jd, dt, phase, gr in zip(
					bce_moons_df.stel_jd[start:stop]
					, bce_moons_df.stel_dt[start:stop]
					, bce_moons_df.phase[start:stop]
					, bce_moons_df.gr[start:stop]
					) 
			])
			acc.append(ans)
			rows += ans.shape[0]
			print(f'{i}/{len(slices)} - {rows} - {time()-ts : .3f}')
			#
		acc_df = pd.concat(acc)
		acc_df.to_csv('../datasets/moon-planet-pos-bce2000-to-bce0100.csv')
		return acc_df

# get_moon_planet_pos() #force=0)
# %%
def plot_full_moon_distance_hist_by_naks(
	from_year=-1999 ,
	num_years=2000, 
	chunks=10, 
	maasa_threshold=8, 
	cuts=5,
	cut_to_plot=0,
	title_tag='Super Moon'
	)-> None:
	"""
	Plot the histogram super full moon instance count by nakshatra for date range divided into chunks
	The maasa_threshold is the number of maasa that must be above the mean to be considered for plotting
	cuts speficies the number of cuts to divide the full moon distance into
	cut_to_plot specifies the cut to plot from the above cuts
	"""
	nu = NaksUtils.NaksUtils()
	fm_df = get_full_moon_planet_pos(force=not True)
	jd_from_year = toStelJD(f'{from_year:06d}-01-01T00:00:00')
	jd_to_year = jd_from_year+num_years*356.25
	fm_df = fm_df[ (fm_df.jd > jd_from_year) & (fm_df.jd < jd_to_year) & (fm_df.planet == 'Moon')]
	# fm_df['naks'] = [ nu.df.nid[math.floor(x) % 27] for x in fm_df.elong/(360/27)]
	fm_df['naks'] = [ math.floor(x) % 27 for x in fm_df.elong/(360/27)]


	fm_df['moon_dist'] = pd.cut(fm_df.r , cuts, labels=[str(x) for x in range(cuts)])
	# display(fm_df.describe(exclude=[np.number]))
	# display(pd.pivot_table(fm_df, index=['moon_dist'], values=['r'], aggfunc=[np.min, np.max, np.mean, np.median]))
	# display(fm_df.sort_values(by='jd'))
	maasas=[]
	for maasa in [m for m in [
		'M01-Ash', 'N02-Bha',  'M03-Kri',  'N04-Roh', 'M05-Mrg', 'N06-Ard', 'N07-Pun',  'M08-Pus', 'N09-Asl',
 		'M10-Mag', 'N11-PPal', 'M12-UPal', 'N13-Has', 'M14-Chi', 'N15-Swa', 'M16-Vis',  'N17-Anu', 'M18-Jye',
 		'N19-Mul', 'M20-PAsh', 'N21-UAsh', 'M22-Shr', 'N23-Dha', 'N24-Sha', 'M25-PBha', 'N26-UBha',
		'N27-Rev'
	] if m[0] == 'M'] :
		maasa = int(maasa[1:3])-1
		maasas.append(maasa)

	min_jd = fm_df.jd.min()
	max_jd = fm_df.jd.max()
	cut_to_plot = str(cut_to_plot)

	# moon_dist = pd.cut(fm_df.r, cuts).apply(lambda x: x.left)
	# ax = moon_dist.hist(width=0.3, cuts=cuts, alpha=0.5)
	if cuts > 1:
		max_dt = fm_df.iloc[-1]['date']
		min_dt = fm_df.iloc[0]['date']
		msg = f'{re.sub("T.*","",min_dt)} to {re.sub("T.*","",max_dt)}'
		ax = fm_df.r.hist(width=0.3, bins=cuts, alpha=0.5, figsize=(6,4))
		ax.set_title(f"Histogram of Full Moons by Earth-Moon Distance\n{msg}") 
		# plt.show()



	gap = (max_jd - min_jd)/chunks
	trend =[]
	for step in range (1,chunks+1)  : 
		fm_filt = fm_df[[ ( (min_jd +(step-1)*gap) <= j <= (min_jd +(step-0)*gap) ) for j in fm_df.jd]].sort_values(by='jd')
		# display(fm_filt.describe(exclude=[np.number]))
		fm_pvt = pd.crosstab(fm_filt.naks, fm_filt.moon_dist)
		markersize = 15
		mean_all_naks = fm_pvt[[cut_to_plot]].values.mean()
		mean_maasa_naks = fm_pvt[[m in maasas for m in fm_pvt.index]][[cut_to_plot]].values.mean()
		mean_not_maasa_naks = fm_pvt[[m not in maasas for m in fm_pvt.index]][[cut_to_plot]].values.mean()
		# print(f'{step}/{chunks} - {mean_all_naks =:.2f} - {mean_maasa_naks =:.2f} - {mean_not_maasa_naks =:.2f}')
		num_maasas_above_mean_all = (fm_pvt[[m in maasas for m in fm_pvt.index]][cut_to_plot].values > mean_all_naks).sum()
		num_not_maasas_above_mean_all = (fm_pvt[[m not in maasas for m in fm_pvt.index]][cut_to_plot].values > mean_maasa_naks).sum()
		# match_metric = (num_maasas_above_mean_all - num_not_maasas_above_mean_all)/num_maasas_above_mean_all
		# match_metric = (num_maasas_above_mean_all**2)/num_not_maasas_above_mean_all
		match_metric = (num_maasas_above_mean_all/12.0)/(num_not_maasas_above_mean_all/17.0)
		# trend.append([ step, mean_all_naks, mean_maasa_naks, mean_not_maasa_naks, match_metric])
		trend.append([ fm_filt.iloc[fm_filt.shape[0]//2,:].date, step, mean_all_naks, mean_maasa_naks, mean_not_maasa_naks, num_maasas_above_mean_all, num_not_maasas_above_mean_all, match_metric])

		if num_maasas_above_mean_all < maasa_threshold: continue

		continue

		ax = fm_pvt[[cut_to_plot]].plot.bar(stacked=True, figsize=(8,3), legend=False)
		ax.plot(fm_pvt.index, [mean_all_naks]*len(fm_pvt), '--', color='red')
		fm_pvt[[cut_to_plot]].plot.line(
			ax=ax 
			,marker='*' ,markersize=markersize ,ls=":" ,lw=0,color='red'
			,markevery=maasas
			,legend=False
		)
		ax.set_ylim(
			math.floor(2*fm_pvt[cut_to_plot].max())/5, 
			math.floor(5.1*fm_pvt[cut_to_plot].max())/5, 
			)
		ax.set_xticklabels(nu.df.nid, rotation=90, fontsize=12)
		for maasa in maasas:
			ax.get_xticklabels()[maasa].set_color("red")
		max_dt = fm_filt.iloc[-1]['date']
		min_dt = fm_filt.iloc[0]['date']
		# msg = f'{re.sub("T.*","",min_dt)} to {re.sub("T.*","",max_dt)} NaksMean {mean1:.2f} , MaasaMean {mean2:.2f}\n{num_maasas_above_mean1} maasa nakshatras have higher frequency than mean nakshatra'
		msg = f'{re.sub("T.*","",min_dt)} to {re.sub("T.*","",max_dt)}\n{num_maasas_above_mean_all} maasa nakshatras have higher frequency than mean nakshatra'
		ax.set_title(f'Histogram of {title_tag} by Naksatra \n {msg}', fontsize=10, color='blue')
		# plt.show()

	if  not False :
		trend = pd.DataFrame(trend, columns=['date', 'step',  'mean_all_naks', 'mean_maasa_naks', 'mean_not_maasa_naks', 'num_maasas_above_mean_all', 'num_not_maasas_above_mean_all', 'match_metric'])
		trend['date'] = trend.date.apply(lambda x: re.sub("......T.*","",x))
		ax = trend.plot(x='date', y=["num_maasas_above_mean_all" , "num_not_maasas_above_mean_all"], figsize=(10,3), legend=False, rot=90, kind='bar', stacked=True, color=['green', 'red'])
		ax.set_title(f'Degree of Alignment - Full moon Naḳshatras with Māsa names', fontsize=10, color='blue')

	# ax = trend.plot(x='date', y=["match_metric"], figsize=(8,3), legend=False, rot=90, kind='bar')
	# # create second y-axis
	# ax2 = ax.twinx()
	# ax = trend.plot(x='date', y=["num_maasas_above_mean_all" , "num_not_maasas_above_mean_all"], figsize=(8,3), legend=False, rot=90, kind='bar', ax=ax2, color=['green', 'red'])

	plt.show()

	# display(trend)
	1
	# ax.set_title(f'Histogram of Full Moon by Nasksatra \n { re.sub("T.*","",min_dt)} to {re.sub("T.*","",max_dt)}', fontsize=20, color='blue')


# !%%
def plot_moon_gruha_long_diff_hist():
	fm_df = get_full_moon_planet_pos(force=not True)
	fm_pvt = fm_df.pivot_table(index=['date', 'jd'], columns='planet', values='elong', aggfunc=np.mean).reset_index()
	# display(fm_pvt)
	fig, axes = plt.subplots(2,3 , figsize=(16,10), sharex=True, sharey=not True)
	GRS = ['Saturn', 'Jupiter', 'Mars', 'Venus', 'Mercury', 'Sun']
	for ix, p, ax in zip( range(len(GRS)),GRS , axes.flatten()) :
		(fm_pvt[p]-fm_pvt.Moon).hist(bins=100,ax=ax) 
		ax.set_title(f"Spread of \n{p} - Moon LongDiff\n at Full Moon")
	plt.show()

# !%%

def super_moon_histogram_by_epoch ():
	# plot_moon_gruha_long_diff_hist()
	plot_full_moon_distance_hist_by_naks(
		from_year=-1999, 
		num_years=1000, 
		chunks=20, 
		maasa_threshold=11, 
		cuts=7, 
		cut_to_plot=0,  
		title_tag='Super Moon') 
		
	# plot_full_moon_distance_hist_by_naks(from_year=-1999, num_years=1000, chunks=20, maasa_threshold=10, 
	# 					cuts=1, cut_to_plot=0,  title_tag='Full Moon') 

super_moon_histogram_by_epoch()

# %%
#%%
def get_moon_for_one_month(jd=PP.JD_BCE_1000_JAN_1, ndays=31):
	pp = PP.PlanetPos()
	dfs = [pp.get_planet_pos(jd+n).reset_index() for n in range(ndays)]
	moons = [ fd[fd.planet == 'Moon'] for fd in dfs]
	suns = [ fd[fd.planet == 'Sun'] for fd in dfs]


	moons = pd.concat(moons)[['jd', 'date', 'elati', 'elong' ,'r']]
	suns = pd.concat(suns)[['jd', 'date', 'elong']]
	moons['sun_elong'] = suns.elong.values
	moons['phase'] = (suns.elong.values - moons.elong.values) %360
	moons['phase'] = moons.phase.apply(lambda x: x if x < 180 else x-360)
	moons['paksha'] = moons.phase.apply(lambda x: 'krishna' if x >0 else 'shukla')

	return  moons

get_moon_for_one_month(jd=PP.JD_BCE_1000_JAN_1-365.25*1000)


#%%

if __name__ == "__main__":
	print (__package__)
	# get_moon_planet_pos ()
	# super_moon_histogram_by_epoch()

#%%

# def _plot_fm_hist_by_naks(fm_pvt, ax=None, markersize=10, maasa_threshold=8) -> None:
# 	"""
# 	Plot the histogram full moon by nakshatra for given input dataframe
# 	"""
# 	nu = NaksUtils.NaksUtils()
# 	maasas=[]
# 	for maasa in [m for m in [
# 		'M01-Ash', 'N02-Bha', 'M03-Kri', 'N04-Roh', 'M05-Mrg', 'N06-Ard', 'N07-Pun', 'M08-Pus', 'N09-Asl',
#  		'M10-Mag', 'N11-PPal', 'M12-UPal', 'N13-Has', 'M14-Chi', 'N15-Swa', 'M16-Vis', 'N17-Anu', 'M18-Jye',
#  		'N19-Mul', 'N20-PAsh', 'M21-UAsh', 'M22-Shr', 'N23-Dha', 'N24-Sha', 'M25-PBha', 'N26-UBha',
# 		'N27-Rev'
# 	] if m[0] == 'M'] :
# 		maasa = int(maasa[1:3])-1
# 		maasas.append(maasa)

# 	max_dt = fm_pvt.iloc[0]['date']
# 	min_dt = fm_pvt.iloc[-1]['date']

# 	# display(fm_pvt.sort_values(by=['jd']))
# 	fm_srs=pd.Series(pd.cut(fm_pvt.Moon, [0] + [ x*360/27 for x in range(1,27+1)]).value_counts().sort_index())
# 	fm_srs.index = range(27)
# 	mean1 = fm_srs.mean()
# 	mean2 = fm_srs[maasas].mean()
# 	num_maasas_above_mean1 = (fm_srs[maasas]>mean1).sum() 
# 	msg = f'{re.sub("T.*","",min_dt)} to {re.sub("T.*","",max_dt)} NaksMean {mean1:.2f} , MaasaMean {mean2:.2f} : {num_maasas_above_mean1}'
# 	# if mean1 > mean2 or num_maasas_above_mean1 < 7 : 
# 	if num_maasas_above_mean1 < maasa_threshold : 
# 		# print(msg)
# 		return

# 	ax= fm_srs.plot(
# 		figsize=(8,3) 
# 		,grid=True
# 		,marker='*' ,markersize=markersize ,ls=":" ,lw=0,color='red'
# 		,markevery=maasas
# 		# ,ax=ax
# 		)
# 	fm_srs.plot(
# 		figsize=(8,3) 
# 		,grid=True
# 		# ,marker='*' ,markersize=markersize ,
# 		,ls=":" ,lw=0.5, color='blue'
# 		,ax=ax
# 		)
# 	ax.plot(fm_srs.index, [mean1]*len(fm_srs), '--', color='red')
# 	ax.set_xticks(range(0,27))
# 	ax.set_xticklabels(nu.df.nid, rotation=60, fontsize=8)
# 	ax.set_xlabel('')
# 	ax.set_ylabel('# of Full Moons')
# 	# ax.set_ylim(200,230)
# 	# ax.set_xticklabels(nu.df.nid, rotation=60, fontsize=12)
# 	for maasa in maasas:
# 		ax.get_xticklabels()[maasa].set_color("red")
# 	# ax.set_title(f'Histogram of Full Moon by Nasksatra \n { re.sub("T.*","",min_dt)} to {re.sub("T.*","",max_dt)}', fontsize=20, color='blue')
# 	ax.set_title(f'Histogram of Full Moon by Naksatra \n {msg}', fontsize=10, color='blue')
# 	plt.show()
# # %%
# def plot_full_moon_hist_by_naks(from_year=-1999 , num_years=2000, chunks=4, maasa_threshold=8 ) -> None:
# 	"""
# 	Plot the histogram full moon instance count by nakshatra for date range divided into chunks
# 	The maasa_threshold is the number of maasa that must be above the mean to be considered for plotting
# 	"""
# 	fm_df = get_full_moon_planet_pos(force=not True)
# 	jd_from_year = toStelJD(f'{from_year:06d}-01-01T00:00:00')
# 	jd_to_year = jd_from_year+num_years*356.25
# 	fm_df = fm_df[ (fm_df.jd > jd_from_year) & (fm_df.jd < jd_to_year) & (fm_df.planet == 'Moon')]
# 	# print(f'jd_from_year {jd_from_year}')
# 	# print(f'jd_to_year {jd_to_year}')
# 	# display(fm_df.sort_values(by='jd'))

# 	fm_pvt = fm_df.pivot_table(index=['date', 'jd'], columns='planet', values='elong', aggfunc=np.mean).reset_index()
# 	# display(fm_pvt)

# 	min_jd = fm_pvt.jd.min()
# 	max_jd = fm_pvt.jd.max()
# 	gap = (max_jd - min_jd)/chunks
# 	for step in range (1,chunks+1)  :
# 		# fig,  axs = plt.subplots(4,1,_ figsize=(16,6), sharex=True)
# 		# axs = axs.flatten()
# 		_plot_fm_hist_by_naks(
# 			fm_pvt[[ ( (min_jd +(step-1)*gap) <= j <= (min_jd +(step-0)*gap) ) for j in fm_pvt.jd]]
# 			# ,axs[step-1]
# 			,15+0*3*step
# 			,maasa_threshold=maasa_threshold
# 		)
# # for yy in range(-2000,-900,100): plot_full_moon_hist_by_naks(yy, 100, chunks=1)	
# # %%

# %%
