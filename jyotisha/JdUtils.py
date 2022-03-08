"""Convert Date to Julian Day number """
#%%
from IPython.display import display
import math
import pandas as pd
import numpy as np
from astropy.time import Time
from time import time
import re

#%%
def gregJD(Y, M, D, H=23, MM=59, S=59) :
	"""
	Lifted from https://en.wikipedia.org/wiki/Julian_day 
	
	Converting Gregorian calendar date to Julian Day Number
	The algorithm is valid for all (possibly proleptic) Gregorian calendar dates after November 23, −4713. 
	Divisions are integer divisions towards zero, fractional parts are ignored.[68]

	JDN = (1461 × (Y + 4800 + (M − 14)/12))/4 +(367 × (M − 2 − 12 × ((M − 14)/12)))/12 − (3 × ((Y + 4900 + (M - 14)/12)/100))/4 + D − 32075
	"""
	return (1461 * (Y + 4800 + (M-14)/12))/4 +(367 * (M-2 - 12 * ((M - 14)/12)))/12 - (3 * ((Y + 4900 + (M - 14)/12)/100))/4 + D - 32075 + H/24 + MM/(24*60)  + S/(24*60*60)

def julianJD(Y, M, D, H=23, MM=59, S=59) :
	"""
	Lifted from https://en.wikipedia.org/wiki/Julian_day 

	Converting Julian calendar date to Julian Day Number
	The algorithm[69] is valid for all (possibly proleptic) Julian calendar years ≥ −4712, that is, for all JDN ≥ 0. Divisions are integer divisions, fractional parts are ignored.

	JDN = 367 × Y − (7 × (Y + 5001 + (M − 9)/7))/4 + (275 × M)/9 + D + 1729777

	"""
	return (367 * Y - (7 * (Y + 5001 + (M - 9)/7))/4 + (275 * M)/9 + D + 1729777) + H/24 + MM/(24*60)  + S/(24*60*60)

def _stelJD(y,  m,  d,  h=23,  mm=59, s=59) :
	""" 
	Code from Stellarium - alternate JD  ( algo2 really, algo1 has QT dependency not easy in Python)

	https://github.com/Stellarium/stellarium/blob/master/src/core/StelUtils.cpp getJDFromDate_alg2 function
	https://github.com/Stellarium/stellarium/blob/1e617e49918ab2e5e5fad318dd1ab4024eb1e41c/src/core/StelUtils.cpp#L892
	"""
	extra = (100.0* y) + m - 190002.5;
	rjd = 367.0 * y;
	rjd -= math.floor(7.0*(y+math.floor((m+9.0)/12.0))/4.0);
	rjd += math.floor(275.0*m/9.0) ;
	rjd += d;
	rjd += (h + (mm + s/60.0)/60.)/24.0;
	rjd += 1721013.5;
	rjd -= 0.5*extra/abs(extra);
	rjd += 0.5;
	return rjd;

def stelJD(y,  m,  d, h=23,  mm=59, sec=59) :
	"""
	The JD number of this matches with Stellarium's JD number compared to AstroPy's JD number.
	  Deltas from comparing _stelAltJD o/p with Stellarium interactive
	  The added delta gets the same result as seem in Stellarium
	"""
	# h, mm, s = 12,0,0  # validated for these hour,minute,sec values
	s = _stelJD(y,  m,  d,  h,  mm, sec)
	(y,  m,  d,  h,  mm, sec)	=  (int(x) for x in (y,  m,  d,  h,  mm, sec))
	delta = 100000000*1
	if s< 2299148.5 : delta = 12 # Before including 1582-10-04 
	elif 2299148.5 <= s < 2299158.5 : # Between 1582-10-05 and 1582-10-14 both inclusive 
		raise ValueError(
			f"Invalid Date {y:04d}-{m:02d}-{d:02d} {h:02d}:{mm:02d}:{sec:02d}" 
			+ " between 1582-10-05 and 1582-10-14 both inclusive"
			)
	elif 2299158.5 <= s < 2342029.5 : delta = 2 # between 1582-10-15 and 1700-02-28 both including
	elif 2342029.5 <= s < 2342030.5  : # there is no 1700-02-29
		raise ValueError(
			f"Invalid Date {y:04d}-{m:02d}-{d:02d} {h:02d}:{mm:02d}:{sec:02d} " 
			)
	elif 2342030.5 <= s < 2378554.5: delta = 1 # between 1700-03-01 and 1800-02-28 both including
	elif 2378554.5 <= s < 2378555.5 : # there is no 1800-02-29
		raise ValueError(
			f"Invalid Date {y:04d}-{m:02d}-{d:02d} {h:02d}:{mm:02d}:{sec:02d} " 
			)
	elif s >= 2378555.5 : delta = 0 # After including 1800-03-01
	if delta > 100: print ("Invalid Date maybe? " , y,m,d,h,mm,sec,s, delta)
	return (s + delta)

def toStelJD(datestr:str) -> float:
	"""Convert a date string to a JD"""
	(y,m,d,hh,mm,ss) =  re.match("([\-]?\d+).(\d+).(\d+).(\d+).(\d+).(\d+)",datestr).groups()
	(y,m,d,hh,mm,ss) = (int(y),int(m),int(d),int(hh),int(mm),int(ss))
	return stelJD(y,m,d,hh,mm,ss)

def find_and_check_date_range_and_delta_params_fo_stel_alt():
	"""
	Tuning function
	This is done now and the stel_alt date ranges and params are finalized - unless some some bugs surface

	Compute JD using various porgrammatic methods for a set of carefully selected dates
	The stel_alt method is the method of interest others are for evaluation

	Then for thes same dates, compute JD using the Stellarium script
	Using the differences seen btween stel_alt and the Stellarium script 
	  tune the date range and delta parameters for those dates in stel_alt method

	Iterate until the computation of JD using the Stellarium script and stel_alt agrees
	"""

	# Part 1 - compute JD using various porgrammatic methods for a set of carefully selected dates
	#======================================================================
	jdf = pd.DataFrame(
	[ [ 
		f'{y:04d}-{m:02d}-{d:02d}T23:59:59' if y>=0 else f'{y:06d}-{m:02d}-{d:02d}T23:59:59'
		, gregJD(y,m,d)
		, julianJD(y,m,d)
		, Time(f'{y:04d}-{m:02d}-{d:02d}T23:59:59' if y>=0 else f'{y:06d}-{m:02d}-{d:02d}T23:59:59').jd
		, stelJD(y,m,d)
	] for y,m,d in [ # carefully selected dates 
		(-4712,1,1),  
		# (-1952,5,17), 
		# (-1000,1,1) , 
		# (-1,1,1) , 
		# (0,1,1) ,     
		# (1500,1,1) ,  
		# (1582,11,15), 
		(1582,10,3),  
		(1582,10,4),  # s += (12 if s<= 2299148)
		#========================================
		#(1582,10,10), # blackhole  2299149 <= s <= 2299158
		#========================================
		(1582,10,15), # s += (2 if 2299159 <= s <= 2342029)
		(1700,2,28),       
		#========================================
			# blackhole  s = 2342030
		#========================================
		(1700,3,1) , # s += (1 if 2342031 <= s <= 2378554) 
		(1800,2,28), 
		#========================================
			# blackhole  s = 2378555
		#========================================
		(1800,3,1) , # s += (0 if s >= 23478556 ) 
		(1800,4,1) , 
		(1800,5,1) , 
		(1800,6,1) , 
		(1800,7,1) , 
		(1800,8,1) , 
		(1800,9,1) , 
		(1800,10,1) , 
		(1800,11,1) , 
		(1800,12,1) , 
		(1900,1,1) , 
		(2000,1,1) ,  
	]], columns=['dt', 'greg', 'julian', 'astro', 'stel_alt'])
	display(jdf)

	# Part 2 - compute JD using the Stellarium script for the same dates
	#======================================================================
	# StelScript to get julian days (jds) given dates (dts =list(jdf.dt))
	# include("nakshatras.inc");
	# ans=[]
	# dts.forEach( function (e,i) {  
	# 	DT(e); W(.5); jd=JD()
	# 	say([ DT(), jd].join("\t"))
	# 	ans.push(jd)
	# } )
	# ddump(ans, 'pretty')
	dts = [
		'-04712-01-01T23:59:59',
		'1582-10-03T23:59:59',
		'1582-10-04T23:59:59',
		'1582-10-15T23:59:59',
		'1700-02-28T23:59:59',
		'1700-03-01T23:59:59',
		'1800-02-28T23:59:59',
		'1800-03-01T23:59:59',
		'1800-04-01T23:59:59',
		'1800-05-01T23:59:59',
		'1800-06-01T23:59:59',
		'1800-07-01T23:59:59',
		'1800-08-01T23:59:59',
		'1800-09-01T23:59:59',
		'1800-10-01T23:59:59',
		'1800-11-01T23:59:59',
		'1800-12-01T23:59:59',
		'1900-01-01T23:59:59',
		'2000-01-01T23:59:59'
	]

	jds= [
		0.49998842592592596,
		2299159.499988426,
		2299160.499988426,
		2299161.499988426,
		2342031.499988426,
		2342032.499988426,
		2378555.499988426,
		2378556.499988426,
		2378587.499988426,
		2378617.499988426,
		2378648.499988426,
		2378678.499988426,
		2378709.499988426,
		2378740.499988426,
		2378770.499988426,
		2378801.499988426,
		2378831.499988426,
		2415021.499988426,
		2451545.499988426
	]

	# Part 3 - Based on diff of STEL  jdf.stel_alt tune the params of stelAltJD and elems of carefully selected dates
	#======================================================================
	jdf['STEL']= jds 
	jdf['S-g'] = jdf.STEL - jdf.greg
	jdf['S-j'] = jdf.STEL - jdf.julian
	jdf['S-a'] = jdf.STEL - jdf.astro
	jdf['S-s'] = jdf.STEL - jdf.stel_alt
	sf = pd.options.display.float_format
	pd.options.display.float_format = '{:.2f}'.format
	display(jdf.sort_values(by='stel_alt'))
	pd.options.display.float_format = sf
	errsum = jdf['S-s'].sum()
	if errsum < 0.01:
		print ("Julian day of Python Function stelAltJD matches with Stellarium. Look at S-s column")
	else:
		print (f"Julian day of Python Function stelAltJD does not match with Stellarium. SumError = {errsum}. Look at S-s column")

	
if __name__ == '__main__':
	find_and_check_date_range_and_delta_params_fo_stel_alt()

# %%
# '''
# // UTC !
# bool getJDFromDate(double* newjd, const int y, const int m, const int d, const int h, const int min, const float s)
# {
# 	static const long IGREG2 = 15+31L*(10+12L*1582);
# 	double deltaTime = (h / 24.0) + (min / (24.0*60.0)) + (static_cast<double>(s) / (24.0 * 60.0 * 60.0)) - 0.5;
# 	QDate test((y <= 0 ? y-1 : y), m, d);
# 	// if QDate will oblige, do so.
# 	// added hook for Julian calendar, because it has been removed from Qt5 --AW
# 	if ( test.isValid() && y>1582)
# 	{
# 		double qdjd = static_cast<double>(test.toJulianDay());
# 		qdjd += deltaTime;
# 		*newjd = qdjd;
# 		return true;
# 	}
# 	else
# 	{
# 		/*
# 		 * Algorithm taken from "Numerical Recipes in C, 2nd Ed." (1992), pp. 11-12
# 		 */
# 		long ljul;
# 		long jy, jm;
# 		long laa, lbb, lcc, lee;

# 		jy = y;
# 		if (m > 2)
# 		{
# 			jm = m + 1;
# 		}
# 		else
# 		{
# 			--jy;
# 			jm = m + 13;
# 		}

# 		laa = 1461 * jy / 4;
# 		if (jy < 0 && jy % 4)
# 		{
# 			--laa;
# 		}
# 		lbb = 306001 * jm / 10000;
# 		ljul = laa + lbb + d + 1720995L;

# 		if (d + 31L*(m + 12L * y) >= IGREG2)
# 		{
# 			lcc = jy/100;
# 			if (jy < 0 && jy % 100)
# 			{
# 				--lcc;
# 			}
# 			lee = lcc/4;
# 			if (lcc < 0 && lcc % 4)
# 			{
# 				--lee;
# 			}
# 			ljul += 2 - lcc + lee;
# 		}
# 		double jd = static_cast<double>(ljul);
# 		jd += deltaTime;
# 		*newjd = jd;
# 		return true;
# 	}
# }

# double getJDFromDate_alg2(const int y, const int m, const int d, const int h, const int min, const int s)
# {
# 	double extra = (100.0* y) + m - 190002.5;
# 	double rjd = 367.0 * y;
# 	rjd -= floor(7.0*(y+floor((m+9.0)/12.0))/4.0);
# 	rjd += floor(275.0*m/9.0) ;
# 	rjd += d;
# 	rjd += (h + (min + s/60.0)/60.)/24.0;
# 	rjd += 1721013.5;
# 	rjd -= 0.5*extra/std::fabs(extra);
# 	rjd += 0.5;
# 	return rjd;
# }
# '''
#%%
# void getDateFromJulianDay(const double jd, int *yy, int *mm, int *dd)
# {
# 	/*
# 	 * This algorithm is taken from
# 	 * "Numerical Recipes in C, 2nd Ed." (1992), pp. 14-15
# 	 * and converted to integer math.
# 	 * The electronic version of the book is freely available
# 	 * at http://www.nr.com/ , under "Obsolete Versions - Older
# 	 * book and code versions".
# 	 */

# 	static const long JD_GREG_CAL = 2299161;
# 	static const int JB_MAX_WITHOUT_OVERFLOW = 107374182;
# 	const long julian = static_cast<long>(floor(jd + 0.5));

# 	long ta, jalpha, tb, tc, td, te;

# 	if (julian >= JD_GREG_CAL)
# 	{
# 		jalpha = (4*(julian - 1867216) - 1) / 146097;
# 		ta = julian + 1 + jalpha - jalpha / 4;
# 	}
# 	else if (julian < 0)
# 	{
# 		ta = julian + 36525 * (1 - julian / 36525);
# 	}
# 	else
# 	{
# 		ta = julian;
# 	}

# 	tb = ta + 1524;
# 	if (tb <= JB_MAX_WITHOUT_OVERFLOW)
# 	{
# 		tc = (tb*20 - 2442) / 7305;
# 	}
# 	else
# 	{
# 		tc = static_cast<long>((static_cast<unsigned long long>(tb)*20 - 2442) / 7305);
# 	}
# 	td = 365 * tc + tc/4;
# 	te = ((tb - td) * 10000)/306001;

# 	*dd = tb - td - (306001 * te) / 10000;

# 	*mm = te - 1;
# 	if (*mm > 12)
# 	{
# 		*mm -= 12;
# 	}
# 	*yy = tc - 4715;
# 	if (*mm > 2)
# 	{
# 		--(*yy);
# 	}
# 	if (julian < 0)
# 	{
# 		*yy -= 100 * (1 - julian / 36525);
# 	}
# }

# void getTimeFromJulianDay(const double julianDay, int *hour, int *minute, int *second, int *millis)
# {
# 	double frac = julianDay - (floor(julianDay));
# 	double secs = frac * 24.0 * 60.0 * 60.0 + 0.0001; // add constant to fix floating-point truncation error
# 	int s = static_cast<int>(floor(secs));

# 	*hour = ((s / (60 * 60))+12)%24;
# 	*minute = (s/(60))%60;
# 	*second = s % 60;
# 	if(millis)
# 	{
# 		*millis = static_cast<int>(floor((secs - floor(secs)) * 1000.0));
# 	}
# }