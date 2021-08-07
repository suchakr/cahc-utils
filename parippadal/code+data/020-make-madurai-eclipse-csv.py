#%%
from numpy.lib.ufunclike import fix
import pandas as pd 
from astropy.time import Time
import glob 
import re 
# %%
fn = glob.glob("*scraped*csv")[0]
me = pd.read_csv(fn)
# %%
me_cols = [ 
'date', 'type', 
'pen_mag', 'umb_mag', 
'pen_start_time', 'pen_start_alt',
'par_start_time', 'par_start_alt',
'ttl_start_time', 'ttl_start_alt',
'mid_ecl_time'  , 'mid_ecl_alt',
'ttl_end_time'  , 'ttl_end_alt',
'par_end_time'  , 'par_end_alt',
'pen_end_time'  , 'pen_end_alt'
]

me.columns = me_cols
alt_cols = [ x for x  in me_cols if '_alt' in x ]
vis_alt_cols = [ x for x  in alt_cols if 'pen_' not in x ]
time_cols = [ x for x  in me_cols if '_time' in x ]
vis_time_cols = [ x for x  in time_cols if 'pen_' not in x ]
me = me.drop(me[ me.type == 'Ecl. Type'].index)
for c in alt_cols : me[c] = me[c].apply ( lambda x: '-99' if '-' == x else x )
me = me.astype ({ x:int for x in alt_cols  })

for c in time_cols : me[c] = me[c].apply ( lambda x: '99:99' if '-' == x else x )
#me = me.astype ({ x:int for x in alt_cols  })


# %%
def is_vis( r, tag, alt_threshold=5):
  st, et, sa, ea = [ r[f'{tag}_{x}'] for x in ['start_time', 'end_time', 'start_alt', 'end_alt'] ]
  return (
    ((st != '99:99') and ( st >= '18:00'  or  st <= '06:00') and (sa > alt_threshold))
    or ((et != '99:99') and ( et >= '18:00'  or  et <= '06:00') and (ea > alt_threshold))
  )    

def direction( r, tag, alt_threshold=5):
  st, et, sa, ea = [ r[f'{tag}_{x}'] for x in ['start_time', 'end_time', 'start_alt', 'end_alt'] ]
  start_west = st < '12:00'
  end_west = et < '12:00'

  if ( start_west and end_west) : return 'west'
  if ( start_west and (not end_west)) : return 'west_start_east_end'
  if ( (not start_west) and end_west) : return 'east_start_west_end'
  if ( (not start_west) and (not end_west)) : return 'east'
  
me['vis00'] = me.apply( lambda x: is_vis(x, 'par', 0)  , axis=1)
me['vis05'] = me.apply( lambda x: is_vis(x, 'par', 5)  , axis=1)
me['vis10'] = me.apply( lambda x: is_vis(x, 'par', 10) , axis=1)
me['direction'] = me.apply( lambda x: direction(x, 'par', 10) , axis=1)
me['ynum'] = me.date.apply( 
  lambda x :  ('-' if x[0] == '-' else '') +  (x.split('-')[ 1 if x[0] == '-' else 0 ])
).apply (lambda x: int(x))
me['pp_range'] = me.ynum.apply( lambda x: (x >=-500) and  (x <=700 ) )
me = me.astype( {'umb_mag':float})
# %%
def fix_astro_date(d) :
  p = d.split('-')
  # print (p)
  neg = p[0] == ''
  p = [ int(x) for x in p[1 if neg else 0 :]]
  # print (p)
  fmt = '%s%02dd-%s-%s' % (
       '-%' if neg else '%', 
       5 if neg else 4,
       '%02d',
       '%02d')
  # print (d , fmt)
  ans = fmt % (p[0], p[1], p[2])
  return ans
# %%
# tsrs = pp_me.date + 'T' + pp_me.par_start_time
me['astro_date'] = me.date.apply( 
  lambda x : x #re.sub( '^.'  if x[0] == '-' else '^' ,  '-00' if x[0] == '-' else '0', x  ) 
) .apply ( lambda x: re.sub( 'Jan', '01', x)
) .apply ( lambda x: re.sub( 'Feb', '02', x)
) .apply ( lambda x: re.sub( 'Mar', '03', x)
) .apply ( lambda x: re.sub( 'Apr', '04', x)
) .apply ( lambda x: re.sub( 'May', '05', x)
) .apply ( lambda x: re.sub( 'Jun', '06', x)
) .apply ( lambda x: re.sub( 'Jul', '07', x)
) .apply ( lambda x: re.sub( 'Aug', '08', x)
) .apply ( lambda x: re.sub( 'Sep', '09', x)
) .apply ( lambda x: re.sub( 'Oct', '10', x)
) .apply ( lambda x: re.sub( 'Nov', '11', x)
) .apply ( lambda x: re.sub( 'Dec', '12', x)
). apply ( fix_astro_date)
me['mnum'] = me.astro_date.apply(lambda x :  int(x.split('-')[-2]) )
me['dnum'] = me.astro_date.apply(lambda x :  int(x.split('-')[-1]) )
me['astro_jd'] = me.astro_date.apply(lambda x : Time(x).jd) 
me['astro_mjd'] = me.astro_date.apply(lambda x : Time(x).mjd) 
# %%
# %%
pp_me = me[me.vis00 & me.pp_range]
pp_me  = pp_me[ [ x  for x in pp_me.columns if not bool( re.match("ttl_|pen_", x))]]
pp_me.shape

# %%
pp_me.to_csv("024-madurai-visible-eclipses.csv", index=None, sep="\t")
pp_me.sample(3).T
# %%
pp_me.set_index('astro_date').T.to_json('026-madurai-visible-eclipses.json')
# %%

# %%
