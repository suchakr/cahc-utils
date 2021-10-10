#%%
"""
Class to compute planet positions given JD. From 

	http://www.stjarnhimlen.se/comp/ppcomp.html and 
	http://www.stjarnhimlen.se/comp/tutorial.html

Usage
-----
	pp = PlanetPos()
	display(pp.get_planet_pos(JD_BCE_3000_JAN_1)) # gets the planet position for JD_BCE_3000_JAN_1

Output
------
	planet		jd	date				elong	elati	r	geo_r	geoc_x	geoc_y	geoc_z
	Jupiter	625332.50	-3000-01-01T00:00:00.000	147.99	1.84	5.39	4.66	-3.95	2.47	0.15
	Mars	625332.50	-3000-01-01T00:00:00.000	201.09	1.11	1.50	1.30	-1.22	-0.47	0.03
	Mercury	625332.50	-3000-01-01T00:00:00.000	280.80	-1.71	0.36	1.35	0.25	-1.33	-0.04
	Moon	625332.50	-3000-01-01T00:00:00.000	82.79	5.14	57.87	57.87	7.23	57.19	5.18
	Saturn	625332.50	-3000-01-01T00:00:00.000	82.17	0.73	9.49	8.54	1.16	8.46	0.11
	Sun	625332.50	-3000-01-01T00:00:00.000	281.09	-0.00	1.00	1.00	0.19	-0.98	-0.00
	Venus	625332.50	-3000-01-01T00:00:00.000	313.16	-0.93	0.72	1.33	0.91	-0.97	-0.02

	jd - Julian Day
	date - Date in format 'yyyy-mm-ddThh:mm:ss.xxx'
	elong - Ecliptic Longitude of the planet (deg) on date 
	elati - Ecliptic Latitude of the planet (deg) on date
	r - Distance to the planet (AU) from Sun , Moon distance is from Earth in earth diameters, Sun is Earth-Sun Distance 
	geo_r - Distance to the planet (AU)  from Earth in Earth-centered frame
	geoc_x - Distance to the planet (AU) from Earth in Earth-centered frame in x-direction
	geoc_y - Distance to the planet (AU) from Earth in Earth-centered frame in y-direction
	geoc_z - Distance to the planet (AU) from Earth in Earth-centered frame in z-direction
"""

from IPython.display import display
import math
import pandas as pd
from astropy.time import Time
import re
from io import StringIO
# import numpy as np
# import datetime
# import time

JD_2000 = 2451543.5
JD_BCE_3000_JAN_1   = 625332.5  # -3000-01-01T00:00:00.000
JD_JEPPY_KALI_YUGA  = 588465.5  # -3101-01-23T00:00:00.000  ( +25 gets to KY 17/Feb/-3101 )
JD_JEPPY_OFFSET     = 2415020   # 1899-12-31T12:00:00.000

##  Vector shorthands for sin, cos, tan ...
_cos = lambda x: x.apply (lambda y: math.cos(y*math.pi/180))
_sin = lambda x: x.apply (lambda y: math.sin(y*math.pi/180))
_atan = lambda x: x.apply (lambda y: math.atan(y)*180/math.pi)
_sqrt = lambda x: x.apply (lambda y: math.sqrt(y))
_dist = lambda x,y,z,L=2 : (x**L+y**L+z**L)**(1/L)
_atan2 = lambda y,x: pd.Series(list(zip(y,x)), index=(y.index)).apply (lambda e: ((arctan_stjarnhimlen(e[1], e[0])) +360) %360 ) #.reindex(index=y.index)
_atan1 = lambda y,x: (y/x).apply (lambda e: math.atan(e)*180/math.pi)

## borrowed from Paul Schlyter's tutorial - regular math.atan doesnt have these properties
def arctan_stjarnhimlen(x,y):
	if x==0:
		if y==0:
			return 0
		elif y>0:
			return 90
		else:
			return -90
	elif x>0:
		return math.atan(y/x)*180/math.pi
	else: ## x<0
		if y>=0:
			return math.atan(y/x)*180/math.pi + 180
		else:
			return math.atan(y/x)*180/math.pi - 180


def rev(x):
	rev = x - math.trunc(x/360.0)*360.0
	if rev < 0.0: rev = rev+360.0
	return rev


def solve_E(M, e):
	TOLERANCE = 1E-6
	e_deg = e*180/math.pi

	## E_ is in degree
	E_ = M + e_deg*_sin(M)

	for n in range(1, 500):
		delta_M = M - (E_ - e_deg*_sin(E_))
		delta_E = delta_M/(1 - e*_cos(E_))
		if (delta_E.abs() < TOLERANCE).all():
			## print(f'converged after {n} iterations')
			break
		E_ = E_ + delta_E
	return E_

STJARMHIMLEN_PARAMS='''
planet,M,M_d,N,N_d,a,a_d,e,e_d,i,i_d,w,w_d
Jupiter,19.8950,+0.0830853001,100.4542,+2.76854E-5,5.20256,0,0.048498,+4.469E-9,1.3030,-1.557E-7,273.8777,+1.64505E-5
Mars,18.6021,+0.5240207766,49.5574,+2.11081E-5,1.523688,0,0.093405,+2.516E-9,1.8497,-1.78E-8,286.5016,+2.92961E-5
Mercury,168.6562,+4.0923344368,48.3313,+3.24587E-5,0.387098,0,0.205635,+5.59E-10,7.0047,+5.00E-8,29.1241,+1.01444E-5
Moon,115.3654,+13.0649929509,125.1228,-0.0529538083,60.2666,0,0.054900,0,5.1454,0,318.0634,+0.1643573223
Saturn,316.9670,+0.0334442282,113.6634,+2.38980E-5,9.55475,0,0.055546,-9.499E-9,2.4886,-1.081E-7,339.3939,+2.97661E-5
Sun,356.0470,+0.9856002585,0.0,0,1.000000,0,0.016709,-1.151E-9,0.0,0,282.9404,+4.70935E-5
Venus,48.0052,+1.6021302244,76.6799,+2.46590E-5,0.723330,0,0.006773,-1.302E-9,3.3946,+2.75E-8,54.8910,+1.38374E-5
'''

class PlanetPos:
	"""Class to compute planet position given JD"""
	def __init__(self):
		""" No parameters needed. Initializes with in build STJARMHIMLEN_PARAMS"""
		stj_params_str = '\n'.join([ x for x in  STJARMHIMLEN_PARAMS.split("\n") if len(x) ])
		PP2 = pd.read_csv(StringIO(stj_params_str), sep=',', comment='#').set_index('planet')	
		# PP2 = pd.read_csv('./planet_params_stjarmhimlen.csv').set_index('planet')
		PP2['L'] = PP2['M'] + PP2['w'] + PP2['N']
		PP2['L_d'] = PP2['M_d'] + PP2['w_d'] + PP2['N_d']
		PP2_Rate = PP2.loc[:, ['a_d', 'e_d', 'i_d', 'L_d', 'M_d', 'N_d' , 'w_d'] ]
		PP2_Base = PP2.loc[:, ['a', 'e', 'i', 'L', 'M', 'N' , 'w'] ]
		self.PP2 = PP2
		self.PP2_Rate = PP2_Rate
		self.PP2_Base = PP2_Base

	def get_planet_pos(self, jd=JD_BCE_3000_JAN_1, isot=None) :
		"""For the given julian day(jd) returns a dataframe with postions of 5 gruhas(mercury,venus,mars,jupiter,saturn,sun+,moon)"""
		if not isot:
			isot = Time(jd, format='jd').isot
			# Need a Stelllarium utility to convert from JD to isot
			# As the input jd is stell normalized, we need to convert it to the normal jd
			# The Astropy Time cals date string is shifted by a varaible value depending of jd
			# Stellarium/stellarium/src/core/StelUtils.cpp getDateFromJulianDay function to be ported to python
		T = (jd - JD_2000)  # /36525
		# print(jd, isot)
		params = self.PP2_Base + self.PP2_Rate.values*T

		params['M'] = params['M'].apply(lambda x: rev(x))
		waileo = params
		e_star = waileo['e'] * 180/math.pi
		waileo = waileo % 360

		En = solve_E(waileo['M'], waileo['e'])
		waileo['E'] = En
		# display(waileo[list("NiwaeMEL")])

		x_prime = waileo['a']*(_cos(En) - waileo['e'])
		y_prime = waileo['a']*_sin(En) * _sqrt(1 - waileo['e'] * waileo['e'])
		v_nu = _atan2(y_prime, x_prime)
		r = _sqrt(y_prime*y_prime + x_prime*x_prime)
		# display(x_prime.Moon, y_prime.Moon, v_nu.Moon, r.Moon, "========")

		lon = (v_nu + waileo['w']) % 360
		N = waileo['N']
		I = waileo['i']

		# display(lon.Moon, N.Moon, I.Moon, "=======")
		## ecliptic rectangular, also called xh,yh,zh
		x_eclip = r * (_cos(N) * _cos(lon) - _sin(N) * _sin(lon) * _cos(I))
		y_eclip = r * (_sin(N) * _cos(lon) + _cos(N) * _sin(lon) * _cos(I))
		z_eclip = r * _sin(lon) * _sin(I)
		# display(x_eclip.Moon, y_eclip.Moon, z_eclip.Moon,"======")

		geoc_x = x_eclip + x_eclip['Sun']
		geoc_y = y_eclip + y_eclip['Sun']
		geoc_z = z_eclip + z_eclip['Sun']

		for obj in ['Moon', 'Sun']:
			geoc_x[obj] = x_eclip[obj]
			geoc_y[obj] = y_eclip[obj]
			geoc_z[obj] = z_eclip[obj]

		geo_r = _dist(geoc_x, geoc_y, geoc_z)

		ecl_long = _atan2(geoc_y, geoc_x)
		ecl_lati = _atan1(geoc_z, _sqrt(geoc_y**2 + geoc_x**2))
		# display(ecl_long.Moon, ecl_lati.Moon,"======")
		# display(T, jd, isot )

		if True:  # block to add moon perturbations
			# Mean Anomaly of the Sun and the Moon
			Ms, Mm = waileo['M'].Sun, waileo['M'].Moon
			Nm = waileo['N'].Moon  # Longitude of the Moon's node
			# Argument of perihelion for the Sun and the Moon
			ws, wm = waileo['w'].Sun, waileo['w'].Moon
			Ls = Ms + ws      # Mean Longitude of the Sun  (Ns=0)
			Lm = Mm + wm + Nm  # Mean longitude of the Moon
			D = Lm - Ls       # Mean elongation of the Moon
			F = Lm - Nm       # Argument of latitude for the Moon

			def dsin(x): return math.sin(x*math.pi/180)

			ecl_long_pert_moon = (
			+0.658 * dsin(2*D)  # (the Variation)
			- 1.274 * dsin(Mm - 2*D)  # (the Evection)
			- 0.186 * dsin(Ms)  # (the Yearly Equation)
			- 0.059 * dsin(2*Mm - 2*D)
			- 0.057 * dsin(Mm - 2*D + Ms)
			+ 0.053 * dsin(Mm + 2*D)
			+ 0.046 * dsin(2*D - Ms)
			+ 0.041 * dsin(Mm - Ms)
			- 0.035 * dsin(D)  # (the Parallactic Equation)
			- 0.031 * dsin(Mm + Ms)
			- 0.015 * dsin(2*F - 2*D)
			+ 0.011 * dsin(Mm - 4*D)
			)

			ecl_lati_pert_moon = (
			-0.173 * dsin(F - 2*D)
			- 0.055 * dsin(Mm - F - 2*D)
			- 0.046 * dsin(Mm + F - 2*D)
			+ 0.033 * dsin(F + 2*D)
			+ 0.017 * dsin(2*Mm + F)
			)

			ecl_long.Moon += ecl_long_pert_moon
			ecl_lati.Moon += ecl_lati_pert_moon

		geoc_r = _dist(geoc_x, geoc_y, geoc_z)
		geoc_r.Moon = geoc_r.Moon + geoc_r.Sun
		geoc_r.Sun = geoc_r.Moon
		geoc_r.Moon = geoc_r.Moon + geoc_r.Sun
		geoc_r.Sun

		ans = pd.DataFrame({
			'jd': ecl_long.apply(lambda v: jd), 
			'date': ecl_long.apply(lambda v: isot), 
			'elong': ecl_long, 
			'elati': ecl_lati, 
			'r': r,
			'geo_r': geo_r, 
			'geoc_x': geoc_x, 
			'geoc_y': geoc_y, 
			'geoc_z': geoc_z, 
		})

		return ans

	def test():
		"""Computes and prints the planet positions dataframe"""
		print('PlanetPos test')
		pp = PlanetPos()
		sf = pd.options.display.float_format
		pd.options.display.float_format = '{:.2f}'.format
		display(pp.get_planet_pos(JD_BCE_3000_JAN_1))
		pd.options.display.float_format = sf

	def sanity_check_with_stellarium():
		"""Plots the diff between computed and stellarium pre-scraped longitidues"""
		import re
		pp = PlanetPos()
		sanity_df = pd.DataFrame([ re.sub("^\t+","",x).split("\t") for x in 
		'''
		0	Moon	-3012-01-02T12:00:00	620926	351.0605397341978	3.5639201681886887
		1	Moon	-2912-01-02T12:00:00	657451	287.1073876406191	-2.2227465620224542
		2	Moon	-2812-01-02T12:00:00	693976	242.44381800152084	-5.798126823045912
		3	Moon	-2712-01-02T12:00:00	730501	181.6325648199842	-1.2864753630676984
		4	Moon	-2612-01-02T12:00:00	767026	133.9091638620454	4.282711065043612
		5	Moon	-2512-01-02T12:00:00	803551	82.28854073552246	0.2180987278098843
		6	Moon	-2412-01-02T12:00:00	840076	26.76599562368953	-5.49466148658984
		7	Moon	-2312-01-02T12:00:00	876601	343.44715952808883	-3.0910844102628237
		8	Moon	-2212-01-02T12:00:00	913126	279.7464163293747	2.8084014100318644
		9	Moon	-2112-01-02T12:00:00	949651	237.09592455457064	2.5823140073542925
		10	Moon	-2012-01-02T12:00:00	986176	171.7442844328694	-3.3614427283095907
		11	Moon	-1912-01-02T12:00:00	1022701	132.54038190376815	-5.178693285518665
		12	Moon	-1812-01-02T12:00:00	1059226	70.39908409899664	0.16775924112087995
		13	Moon	-1712-01-02T12:00:00	1095751	26.30329990446946	4.216615467391569
		14	Moon	-1612-01-02T12:00:00	1132276	331.0151242074734	-1.3529928185854017
		15	Moon	-1512-01-02T12:00:00	1168801	277.1173566335984	-5.844691115303167
		16	Moon	-1412-01-02T12:00:00	1205326	226.62721682467281	-2.208507696141795
		17	Moon	-1312-01-02T12:00:00	1241851	168.0271338314494	3.870938973936796
		18	Moon	-1212-01-02T12:00:00	1278376	127.32168645766644	0.9290564649247705
		19	Moon	-1112-01-02T12:00:00	1314901	63.14624599367218	-4.506070023928983
		'''.split("\n") if len(re.sub("^\t+","",x)) ], columns=['idx', 'obj', 'dt', 'jd', 'lon', 'lat'])
		# display(sanity_df)
		offset = 8/24.0
		ans = sanity_df.apply(lambda x: [
			x['dt'], float(x['jd'])+ offset,
			pp.get_planet_pos(float(x.jd) + offset ).loc['Moon', 'elong'] - float(x.lon), 
			pp.get_planet_pos(float(x.jd) + offset ).loc['Moon', 'elong'], 
			x.lon, ], axis=1)
		sdf = pd.DataFrame(ans.tolist(), 
			columns=[
				'dt','jd', 'diff','lon_astro', 'lon_stel'
			]).astype({
			'diff':float
			,'lon_astro':float
			,'lon_stel':float
			})
		sf = pd.options.display.float_format
		pd.options.display.float_format = '{:.2f}'.format
		display(sdf)
		pd.options.display.float_format = sf
		'''
			dt			jd		diff	lon_astro	lon_stel
		0	-3012-01-02T12:00:00	620926.33	-2.57	348.49		351.06
		1	-2912-01-02T12:00:00	657451.33	-3.54	283.57		287.11
		2	-2812-01-02T12:00:00	693976.33	-0.98	241.46		242.44
		3	-2712-01-02T12:00:00	730501.33	-3.75	177.88		181.63
		4	-2612-01-02T12:00:00	767026.33	1.12	135.03		133.91
		5	-2512-01-02T12:00:00	803551.33	-3.09	79.20		82.29
		6	-2412-01-02T12:00:00	840076.33	1.03	27.79		26.77
		7	-2312-01-02T12:00:00	876601.33	-2.81	340.63		343.45
		8	-2212-01-02T12:00:00	913126.33	0.18	279.93		279.75
		9	-2112-01-02T12:00:00	949651.33	-0.98	236.11		237.10
		10	-2012-01-02T12:00:00	986176.33	0.36	172.11		171.74
		11	-1912-01-02T12:00:00	1022701.33	1.39	133.93		132.54
		12	-1812-01-02T12:00:00	1059226.33	-0.12	70.28		70.40
		13	-1712-01-02T12:00:00	1095751.33	1.65	27.95		26.30
		14	-1612-01-02T12:00:00	1132276.33	-0.98	330.03		331.02
		15	-1512-01-02T12:00:00	1168801.33	1.92	279.04		277.12
		16	-1412-01-02T12:00:00	1205326.33	0.19	226.82		226.63
		17	-1312-01-02T12:00:00	1241851.33	2.59	170.62		168.03
		18	-1212-01-02T12:00:00	1278376.33	1.65	128.97		127.32
		19	-1112-01-02T12:00:00	1314901.33	2.12	65.27		63.15
		'''
		sdf.dt = sdf.dt.apply(lambda x: re.sub("T.*","",x))
		sdf =sdf.set_index('dt')
		ax = sdf[['lon_astro', 'lon_stel']].plot(kind='line', grid=True, marker="*" , markersize=20, rot=60, figsize=(20,12), fontsize=25, lw=1, ls=':')
		ax.legend(['lon_astro - fast compute', 'lon_stel - slow stel scrape'], loc='lower center', fontsize=20) 
		ax = sdf[['diff']].plot(ax=ax.twinx(),rot=60, grid=not True, color='red', lw=1, ls=':',  marker='x', markersize=12, fontsize=20) 
		ax.set_ylabel('diff', color='red', fontsize=20)
		ax.legend(['diff'], loc='lower right', fontsize=20) 
		ax.set_title('Moon Longitudes - Compute vs Scrape', fontsize=20)
		return ans


#%%
if __name__ == '__main__':
	sdf = PlanetPos.sanity_check_with_stellarium()
