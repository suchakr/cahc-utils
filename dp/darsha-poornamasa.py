import ephem
from datetime import datetime 
import math
import sys

def warn(*args, **kwargs): print(*args, file=sys.stderr, **kwargs)

obs =ephem.Observer() 
#sun, moon = ephem.Sun(), ephem.Moon();
moon = ephem.Moon()
'''
28.8341434,74.8579096 kuru
28.5272181,77.0688997 delhi
28.4136484,75.3756879 jaipur
29° 58' 10.2468'' N and 76° 52' 41.8116'' E. kuru
'''
#obs.lon, obs.lat = '77.5946', '12.9716'  # bangalore
#obs.lon, obs.lat = '75.7873', '26.9124'  # jaipur
obs.lon, obs.lat = '74.8679', '28.8341'  # kuru
now = datetime.now()
#start_date =  datetime( now.year , now.month , now.day )
#stop_date =  datetime( now.year+40 , now.month , now.day )
#start_date =  datetime( 2000 , 7 , 16 )  #  Total Lunar Eclipse at Kurukshetra
#stop_date =  datetime( 2101 , 1 , 1 )
start_year = 0 #2000
span = 1  # 101
start_date =  datetime( start_year , 7 , 16 )  #  Total Lunar Eclipse at Kurukshetra
stop_date =  datetime( start_year+ span , 1 , 1 )
ttl_days = (stop_date - start_date).days
prev_phase = -1
obs.date = start_date
curr_date = start_date
print( "%s\t%s\t%s\t%s\t%s\t%s" % ('Rise', 'Az', 'Phase', 'Paksha', 'RA', 'Dec') )
while ( curr_date < stop_date):
  mr=obs.next_rising(moon)  
  obs.date = mr
  curr_phase = moon.phase
  paksha = "Krishna" if curr_phase < prev_phase else 'Shukla'
  #print( "%20s\t%20s\t%2.8f\t%2.8f\t%10s" % (mr ,  moon.az, (moon.az+0)*180/math.pi , moon.phase, paksha) )
  print( "%s\t%2.8f\t%2.8f\t%s\t%2.8f\t%2.8f" % (mr, (moon.az+0)*180/math.pi , moon.phase, paksha, moon.ra, moon.dec) )
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

