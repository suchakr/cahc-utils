#%%
# Util to get Moon Rise, Phase, RA, Dec for a data range using ephem ( may be try astropy or astroplan)
# For given start year ,num of years, and lat long
# Cant do BCE  Dates
import ephem
from datetime import datetime 
import math
import sys

#======= Parameters ===========

start_year = 2000 #  > 1
num_years = 18  
lat = 28.8341  # kuru lat lon
lon = 74.8679

#===============

def warn(*args, **kwargs): print(*args, file=sys.stderr, **kwargs)
obs =ephem.Observer() 
#sun, moon = ephem.Sun(), ephem.Moon();
moon = ephem.Moon()
obs.lon, obs.lat = str(74.8679), str(28.8341)  # kuru
now = datetime.now()
start_date =  datetime( start_year , 7 , 16 ) 
stop_date =  datetime( start_year+ num_years , 12 , 31 )
ttl_days = (stop_date - start_date).days
prev_phase = -1
obs.date = start_date
curr_date = start_date
print( "%s,%s,%s,%s,%s,%s" % ('rise', 'az', 'phase', 'paksha', 'ra', 'dec' ) )
while ( curr_date < stop_date):
  mr=obs.next_rising(moon)  
  obs.date = mr
  curr_phase = moon.phase
  paksha = "Krishna" if curr_phase < prev_phase else 'Shukla'
  #print( "%20s\t%20s\t%2.8f\t%2.8f\t%10s" % (mr ,  moon.az, (moon.az+0)*180/math.pi , moon.phase, paksha) )
  print( "%s,%2.2f,%2.2f,%s,%2.2f,%2.2f" % 
        (mr, (moon.az+0)*180/math.pi , moon.phase, paksha, moon.ra, moon.dec) )
  obs.date = obs.date+1
  ( yyyy, mm, dd, _, _, _) = obs.date.tuple()
  try :
    curr_date = datetime(yyyy, mm, dd )
  except:
    warn ( 'yyy=%d mm=%d  dd=%d' % (yyyy, mm, dd ))
  prev_phase = curr_phase
  days_done = (curr_date - start_date).days
  if ( dd == 1 ) :
    pct =  100*days_done/ttl_days
    warn ( '%0.2f%s ( % 4d of % 4d days) || %s || %s  ||  %s' %  
    ( pct, '%', days_done, ttl_days, curr_date, start_date, stop_date  )
    )
#%%
# %%
#start_date =  datetime( 2000 , 7 , 16 )  #  Total Lunar Eclipse at Kurukshetra
# '''
# 28.8341434,74.8579096 kuru
# 28.5272181,77.0688997 delhi
# 28.4136484,75.3756879 jaipur
# 29° 58' 10.2468'' N and 76° 52' 41.8116'' E. kuru
# '''
# #obs.lon, obs.lat = '77.5946', '12.9716'  # bangalore
# #obs.lon, obs.lat = '75.7873', '26.9124'  # jaipur

# %%
