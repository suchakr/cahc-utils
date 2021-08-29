#%%
from IPython.core.display import display_latex
from IPython.display import display
import math
from astropy.coordinates.representation import PhysicsSphericalRepresentation
import pandas as pd
import numpy as np
from astropy.time import Time
from time import time
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

	def __init__(self, force=False):
		try :
			if force : raise FileNotFoundError
			self.df = pd.read_csv('../datasets/n27_full_meta.csv')
			return
		except :
			print('No data file found. Regenerating...')
			pass

		
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
		self.df.to_csv("../datasets/n27_full_meta.csv")



def _main():
	pd.options.display.float_format = '{:.2f}'.format
	nu = NaksUtils()
	display(nu.df)


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


