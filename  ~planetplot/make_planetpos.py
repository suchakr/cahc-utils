# %% [markdown]
# Utility to plot planet positions for a date range.
# Based on info https://ssd.jpl.nasa.gov/?planet_pos and https://ssd.jpl.nasa.gov/txt/aprx_pos_planets.pdf

# %%
from IPython import get_ipython
from IPython.display import display
import math
from astropy.utils.misc import walk_skip_hidden
import numpy as np
import pandas as pd
import datetime
import time
import glob
from astropy.time import Time
import re
import matplotlib.pyplot as plt
import random
get_ipython().run_line_magic('matplotlib', 'inline')
pd.options.display.float_format = '{:,.6f}'.format

# %%
## borrowed from Paul Schlyter's tutorial - regular math.atan doesnt have these properties
def arctan_stleimlen(x,y):
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
        
##  Vector shorthands for sin, cos, tan ...
_cos = lambda x: x.apply (lambda y: math.cos(y*math.pi/180))
_sin = lambda x: x.apply (lambda y: math.sin(y*math.pi/180))
_atan = lambda x: x.apply (lambda y: math.atan(y)*180/math.pi)
_sqrt = lambda x: x.apply (lambda y: math.sqrt(y))
_dist = lambda x,y,z,L=2 : (x**L+y**L+z**L)**(1/L)
_atan2 = lambda y,x: pd.Series(list(zip(y,x)), index=(y.index)).apply (lambda e: ((arctan_stleimlen(e[1], e[0])) +360) %360 ) #.reindex(index=y.index)
_atan1 = lambda y,x: (y/x).apply (lambda e: math.atan(e)*180/math.pi)

# From http://www.stjarnhimlen.se/comp/ppcomp.html - this method validates with Stellarium ( better than Standish )
PP2 = pd.read_csv('./planet_params_stjarmhimlen.csv' ).set_index('planet')
PP2['L'] = PP2['M'] + PP2['w'] + PP2['N']
PP2['L_d'] = PP2['M_d'] + PP2['w_d'] + PP2['N_d']
PP2
PP2_Rate = PP2.loc[:, ['a_d', 'e_d', 'i_d', 'L_d', 'M_d', 'N_d' , 'w_d'] ]
PP2_Base = PP2.loc[:, ['a', 'e', 'i', 'L', 'M', 'N' , 'w'] ]
#display(PP2_Rate)
#display(PP2_Base)

# %%
JD_2000 = 2451543.5
JD_BCE_3000_JAN_1   = 625332.5  # -3000-01-01T00:00:00.000
JD_JEPPY_KALI_YUGA  = 588465.5  # -3101-01-23T00:00:00.000  ( +25 gets to KY 17/Feb/-3101 )
JD_JEPPY_OFFSET     = 2415020   # 1899-12-31T12:00:00.000

def rev(x):
    rev = x - math.trunc(x/360.0)*360.0
    if rev<0.0:
        rev=rev+360.0      
    return rev

def solve_E(M, e):
    TOLERANCE = 1E-6
    e_deg = e*180/math.pi
    
    ## E_ is in degree
    E_ = M + e_deg*_sin(M)
    
    for n in range(1,500):
        delta_M = M - (E_ - e_deg*_sin(E_))
        delta_E = delta_M/(1 - e*_cos(E_))
        if (delta_E.abs() < TOLERANCE).all() :
            ## print(f'converged after {n} iterations')
            break
        E_ = E_ + delta_E
        
    return E_

def get_planet_pos_starjm (jd = JD_BCE_3000_JAN_1) :
    isot = Time(jd, format='jd').isot
    T = ( jd - 2451543.5) #/36525
#     T = ( jd - 2451543) #/36525
    print(jd, isot)
    params = PP2_Base + PP2_Rate.values*T
    # display (params)
    
    params['M'] = params['M'].apply( lambda x : rev(x))
    waileo = params
    e_star = waileo['e'] * 180/math.pi
    waileo = waileo % 360

    En = solve_E(waileo['M'], waileo['e'])
    waileo['E'] = En
    # display(waileo[list("NiwaeMEL")])

    x_prime = waileo['a']*(_cos(En) - waileo['e'])
    y_prime = waileo['a']*_sin(En)* _sqrt( 1 - waileo['e'] *waileo['e'] )
    v_nu = _atan2(y_prime, x_prime)
    r = _sqrt ( y_prime*y_prime + x_prime*x_prime)
    # display(x_prime.Moon, y_prime.Moon, v_nu.Moon, r.Moon, "========")
    
    lon = (v_nu+ waileo['w'])%360
    N=waileo['N']
    I=waileo['i']

    # display(lon.Moon, N.Moon, I.Moon, "=======")
    ## ecliptic rectangular, also called xh,yh,zh
    x_eclip = r * ( _cos(N) * _cos(lon) - _sin(N) * _sin(lon) * _cos(I) )
    y_eclip = r * ( _sin(N) * _cos(lon) + _cos(N) * _sin(lon) * _cos(I) )
    z_eclip = r * _sin(lon) * _sin(I)   
    # display(x_eclip.Moon, y_eclip.Moon, z_eclip.Moon,"======")

    geoc_x = x_eclip + x_eclip['Sun']
    geoc_y = y_eclip + y_eclip['Sun']
    geoc_z = z_eclip + z_eclip['Sun']
    
    for obj in ['Moon', 'Sun'] :
        geoc_x[obj] = x_eclip[obj]
        geoc_y[obj] = y_eclip[obj]
        geoc_z[obj] = z_eclip[obj]
        
    geo_r = _dist(geoc_x, geoc_y, geoc_z)
        
    ecl_long = _atan2( geoc_y, geoc_x)
    ecl_lati = _atan1( geoc_z, _sqrt ( geoc_y**2 + geoc_x**2 ) )
    # display(ecl_long.Moon, ecl_lati.Moon,"======")
    # display(T, jd, isot )

    if not True: # block to add moon perturbations
        Ms, Mm  = waileo['M'].Sun , waileo['M'].Moon    # Mean Anomaly of the Sun and the Moon
        Nm      = waileo['N'].Moon  # Longitude of the Moon's node
        ws, wm  = waileo['w'].Sun , waileo['w'].Moon    # Argument of perihelion for the Sun and the Moon
        Ls = Ms + ws      # Mean Longitude of the Sun  (Ns=0)
        Lm = Mm + wm + Nm # Mean longitude of the Moon
        D = Lm - Ls       # Mean elongation of the Moon
        F = Lm - Nm       # Argument of latitude for the Moon

        def dsin(x) : return math.sin(x*math.pi/180)

        ecl_long_pert_moon = ( 
        +0.658 * dsin(2*D)               #(the Variation)
        -1.274 * dsin(Mm - 2*D)          #(the Evection)
        -0.186 * dsin(Ms)                #(the Yearly Equation)
        -0.059 * dsin(2*Mm - 2*D)
        -0.057 * dsin(Mm - 2*D + Ms)
        +0.053 * dsin(Mm + 2*D)
        +0.046 * dsin(2*D - Ms)
        +0.041 * dsin(Mm - Ms)
        -0.035 * dsin(D)                 #(the Parallactic Equation)
        -0.031 * dsin(Mm + Ms)
        -0.015 * dsin(2*F - 2*D)
        +0.011 * dsin(Mm - 4*D)
        )

        ecl_lati_pert_moon = ( 
        -0.173 * dsin(F - 2*D)
        -0.055 * dsin(Mm - F - 2*D)
        -0.046 * dsin(Mm + F - 2*D)
        +0.033 * dsin(F + 2*D)
        +0.017 * dsin(2*Mm + F)
        )

        ecl_long.Moon += ecl_long_pert_moon
        ecl_lati.Moon += ecl_lati_pert_moon

    geoc_r = _dist(geoc_x, geoc_y, geoc_z)
    geoc_r.Moon = geoc_r.Moon + geoc_r.Sun
    geoc_r.Sun = geoc_r.Moon
    geoc_r.Moon = geoc_r.Moon + geoc_r.Sun
    geoc_r.Sun
    
    ans = pd.DataFrame ({
        'jd' : ecl_long.apply(lambda v : jd )
        , 'date' : ecl_long.apply(lambda v : isot ) 
        ,'ecl_long' : ecl_long
        ,'ecl_lati' : ecl_lati
        ,'geo_r'  : geo_r
        ,'geoc_x' : geoc_x
        ,'geoc_y' : geoc_y
        ,'geoc_z' : geoc_z
        ,'r': r
    })

    return ans

# get_planet_pos_starjm(Time('-00800-04-19').jd)
# get_planet_pos_starjm(Time('1990-04-19').jd)
T = Time('0990-04-19').jd
T = 1359563.500000
T = 629063.500000 * 1
# T = 0
# print(T)

xxx = pd.concat([ get_planet_pos_starjm( (x*36525*1+620926)) for x in range(0,20)])
xxx[ [x == 'Moon' for x in xxx.index] ]

#%%
Time(0, format='jd').isot
yyy = pd.DataFrame([ x.split("\t") for x in 
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
'''.split("\n") if len(x) ], columns=['idx', 'obj', 'dt', 'jd', 'lon', 'lat'])

xxx['stel_long'] = yyy['lon']
xxx



# %%
def save_snapshot (tag, acc, f_cnt) :
    if not len(acc) :
        return
    
    ans = pd.DataFrame().append(acc)
    fn = tag + ".csv"
    if (f_cnt < 10 and f_cnt %1 == 0) or (f_cnt < 100 and f_cnt %1 == 0) or (f_cnt % 100 == 0) :
        print ( '%6.2f secs, %5d files, %s %s %s' % (  time.time() - begin_time, f_cnt, "Saving" , fn,  str(ans.shape) ))
    ans.to_csv(fn)
    

acc = []
pyear = None
pcentury = None
begin_time = time.time()
f_cnt = 1 
for jd in range ( 0, 365*5000, 7 ) :
    t = JD_BCE_3000_JAN_1 + jd*1 
    #t = (1720335.5+7) + jd*1  # ran till here -2-01-07T00:00:00.000 , died when entered CE due to bad regex see below 
    tstr =  Time(t, format='jd').isot
    year = re.match("^(.?\d+)\-", tstr)[1]  # added ? to fix CE parse bug
    n = int (year)
    century = ('%03d00' if n<0 else '%02d00') % (n//100) 
    century = 'c_' + century
    if not pyear:
        pyear = year
        pcentury = century
        
    if pcentury != century :
        save_snapshot (pcentury, acc, f_cnt)
        f_cnt = f_cnt +1
        acc = []
        
    if (( jd < 365*140 and jd % 365 == 0 ) ) :
        print ( '%6.2f secs, %5d years  - %s  : %s : %d'  % (  time.time() - begin_time, jd //365,  tstr , pcentury, len(acc) )) 
        if len(acc) : display (acc[-1] )
        
    df = get_planet_pos_starjm(t) #2453005.458333 1539168.9791665
    acc.append(df)
    pcentury = century

save_snapshot (pcentury, acc, f_cnt)


# %%
acc = []
for f in glob.glob('c*csv') :
    print(f)
    acc.append(pd.read_csv(f))


# %%
pp_df = pd.DataFrame().append(acc).rename(columns={"r": "helio_r"}).sort_values( by = ['jd', 'planet']).reset_index() 
display(pp_df.shape)


# %%
display(pp_df.head(10))
display(pp_df.tail(10))
pp_df.shape


# %%
pp_df.to_csv("./planets_positions_from_3000BCE_for_5k_years_at_7day_interval.csv", index=None)
#head helio_long.csv


# %%
get_ipython().system('ls -hal planets*csv ')


# %%
#[Time(t, format='jd').unix for t in [JD_BCE_3000_JAN_1, JD_JEPPY_KALI_YUGA, JD_JEPPY_OFFSET,  JD_JEPPY_OFFSET + 365*120+18.75] ]


# %%
#[ (  n , ('%05d' if n<0 else '%04d') % (n//1000) )for n in range(-3000,3001, 80)]


# %%
# Standish -  Unable to get this to work
#http://www.met.rdg.ac.uk/~ross/Astronomy/Planets.html - for earth
#https://ssd.jpl.nasa.gov/txt/aprx_pos_planets.pdf for rest
planet_params = pd.read_csv('planet_params.csv' ).set_index('planet')
planet_params2 = pd.read_csv('planet_params2.csv' ).set_index('planet')
PP = pd.merge ( planet_params, planet_params2 , how='left' , on ='planet')
PP=PP.drop ( ['Uranus','Neptune','Pluto'] )
WAILEO  = ['a', 'e', 'I', 'L', 'w', 'O']
WAILEO_CY = [ x + '_cy' for x in WAILEO]
BCSF = ['b','c','s','f']
bcsf =  PP.loc[ :, BCSF]


# %%
def get_planet_pos_standish (jd = JD_BCE_3000_JAN_1) :
    
    display(jd, Time(jd, format='jd').isot)
    T = ( jd - 2451545.0)/36525
    waileo = PP.loc[ :, WAILEO] + PP.loc[ :, WAILEO_CY].values*T
    #display(waileo)

    #=======================
    waileo["w-O"] = waileo['w'] - waileo['O'] # perihi

    x = ( #mean_anomaly
        waileo['L'] - waileo['w'] 
        + bcsf['b']*T*T 
        + bcsf['c'] * _cos(bcsf['f']*T) 
        + bcsf['s'] * _sin(bcsf['f']*T) 
    ) 
    waileo["M"]= ((np.sign(x)*x)%180.0)*np.sign(x)

    e_star = waileo['e'] * 180/math.pi

    waileo['E0'] = waileo['M'] + e_star*_sin(waileo['M'])
    #display(waileo)

    #----------------
    M  = waileo["M"]
    En = waileo['E0']
    TOLERANCE = 1E-6
    for n in range(1,500):
        #deltaM = M - ( En - [e_star*math.sin(x) for x in En*math.pi/180] )
        #deltaE = deltaM /(1 - math.e*np.array([math.cos(x) for x in En*math.pi/180]) )

        deltaM = M - ( En - e_star*_sin(En) )
        deltaE = deltaM /(1 - waileo['e']*_cos(En))   
        if (deltaE.abs() < TOLERANCE).all() :
            waileo['E'] = En
            break 
        En = En + deltaE

    waileo['M_check'] = En - e_star*_sin(En)
    x_prime = waileo['a']*(_cos(En) - waileo['e'])
    y_prime = waileo['a']*_sin(En)* _sqrt( 1 - waileo['e'] *waileo['e'] )
    pd.DataFrame ({ 'x_prime': x_prime, 'y_prime' : y_prime})
    waileo['x_prime'] = x_prime
    waileo['y_prime'] = y_prime
    #display(waileo)

    #===========
    w,O,I =waileo['w-O'], waileo['O'], waileo['I']
    #display (w,O,I)

    sur_x = (_cos(w)*_cos(O) - _sin(w)*_sin(O)*_cos(I))*x_prime + ( -_sin(w)*_cos(O) - _cos(w)*_sin(O)*_cos(I)) *y_prime
    sur_y = (_cos(w)*_sin(O) + _sin(w)*_cos(O)*_cos(I))*x_prime + ( -_sin(w)*_sin(O) + _cos(w)*_cos(O)*_cos(I)) *y_prime
    sur_z = _sin(w)*_sin(I)*x_prime + _cos(w)*_sin(I)*y_prime
    
    #wrt= 'EM_Bary'
    wrt = 'Earth'
    
    bhu_x = sur_x - sur_x[wrt]
    bhu_y = sur_y - sur_y[wrt]
    bhu_z = sur_z - sur_z[wrt]
    
    sur_long = _atan(sur_y/sur_x)
    sur_lati = _atan(sur_z/_sqrt(sur_x**2 + sur_y**2 ))  
    #sur_long = _atan1(sur_y, sur_x)
    #sur_lati = _atan1(sur_z, _sqrt(sur_x**2 + sur_y**2 ))
    #sur_long = _atan2(sur_y,sur_x)
    #sur_lati = _atan2(sur_z,_sqrt(sur_x**2 + sur_y**2 ))
    sur_dist = _sqrt(sur_x**2 + sur_y**2 + sur_z**2  ) 

    bhu_long = _atan(bhu_y/bhu_x)
    bhu_lati = _atan(bhu_z/_sqrt(bhu_x**2 + bhu_y**2) )    
    #bhu_long = _atan1(bhu_y,bhu_x)
    #bhu_lati = _atan1(bhu_z,_sqrt(bhu_x**2 + bhu_y**2) )    
    bhu_dist = _sqrt(bhu_x**2 + bhu_y**2 + bhu_z**2  ) 
    #display (pd.DataFrame ( {'sur': sur_long} ) )
    #display (pd.DataFrame ( {'bhu': bhu_long} ) )
    
    ans = pd.DataFrame ( {
         'sur_x' : sur_x, 'sur_y' : sur_y, 'sur_z': sur_z,
         'sur_lati' : sur_lati, 'sur_long' : sur_long, 'sur_dist': sur_dist,
         'bhu_x' : bhu_x, 'bhu_y' : bhu_y, 'bhu_z': bhu_z,
         'bhu_lati' : bhu_lati, 'bhu_long' : bhu_long, 'bhu_dist': bhu_dist,
    }) #, columns = ['w', '_w'] )    

    #xdf['_sumsq']  = xdf['_cw']*xdf['_cw'] + xdf['_sw']*xdf['_sw']  
    return ans , waileo


# %%
def test_standish () :
    ans, wlo = get_planet_pos_standish( 
          0*806471.355405 
        + 0*623846.480405 
        + 1*2453005.458333
        + 0*2457005
    )
    #(2453006)
    display(ans)

test_standish()
#%%
def day_num(y,m,D):
	return ( 
		367*y 
		- (7 * ( y + (m+9)/12 ) / 4) 
		- (3 * ( ( y + (m-9)/7 ) / 100 + 1 ) / 4 )
		+ 275*m/9 + D 
		- 730515 ,
		367*y - (7*(y + ((m+9)/12)))/4 + (275*m)/9 + D - 730530
		)


day_num(1990,4,19)

# %%
T1 = ( Time('1990-04-19').jd1 - 2451543.5) #/36525
T0 = -3543.0
T = ( Time('1990-04-19').jd1 - 2451543) #/36525
params = PP2_Base + PP2_Rate.values*T
z = params.loc[['Moon']].T
pd.concat( [z, z%360], axis=1).sort_index( )

# %%
    a =   60.2666            =  60.2666      
    e =    0.054900          =   0.054900
    i =    5.1454_deg        =   5.1454_deg
    w = -264.2546_deg        =  95.7454_deg
    M = -46173.9046_deg      = 266.0954_deg
    N =  312.7381_deg        = 312.7381_degA


a =  60.2666          
e =   0.054900
i =   5.1454_deg
w =  95.7454_deg
M = 266.0954_deg
N = 312.7381_degA

