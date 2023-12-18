#%%
from IPython.core.display import display_latex
from IPython.display import display
import pandas as pd
import numpy as np
from astropy.time import Time
from time import time
import math
import re

class NaksUtils:
	"""
	Utilities for the Naks project.
	"""
	def VGJ_TARAS(): 
		return  [
		'(α,β,γ) Ari',
		'(35,39,41) Ari',
		'(17,19,20,23,27,η) Tau',
		'(α,γ,λ) Ori',
		'(γ) Gem',
		'(α,γ,δ1,ε,θ2) Tau',
		'(α,β) Gem',
		'(δ) Cnc',
		'(δ,ε,ζ,η,ρ,σ) Hya',
		'(α,γ1,ε,ζ,η,μ) Leo',
		'(δ,θ) Leo',
		'(93,β) Leo',
		'(α,β,γ,δ,ε) Crv',
		'(α) Vir',
		'(α) Boo',
		'(α1,α2) Lib',
		'(β1,δ,π,ω1) Sco',
		'(α,ε,σ,(τ)) Sco',
		'(ζ2,θ,ι1,κ,λ,ν) Sco',
		'(γ,δ,ε,λ) Sgr',
		'(ζ,σ,τ,φ) Sgr',
		'(α,β,γ) Aql',
		'(α,β,γ2,δ) Del',
		'(λ) Aqr',
		'(α,β) Peg',
		'(γ,λ) Peg',
		'(ε,(α,ζ)) Psc',
	]

	def ABH_TARAS () : 
		return [
		'β Ari',
		'41 Ari',
		'η Tau',
		'α Tau',
		'λ Ori',
		'γ Gem',
		'β Gem',
		'δ Cnc',
		'ζ Hya',
		'α Leo',
		'δ Leo',
		'β Leo',
		'γ Crv',
		'α Vir',
		'α Boo',
		'α Lib',
		'δ Sco',
		'α Sco',
		'λ Sco',
		'δ Sgr',
		'σ Sgr',
		'β Del',
		'β Aqr',
		'α PsA',
		'α Peg',
		'λ Peg',
		'ζ Psc (α And)',
	]

	def ASTROGRAPHS(): 
		return [
		'Horseneck',
		'Bhaga (Perineum)',
		'Knife/Cleaver',
		'Cart',
		'Deer’s Head',
		'Bāhuḥ (Arm)/Red Dot',
		'Balance',
		'Śarāva (Pot-lid)',
		'Snake Head/Flag',
		'Enclosure',
		'Half-chair',
		'Half-chair',
		'Hasta (hand)',
		'Madhupuṣpa (Flower)',
		'Kīlaka (Wedge)',
		'Divider Rope',
		'Necklace',
		'Elephant Tusk',
		'Root/Scorpion Tail"',
		'Gajavikrama (Elephant Step)',
		'Siṁhaniṣadya (Lion seat)',
		'Ear/Yavamadhya (Barleyseed)',
		'Śakuni-pañjara (Bird cage)',
		'Puṣpopacāra (Flower Boquet)',
		'Cow’s Foot',
		'Cow’s Foot',
		'Boat2',
		]

	def ll_to_rd (cls, lat, lon, obl = 23.439281):
		'''
		Declination δ=arcsin(cosε×sinβ+sinε×cosβ×sinλ)
		Right ascension α=arctan((cosε×sinλ−sinε×tanβ)/cosλ)
				α=atan2(cosβsinλcosε−sinβsinε,cosβcosλ) ( better)
		Where
		β = ecliptic geocentric latitude
		λ = ecliptic geocentric longitude
		ε = obliquity of the ecliptic
		'''
		lat -= 180 if lat>180 else 0
		lon -= 180 if lon>180 else 0
		R = np.pi/180
		lat = lat * R
		lon = lon * R
		obl = obl * R

		s,c, si, at2 = np.sin, np.cos, np.arcsin, np.arctan2
		decl = si(c(obl)*s(lat) + s(obl)*c(lat)*s(lon))
		ra = at2(c(lat)*s(lon)*c(obl) - s(lat)*s(obl), c(lat)*c(lon))
		return lat/R, lon/R, ra/R, decl/R

	def test_ll_to_rd( cls ):
		display (
		pd.DataFrame([ cls.ll_to_rd(0,lon) for lon in range(0,361,45)], columns=['lat', 'lon', 'ra', 'decl']).applymap(lambda x: x).style.set_precision(2),
		pd.DataFrame([ cls.ll_to_rd(lat,0) for lat in range(-90,91,45)], columns=['lat', 'lon', 'ra', 'decl']).applymap(lambda x: x).style.set_precision(2)
		)

	def rd_to_ll (cls, ra, decl, obl = 23.439281):
		'''
		Where
		β = ecliptic geocentric latitude
		λ = ecliptic geocentric longitude
		ε = obliquity of the ecliptic
		δ = declination
		α = right ascension

		Lat sin(β) = sin(δ) cos(ε) - cos(δ) sin(ε) sin(α) 
		Lon cos(λ) cos(β) = cos(α) cos(δ)
		'''
		R = np.pi/180
		ra = ra * R
		decl = decl * R
		obl = obl * R

		s,c, si, at2, ac = np.sin, np.cos, np.arcsin, np.arctan2, np.arccos
		lat = si(s(decl)*c(obl) - c(decl)*s(obl)*s(ra))
		lon = 0 if (-1e-4<=c(lat)<=1e-4) else ac(c(ra)*c(decl)/c(lat)) 
		if ( ra > np.pi and ra < 2*np.pi ):
			lon = 2*np.pi - lon
		if math.isnan(lon):
			lon = 0

		return  ra/R, decl/R, lat/R, lon/R
	

	def test_ll_to_rd2( cls ):
		df = pd.concat ( [
			pd.DataFrame([ cls.rd_to_ll(ra,dec) for dec in range(0,361,55) for ra in range(0,361,55)], columns=[ 'ra', 'decl', 'lat', 'lon']).applymap(lambda x: x),
		]).reset_index(drop=True)

		dx = df.apply(lambda x: pd.Series(cls.ll_to_rd(x.lat,x.lon)), axis=1)
		dx.columns = ['lat1', 'lon1', 'ra1', 'decl1']
		# display(df.join(dx).style.set_precision(2))
		dy = df.join(dx)#.applymap(lambda x: int(x*10)).astype(int)
		dy = dy.assign (
			# sum1 = lambda y: y.apply (lambda x :pd.Series( [
			# 	(1000*abs(x.ra-x.ra))%(360*1000-10)/1000 #< 1e-1
			# 	,(1000*abs(x.decl1-x.decl))%(360*1000-10)/1000 #< 1e-1
			# 	,(1000*abs(x.lat1-x.lat))%(360*1000-10)/1000 #< 1e-1
			# 	,(1000*abs(x.lon1-x.lon))%(360*1000-10)/1000 #< 1e-1
			# 	]).sum() , axis=1),
			check1 = lambda y: y.apply (lambda x :pd.Series( [
				(1000*abs(x.ra-x.ra))%(360*1000-10)/1000 < 1e-1
				,(1000*abs(x.decl1-x.decl))%(360*1000-10)/1000 < 1e-1
				,(1000*abs(x.lat1-x.lat))%(360*1000-10)/1000 < 1e-1
				,(1000*abs(x.lon1-x.lon))%(360*1000-10)/1000 < 1e-1
				]).sum()==4, axis=1),
		)
		display(dy.shape, dy[dy.check1==False].shape, dy.sample(10))
		display(dy[dy.check1==False].style.set_caption('Failed Test'))
		




	def __init__(self, force=False):
		try :
			if force : raise FileNotFoundError
			self.df = pd.read_csv('../datasets/n27_full_meta.csv')
			self.df28 = pd.read_csv('../datasets/n28_full_meta.csv')
			self.df28_good = pd.read_csv('../datasets/n28_good_meta.csv')
			return
		except :
			print('No data file found. Regenerating...')
			self.df = self._regenerate_df()
			self.df28 = self._regenerate_df28()


	def _regenerate_df28(self):
		'''Need to make this better'''
		return pd.read_csv('../datasets/n28_full_meta.csv')

	def _regenerate_df(self):
		'''Combine various pieces of n27'''
		df1 = pd.read_csv("../datasets/n27_limited_meta.csv")
		df2 = pd.read_csv("../datasets/n27.csv")
		df3 = pd.read_csv("../datasets/naks-marga-veethi.tsv", sep="\t")
		df4 = pd.read_csv("../datasets/n27_lon_divisions.csv")
		df5 = pd.read_csv("../datasets/naks_eq_bounds_report.csv")
		df = pd.merge( pd.merge(pd.merge(pd.merge(
			df1, 
			df2, on="nid", how="inner"),
			df3, on="nid", how="inner"),
			df4, on="nid", how="inner"),
			df5[['nid','num_stars_in_naks' ]], on="nid", how="inner")
		df.drop(
			columns=["naks_y"], inplace=True
		)
		LON_EQ, LON_UE = 'lon' , 'lon_ue' # equal_division_start,  unequal_division_start 
		SPAN_EQ, SPAN_UE = 'span' , 'span_ue' # equal_division_start,  unequal_division_start 
		df.rename(
			columns={
				"naks_x": "naks"
				,"Marga": "marga"
				,"Veethi": "veethi"
				,'num_stars_in_naks' : 'vgj_cnt'
				,"Eq" : LON_EQ      
				,"Ue" : LON_UE
				,"gname" : "proxy"
				}, 
			inplace=True
		)
		divs =  (df[LON_EQ].diff() % 360).shift(-1)
		divs[-1:]=13.33
		df[SPAN_EQ] = divs 

		divs =  (df[LON_UE].diff() % 360).shift(-1)
		divs[-1:]=13.33
		df[SPAN_UE] = divs
		df[LON_EQ] = (df[LON_EQ] - df[LON_EQ][0]) % 360
		df[LON_UE] = (df[LON_UE] - df[LON_UE][0]) % 360

		df['vgj_stars'] = NaksUtils.VGJ_TARAS()
		df['abh_stars'] = NaksUtils.ABH_TARAS()
		df['shape'] = NaksUtils.ASTROGRAPHS()

		df = df [[
			'nnid',
			'nid',
			'naks',
			'enaks',
			'daivata',
			'marga',
			'veethi',
			'shape',
			'vgj_cnt',
			'vgj_stars',
			'proxy',
			'sname',
			'hip',
			'abh_stars',
			LON_EQ, SPAN_EQ,
			LON_UE, SPAN_UE,
		]]
		self.df = df
		# self.df.to_csv("../datasets/n27_full_meta.csv")
		return df



def _main():
	pd.options.display.float_format = '{:.2f}'.format
	nu = NaksUtils()
	# display(nu.df)
	# display(nu.df28[['nid', 'scp_muhurta']][21:])
	# display(nu.df28[['nid', 'scp_muhurta']][:21])
	# display(nu.df28.scp_muhurta.sum() , nu.df28.scp_ahoratra.sum())
	# display(nu.df28_good.scp_muhurta.sum() , nu.df28_good.columns)
	# nu.test_ll_to_rd()
	nu.test_ll_to_rd2()
	print(nu.rd_to_ll (ra=-17.73, decl=-7.52, obl = 23.439281))
	print(nu.rd_to_ll (ra=-17.73+360, decl=-7.52, obl = 23.439281))
	print(nu.rd_to_ll (ra=-17.73+360, decl=-7.52+360, obl = 23.439281))
	print(nu.rd_to_ll (ra=-17.73, decl=-7.52+360, obl = 23.439281))


if __name__ == "__main__" :
	_main()
# %%
# pandas datafrane style print aligning
def _print_align(df):
	pd.set_option('display.precision', 2)
	pd.set_option('display.width', 200)
	pd.set_option('display.max_rows', 100)
	pd.set_option('display.max_columns', 20)
	pd.set_option('display.max_colwidth', 100)
	pd.set_option('display.float_format', '{:.2f}'.format)	
	pd.set_option('display.notebook_repr_html', True)
	pd.set_option('display.max_seq_items', None)




def rotate(s, n):
	return s.shift(-n)

# %%
