#%%
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib as mpl
import math
from matplotlib import colors
from scipy.interpolate import interp1d
from scipy import stats
import NasaMoonScrapeUtils as nmsu
import NaksUtils as nsu
import PlanetPos as PP
import JdUtils as ju


#%%
def make_n27_lon_divisions() :
  lon_divisions = pd.read_csv("../datasets/n27_lon_divisions.csv").set_index('nid')
  lon_divisions['r_eq'] = np.roll(lon_divisions.Eq,1)
  lon_divisions['l_eq'] = np.roll(lon_divisions.Eq,0)
  lon_divisions['r_ue'] = np.roll(lon_divisions.Ue,1)
  lon_divisions['l_ue'] = np.roll(lon_divisions.Ue,0)

  lon_divisions['r_eq1'] = (lon_divisions.r_eq -350)%360
  lon_divisions['l_eq1'] = (lon_divisions.l_eq -350)%360
  return lon_divisions

def between ( x, bounds) :
  bounds = sorted(bounds)
  if ( bounds[1] - bounds[0]) > 50 : # 3 and 350 case ; 50 is a safe number ; Bharani Case
    bounds[1] = (bounds[1] + 50 ) % 360
    bounds[0] = (bounds[0] + 50 ) % 360
    x = (x + 50 ) % 360
    bounds = sorted(bounds)
  return bounds[0] <= x <= bounds[1] 

def naks_lon_err(n27_df):
  def _naks_lon_err(ndf,nbase,attr):
    err = ndf.apply( lambda r : r.lon - nbase.loc[r.nid,attr], axis=1)
    err = (err + 360)%360
    err = err.apply( lambda e :  abs( 360 -e if e > 180 else e))
    return err
  
  long_err_left = _naks_lon_err(n27_df,n27_lon_divisions, 'l_eq')
  long_err_right = _naks_lon_err(n27_df,n27_lon_divisions, 'r_eq')
  n27_df['err_lon_sq_eq'] = min( (long_err_right**2).values.tolist(), (long_err_left**2).values.tolist())
  n27_df['err_lon_abs_eq'] = (long_err_right+long_err_left)/2
  n27_df['err_lon_bounds_eq'] = np.array(
    [min(r,l) for r,l in zip(long_err_right,long_err_left)]
  ) * n27_df.apply( lambda x : 0 if between (
        x.lon , [ n27_lon_divisions.loc[x.nid,'l_eq'] , n27_lon_divisions.loc[x.nid,'r_eq'] ]
      ) else 1, axis=1)

  long_err_left1 = _naks_lon_err(n27_df,n27_lon_divisions, 'l_eq1')
  long_err_right1 = _naks_lon_err(n27_df,n27_lon_divisions, 'r_eq1')
  n27_df['err_lon_bounds_eq1'] = np.array(
    [min(r,l) for r,l in zip(long_err_right1,long_err_left1)]
  ) * n27_df.apply( lambda x : 0 if between (
        x.lon , [ n27_lon_divisions.loc[x.nid,'l_eq1'] , n27_lon_divisions.loc[x.nid,'r_eq1'] ]
      ) else 1, axis=1)

  long_err_left = _naks_lon_err(n27_df,n27_lon_divisions, 'l_ue')
  long_err_right = _naks_lon_err(n27_df,n27_lon_divisions, 'r_ue')
  n27_df['err_lon_sq_ue'] = min( (long_err_right**2).values.tolist(), (long_err_left**2).values.tolist())
  n27_df['err_lon_abs_ue'] = (long_err_right+long_err_left)/2
  n27_df['err_lon_bounds_ue'] = np.array(
    [min(r,l) for r,l in zip(long_err_right,long_err_left)]
  ) * n27_df.apply( lambda x : 0 if between (
        x.lon , [ n27_lon_divisions.loc[x.nid,'l_ue'] , n27_lon_divisions.loc[x.nid,'r_ue'] ]
      ) else 1, axis=1)

  return n27_df

def naks_lon_mae(n27_err_df) :
  p27_mae_lon_eq = pd.DataFrame(n27_err_df.groupby(by='year').apply(lambda df: df.err_lon_abs_eq.sum()/df.shape[0]), columns=['mae_lon_eq'])
  p27_mae_lon_ue = pd.DataFrame(n27_err_df.groupby(by='year').apply(lambda df: df.err_lon_abs_ue.sum()/df.shape[0]), columns=['mae_lon_ue'])
  p27_mae_lon = pd.merge( p27_mae_lon_eq, p27_mae_lon_ue, on='year', how='left')
  return p27_mae_lon

def naks_lon_mse(n27_err_df) :
  p27_mse_lon_eq = pd.DataFrame(n27_err_df.groupby(by='year').apply(lambda df: df.err_lon_sq_eq.sum()/df.shape[0]), columns=['mse_lon_eq'])
  p27_mse_lon_ue = pd.DataFrame(n27_err_df.groupby(by='year').apply(lambda df: df.err_lon_sq_ue.sum()/df.shape[0]), columns=['mse_lon_ue'])
  p27_mse_lon = pd.merge( p27_mse_lon_eq, p27_mse_lon_ue, on='year', how='left')
  return p27_mse_lon

def naks_lon_mbe(n27_err_df) :
  p27_mbe_lon_eq = pd.DataFrame(n27_err_df.groupby(by='year').apply(lambda df: df.err_lon_bounds_eq.sum()/df[df.err_lon_bounds_eq>0].shape[0]), columns=['mbe_lon_eq'])
  p27_mbe_lon_ue = pd.DataFrame(n27_err_df.groupby(by='year').apply(lambda df: df.err_lon_bounds_ue.sum()/df[df.err_lon_bounds_ue>0].shape[0]), columns=['mbe_lon_ue'])
  #p27_mbe_lon_eq = pd.DataFrame(n27_err_df.groupby(by='year').apply(lambda df: df[df.err_lon_bounds_eq>0].shape[0]), columns=['mbe_lon_eq'])
  #p27_mbe_lon_ue = pd.DataFrame(n27_err_df.groupby(by='year').apply(lambda df: df[df.err_lon_bounds_ue>0].shape[0]), columns=['mbe_lon_ue'])
  p27_mbe_lon = pd.merge( p27_mbe_lon_eq, p27_mbe_lon_ue, on='year', how='left')
  return p27_mbe_lon

def n27_extrapolate(n27_for_a_year_df, num_of_steps=60, years_per_step=50): 
  lon_df = pd.pivot_table(n27_for_a_year_df, columns='year', index=['nid', 'gname'],  values='lon' , aggfunc=max)
  start_year = n27_for_a_year_df.year.min()
  degrees_per_year = 1/72
  for y in range ( start_year,start_year + num_of_steps*years_per_step , years_per_step) :
    lon_df[y+years_per_step] = (lon_df[y]+ degrees_per_year*years_per_step)%360
  return lon_df.stack().reset_index().rename(columns={0:'lon'})

def load_naks_data(naks_tsv):
  naks_df = pd.read_csv(naks_tsv, sep="\t").drop_duplicates()
  naks_df = naks_df[naks_df.year <= 500]
  naks_df['gnid'] = naks_df.nid + ' ( ' + naks_df.gname + ' ) '
  lon_df = pd.pivot_table(naks_df, columns='year', index=['nid', 'gname', 'gnid'],  values='lon' , aggfunc=max)
  return lon_df.stack().reset_index().rename(columns={0:'lon'})

def  _do_plot_err(filtDf, err, filtTag, errTag, barColor='blue', chartType='bar'):
  _err_df = pd.DataFrame(filtDf.groupby(by='year').apply(lambda df: df[err].sum()/df.shape[0]), columns=[f'{errTag}'])
  ax =_err_df.plot(color=barColor,figsize=(15,5), 
    kind=chartType,
    #kind='line', marker='o',
    title=f'{errTag} - {filtTag}' if filtTag else '' , 
    logy=not True,
    grid=1,
    )
  # _mse.plot(kind='bar', ax=ax, x='year', y='MBE')
  # rect = patches.Rectangle((21, -5), 7,1400, linewidth=3, edgecolor='g', facecolor='none')
  # ax.add_patch(rect)
  ax.set_title(f'{errTag} - {filtTag}' if filtTag else '' , fontsize=40) 
  ax.yaxis.set_tick_params(labelsize=8, rotation=0)
  ax.xaxis.set_tick_params(labelsize=12, rotation=90)
  ax.set_yticks(range(0,31,1))
  if chartType == 'line' : ax.set_xticks(range(-2500,500,50))
  ax.set_ylabel("error", fontsize=30)
  ax.set_xlabel("year", fontsize=30)
  return _err_df

#do_plot_err_mbe(n27Feb24[n27Feb24.year<=0], chartType='line') #("Feb24-Set")
#do_plot_err_mbe(n27Feb24[n27Feb24.year<=0], chartType='bar') #("Feb24-Set")

def do_plot_err_mse(n27_df, tag) :
  p06 = n27_df[ [ x in  bright9Naks  for x in n27_df.nid ] ]
  _do_plot_err(p06 , 'err_lon_sq_eq', ','.join(bright9Lbls) + f' - Bright6 - {tag}', 'EquiSpacedNaks - MSE');
  #_do_plot_err(p06 , 'err_lon_sq_ue', ','.join(bright6Lbls) + f' - Bright6 - {tag}', 'NotEquiSpacedNaks - MSE', barColor='brown');

  _do_plot_err(n27_df , 'err_lon_sq_eq', f'All 27 Nakshatras - {tag}', 'EquiSpacedNaks - MSE')
  #_do_plot_err(n27_df , 'err_lon_sq_ue', f'All 27 Nakshatras - {tag}', 'NotEquiSpacedNaks - MSE', barColor='brown');

def do_plot_err_mae(n27_df, tag) :
  p06 = n27_df[ [ x in  bright9Naks  for x in n27_df.nid ] ]
  _do_plot_err(p06 , 'err_lon_abs_eq', ','.join(bright9Lbls) + f' - Bright6 - {tag}', 'EquiSpacedNaks - MAE');
  #_do_plot_err(p06 , 'err_lon_abs_ue', ','.join(bright6Lbls) + f' - Bright6 - {tag}', 'NotEquiSpacedNaks - MAE', barColor='brown');

  _do_plot_err(n27_df ,'err_lon_abs_eq', f'All 27 Nakshatras - {tag}', 'EquiSpacedNaks - MAE')
  #_do_plot_err(n27_df, 'err_lon_abs_ue', f'All 27 Nakshatras - {tag}', 'NotEquiSpacedNaks - MAE', barColor='brown');

def do_plot_err_mbe(n27_df, chartType='bar') :
  pbri = n27_df[ [ x in  bright9Naks  for x in n27_df.nid ] ]
  ns = len(bright9Naks)
  _do_plot_err(pbri , 'err_lon_bounds_eq', ','.join(bright9Lbls) + f' - Bright {ns}', 'MBE' , chartType=chartType)
  #_do_plot_err(p06 , 'err_lon_bounds_ue', ','.join(bright6Lbls) + f' - Bright6 - {tag}', 'NotEquiSpacedNaks - MBE', barColor='brown');

  _do_plot_err(n27_df ,'err_lon_bounds_eq', f'All 27 Nakshatras', 'MBE', chartType=chartType)
  #_do_plot_err(n27_df, 'err_lon_bounds_ue', f'All 27 Nakshatras - {tag}', 'NotEquiSpacedNaks - MBE', barColor='brown');

def bounded(df) :
  df_bounded = pd.merge(df,n27_lon_divisions, on='nid', how='left')
  df_bounded['lon_bounded_eq'] = df_bounded.apply ( lambda x: between(x.lon, [x.l_eq, x.r_eq] ), axis=1)
  df_bounded['lon_bounded_ue'] = df_bounded.apply ( lambda x: between(x.lon, [x.l_ue, x.r_ue] ), axis=1)
  df_bounded['nnid'] = df_bounded.nid.apply( lambda x: int(re.sub("\D","",x)))
  return df_bounded

def mbounded(df) :
  df_bounded = df
  df_bounded['nnid'] = df_bounded.nid.apply( lambda x: int(re.sub("\D","",x)))
  df_bounded['lon_bounded_eq'] = df_bounded.apply ( lambda x: between(x.lon, [(x.nnid-2)*30%360, (x.nnid-1)*30%360] ), axis=1)
  df_bounded['lon_bounded_ue'] = df_bounded.apply ( lambda x: between(x.lon, [(x.nnid-2)*30%360, (x.nnid-1)*30%360] ), axis=1)
  return df_bounded

def _do_plot_bounded(plt_df, title, ofs, sizes) :
  fig , ax = plt.subplots(figsize=(25,11))
  nnaks = plt_df.nnid.unique().shape[0]
  max_size = max(sizes)
  ax.scatter(y=plt_df.nnid , x=plt_df.year, 
    # s=[ 100*sizes[x] for x in plt_df.year ],
    s=[ 100*1 for x in plt_df.year ],
    c=[ 
           'red' if sizes[x] == max_size
      else 'red' if sizes[x] >= 21
      else (1-sizes[x]/max_size ,0,0) if sizes[x]/max_size >= .75
      else (1-sizes[x]/max_size,1-sizes[x]/max_size,0) if sizes[x] >= .50 
      else (1-sizes[x]/max_size,1-sizes[x]/max_size,1-sizes[x]/max_size) 
      for x in plt_df.year ],
    )
  ax.set_title(title, fontsize=40)
  ax.set_axisbelow(True)
  # ax.minorticks_on()
  ax.set_xlim(-2500, plt_df.year.max())
  ax.set_xticks(range(-2500,plt_df.year.max()+550,50))
  ax.set_xticklabels( [ str(x) for x in range(-2500,550,50)], rotation=90)

  ax.set_ylim(-1, 30)
  ax.set_yticks(range(-1,31,1))
  ax.set_yticklabels( [ str(x) for x in range(-1,31,)], rotation=0)
  ax.grid(which='major', linestyle='-', linewidth='0.5', color='gray')
  # ax.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
  ax.yaxis.set_tick_params(labelsize=13)
  ax.xaxis.set_tick_params(labelsize=20)
  ax.set_ylabel("nakṣatra", fontsize=30)
  ax.set_xlabel("year", fontsize=30)
  rect = patches.Rectangle((-1450, -5), 450,40, linewidth=3, edgecolor='g', facecolor='none')
  # ax.add_patch(rect)

  if 'gname' in plt_df.columns:
    plt_df.nid = plt_df.nid + ' ( ' + plt_df.gname + ' ) '

  for n in plt_df.nid.unique().tolist() :
    #y = int(re.sub("\D","",n))   
    y = int(re.sub("^.","",re.sub("\-.*","",n)))
    ax.annotate( n, (ofs - 400*(y%2), y ), fontsize=20, color='purple', va='center')

  plt_df.apply( lambda x: ax.annotate( int(sizes[x.year]) , (x.year, -.5), fontsize=20, ha='center', rotation=90 , color='blue'), axis=1,  )

  plt.show();

def do_bounded_plot(n27_df, tag):
  p27_bounded = bounded(n27_df)
  plt_df=p27_bounded[p27_bounded.lon_bounded_eq]
  sizes = plt_df.groupby(by='year').agg(sum).lon_bounded_eq
  #_do_plot_bounded (plt_df, f"All 27 Naks within Bounds - Equal spacing case - {tag}", -3000+3000-100, sizes)
  _do_plot_bounded (plt_df, f"Bounds - {tag}", -3000+3000+100, sizes)

  plt_df=p27_bounded[p27_bounded.lon_bounded_ue]
  sizes = plt_df.groupby(by='year').agg(sum).lon_bounded_ue
  #_do_plot_bounded (plt_df, f"All 27 Naks within Bounds - Unequal spacing case - {tag}", -3000, sizes)

def sanity_plot_lon(n27_df, tag) :
  pd.pivot_table(n27_df, 
    index='year', columns='gnid', values='lon'
    ).diff().plot(
      figsize=(20,8)
    ).set_title(f'Sanity Plots - Longitudes Diffs - {tag}', fontsize=25)

  pd.pivot_table(n27_df, 
    index='year', columns='gnid', values='lon'
    ).diff().applymap(lambda x: 360+x if x <-180 else x).plot(
      figsize=(20,8)
    ).set_title(f'Sanity Plot - Longitudes Diffs Normed - {tag}')

  fig, ax = plt.subplots( 
    nrows=1, ncols=5, sharex=True, sharey=True, 
    figsize=(20,8)
    )
  axs = ax.flat
  for ax, y in zip( axs ,[ -2500, -1500, -500, 0, 500]) :
      n27_df[n27_df.year==y][['gnid', 'lon']].set_index('gnid').sort_index(ascending=False).plot.barh(
        ax=ax, grid=True, 
        title= f'longitude sanity check - {tag}\nfor year {y}' if y==-2500 else f'year {y}' 
        )
  plt.show()

def plot_smooth_mbe(n_df, tag) :
  discrete_df = pd.DataFrame(n_df.groupby(by='year').apply(lambda df: df['err_lon_bounds_eq'].sum()/df.shape[0]), columns=[f'mbe'])
  # smooth_fn = interp1d(discrete_df.index, discrete_df['mbe'],kind='cubic')
  smooth_fn = interp1d(discrete_df.index, discrete_df['mbe'],kind='cubic')
  smooth_df = pd.DataFrame()
  smooth_index = np.arange(-2500,501)
  #smooth_df['mbe'] = smooth_fn(smooth_index)
  smooth_df['mbe'] = [ x if x>0 else 0 for x in smooth_fn(smooth_index)]
  smooth_df.index = smooth_index

  major_ticks=np.arange(-2500,501,50)
  # minor_ticks=np.arange(-2500,501,20)

  ax = smooth_df.plot.line(figsize=(25,8), color='green')
  ax.set_title(f'Minimum Bound Error - {tag}', fontsize=30)
  ax.set_xlabel("year" , fontsize=20)
  ax.set_ylabel("error", fontsize=20)
  ax.set_xticks(major_ticks)
  ax.set_yticks(range(0,31))
  ax.set_xticklabels( 
    [str(x) for x in smooth_df.index if x%50 == 0], 
    rotation=90,
    fontsize=20
  )
  ax.set_yticklabels( 
    [str(x) for x in range(0,31)], 
    rotation=0,
    fontsize=12
  )
  ax.grid(which='major')
#%%
def plot_smooth_mbe2(n_df, n_dfAbh=None, tag="") :
  mark = '1' if 'Bha' in tag else ''
  discrete_df = pd.DataFrame(n_df.groupby(by='year').apply(lambda df: df[f'err_lon_bounds_eq{mark}'].sum()/df.shape[0]), columns=[f'mbe'])
  year_min = n_df.year.min()
  year_max = n_df.year.max()
  step = 250 #if year_max - year_min > 2000 else 10

  n_df2 = n_df[ [ x in  bright9Naks  for x in n_df.nid ] ]
  discrete_df2 = pd.DataFrame(n_df2.groupby(by='year').apply(lambda df: df[f'err_lon_bounds_eq{mark}'].sum()/df.shape[0]), columns=[f'mbe'])

  smooth_fn = interp1d(discrete_df.index, discrete_df['mbe'],kind='cubic' if step==50 else 'linear')
  smooth_fn2 = interp1d(discrete_df2.index, discrete_df2['mbe'],kind='cubic' if step==50 else 'linear')

  smooth_df = pd.DataFrame()
  smooth_index = np.arange(year_min,year_max)
  smooth_df['mbe_all_27'] = smooth_fn(smooth_index)
  smooth_df['mbe_bright_9'] = [ x if x>0 else 0 for x in smooth_fn2(smooth_index)]
  smooth_df.index = smooth_index
  smooth_df.to_csv(f"../datasets/mbe-{tag}.csv")
  major_xticks=np.arange(smooth_df.index.min(),smooth_df.index.max(), step) 
  major_xticks=np.arange(smooth_df.index.min()*0-2500,smooth_df.index.max()*0+501, step) 
  major_yticks=np.arange(0,36,5) 
  smooth_df = smooth_df.rolling(1).mean()
  if ( 'clip' in tag) :
    smooth_df = smooth_df[smooth_df.index <= -250]

  ax = smooth_df[['mbe_all_27']].plot.line(figsize=(25,10), linestyle='-', lw=2, color='green')
  smooth_df[['mbe_bright_9']].plot.line(linestyle='-.', ax=ax, lw=3, color='green')
  ax.set_xticks(major_xticks)
  ax.set_yticks(major_yticks)
  ax.set_xticklabels( 
    # [str(x) if x%250 ==0 else '' for x in smooth_df.index if x%step  == 0], 
    [str(x) if x%250 ==0 else '' for x in major_xticks if x%step  == 0], 
    rotation=0,
    fontsize=25
  )
  ax.set_yticklabels( 
    [f"{int(d)}°" if (d%5==0) else '' for d in major_yticks ], 
    rotation=0,
    fontsize=25
  )

  ylim = 35 - 20
  if n_dfAbh is not None :
    n27_mbe = n_dfAbh.groupby(by=['year']).agg( { 
        'err_lon_bounds_eq' : np.mean,
        'err_lon_bounds_eq1' : np.mean,
        } )
    n27_mbe.columns = ['N27_MBE_BHA_350', 'N27_MBE_BHA_0']
    # n27_mbe = n27_mbe[n27_mbe.N27_MBE_BHA_350 <=26]
    # n27_mbe = n27_mbe[n27_mbe.N27_MBE_BHA_0 <=26]
    n27_mbe = n27_mbe.rolling(1).mean()
    n27_mbe[(n27_mbe.N27_MBE_BHA_350 <=ylim) &  (n27_mbe.index  <= 300)][['N27_MBE_BHA_350']].plot.line(
      ax=ax, linewidth=5, style=[':', ':'], color='green')
  ax.legend([])

  ax.annotate("27 nakṣatra".upper(), (-1500,11), fontsize=25, color='black')
  ax.plot([-1050,-900 ] , [11.25,11.25], linestyle='-', linewidth=3, color='black')
  ax.annotate("9 seasonal nakṣatra".upper(), (-1500, 10), fontsize=25, color='black')
  ax.plot([-800,-650 ] , [10.25,10.25], linestyle='-.', linewidth=3, color='black')
  ax.annotate("Abhyankar's Yogatārā".upper(), (-1500, 9), fontsize=25, color='black')
  ax.plot([-750,-600 ] , [9.25,9.25], linestyle=':', linewidth=3, color='black')

  # ax.annotate("27 nakṣatra".upper(), (-1250, 22), fontsize=20, color='black')
  # ax.plot([-900,-750 ] , [22.5,22.5], linestyle='-', linewidth=3, color='black')
  # ax.annotate("9 seasonal nakṣatra".upper(), (-1250, 20), fontsize=20, color='black')
  # ax.plot([-700,-600 ] , [20.5,20.5], linestyle='-.', linewidth=3, color='black')

  ax.annotate("ādityacāra".upper(), (-2450, 12.5), fontsize=30, color='green')
  ax.annotate("year".upper(), (-2453, .2), fontsize=25, color='black')
  ax.annotate("postion error".upper(), (-2475, 2.8), fontsize=25, color='black', rotation=90)

  ax.minorticks_on()
  ax.yaxis.grid(which='major', linestyle='-', linewidth='1', color='gray')
  ax.yaxis.grid(which='minor', linestyle=':', linewidth='0.75', color='gray')
  ax.xaxis.grid(which='major', linestyle='-', linewidth='1.1', color='gray')
  ax.xaxis.grid(which='minor', linestyle=':', linewidth='0.75', color='gray')
  ax.set_ylim(ymin=0, ymax=15)


    #n27_mbe[(n27_mbe.N27_MBE_BHA_0 <=ylim) & (n27_mbe.index  >= -1500)][['N27_MBE_BHA_0']].plot.line(
    #  ax=ax, linewidth=2, style=[':', ':'], color='red')
  # ax.set_xlim(xmin=2500, xmax=500)

# plot_smooth_mbe2(n27Feb24_sensitivity, n_dfAbh=n27Feb24_abhyankar, tag="Sensitivity - Shr(β Del) Dha(β Aqr)")
#plot_smooth_mbe2(n27Feb24_sensitivity, "xx")
# plot_smooth_mbe2(n27Feb24_sensitivity, "clip")
#%%
#%%
def plot_n87():
  n87 = pd.read_csv("../datasets/n87_bce1400.csv")
  n87['nnid'] = n87.nid.apply( lambda x: int(re.sub("\D","",x)))
  cnt = n87.nid.unique().shape[0]
  def numof(n): return int(re.sub("\D","", n)); 
  def clrof(n): z=numof(n); return((z%2)*z/cnt,((z+1)%2)*z/cnt,((z+2)%2)*z/cnt)
  mcolors = [ x for x in colors.XKCD_COLORS.values()]
  c=[ mcolors[numof(x)*66 % len(mcolors) ]for x in n87.nid ]

  fig, ax = plt.subplots(figsize=(15,7))
  ax.scatter(x=n87.lon, y=n87.lat, c=c, s=600*(1/n87.ncnt))

  ax.set_xticks(range(-30,361,30))
  ax.set_yticks(range(-30,90,10))
  ax.grid()
  ax.set_title(f'{n87.shape[0]} Taras over {n87.nid.unique().shape[0]} Nakshatras - Largely From PT Book, few from chats', fontsize=20)
  ax.set_ylabel("latitude - 1400BCE", fontsize=15)
  ax.set_xlabel("longitude - 1400BCE", fontsize=15)
  n28_mean = n87[['nid','lat', 'lon']].groupby(by='nid').agg(lambda x: np.mean((x-10)%360)+10)
  n28_mean['nnid'] = n28_mean.reset_index().nid.apply( lambda x: int(re.sub("\D","",x))).values
  n28_mean.reset_index().apply( lambda x: ax.annotate(x.nid, (x.lon , 40 + (x.nnid%3)), fontsize=12,rotation=90) ,axis=1);
  n87.reset_index().apply( lambda x: ax.annotate(x.nnid, (x.lon, x.lat), fontsize=13, color='blue', rotation=0 ) ,axis=1);
  plt.show()

# αβγδεσηθικλμνξοπρστυφχψω
def greekify(s) :
  _xlat = {
  'alf' : 'α',
  'bet' : 'β',
  'gam' : 'γ',
  'del' : 'δ',
  'eps' : 'ε',
  'zet' : 'ζ',
  'eta' : 'η',
  'tet' : 'θ', 
  'iot' : 'ι',
  'kap' : 'κ',
  'lam' : 'λ',
  'mu'  : 'μ',
  'nu'  : 'ν',
  'xi'  : 'ξ',
  'omi' : 'ο',
  'pi' :  'π',
  'rho' : 'ρ',
  'sig' : 'σ',
  'tau' : 'τ',
  'ups' : 'υ',
  'phi' : 'φ',
  'chi' : 'χ',
  'psi' : 'ψ',
  'ome' : 'ω'
  }
  xlat = {}
  for k,v in _xlat.items(): 
    xlat[k] = v
    for n in range(1,4):
      xlat[k+str(n)] = v + str(n)
  ans = ' '.join([  xlat[x] if x in xlat else x  for x in re.split("\s+", s)])
  for k,v in _xlat.items(): 
    if v in ans:
      ans = re.sub("^\*\s+","",ans)
      return ans
  return ans

# one time run .. unless bug fixes
def make_naks_meta():
  n87 = pd.read_csv("../datasets/n87.csv")[['nid', 'gname', 'sname', 'hip']]
  n87.hip =n87.hip.apply(
    lambda x: re.sub("HIP\s+","HIP ",x)
  ).apply(
    lambda x: re.sub("^\s+","",x)
  ).apply(
    lambda x: re.sub("\s+$","",x)
  )

  n27 = pd.read_csv("../datasets/n27.csv")[['nid', 'gname', 'sname', 'hip']]
  n27.hip =n27.hip.apply(
    lambda x: re.sub("HIP\s+","HIP ",x)
  ).apply(
    lambda x: re.sub("^\s+","",x)
  ).apply(
    lambda x: re.sub("\s+$","",x)
  )

  n87.gname = n87.gname.apply(lambda x: greekify(x))
  n27.gname = n27.gname.apply(lambda x: greekify(x))

  n27['tag'] = 'rep'
  n87['tag'] = 'other'
  nU=pd.concat( [n27, n87])

  naks_meta = pd.read_csv("../datasets/n27_limited_meta.csv").set_index('nid')
  nU = nU[['nid', 'gname', 'sname', 'hip', 'tag']].set_index('nid').join(naks_meta)
  nU = nU.dropna()

  ans=[]
  for g, df in nU.groupby(by='hip'):
      ans.append(df[df.tag == 'rep'] if df.shape[0] > 1  else df)
      # if df.index.unique().shape[0] > 1: display(df)
  meta_df=pd.concat(ans).sort_values(
    by=['nnid','tag','gname'],
    ascending=[True,False,True]
  )

  meta_df.nnid= [int(x) for x in meta_df.nnid]

  meta_df=meta_df[ ['nnid', 'tag', 'gname', 'sname', 'hip', 'naks', 'enaks', 'daivata'] ]
  meta_df.to_csv("../datasets/~naks_full_meta.csv")
  return meta_df

# make_naks_meta()

def read_naks_meta () :
  return pd.read_csv("../datasets/n83_full_meta.csv")

def bounded_years(n27Date) :
  n27_bounds = bounded(n27Date)[['nid', 'year', 'lon_bounded_eq' ]]
  n27_bounds = n27_bounds[n27_bounds.lon_bounded_eq][['nid', 'year']]
  n27_bounds = n27_bounds.groupby(by='nid').agg(['min','max'])
  n27_bounds.columns = [ '_'.join(x) for x in n27_bounds.columns]
  return n27_bounds

def make_naks_bounds_report(n_df):
  meta_df = read_naks_meta()
  bounded_df = bounded_years(n_df)

  ans = []
  for nid, df in meta_df.groupby(by=['nid']) :
    ans.append( [
      df.nnid.iloc[0],
      nid,
      df.enaks.iloc[0],
      df[df.tag == 'rep'].iloc[0].gname, 
      bounded_df.loc[nid].year_min,
      bounded_df.loc[nid].year_max,
      n27_lon_divisions.loc[nid].l_eq,
      n27_lon_divisions.loc[nid].r_eq,
      df.gname.shape[0],
      # ';'.join(df.gname.tolist()),
      ';'.join( pd.Series(df.gname).sort_values()),
      df.daivata.iloc[0],
      ]
      )

  return pd.DataFrame(ans, columns=[
    '#',
    'nid',
    'nakshatra',
    'rep_star',
    'vis_start_epoch',
    'vis_end_epoch',
    'left_bound',
    'right_bound',
    'num_stars_in_naks',
    'stars_in_naks',
    'daivata',
  ])

#%%
def plot_vgj_seasons ():
  VGJSeasons = '''
  श्रविष्ठादीनि चत्वारि पौष्णार्धञ्च दिवाकरः । वर्धयन् सरसस्तिक्तं मासौ तपति शैशिरे ॥   
  रोहिण्यन्तानि विचरन् पौष्णार्धाद्याच्च भानुमान् । मासौ तपति वासन्तौ कषायं वर्धयन् रसम् ॥          
  सार्पार्धान्तानि विचरन् सौम्याद्यानि तु भानुमान् । ग्रैष्मिकौ तपते मासौ कटुकं वर्धयन् रसम् ॥   
  सावित्रान्तानि विचरन् सार्पार्धाद्यानि भास्करः । वार्षिकौ तपते मासौ रसमम्लं विवर्धयन् ॥    
  चित्रादीन्यथ चत्वारि ज्येष्ठार्धञ्च दिवाकरः । शारदौ लवणाख्यं च तपत्याप्याययन् रसम् ॥                   
  ज्येष्ठार्धादीनि चत्वारि वैष्णवान्तानि भास्करः । हेमन्ते तपते मासौ मधुरं वर्धयन् रसम् ॥ 
  (Ādityacāra; v. 47, 48, 52, 53, 54, 55)
  '''

  fig, ax = plt.subplots(subplot_kw={'projection': 'polar'},figsize=(8,8))
  ax.set_theta_zero_location('E', offset=2*int(360/27))
  ax.set_theta_direction(-1)
  naks = [ re.sub(r"^N...","",x) for x in  n27_lon_divisions.index]
  angles = [ x/1000 for x in range(0, 360000, 13333)]
  angles = angles[:len(naks)]
  # ax.set_rlabel_position(-32.5)  # Move radial labels away from plotted line
  lines, labels = plt.thetagrids(angles, naks) 
  ax.grid(not False)

  angles = np.linspace(0,359.99,num=54)
  cidx = np.roll(np.array([ math.floor(x/(4.5*360/27)) for x in angles]),-1)

  # for f,m in zip(range(0,6), list('o*^pds')) :
  #   ang=angles[cidx==f]
  #   cdx=cidx[cidx==f]

  #   c = ax.scatter(
  #     [x*np.pi/180 for x in ang], 
  #     [3+f%2 for x in ang], 
  #     c=[f for x in cdx], 
  #     s=[50*(1+0*f%2 ) + 0*25*cdx for x in ang], 
  #     cmap='rainbow', 
  #     marker=m,
  #     alpha=0.75)
  ax.set_rticks([])  # Less radial ticks

  delta = np.pi/27
  seasons = [ 'śiśira', 'vāsanta', 'grīṣma',  'varṣā', 'śarat', 'hemanta',]

  for s in range(-1,5) :
    S = 2*np.pi/6 
    L = 8
    _angles = [ x-1*delta for x in [s*S, s*S, (s*S+S)] ]
    if s==0 : _angles[2] = _angles[2] - delta/4 # रोहिण्यन्तानि
    if s==1 : _angles[1] = _angles[1] + delta/4 # सौम्याद्यानि

    if s==2 : _angles[2] = _angles[2] - delta/4 # सावित्रान्तानि
    if s==3 : _angles[1] = _angles[1] + delta/4 # चित्रादीन्य

    if s==4 : _angles[2] = _angles[2] - delta/4 # वैष्णवान्तानि
    if s==-1 : _angles[1] = _angles[1] + delta/4 # श्रविष्ठादीनि
    # print([ x*180/np.pi for x in _angles])
    _vertex = [0,L,L]
    plt.plot(_angles, _vertex, 'b', lw=0, alpha=.2)
    plt.fill(_angles, _vertex,  alpha=.1) 
    if (s > -2 ) :
      season = seasons[(s+1)%len(seasons)]
      L=len(season)
      plt.text(_angles[1] + 2.7/L, L*.72 ,season , fontsize=12, ha='center', va='center')

  plt.title(" Ādityacāra: v. 47, 48, 52, 53, 54, 55\n(Vṛddha-Gārgīya Jyotiṣa Seasons)", fontsize=15)
  plt.show();
  print(VGJSeasons)

# plot_vgj_seasons()
#%%

def plot_mbounds(inm12, tag) :
  m12 = mbounded(inm12)
  m12_pvt=pd.pivot_table(m12, index='year', columns='nnid', values='lon_bounded_eq', aggfunc=sum)
  m12_pvt_sum = m12_pvt.apply(sum, axis=1)
  fig, ax = plt.subplots(figsize=(15,7))
  m12_pvt_sum.plot.bar(figsize=(25,7), grid=True, ax=ax), 
  ax.set_title(f'Monthly Bounds - {tag}', fontsize='30')

  plt.show();

def prev_plot_mbe2_83() :
  # n83_err = naks_lon_err (load_naks_data("../datasets/n83_base_Feb24_bce2500_to_ce0500.tsv"))
  n83_err = naks_lon_err (load_naks_data("../datasets/n83_lat_lon_ra_dec_bce2500_ce1000.tsv"))
  n83_lon = n83_err[ n83_err.year ==  -1500][ ['gname', 'lon']]
  n83_err = pd.merge ( n83_err , n83_lon , on='gname', how='left')
  n83_err = n83_err[ ['nid', 'gname', 'year', 'lon_x', 'err_lon_bounds_eq' , 'err_lon_bounds_eq1', 'lon_y'] ]
  n83_mbe = n83_err.groupby(by=['year']).agg( { 
      'err_lon_bounds_eq' : np.mean,
      'err_lon_bounds_eq1' : np.mean,
      } )
  n83_mbe.columns = ['N83_MBE_BHA_350', 'N83_MBE_BHA_0']
  n83_mbe = n83_mbe[['N83_MBE_BHA_350']]
      
  ax = n83_mbe.plot.line(figsize=(25,10), grid=True, style=['-.'], linewidth=2)
  n27_mbe = n27Feb24.groupby(by=['year']).agg( { 
      'err_lon_bounds_eq' : np.mean,
      'err_lon_bounds_eq1' : np.mean,
      } )
  n27_mbe.columns = ['N27_MBE_BHA_350', 'N27_MBE_BHA_0']
  n27_mbe = n27_mbe[['N27_MBE_BHA_350']]
  ax = n27_mbe.plot.line(ax=ax, linewidth=2)
  ax.set_title ("Minimum Bound Error wrt \n Bharani(41 Ari) from 350, equivalently\n Dhanista (β Del) from 270", fontsize=30)
  r0_35 = range(0,36)
  ax.set_xticks(n27_mbe.index)
  ax.set_xlabel('year', fontsize=20)
  ax.set_ylabel('error', fontsize=20)
  ax.set_yticks(r0_35)
  ax.set_xticklabels(n27_mbe.index, rotation=90, fontsize=25)
  ax.set_yticklabels(r0_35, rotation=0, fontsize=15)
  ax.legend( 
    ['Error using all 83 taras', 'Error using 27 representative taras'], 
    fontsize=30)
  ax.grid(True)

#%%
def plot_mbe2_83(n_df, n_df2 = None, only_abhyankar_27=False) :
  n83_err = naks_lon_err (load_naks_data("../datasets/n83_base_Feb24_bce2500_to_ce0500.tsv"))
  # n83_err = naks_lon_err (load_naks_data("../datasets/n83_lat_lon_ra_dec_bce2500_ce1000.tsv"))
  n83_lon = n83_err[ n83_err.year ==  -1500][ ['gname', 'lon']]
  n83_err = pd.merge ( n83_err , n83_lon , on='gname', how='left')
  n83_err = n83_err[ ['nid', 'gname', 'year', 'lon_x', 'err_lon_bounds_eq' , 'err_lon_bounds_eq1', 'lon_y'] ]
  n83_mbe = n83_err.groupby(by=['year']).agg( { 
      'err_lon_bounds_eq' : np.mean,
      'err_lon_bounds_eq1' : np.mean,
      } )
  n83_mbe.columns = ['N83_MBE_BHA_350', 'N83_MBE_BHA_0']
  # n83_mbe = n83_mbe[n83_mbe.N83_MBE_BHA_350 <=26]
  # n83_mbe = n83_mbe[n83_mbe.N83_MBE_BHA_0 <=26]
  n83_mbe = n83_mbe.rolling(1).mean()

  # n83_mbe = n83_mbe[['N83_MBE_BHA_350']]

  DELTA=20 
  ylim = 35 - 20
  #ax = n83_mbe.plot.line(figsize=(25,10), grid=True, style=['--', '--'], linewidth=2)
  #See if you can terminate the Green curves at -250 and start the red at -1500
  ax = n83_mbe[(n83_mbe.N83_MBE_BHA_350 <=ylim) &  (n83_mbe.index  <= -250) ][['N83_MBE_BHA_350']].plot.line(
    figsize=(25,10), grid=True, style=['--', '--'], linewidth=2 if not only_abhyankar_27 else 0, color='green')
  n83_mbe[(n83_mbe.N83_MBE_BHA_0 <=ylim) & (n83_mbe.index  >= -1500)][['N83_MBE_BHA_0']].plot.line(
    style=['--', '--'], linewidth=2 if not only_abhyankar_27 else 0, ax=ax, color='red')

  n27_mbe = n_df.groupby(by=['year']).agg( { 
      'err_lon_bounds_eq' : np.mean,
      'err_lon_bounds_eq1' : np.mean,
      } )
  n27_mbe.columns = ['N27_MBE_BHA_350', 'N27_MBE_BHA_0']
  # n27_mbe = n27_mbe[n27_mbe.N27_MBE_BHA_350 <=26]
  # n27_mbe = n27_mbe[n27_mbe.N27_MBE_BHA_0 <=26]
  n27_mbe = n27_mbe.rolling(1).mean()
  n27_mbe[(n27_mbe.N27_MBE_BHA_350 <=ylim) &  (n27_mbe.index  <= -250)][['N27_MBE_BHA_350']].plot.line(
    ax=ax, linewidth=2
    , style=['-', '-'] if not only_abhyankar_27 else [':', ':']
    , color='green')
  n27_mbe[(n27_mbe.N27_MBE_BHA_0 <=ylim) & (n27_mbe.index  >= -1500)][['N27_MBE_BHA_0']].plot.line(
    ax=ax, linewidth=2
    , style=['-', '-'] if not only_abhyankar_27 else [':', ':']
    , color='red')

  if n_df2 is not None :
    n27_mbe = n_df2.groupby(by=['year']).agg( { 
        'err_lon_bounds_eq' : np.mean,
        'err_lon_bounds_eq1' : np.mean,
        } )
    n27_mbe.columns = ['N27_MBE_BHA_350', 'N27_MBE_BHA_0']
    # n27_mbe = n27_mbe[n27_mbe.N27_MBE_BHA_350 <=26]
    # n27_mbe = n27_mbe[n27_mbe.N27_MBE_BHA_0 <=26]
    n27_mbe = n27_mbe.rolling(1).mean()
    n27_mbe[(n27_mbe.N27_MBE_BHA_350 <=ylim) &  (n27_mbe.index  <= -250)][['N27_MBE_BHA_350']].plot.line(
      ax=ax, linewidth=2, style=[':', ':'], color='green')
    n27_mbe[(n27_mbe.N27_MBE_BHA_0 <=ylim) & (n27_mbe.index  >= -1500)][['N27_MBE_BHA_0']].plot.line(
      ax=ax, linewidth=2, style=[':', ':'], color='red')

  n09_df = n_df[ [ x in  bright9Naks  for x in n_df.nid ] ]
  n09_mbe = n09_df.groupby(by=['year']).agg( { 
    'err_lon_bounds_eq' : np.mean,
    'err_lon_bounds_eq1' : np.mean,
    } )
  n09_mbe.columns = ['N27_MBE_BHA_350', 'N27_MBE_BHA_0']
  # n09_mbe = n09_mbe[n09_mbe.N27_MBE_BHA_350 <=26]
  # n09_mbe = n09_mbe[n09_mbe.N27_MBE_BHA_0 <=26]
  n09_mbe = n09_mbe.rolling(1).mean()
  ax = n09_mbe[(n09_mbe.N27_MBE_BHA_350 <=ylim) & (n09_mbe.index <=-250)][['N27_MBE_BHA_350']].plot.line(
    ax=ax, linewidth=2 if not only_abhyankar_27 else 0, style=['-.'], color='green')
  # ax = n09_mbe[n09_mbe.N27_MBE_BHA_0 <=ylim][['N27_MBE_BHA_0']].plot.line(ax=ax, linewidth=3, style=['-.'], color='red')

  # ax.set_title ("Minimum Bound Error wrt \n Bharani(41 Ari) from 350, equivalently\n Dhanista (β Del) from 270", fontsize=30)
  r0_35 = range(0,ylim+1,5)
  # ax.set_xticks([ y for y in n27_mbe.index])
  xrange = [ y for y in range(-2500,501,int(500/2))]
  ax.set_xticks(xrange)
  ax.set_xlabel('', fontsize=20)
  ax.set_ylabel('', fontsize=20)
  ax.set_yticks(r0_35)
  # ax.set_xticklabels([ z if z in [-2500, -2000, -1500, -13000, -1000, -500, 0, 500 ] else '' for z in n27_mbe.index], rotation=0, fontsize=25)
  ax.set_xticklabels(xrange, rotation=0, fontsize=25)
  ax.set_yticklabels( [ f"{d}°" if (d %1 == 0 ) else ''  for d in r0_35], rotation=0, fontsize=25)
  # print(dir(ax.get_legend().texts[0]))
  ax.legend( [ ], # [ l.get_text() for l in ax.get_legend().texts],
    # ['83 constituent taras'.upper(), '      ', 
    #  '27 nakṣatras'.upper(),         '      ' ], 
    loc="lower left",
  fontsize=0)
  # ax.annotate("83 stars            --- dotted line".upper(), (-1250, 24), fontsize=20, color='black')
  # ax.annotate("27 nakṣatra         - solid line".upper(), (-1250, 22), fontsize=20, color='black')
  # ax.annotate("9 seasonal nakṣatra - dash-dot line".upper(), (-1250, 20), fontsize=20, color='black')
  if not only_abhyankar_27 :
    ax.annotate("83 stars ".upper(), (-1250, 24/2), fontsize=25, color='black')
    ax.plot([-1000+100,-850+100 ] , [24.5/2,24.5/2], linestyle='--', linewidth=3, color='black')
    ax.annotate(f"27 nakṣatra".upper(), (-1250, 22/2), fontsize=25, color='black')
    ax.plot([-900+100,-750+100 ] , [22.5/2,22.5/2], linestyle='-' if not only_abhyankar_27 else ':' , linewidth=3, color='black')
    ax.annotate("9 seasonal nakṣatra".upper(), (-1250, 20/2), fontsize=25, color='black')
    ax.plot([-700+150,-600+150 ] , [20.5/2,20.5/2], linestyle='-.', linewidth=3, color='black')
  else :
    ax.annotate("27 nakṣatra Abhyankar".upper(), (-1250, 18/2), fontsize=25, color='black')
    ax.plot([-600+150,-500+150 ] , [18.5/2,18.5/2], linestyle=':', linewidth=3, color='black')
  if n_df2 is not None:
    ax.annotate("27 nakṣatra Abhyankar".upper(), (-1250, 18/2), fontsize=25, color='black')
    ax.plot([-600+150,-500+150 ] , [18.5/2,18.5/2], linestyle=':', linewidth=3, color='black')
  ax.annotate("ṛtusvabhāva".upper(), (0, 25/2), fontsize=30, color='red')
  ax.annotate("ādityacāra".upper(), (-2450, 25/2), fontsize=30, color='green')
  ax.annotate("year".upper(), (-2453, .2), fontsize=25, color='black')
  ax.annotate("position error".upper(), (-2475, 3), fontsize=25, color='black', rotation=90)
  # for x1 in range( -2500, 499, 100) :
    # ax.plot ( [x1, x1], [-1,1 + 1 if x1%500==0 else 0], linewidth=2, color='black')
  ax.minorticks_on()
  # ax.grid(True)
  ax.yaxis.grid(which='major', linestyle='-', linewidth='1.2', color='gray')
  ax.yaxis.grid(which='minor', linestyle=':', linewidth='0.75', color='gray')
  ax.xaxis.grid(which='major', linestyle='-', linewidth='1.2', color='gray')
  ax.xaxis.grid(which='minor', linestyle=':', linewidth='0.75', color='gray')
  ax.set_ylim(ymin=0, ymax=30-15)
  ax.set_xlim(xmin=-2500, xmax=500)

#plot_mbe2_83(n27Feb24)
# plot_mbe2_83(n27Feb24)
# plot_mbe2_83(n27Feb24, n27Feb24_abhyankar, only_abhyankar_27=False)
# plot_mbe2_83(n27Feb24_abhyankar, only_abhyankar_27=True)

#%%
def plot_n83_ll(yrs=[-500]) :
  n83a = pd.read_csv("../datasets/n83_lat_lon_ra_dec_bce2500_ce1000.tsv", sep="\t")
  n83_mag = pd.read_csv("../datasets/n83_mag.tsv", sep="\t")[['gname','mag']]
  n83a = pd.merge(n83a, n83_mag, on='gname', how='left')

  def numof(n): return int(re.sub("\D","", n)); 
  # def clrof(n): z=numof(n); return((z%2)*z/cnt,((z+1)%2)*z/cnt,((z+2)%2)*z/cnt)
  mcolors = [ x for x in colors.XKCD_COLORS.values() if '3' in x]
  n83a['ra_adj'] = n83a.ra - n83a.ra.min()
  n83a['lon'] = (n83a.lon-330) % 360

  # yrs = [-500] if rni_only else [-1500,-500]
  for yr in  yrs :
    n83 = n83a[ n83a.year ==  yr]#[ ['gname', 'lon']]
    c=[ mcolors[numof(x)*66 % len(mcolors) ]for x in n83.nid ]
    # n27lbls  = [re.sub('N\d\d\-','', f'{k}:{v}') for k,v in n83.nid.value_counts().sort_index().items()]
    n27_mean = n83.groupby(by='nid').agg( {
      'lon': np.median, 
      'lat': np.median, 
      'ra': np.median, 
      'dec': np.median, 
      'nid': len
      }).rename( columns={'nid': 'cnt'} )
    n27_mean_lbls  = n27_mean.reset_index().sort_values(by=['lon']).apply( 
      lambda x: re.sub('N\d\d\-','', f'{x.nid}:{x.cnt}'), axis =1)
    n27_mean_lon  = n27_mean.reset_index().sort_values(by=['lon']).lon 
    n27_mean_lat  = n27_mean.reset_index().sort_values(by=['lon']).lat
    # n27_mean_ra  = n27_mean.reset_index().sort_values(by=['ra']).ra 
    # n27_mean_dec  = n27_mean.reset_index().sort_values(by=['ra']).dec
    if ( yr == -500 +10000): # 10k to mask the hack
      n83.at[403, 'lon'] = 359 # 408 UBha	उत्तराभाद्रपदा	γ Peg 4.512 => 359 for visual simplicity hack
    # display(n83.sort_values(by='lon').head())

    yspan = np.linspace(-40,40,9) 
    xspan = np.linspace(0,360,13)
    ax = n83.plot.scatter(x="lon", y="lat", c=c, 
      s=pd.cut(n83.mag.max()-n83.mag+1,5).apply(lambda x: 100), 
      # s=pd.cut(n83.mag.max()-n83.mag+1,5).apply(lambda x: 2.5**x.right), 
      # s=pd.cut(n83.mag.max()-n83.mag+1,5).apply(lambda x: 25*x.right), 
      figsize=(25,10)

    )

    #ayana_lbls = ['visuvat', 'd-ayana', 'visuvat', 'u-ayana']
    #for ayana, l in zip( np.linspace(0,360,5), ayana_lbls) :
    #  ax.plot( [ ayana for x in yspan[:2]], [ x for x in yspan[:2]], linestyle="-", linewidth=4 )
    #  ax.annotate( l, (ayana, yspan[:2].mean() ), fontsize=20, color='black', va='center', ha='center', rotation=0)

    louaki_maasa_lbls = "caitra vaiśākha jyeṣṭha āṣāḍha śrāvaṇa bhādra\npada āśvayuja kārtika mārga\nśira pauṣa māgha phālguna".split(" ")
    vedic_maasa_lbls =  "madhu mādhava śuci śukra nabhaḥ nabhasya iṣu ūrja sahas sahasya tapas tapasya".split(" ")
    for lon, l , v in zip( np.linspace(0,360,13), louaki_maasa_lbls, vedic_maasa_lbls) :
      ax.plot( [ lon for x in yspan[:4]], [ x for x in yspan[:4]], linestyle="-", linewidth=0 )
      lon = (lon+15)%360
      # ax.annotate( l, (lon-4, yspan[2:4].mean() ), fontsize=21, color='black', va='center', ha='center', rotation=90)
      # ax.annotate( v, (lon+4, yspan[2:4].mean() ), fontsize=21, color='blue', va='center', ha='center', rotation=90)
      ax.annotate( v.upper(), (30* lon//30, yspan[2:4].mean()-8 ), fontsize=20, color='blue', va='top', ha='center', rotation=0)
      ax.annotate( l.upper(), (30 *lon//30, yspan[2:4].mean()-12 ), fontsize=20, color='black', va='top', ha='center', rotation=0)


    rtu_lbls = ['vasanta', 'grīṣma',  'varṣā', 'śarat', 'hemanta', 'śiśira']
    for rtu,l in zip((np.linspace(0,360,7)- 330) %360 , rtu_lbls) :
      ax.plot( [ rtu-30 for x in yspan[-2:]], [ x for x in yspan[-2:]], linestyle="-.", linewidth=4 )
      ax.plot( [ rtu+30 for x in yspan[-2:]], [ x for x in yspan[-2:]], linestyle="-.", linewidth=4 )
      ax.annotate( l.upper(), (rtu + 0*30, yspan[-2:].mean() ), fontsize=20, color='black', va='center', ha='center', rotation=0)

    ax.plot( [ x for x in xspan], [ 0 for x in xspan] )
    # ax.set_title(f'VGJ - 83 Taras - 27 Nakshatras - Rtu - Ayana\n Longitude Latitude Plot for year {yr}', fontsize=30)
    ax.set_xticks( [ x for x in xspan] )
    # ax.set_xlabel( 'longitude', fontsize=20, rotation=0)
    ax.set_xlabel( '', fontsize=20, rotation=0)
    ax.annotate( 'longitude'.upper(), (3.5, -33 ), fontsize=22, color='black', va='center', ha='left', rotation=0)
    ax.annotate( 'latitude'.upper(), (4.6, -15 ), fontsize=22, color='black', va='bottom', ha='center', rotation=90)
    if ( yr == -500):
      ax.annotate(f"ṛtusvabhāva\n({yr})".upper(), (220, 20), fontsize=30, color='red', ha='left')
    if ( yr == -1500):
      ax.annotate(f"Year\n({yr})".upper(), (220, 20), fontsize=30, color='red', ha='left')
    # ax.set_xticklabels( ['%.2f'%x for x in xspan], fontsize=20, rotation=90)
    # ax.set_xticklabels( ["%02d°%02d'"% (math.floor(x), math.floor(60*(x-math.floor(x))) ) for x in xspan], fontsize=20, rotation=90)
    ax.set_xticklabels( ["%0d°"% ((math.floor(x)+330)%360) for x in xspan], fontsize=25, rotation=0)
    ax.set_yticks( [ x for x in yspan] )
    ax.set_ylabel( '', fontsize=20, rotation=90)
    ax.set_yticklabels( ['%d°'%int(x) if -40 <=x <=40 else '' for x in yspan], fontsize=25, rotation=0)
    # for x, l  in zip( xspan[0:27] + (xspan[1]-xspan[0])/2 , n27lbls) :
    for x, y, l, n  in zip( n27_mean_lon, n27_mean_lat, n27_mean_lbls, range(n27_mean_lon.shape[0])) :
      xdelta = 0
      ydelta = 0
      xdelta = -5 if 'Pus' in l else xdelta 
      xdelta = +5 if 'Asl' in l else xdelta
      xdelta = 5 if 'UPal' in l else xdelta 
      xdelta = 178 if 'UBha' in l else xdelta 
      xdelta = -8 if 'PBha' in l else xdelta 

      ydelta = 0 if 'Ash' in l else ydelta
      ydelta = 0 if 'Bha' in l else ydelta
      ydelta = 0 if 'Kri' in l else ydelta
      ydelta = 20 if 'Roh' in l else ydelta
      ydelta = 20 if 'Mrg' in l else ydelta
      ydelta = 20 if 'Ard' in l else ydelta
      ydelta = 0 if 'Pun' in l else ydelta
      ydelta = 5 if 'Pus' in l else ydelta
      ydelta = 18 if 'Asl' in l else ydelta
      ydelta = 0 if 'Mag' in l else ydelta
      ydelta = -20 if 'PPal' in l else ydelta
      ydelta = -20 if 'UPal' in l else ydelta
      ydelta = 25 if 'Has' in l else ydelta
      ydelta = +5 if 'Chi' in l else ydelta
      ydelta = -20 if 'Swa' in l else ydelta
      ydelta = 20 if 'Anu' in l else ydelta
      ydelta = 20 if 'Mul' in l else ydelta
      ydelta = 25 if 'PAsh' in l else ydelta
      ydelta = 20 if 'UAsh' in l else ydelta
      ydelta = -20 if 'Shr' in l else ydelta
      ydelta = -20 if 'Dha' in l else ydelta
      ydelta = 5 if 'Sha' in l else ydelta
      ydelta = -20 if 'PBha' in l else ydelta
      ydelta =  -10 if 'UBha' in l else ydelta
      ydelta = -2 if 'Rev' in l else ydelta

      sname = "Kṛt Roh Mṛg Ārd Pun Puṣ Āśl Mag PPha UPha Has Cit Svā Viś Anū Jye Mūl PAṣā UAṣā Śra Śrv Śat PPro UPro Rev Aśv Bha".split(" ")
      ename = "Kri Roh Mrg Ard Pun PuS Asl Mag PPal UPal Has Chi Swa Vis Anu Jye Mul PAsh UAsh Śhr Dha Sha PBha UBha Rev Ash Bha".split(" ")

      for e ,s in zip ( ename, sname) :
        l = l.replace(e,s)

      # l = l.replace("Dha:", 'Shrvst:')
      ax.annotate( l, (x + xdelta , y + (-1 if y<0 else 1 ) *10 + ydelta), fontsize=25, color='purple', va='center', ha='center', rotation=90)

    # patch swati for smoothening purpose
    n27_mean_lon[14] =  n27_mean_lon[14] + 10

    smooth_fn = interp1d(n27_mean_lon, n27_mean_lat, kind='cubic')
    smooth_x = np.arange(n27_mean_lon.min(), n27_mean_lon.max(), 1)
    smooth_y = smooth_fn(smooth_x)
    ax.plot( smooth_x, smooth_y, linewidth=2, color='olive')

    if (yr == -1500) :
      moon_df = pd.read_csv("../datasets/full_moon_bce1500.tsv", sep="\t")
      moon_df = moon_df[moon_df.sz.diff() != 0]
      # print(yr)
      m = moon_df[moon_df.year == moon_df.year.unique()[0]] 
      smooth_fn = interp1d(m.lon, m.lat, kind='cubic')
      smooth_x = np.arange(m.lon.min(), m.lon.max(), 30)
      smooth_y = smooth_fn(smooth_x)
      ax.plot( smooth_x, smooth_y, linewidth=1, color='gray', marker='$\odot$', markersize=.30)
      ax.plot( m.lon, m.lat, linewidth=0, color='gray', marker='$\odot$', markersize=30)

    ax.set_xlim(xmin=0, xmax=360)
    ax.set_ylim(ymin=-34, ymax=38)
    ax.grid(True)
    # return ax

# plot_n83_ll()
# axis.get_figure().savefig("../_info/fig4.png")

#%%
def mars_df(start=None, numdays=None) :
  bce501 = ju.julianJD(-590, 6, 1)
  start = start or bce501
  numdays = numdays or 365*2
  
  pp = PP.PlanetPos()
  mars_sun = pd.concat([pp.get_planet_pos(jd=j+bce501).loc[['Mars', 'Sun']] for j in range(0, numdays, 1)])
  mars = mars_sun.loc[['Mars']]
  sun = mars_sun.loc[['Sun']]
  # display(mars.shape, sun.shape, sun)

  nu = nsu.NaksUtils()
  ra_decl = mars.apply( lambda x : pd.Series(nu.ll_to_rd(x.elati, x.elong)[-2:]), axis=1)
  ra_decl.columns = ['ra', 'decl']
  # display(ra_decl, ra_decl.describe())

  mars['year'] = mars.date.apply(lambda x: -int(x.split("-")[1]))
  lon_factor = (mars.elong.diff().apply(lambda x: 0 if x > -300 else 1).cumsum()-1)*360
  ra_factor = lon_factor #(ra_decl.ra.diff().apply(lambda x: 0 if x > -300 else 1).cumsum()-1)*360
  mars['lon'] = mars.elong + lon_factor
  mars['_raf'] = ra_factor
  mars['_ra'] = ra_decl.ra #+ ra_factor
  mars['ra'] = ra_decl.ra + ra_factor

  mars['lat'] = mars.elati
  mars['decl'] = ra_decl.decl
  mars['sun_elong'] = list(sun.elong)
  # mars['tag'] = mars.elong.diff().apply(lambda x: 1 if x < -300 else 0).cumsum()
  mars['tag'] = (mars.elong - mars.sun_elong).abs().apply(lambda x: x if x<=180 else 360-x)
  mars= mars.reset_index()[['jd', 'date', 'year', 'lon', 'lat', '_raf', '_ra', 'ra' , 'decl' , 'elong', 'tag', 'sun_elong']]

  display(mars)
  return mars

# mars_501_2yrs = mars_df()
# mars_501_4yrs = mars_df(numdays=365*15)
mars_501_4yrs = mars_df(numdays=365*15)
#
#%%
axm = mars_501_4yrs.plot.scatter(x="lon", y="lat",  
  # c="tag", cmap="RdPu", 
  s=mars_501_4yrs.tag.apply(lambda x: 10 if x<=20 else 30),
  c=mars_501_4yrs.tag.apply(lambda x: 'red' if x<=20 else 'blue'),
  alpha=0.5, 
  figsize=(25,8)
  )
axm.grid(True)

axm = mars_501_4yrs.plot.scatter(x="lon", y="decl",  
  # c="tag", cmap="RdPu", 
  s=mars_501_4yrs.tag.apply(lambda x: 10 if x<=20 else 30),
  c=mars_501_4yrs.tag.apply(lambda x: 'red' if x<=20 else 'blue'),
  alpha=0.5, 
  figsize=(25,8),
  ax=axm,
  secondary_y=True
  )
axm.grid(True)

#%%
def plot_n83_ll_with_mars_overlay(yrs=[-500]) :
  n83a = pd.read_csv("../datasets/n83_lat_lon_ra_dec_bce2500_ce1000.tsv", sep="\t")
  n83_mag = pd.read_csv("../datasets/n83_mag.tsv", sep="\t")[['gname','mag']]
  n83a = pd.merge(n83a, n83_mag, on='gname', how='left')

  START_LON = 210
  nu = nsu.NaksUtils()
  def numof(n): return int(re.sub("\D","", n)); 
  # def clrof(n): z=numof(n); return((z%2)*z/cnt,((z+1)%2)*z/cnt,((z+2)%2)*z/cnt)
  mcolors = [ x for x in colors.XKCD_COLORS.values() if '3' in x]
  n83a['ra_adj'] = n83a.ra - n83a.ra.min()
  n83a['lon'] = (n83a.lon-START_LON) % 360

  # yrs = [-500] if rni_only else [-1500,-500]
  for yr in  yrs :
    n83 = n83a[ n83a.year ==  yr]#[ ['gname', 'lon']]
    ra_decl = n83.apply( lambda x : pd.Series(nu.ll_to_rd(x.lat, x.lon)[-2:]), axis=1)
    ra_decl.columns = ['ra', 'decl']
    n83.ra = ra_decl.ra
    n83['decl'] = ra_decl.decl
    n83_copy = n83.copy()
    n83_copy['lon'] = n83_copy.lon + 360
    n83_copy['ra'] = n83_copy.ra + 360
    n83_copy['nid'] = n83_copy.nid.apply(lambda x: x +'_1')
    n83 = n83.append(n83_copy)
    # display(n83.shape, n83.head(), n83.tail())
    # return
    c=[ mcolors[numof(x)*66 % len(mcolors) ]for x in n83.nid ]
    # n27lbls  = [re.sub('N\d\d\-','', f'{k}:{v}') for k,v in n83.nid.value_counts().sort_index().items()]
    n27_mean = n83.groupby(by='nid').agg( {
      'lon': np.median, 
      'lat': np.median, 
      'ra': np.median, 
      'dec': np.median, 
      'nid': len
      }).rename( columns={'nid': 'cnt'} )
    n27_mean_lbls  = n27_mean.reset_index().sort_values(by=['lon']).apply( 
      lambda x: re.sub('N\d\d\-','', f'{x.nid}:{x.cnt}'), axis =1)
    n27_mean_lon  = n27_mean.reset_index().sort_values(by=['lon']).lon 
    n27_mean_lat  = n27_mean.reset_index().sort_values(by=['lon']).lat
    # display(n27_mean.sort_values(by=['lon']).reset_index().head(30))
    # n27_mean_ra  = n27_mean.reset_index().sort_values(by=['ra']).ra 
    # n27_mean_dec  = n27_mean.reset_index().sort_values(by=['ra']).dec
    if ( yr == -500 +10000): # 10k to mask the hack
      n83.at[403, 'lon'] = 359 # 408 UBha	उत्तराभाद्रपदा	γ Peg 4.512 => 359 for visual simplicity hack
    # display(n83.sort_values(by='lon').head())

    yspan = np.linspace(-40,40,9) 
    xspan = np.linspace(0,360*2,13)
    ax = n83.plot.scatter(x="lon", y="lat", c=c, 
      s=pd.cut(n83.mag.max()-n83.mag+1,5).apply(lambda x: 100), 
      # s=pd.cut(n83.mag.max()-n83.mag+1,5).apply(lambda x: 2.5**x.right), 
      # s=pd.cut(n83.mag.max()-n83.mag+1,5).apply(lambda x: 25*x.right), 
      # figsize=(60,10)
      figsize=(30,10)

    )

    #ayana_lbls = ['visuvat', 'd-ayana', 'visuvat', 'u-ayana']
    #for ayana, l in zip( np.linspace(0,360,5), ayana_lbls) :
    #  ax.plot( [ ayana for x in yspan[:2]], [ x for x in yspan[:2]], linestyle="-", linewidth=4 )
    #  ax.annotate( l, (ayana, yspan[:2].mean() ), fontsize=20, color='black', va='center', ha='center', rotation=0)

    loukika_maasa_lbls = "caitra vaiśākha jyeṣṭha āṣāḍha śrāvaṇa bhādra\npada āśvayuja kārtika mārga\nśira pauṣa māgha phālguna".split(" ")
    vedic_maasa_lbls =  "madhu mādhava śuci śukra nabhaḥ nabhasya iṣu ūrja sahas sahasya tapas tapasya".split(" ")
    loukika_maasa_lbls = loukika_maasa_lbls[8:] + loukika_maasa_lbls[:8]
    vedic_maasa_lbls  = vedic_maasa_lbls[8:] + vedic_maasa_lbls[:8]

    for lon, l , v in zip( np.linspace(0,360*2,2*12+1), loukika_maasa_lbls+loukika_maasa_lbls, vedic_maasa_lbls+vedic_maasa_lbls) :
      ax.plot( [ lon for x in yspan[:4]], [ x for x in yspan[:4]], linestyle="-", linewidth=0 )
      _yr = lon//360
      lon = (lon+15)%(360*2)
      # ax.annotate( v.upper() if _yr==0 else v.lower(), (30* lon//30, yspan[2:4].mean()-8 ), fontsize=20, color='blue' if _yr==0 else 'black', va='top', ha='center', rotation=0)
      # ax.annotate( l.upper() if _yr==0 else l.lower(), (30 *lon//30, yspan[2:4].mean()-12 ), fontsize=20, color='black' if _yr==0 else 'blue', va='top', ha='center', rotation=0)


    rtu_lbls = ['vasanta', 'grīṣma',  'varṣā', 'śarat', 'hemanta', 'śiśira']
    for rtu,l in zip((np.linspace(0,360*2,6*2+1)- START_LON) , rtu_lbls+rtu_lbls) :
      _yr = rtu//360
      rtu = (rtu+0)%(360*2)
      ax.plot( [ rtu-30 for x in yspan[-2:]], [ x for x in yspan[-2:]], linestyle="-.", linewidth=4 )
      ax.plot( [ rtu+30 for x in yspan[-2:]], [ x for x in yspan[-2:]], linestyle="-.", linewidth=4 )
      ax.annotate( l.upper() if _yr==0 else l.lower(), (rtu + 0*30, yspan[-2:].mean() ), fontsize=20, color='black' if _yr==0 else 'blue', va='center', ha='center', rotation=0)

    ax.plot( [ x for x in xspan], [ 0 for x in xspan] )
    # ax.set_title(f'VGJ - 83 Taras - 27 Nakshatras - Rtu - Ayana\n Longitude Latitude Plot for year {yr}', fontsize=30)
    ax.set_xticks( [ x for x in xspan] )
    # ax.set_xlabel( 'longitude', fontsize=20, rotation=0)
    ax.set_xlabel( '', fontsize=20, rotation=0)
    ax.annotate( 'longitude'.upper(), (40, -33 ), fontsize=22, color='black', va='center', ha='left', rotation=0)
    ax.annotate( 'latitude'.upper(), (4.6, 5 ), fontsize=22, color='black', va='bottom', ha='center', rotation=90)
    # if ( yr == -500):
      # ax.annotate(f"ṛtusvabhāva\n({yr})".upper(), (220, 20), fontsize=30, color='red', ha='left')
    # if ( yr == -1500):
      # ax.annotate(f"Year\n({yr})".upper(), (220, 20), fontsize=30, color='red', ha='left')
    # ax.set_xticklabels( ['%.2f'%x for x in xspan], fontsize=20, rotation=90)
    # ax.set_xticklabels( ["%02d°%02d'"% (math.floor(x), math.floor(60*(x-math.floor(x))) ) for x in xspan], fontsize=20, rotation=90)
    ax.set_xticklabels( ["%0d°"% ((math.floor(x)+ START_LON)%360) for x in xspan], fontsize=25, rotation=0)
    ax.set_yticks( [ x for x in yspan] )
    ax.set_ylabel( '', fontsize=20, rotation=90)
    ax.set_yticklabels( ['%d°'%int(x) if -40 <=x <=40 else '' for x in yspan], fontsize=25, rotation=0)
    # for x, l  in zip( xspan[0:27] + (xspan[1]-xspan[0])/2 , n27lbls) :
    for x, y, l, n  in zip( n27_mean_lon, n27_mean_lat, n27_mean_lbls, range(n27_mean_lon.shape[0])) :
      xdelta = 0
      ydelta = 0
      xdelta = -5 if 'Pus' in l else xdelta 
      xdelta = +5 if 'Asl' in l else xdelta
      xdelta = 5 if 'UPal' in l else xdelta 
      xdelta = 178 if 'UBha' in l else xdelta 
      xdelta = -8 if 'PBha' in l else xdelta 

      ydelta = 0 if 'Ash' in l else ydelta
      ydelta = 0 if 'Bha' in l else ydelta
      ydelta = 0 if 'Kri' in l else ydelta
      ydelta = 20 if 'Roh' in l else ydelta
      ydelta = 20 if 'Mrg' in l else ydelta
      ydelta = 20 if 'Ard' in l else ydelta
      ydelta = 0 if 'Pun' in l else ydelta
      ydelta = 5 if 'Pus' in l else ydelta
      ydelta = 18 if 'Asl' in l else ydelta
      ydelta = 0 if 'Mag' in l else ydelta
      ydelta = -20 if 'PPal' in l else ydelta
      ydelta = -20 if 'UPal' in l else ydelta
      ydelta = 25 if 'Has' in l else ydelta
      ydelta = +5 if 'Chi' in l else ydelta
      ydelta = -20 if 'Swa' in l else ydelta
      ydelta = 20 if 'Anu' in l else ydelta
      ydelta = 20 if 'Mul' in l else ydelta
      ydelta = 25 if 'PAsh' in l else ydelta
      ydelta = 20 if 'UAsh' in l else ydelta
      ydelta = -20 if 'Shr' in l else ydelta
      ydelta = -20 if 'Dha' in l else ydelta
      ydelta = 5 if 'Sha' in l else ydelta
      ydelta = -20 if 'PBha' in l else ydelta
      ydelta =  -10 if 'UBha' in l else ydelta
      ydelta = -2 if 'Rev' in l else ydelta

      sname = "Kṛt Roh Mṛg Ārd Pun Puṣ Āśl Mag PPha UPha Has Cit Svā Viś Anū Jye Mūl PAṣā UAṣā Śra Śrv Śat PPro UPro Rev Aśv Bha".split(" ")
      ename = "Kri Roh Mrg Ard Pun PuS Asl Mag PPal UPal Has Chi Swa Vis Anu Jye Mul PAsh UAsh Śhr Dha Sha PBha UBha Rev Ash Bha".split(" ")

      _yr = n//27
      for e ,s in zip ( ename, sname) :
        l = l.replace(e,s)

      # l = l.replace("Dha:", 'Shrvst:')
      ax.annotate( re.sub("_1","",re.sub(":.*","",l)), (x + xdelta , y + (-1 if y<0 else 1 ) *10 + ydelta), fontsize=20, color='purple' if _yr==0 else "magenta", va='center', ha='center', rotation=90)

    # patch swati for smoothening purpose
    # n27_mean_lon[24] =  n27_mean_lon[24] + 10
    # n27_mean_lon[24+27] =  n27_mean_lon[24+27] + 10
    n27_mean_lon[22] +=  0
    n27_mean_lon[23] +=  0
    n27_mean_lon[24] +=  0 


    smooth_fn = interp1d(n27_mean_lon, n27_mean_lat, kind='linear')
    smooth_x = np.arange(n27_mean_lon.min(), n27_mean_lon.max(), 1)
    smooth_y = smooth_fn(smooth_x)
    ax.plot( smooth_x, smooth_y, linewidth=1, color='olive', linestyle=":")

    if (yr == -1500) :
      moon_df = pd.read_csv("../datasets/full_moon_bce1500.tsv", sep="\t")
      moon_df = moon_df[moon_df.sz.diff() != 0]
      # print(yr)
      m = moon_df[moon_df.year == moon_df.year.unique()[0]] 
      smooth_fn = interp1d(m.lon, m.lat, kind='cubic')
      smooth_x = np.arange(m.lon.min(), m.lon.max(), 30)
      smooth_y = smooth_fn(smooth_x)
      ax.plot( smooth_x, smooth_y, linewidth=1, color='gray', marker='$\odot$', markersize=.30)
      ax.plot( m.lon, m.lat, linewidth=0, color='gray', marker='$\odot$', markersize=30)

    ax.set_xlim(xmin=0, xmax=360*2)
    ax.set_ylim(ymin=-34, ymax=38)

    ax.set_xticks( [ x for x in xspan] ) 

    mars = mars_501_4yrs.copy()
    mars.lon = mars.lon - 210*3
    mars = mars[(mars.lon >= 0) & (mars.lon <= 360*2)]
    # display(mars.describe())
    mars.plot.scatter(x="lon", y="lat", 
      s=mars.tag.apply(lambda x: 10 if x<=20 else 30),
      c=mars.tag.apply(lambda x: 'red' if x<=20 else 'blue'),
      alpha=0.95, ax=ax)
    # mars.plot.scatter(x="lon", xy="lat", s=mars.tag.apply(lambda x: 20*(x//40)+10),  c="tag", cmap="RdPu", alpha=0.95, ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.grid(True)


    return ax

axx=plot_n83_ll_with_mars_overlay()
# axis.get_figure().savefig("../_info/fig4.png")

#%%
def plot_n83_rd_with_mars_overlay(yrs=[-500]) :
  n83a = pd.read_csv("../datasets/n83_lat_lon_ra_dec_bce2500_ce1000.tsv", sep="\t")
  n83_mag = pd.read_csv("../datasets/n83_mag.tsv", sep="\t")[['gname','mag']]
  n83a = pd.merge(n83a, n83_mag, on='gname', how='left')

  START_LON = 210
  nu = nsu.NaksUtils()
  def numof(n): return int(re.sub("\D","", n)); 
  # def clrof(n): z=numof(n); return((z%2)*z/cnt,((z+1)%2)*z/cnt,((z+2)%2)*z/cnt)
  mcolors = [ x for x in colors.XKCD_COLORS.values() if '3' in x]
  n83a['ra_adj'] = n83a.ra - n83a.ra.min()
  n83a['lon'] = (n83a.lon-START_LON) % 360

  # yrs = [-500] if rni_only else [-1500,-500]
  for yr in  yrs :
    n83 = n83a[ n83a.year ==  yr]#[ ['gname', 'lon']]
    ra_decl = n83.apply( lambda x : pd.Series(nu.ll_to_rd(x.lat, x.lon)[-2:]), axis=1)
    ra_decl.columns = ['ra', 'decl']
    n83.ra = ra_decl.ra.apply( lambda x: x + (360 if x < 0 else 0))
    n83['decl'] = ra_decl.decl
    n83_copy = n83.copy()
    n83_copy['lon'] = n83_copy.lon + 360
    n83_copy['ra'] = n83_copy.ra + 360
    n83_copy['nid'] = n83_copy.nid.apply(lambda x: x +'_1')
    n83 = n83.append(n83_copy)
    # display(n83.shape, n83.head(), n83.tail())
    # return
    c=[ mcolors[numof(x)*66 % len(mcolors) ]for x in n83.nid ]
    # n27lbls  = [re.sub('N\d\d\-','', f'{k}:{v}') for k,v in n83.nid.value_counts().sort_index().items()]
    n27_mean = n83.groupby(by='nid').agg( {
      'lon': np.median, 
      'lat': np.median, 
      'ra': np.median, 
      'dec': np.median, 
      'nid': len
      }).rename( columns={'nid': 'cnt'} )
    n27_mean_lbls  = n27_mean.reset_index().sort_values(by=['lon']).apply( 
      lambda x: re.sub('N\d\d\-','', f'{x.nid}:{x.cnt}'), axis =1)
    n27_mean_lon  = n27_mean.reset_index().sort_values(by=['lon']).lon 
    n27_mean_lat  = n27_mean.reset_index().sort_values(by=['lon']).lat
    n27_mean_ra  = n27_mean.reset_index().sort_values(by=['ra']).ra 
    n27_mean_dec  = n27_mean.reset_index().sort_values(by=['ra']).dec
    if ( yr == -500 +10000): # 10k to mask the hack
      n83.at[403, 'lon'] = 359 # 408 UBha	उत्तराभाद्रपदा	γ Peg 4.512 => 359 for visual simplicity hack
    # display(n83.sort_values(by='lon').head())

    yspan = np.linspace(-60,70,14) 
    xspan = np.linspace(0,360*2,25)
    ax = n83.plot.scatter(x="ra", y="decl", c=c, 
      # s=pd.cut(n83.mag.max()-n83.mag+1,5).apply(lambda x: 100), 
      # figsize=(60,10)
      figsize=(30,10)

    )
    # display(n83.head(43), n83.tail(43), n83.describe())

    if False : # maasa names
      loukika_maasa_lbls = "caitra vaiśākha jyeṣṭha āṣāḍha śrāvaṇa bhādra\npada āśvayuja kārtika mārga\nśira pauṣa māgha phālguna".split(" ")
      vedic_maasa_lbls =  "madhu mādhava śuci śukra nabhaḥ nabhasya iṣu ūrja sahas sahasya tapas tapasya".split(" ")
      loukika_maasa_lbls = loukika_maasa_lbls[8:] + loukika_maasa_lbls[:8]
      vedic_maasa_lbls  = vedic_maasa_lbls[8:] + vedic_maasa_lbls[:8]

      for lon, l , v in zip( np.linspace(0,360*2,2*12+1), loukika_maasa_lbls+loukika_maasa_lbls, vedic_maasa_lbls+vedic_maasa_lbls) :
        ax.plot( [ lon for x in yspan[:4]], [ x for x in yspan[:4]], linestyle="-", linewidth=0 )
        _yr = lon//360
        lon = (lon+15)%(360*2)
        # ax.annotate( v.upper() if _yr==0 else v.lower(), (30* lon//30, yspan[2:4].mean()-8 ), fontsize=20, color='blue' if _yr==0 else 'black', va='top', ha='center', rotation=0)
        # ax.annotate( l.upper() if _yr==0 else l.lower(), (30 *lon//30, yspan[2:4].mean()-12 ), fontsize=20, color='black' if _yr==0 else 'blue', va='top', ha='center', rotation=0)
        1

    rtu_lbls = ['vasanta', 'grīṣma',  'varṣā', 'śarat', 'hemanta', 'śiśira']
    for rtu,l in zip((np.linspace(0,360*2,6*2+1)- START_LON) , rtu_lbls+rtu_lbls) :
      _yr = rtu//360
      rtu = (rtu+0)%(360*2)
      ax.plot( [ rtu-30 for x in yspan[-2:]+10], [ x for x in yspan[-2:]+10+5], linestyle="-", linewidth=4 )
      ax.plot( [ rtu+30 for x in yspan[-2:]+10], [ x for x in yspan[-2:]+10+5], linestyle="-", linewidth=4 )
      ax.annotate( l.upper() if _yr==0 else l.lower(), (rtu + 0*30, yspan[-2:].mean()+10+5 ), fontsize=20, color='black' if _yr==0 else 'blue', va='center', ha='center', rotation=0)


    ax.plot( [ x for x in xspan], [ 0 for x in xspan] )
    ax.annotate( 'ra'.upper(), (-20, -50 ), fontsize=22, color='black', va='center', ha='left', rotation=0)
    ax.annotate( 'declination'.upper(), (-20, -40 ), fontsize=22, color='black', va='bottom', ha='center', rotation=90)
    # ax.set_title(f'VGJ - 83 Taras - 27 Nakshatras - Rtu - Ayana\n Longitude Latitude Plot for year {yr}', fontsize=30)
    ax.set_xticks( [ x for x in xspan] )
    # ax.set_xlabel( 'longitude', fontsize=20, rotation=0)
    ax.set_xlabel( '', fontsize=20, rotation=0)
    ax.set_xticklabels( 
        ["%0d°"%((x+START_LON)%360)  for x in (xspan)%360], 
        fontsize=20, 
        rotation=90)
    # return
    # ax.set_xticklabels( ["%0d°"% ((math.floor(x)+ START_LON)%360) for x in xspan], fontsize=25, rotation=0)
    ax.set_yticks( [ x for x in yspan] )
    ax.set_ylabel( '', fontsize=20, rotation=90)
    ax.set_yticklabels( ['%d°'%int(x) if -40 <=x <=80 else '' for x in yspan], fontsize=25, rotation=0)

    # return

    # for x, l  in zip( xspan[0:27] + (xspan[1]-xspan[0])/2 , n27lbls) :
    for x, y, l, n  in zip( n27_mean_ra, n27_mean_dec, n27_mean_lbls, range(n27_mean_lon.shape[0])) :
      # break
      xdelta = 0
      # ydelta = 0
      xdelta = -3 if 'Kri' in l else xdelta 
      xdelta = -3 if 'Pus' in l else xdelta 
      xdelta = +3 if 'Asl' in l else xdelta
      xdelta = -5 if 'Has' in l else xdelta 
      xdelta = 1 if 'UBha' in l else xdelta 
      xdelta = -1 if 'PBha' in l else xdelta 

      # ydelta = 0 if 'Ash' in l else ydelta
      # ydelta = 0 if 'Bha' in l else ydelta
      # ydelta = 0 if 'Kri' in l else ydelta
      # ydelta = 20 if 'Roh' in l else ydelta
      # ydelta = 20 if 'Mrg' in l else ydelta
      # ydelta = 20 if 'Ard' in l else ydelta
      # ydelta = 0 if 'Pun' in l else ydelta
      # ydelta = 5 if 'Pus' in l else ydelta
      # ydelta = 18 if 'Asl' in l else ydelta
      # ydelta = 0 if 'Mag' in l else ydelta
      # ydelta = -20 if 'PPal' in l else ydelta
      # ydelta = -20 if 'UPal' in l else ydelta
      # ydelta = 25 if 'Has' in l else ydelta
      # ydelta = +5 if 'Chi' in l else ydelta
      # ydelta = -20 if 'Swa' in l else ydelta
      # ydelta = 20 if 'Anu' in l else ydelta
      # ydelta = 20 if 'Mul' in l else ydelta
      # ydelta = 25 if 'PAsh' in l else ydelta
      # ydelta = 20 if 'UAsh' in l else ydelta
      # ydelta = -20 if 'Shr' in l else ydelta
      # ydelta = -20 if 'Dha' in l else ydelta
      # ydelta = 5 if 'Sha' in l else ydelta
      # ydelta = -20 if 'PBha' in l else ydelta
      # ydelta =  -10 if 'UBha' in l else ydelta
      # ydelta = -2 if 'Rev' in l else ydelta

      sname = "Kṛt Roh Mṛg Ārd Pun Puṣ Āśl Mag PPha UPha Has Cit Svā Viś Anū Jye Mūl PAṣā UAṣā Śra Śrv Śat PPro UPro Rev Aśv Bha".split(" ")
      ename = "Kri Roh Mrg Ard Pun PuS Asl Mag PPal UPal Has Chi Swa Vis Anu Jye Mul PAsh UAsh Śhr Dha Sha PBha UBha Rev Ash Bha".split(" ")

      _yr = n//27
      for e ,s in zip ( ename, sname) :
        l = l.replace(e,s)

      # l = l.replace("Dha:", 'Shrvst:')
      ax.plot( 
        [x, x], 
        [-50,60], 
        linestyle=":",
        color='purple' if _yr==0 else "magenta", alpha=0.2)

      l1 = re.sub("_1","",re.sub(":.*","",l))
      ax.annotate( 
        # f'{l1}:{x:.0f}°',
        re.sub("_1","",re.sub(":.*","",l)), 
        # (x + xdelta , y + (-1 if y<0 else 1 ) *10 + ydelta), 
        (x +xdelta , -50+50+65 if n%2==0 else 65), 
        fontsize=20-20+13, color='purple' if _yr==0 else "magenta", 
        va='center', ha='center', rotation=90)

    # for x, y, l, n  in zip( n27_mean_ra, n27_mean_dec, n27_mean_lbls, range(n27_mean_ra.shape[0])) :
    #   ax.annotate( l, (x, y + (-1 if yr<0 else 1 ) * (10 if abs(yr)<24 else -10) ), fontsize=20, color='purple', va='center', ha='center', rotation=90)

    # patch swati for smoothening purpose
    # n27_mean_lon[24] =  n27_mean_lon[24] + 10
    # n27_mean_lon[24+27] =  n27_mean_lon[24+27] + 10

    smooth_fn = interp1d(n83.ra, n83.decl, kind='cubic')
    smooth_x = np.arange(n83.ra.min(), n83.ra.max(), 1)
    smooth_y = smooth_fn(smooth_x)
    smooth_y1 = [x if x<=60 else 60 for x in smooth_y]
    smooth_y1 = [x if x>=-40 else -40 for x in smooth_y1]
    ax.plot( smooth_x, smooth_y1, linewidth=1, color='olive', linestyle=":")

    if (yr == -1500) :
      moon_df = pd.read_csv("../datasets/full_moon_bce1500.tsv", sep="\t")
      moon_df = moon_df[moon_df.sz.diff() != 0]
      # print(yr)
      m = moon_df[moon_df.year == moon_df.year.unique()[0]] 
      smooth_fn = interp1d(m.lon, m.lat, kind='cubic')
      smooth_x = np.arange(m.lon.min(), m.lon.max(), 30)
      smooth_y = smooth_fn(smooth_x)
      ax.plot( smooth_x, smooth_y, linewidth=1, color='gray', marker='$\odot$', markersize=.30)
      ax.plot( m.lon, m.lat, linewidth=0, color='gray', marker='$\odot$', markersize=30)

    mars = mars_501_4yrs.copy()
    mars.lon = mars.lon - START_LON*3
    mars = mars[(mars.lon >= 0) & (mars.lon <= 360*2)]
    daynums = (mars.jd  - mars.jd.iloc[0])
    mars.plot.scatter(x="lon", y="decl", 
      s=mars.tag.apply(lambda x: 1 if x<=20 else 1),
      c=mars.tag.apply(lambda x: 'red' if x<=20 else 'blue'),
      alpha=0.95, ax=ax)


    # mars = mars_501_4yrs.copy()
    # mars.ra = mars.ra - START_LON*3
    # mars = mars[(mars.ra >= 0) & (mars.ra <= 360*2)]
    # daynums = (mars.jd  - mars.jd.iloc[0])
    # mars.plot.scatter(x="ra", y="decl", 
    #   s=mars.tag.apply(lambda x: 1 if x<=20 else 1),
    #   c=mars.tag.apply(lambda x: 'red' if x<=20 else 'blue'),
    #   alpha=0.95, ax=ax)


    # mars.plot.scatter(x="lon", xy="lat", s=mars.tag.apply(lambda x: 20*(x//40)+10),  c="tag", cmap="RdPu", alpha=0.95, ax=ax)
    for daynum,lon in zip(daynums.apply(int), mars.lon) :
      if daynum in [0, 220,270,220+120, 540, 585, 765,990,990+120, 1230] :
        ax.annotate( 
        f'day {daynum}', (lon, -40), 
        fontsize=15, 
        color='red' if daynum in [220,220+120,990,990+120] else 'blue' if daynum in [585,765] else 'black',
        va='center', ha= 'center' if daynum>0 else 'left', rotation=90)
    ax.set_xlabel("")
    ax.set_ylabel("")


    return ax

axx=plot_n83_rd_with_mars_overlay()
# axis.get_figure().savefig("../_info/fig4.png")

#%%

def get_fm_df():
  df = nmsu.get_full_moon_planet_pos()
  df = df[df.planet == 'Moon']
  df = df.reset_index().drop(['index' , 'geo_r', 'geoc_x', 'geoc_y', 'geoc_z' , 'planet'], axis=1)
# #year	mm	phase	lon	lat	ra	dec	sz
  df = df.assign (
    year = lambda x: x.date.apply( lambda e: int(re.sub("......T.*", "" , e)))
    , mm =  lambda x: x.date.apply( lambda e: int([x for x in e.split("-") if len(x) >0][1]))
    # , phase =  lambda x: x.jd.apply( lambda e: .99)
    , lon = lambda x: x.elong
    , lat = lambda x: x.elati
  
  ).drop( columns = ['elong', 'elati',])
  nu =  nsu.NaksUtils()
  ra_decl = df.apply(lambda x: nu.ll_to_rd(x.lat, x.lon), axis=1)
  df = df.assign (
    ra = ra_decl.apply(lambda x: x[2]),
    dec = ra_decl.apply(lambda x: x[3]),
    dist = lambda x: x.r,
    sz = lambda x: x.dist/x.dist.mean()
  )
  return df.drop( columns = ['r'])


# fm_df = get_fm_df()
# fm_df

#%%
def n83_drift_rate(n83a = None ):
  if n83a is None:
    n83a = pd.read_csv("../datasets/n83_lat_lon_ra_dec_bce2500_ce1000.tsv", sep="\t")

  ans =[]
  # for n, _df in n83a[(n83a.gname == "ω1 Sco") | (n83a.gname  =="* 17 Tau")][['gname', 'lat', 'lon' , 'ra', 'dec']].groupby('gname') :
  for n, _df in n83a[['gname', 'lat', 'lon' , 'ra', 'dec']].groupby('gname') :
    # display(_df)
    _df = (_df.set_index('gname').diff()).dropna()#.applymap(lambda x: x)
    # display(_df, pd.DataFrame(stats.zscore(_df)))
    _df = _df[(np.abs(stats.zscore(_df)) < 2).all(axis=1)] # remove outliers
    ans.append(_df)
    # display(_df)
  drifts = pd.concat(ans).groupby('gname').mean()
  drifts.rename( columns = { c : f"{c}_drift_per_500_years"  for c in drifts.columns}, inplace=True)
  return drifts

# ans = n83_drift_rate()
# display(ans.sort_values(by =['gname']) , ans.describe())

#%%
def get_year_n83(yr=-2500, n83a=None, n83_drifts=None) :
  if n83a is None:
    n83a = pd.read_csv("../datasets/n83_lat_lon_ra_dec_bce2500_ce1000.tsv", sep="\t")

  if n83_drifts is None:
    n83_drifts = n83_drift_rate(n83a)

  years = n83a.year.unique()
  if yr in years: return n83a[n83a.year == yr]
  min_year = n83a.year.min()
  min_jd = n83a.jd.min()
  delta = yr - min_year
  base_df = n83a[n83a.year == min_year]
  ans = base_df.assign(
    year = lambda x: yr
    , date = lambda x: f"{yr}-12-31T06:00:00"
    , jd = lambda x: min_jd + delta*365.25
    , lon = lambda x: x.lon + x.gname.apply(lambda y: n83_drifts.loc[y, 'lon_drift_per_500_years'])*delta/500
    , lat = lambda x: x.lat + x.gname.apply(lambda y: n83_drifts.loc[y, 'lat_drift_per_500_years'])*delta/500
    , ra = lambda x: x.ra + x.gname.apply(lambda y: n83_drifts.loc[y, 'ra_drift_per_500_years'])*delta/500
    , dec = lambda x: x.dec + x.gname.apply(lambda y: n83_drifts.loc[y, 'dec_drift_per_500_years'])*delta/500
  )

  return ans

def test_get_year_n83(yr=-2500):
  n83a = pd.read_csv("../datasets/n83_lat_lon_ra_dec_bce2500_ce1000.tsv", sep="\t")
  n83_mag = pd.read_csv("../datasets/n83_mag.tsv", sep="\t")[['gname','mag']]
  n83a = pd.merge(n83a, n83_mag, on='gname', how='left')
  n83_drifts = n83_drift_rate(n83a)
  return get_year_n83(yr, n83a, n83_drifts)

# test_get_year_n83(yr=-2570)

#%%


#%%

def plot_n83_rd(yrs=[-1500]) :
  n83a = pd.read_csv("../datasets/n83_lat_lon_ra_dec_bce2500_ce1000.tsv", sep="\t")
  n83_mag = pd.read_csv("../datasets/n83_mag.tsv", sep="\t")[['gname','mag']]
  n83a = pd.merge(n83a, n83_mag, on='gname', how='left')
  n83_drifts = n83_drift_rate(n83a)
  # n83a = pd.merge(n83a, n83_drifts, on='gname', how='left')

  def numof(n): return int(re.sub("\D","", n)); 
  # def clrof(n): z=numof(n); return((z%2)*z/cnt,((z+1)%2)*z/cnt,((z+2)%2)*z/cnt)
  mcolors = [ x for x in colors.XKCD_COLORS.values() if '3' in x]

  # for yr in  [-1500, -500] :
  for yr in  yrs :
    # n83 = n83a[ n83a.year ==  yr]#[ ['gname', 'lon']]
    n83 = get_year_n83(yr, n83a, n83_drifts)
    n83['ra_adj'] = [ 360+x if x<0 else x  for x in  n83.ra] 
    c=[ mcolors[numof(x)*66 % len(mcolors) ]for x in n83.nid ]
    # n27lbls  = [re.sub('N\d\d\-','', f'{k}:{v}') for k,v in n83.nid.value_counts().sort_index().items()]
    n27_mean = n83.groupby(by='nid').agg( {
      'lon': np.median, 
      'lat': np.median, 
      'ra_adj': np.median, 
      'dec': np.median, 
      'nid': len
      }).rename( columns={'nid': 'cnt', 'ra_adj': 'ra'} )
    n27_mean_lbls  = n27_mean.reset_index().sort_values(by=['ra']).apply( 
      lambda x: re.sub('N\d\d\-','', f'{x.nid}:{x.cnt}'), axis =1)
    n27_mean_lon  = n27_mean.reset_index().sort_values(by=['lon']).lon 
    n27_mean_lat  = n27_mean.reset_index().sort_values(by=['lon']).lat
    n27_mean_ra  = n27_mean.reset_index().sort_values(by=['ra']).ra 
    n27_mean_dec  = n27_mean.reset_index().sort_values(by=['ra']).dec 

    # yspan = np.linspace(-42,57,14) 
    yspan = np.linspace(-60,60,15) 
    xspan = np.linspace(0,360,28)
    ax = n83.plot.scatter(x="ra_adj", y="dec", c=c, 
      s=pd.cut(n83.mag.max()-n83.mag+1,5).apply(lambda x: 2.5**x.right), 
      # s=pd.cut(n83.mag.max()-n83.mag+1,5).apply(lambda x: 25*x.right), 
      figsize=(24,10))

    ayana_lbls = ['visuvat', 'd-ayana', 'visuvat', 'u-ayana']
    for ayana, l in zip( np.linspace(0,360,5), ayana_lbls) :
      ax.plot( [ ayana for x in yspan[:2]], [ x for x in yspan[:2]], linestyle="-", linewidth=4 )
      ax.annotate( l, (ayana, yspan[:2].mean() ), fontsize=20, color='black', va='center', ha='center', rotation=0)

    rtu_lbls = [ 'śiśira', 'vāsanta', 'grīṣma',  'varṣā', 'śarat', 'hemanta',]
    for rtu,l in zip((np.linspace(0,360,7)+ 270) %360 , rtu_lbls) :
      ax.plot( [ rtu for x in yspan[-2:]], [ x for x in yspan[-2:]], linestyle="-.", linewidth=4 )
      ax.annotate( l, (rtu + 30, yspan[-2:].mean() ), fontsize=20, color='black', va='center', ha='center', rotation=0)


    ax.plot( [ x for x in xspan], [ 0 for x in xspan] )
    # ax.set_title(f'VGJ - 83 Taras - 27 Nakshatras\n RA Declination Plot for year {yr}', fontsize=30)
    ax.set_title(f'RA Declination Plot for year {yr}', fontsize=20)
    ax.set_xticks( [ x for x in xspan] )
    ax.set_xlabel( 'ra', fontsize=20, rotation=0)
    # ax.set_xticklabels( ['%.2f'%x for x in xspan], fontsize=20, rotation=90)
    ax.set_xticklabels( ["%02d°\n%02d'"% (math.floor(x), math.floor(60*(x-math.floor(x))) ) for x in xspan+ 0*n83a.ra.min()], fontsize=15, rotation=00)
    ax.set_yticks( [ x for x in yspan] )
    ax.set_ylabel( 'declination', fontsize=15, rotation=90)
    ax.set_yticklabels( ['%d'%int(x) for x in yspan], fontsize=20, rotation=0)
    # for x, l  in zip( xspan[0:27] + (xspan[1]-xspan[0])/2 , n27lbls) :
    for x, y, l, n  in zip( n27_mean_ra, n27_mean_dec, n27_mean_lbls, range(n27_mean_ra.shape[0])) :
      ax.annotate( l, (x, y + (-1 if yr<0 else 1 ) * (10 if abs(yr)<24 else -10) ), fontsize=20, color='purple', va='center', ha='center', rotation=90)

    ax.plot( n27_mean_ra, n27_mean_dec , linestyle=':')
    # n27_mean_lon[14] =  n27_mean_lon[14] + 10

    smooth_fn = interp1d(n27_mean_ra, n27_mean_dec, kind='cubic')
    smooth_x = np.arange(n27_mean_ra.min(), n27_mean_ra.max(), 1)
    smooth_y = smooth_fn(smooth_x)
    ax.plot( smooth_x, smooth_y, linewidth=2, color='olive')

    if True or (yr == -1500) :
      # moon_df = pd.read_csv("../datasets/full_moon_bce1500.tsv", sep="\t")
      moon_df = get_fm_df()
      moon_df['ra_adj'] = [ 360+x if x<0 else x  for x in  moon_df.ra] 
      moon_df = moon_df[moon_df.sz.diff() != 0] #drop noise
      for nmoon in range(0,1) :
        # m = moon_df[moon_df.year == moon_df.year.unique()[nmoon]] 
        # m = moon_df[moon_df.year == -1399] 
        m = moon_df[moon_df.year == yr] 
        smooth_fn = interp1d(m.ra_adj, m['dec'], kind='cubic')
        smooth_x = np.arange(m.ra_adj.min(), m['dec'].max(), 30)
        smooth_y = smooth_fn(smooth_x)
        # ax.plot( smooth_x, smooth_y, linewidth=0, color='gray', marker='$\odot$', markersize=30)
        # ax.plot( 
        #   m.ra_adj, m.dec, linewidth=0, color='gray', marker='.', 
        #   markersize=30
        # )
        ax.scatter( 
          x=m.ra_adj, y=m.dec, marker='$\odot$', 
          s=500 + 40000*(m.sz - m.sz.min()),
          c = c[15*nmoon%len(c)]
        )

    ax.grid(True)

plot_n83_rd(yrs=list(range( -500,-2000,-500)))


#%%
def fig1(): return plot_mbe2_83(n27Feb24, n27Feb24_abhyankar)
def fig2(): return plot_smooth_mbe2(n27Feb24_sensitivity, n27Feb24_abhyankar, tag="Sensitivity - Shr(β Del) Dha(β Aqr)")
def fig3(): return plot_n83_ll()  

def rni_paper_plots() :
  # ĀDITYACĀRA and ṚTUSVABHĀVA plots
  # plot_mbe2_83(n27Feb24) 
  fig1() ; fig2() ; fig3()
  # plot_mbe2_83(n27Feb24_abhyankar)
  # plot_smooth_mbe2(n27Feb24, "Base - Minima around 1200 BCE")
  # plot_smooth_mbe2(n27Feb24_sensitivity, "Sensitivity - Shr(β Del) Dha(β Aqr)- clip")

#%%
def all_plots() :
  print("Plots for Transit of sun through the seasonal nakṣatra cycle in the Vṛddha-Gārgīya Jyotiṣa")
  print("Indian Journal of History of Science, 56.3(2021)")
  rni_paper_plots(); plt.show()

  print("Other Plots")
  plot_n83_ll(yrs=[-1500])
  plot_n83_rd()
  do_bounded_plot(n27Feb24, "All 27")
  plot_vgj_seasons()
  print("End Other Plots")

#%%
n27_lon_divisions = None
bright6Naks = None
bright6Lbls = None
bright9Naks = None
bright9Lbls = None
n27Feb24 = None
n27Feb24_sensitivity = None
n27Feb24_abhyankar = None
naks_eq_bounds_report = None
m12 = None

def init_globals () :
  global n27_lon_divisions
  global bright6Naks
  global bright6Lbls
  global bright9Naks
  global bright9Lbls
  global n27Feb24
  global n27Feb24_sensitivity
  global n27Feb24_abhyankar
  global naks_eq_bounds_report
  global m12

  if n27_lon_divisions is not None : return

  n27_lon_divisions = make_n27_lon_divisions()
  bright6Naks = [ x for x in n27_lon_divisions.index if re.match('^.*(03|04|10|14|16|18).*$', x) ]
  bright6Lbls = [ re.sub("^N\d\d.","", x) for x in n27_lon_divisions.index if re.match('^.*(03|04|10|14|16|18).*$', x) ]
  #dhanishtha, revati, rohini, mrgashira, ashlesha, hasta, chitra, jyeshtha, shravana.
  bright9Naks = [ x for x in n27_lon_divisions.index if re.match('^.*(dha|rev|roh|mrg|asl|has|chi|jye|shr).*$', x,re.IGNORECASE) ]
  bright9Lbls = [ re.sub("^N\d\d.","", x) for x in bright9Naks ]

  # This TSH has incorrect ASHadas .. no need to patch as below
  # patch Feb24 which had wrong ASH with Feb20 info which has correct ASH - from stell
  n27Feb24 = load_naks_data("../datasets/n27_base_Feb24_bce2500_to_ce0500.tsv")
  n27Feb24 = naks_lon_err(n27Feb24)
  n27Feb20_delta  = load_naks_data("../datasets/n27_delta_Feb20_bce2500_to_ce0500.tsv")
  n27Feb20_delta = naks_lon_err(n27Feb20_delta)
  ash_patch = n27Feb20_delta[ [('20' in x) or ('21' in x) for x in n27Feb20_delta.nid ]]
  n27Feb24_nonash = n27Feb24[ [not(('20' in x) or ('21' in x)) for x in n27Feb24.nid ]]
  n27Feb24Patched = pd.concat( [n27Feb24_nonash, ash_patch])
  n27Feb24 = n27Feb24Patched.sort_values(['nid', 'year'])

  # Generate table for the IJHS paoer
  naks_eq_bounds_report = make_naks_bounds_report(n27Feb24)
  # naks_eq_bounds_report.to_csv("../datasets/naks_eq_bounds_report.csv", index=None)
  # naks_eq_bounds_report

  # patch Shr and Dha for sensitivity plots
  n27Feb24_shr_dha_delta  = load_naks_data("../datasets/n27_delta_shr_dha_bce2500_to_ce0500.tsv")
  n27Feb24_shr_dha_delta = naks_lon_err(n27Feb24_shr_dha_delta )
  n27Feb24_non_shr_dha = n27Feb24[ [not(('Shr' in x) or ('Dha' in x)) for x in n27Feb24.nid ]]
  n27Feb24_sensitivity = pd.concat([ n27Feb24_non_shr_dha, n27Feb24_shr_dha_delta])
  n27Feb24_sensitivity = n27Feb24_sensitivity.sort_values(['nid', 'year'])

  # n27Feb24zoom = load_naks_data("../datasets/n27_base_Feb24_bce1400_to_bce0900_zoom.tsv")
  # n27Feb24zoom = naks_lon_err(n27Feb24zoom)

  m12 = load_naks_data("../datasets/m12_base_mar20_bce2500_to_ce0500.tsv")
  # zm12 = load_naks_data('../datasets/m12_base_mar20_bce0700_to_ce0000_zoom.tsv')

  # patch Abhyankar nakshatras
  # var $NAbhyankar = [
  #   "N10-Mag	मघाः	α Leo	Regulus	HIP 49669",
  #   "N13-Has	हस्तः	γ Crv	Gienan	HIP  59803",
  #   "N18-Jye	ज्येष्ठा	α Sco	Antares	HIP  80763",
  #   "N19-Mul	मूलं	λ Sco	Shaula	HIP  85927",
  #   "N20-PAsh	पूर्वाषाढा	δ Sgr	Kaus Media	HIP 89931",
  #   "N21-UAsh	उत्तराषाढा	σ Sgr	Nunki	HIP 92855",	

  #   //"N22-Shr	धनिष्ठा	β Del	Rotanev	HIP 101769",  // Included in NSensitivity
  #   //"N23-Dha	धनिष्ठा	β Aqr	Sadalsuud	HIP 106278",

  #   "N24-Sha	शतभिषक्	α PsA	Fomalhaut	HIP 113368",
  #   "N27-Rev	रेवती	ζ Psc	Revati	HIP 5737",
  # ]
  # */
  n27Feb24_abhyankar_delta = load_naks_data("../datasets/n27_delta_abhyankar_bce2500_to_ce0500.tsv")
  n27Feb24_abhyankar_delta = naks_lon_err(n27Feb24_abhyankar_delta)
  n27Feb24_non_abhyankar = n27Feb24[ [not(
    ('Mag' in x) or ('Has' in x) or ('Jye' in x) or ('Mul' in x) 
    or ('PAsh' in x) or ('UAsh' in x) or ('Shr' in x) or ('Dha' in x)
    or ('Sha' in x) or ('Rev' in x)
    ) for x in n27Feb24.nid ]]
  n27Feb24_abhyankar = pd.concat([ n27Feb24_non_abhyankar, n27Feb24_shr_dha_delta, n27Feb24_abhyankar_delta])
  n27Feb24_abhyankar = n27Feb24_abhyankar.sort_values(['nid', 'year'])


# %%
#### NON CORE STUFF

def spot_check():
  rni = n27Feb24[ 
    ( n27Feb24.year < 10000) 
    # (n27Feb24.gname == 'β Del') & (n27Feb24.err_lon_bounds_eq < 2) 
    # (n27Feb24.nid == 'N23-Dha') & (n27Feb24.err_lon_bounds_eq < 2)
    # (n27Feb24.err_lon_bounds_eq < 2)
    #(abs(n27Feb24.lon - 270) < 1)
    ][
      ['nid','gname', 'year', 'lon', 'err_lon_bounds_eq']
      ].sort_values(['nid', 'year'])

  sens = n27Feb24_sensitivity [ 
    ( n27Feb24_sensitivity.year < 10000) 
    # (n27Feb24_sensitivity.gname == 'β Del') & (n27Feb24_sensitivity.err_lon_bounds_eq < 2) 
    # (n27Feb24_sensitivity.nid == 'N23-Dha') & (n27Feb24_sensitivity.err_lon_bounds_eq < 2) 
    # (n27Feb24_sensitivity.err_lon_bounds_eq < 2) 
    # (abs (n27Feb24_sensitivity.lon -270) < 1)
    ][
      ['nid','gname', 'year', 'lon', 'err_lon_bounds_eq']
      ].sort_values(['nid', 'year'])


  abh = n27Feb24_abhyankar [ 
    ( n27Feb24_abhyankar.year < 10000) 
    # (n27Feb24_sensitivity.gname == 'β Del') & (n27Feb24_sensitivity.err_lon_bounds_eq < 2) 
    # (n27Feb24_abhyankar.nid == 'N23-Dha') & (n27Feb24_abhyankar.err_lon_bounds_eq < 2) 
    # (n27Feb24_abhyankar.err_lon_bounds_eq < 2) 
    # (abs(n27Feb24_abhyankar.lon - 270) <1)
    ][
      ['nid','gname', 'year', 'lon', 'err_lon_bounds_eq']
      ].sort_values(['nid', 'year'])

  ans = sens.sample(10).sort_values(['nid','gname','year']).apply(lambda x: x.tolist(), axis=1).tolist(
  ) + sens[sens.nid.apply(lambda x: bool(re.match("^.*(2\d).*$",str(x))))].sample(10).sort_values(['nid','gname','year']).apply(lambda x: x.tolist(), axis=1).tolist(  
  ) + rni.sample(10).sort_values(['nid','gname','year']).apply(lambda x: x.tolist(), axis=1).tolist(
  ) + rni[rni.nid.apply(lambda x: bool(re.match("^.*(2\d).*$",str(x))))].sample(10).sort_values(['nid','gname','year']).apply(lambda x: x.tolist(), axis=1).tolist(  
  ) + abh.sample(10).sort_values(['nid','gname','year']).apply(lambda x: x.tolist(), axis=1).tolist(
  ) + abh[abh.nid.apply(lambda x: bool(re.match("^.*(2\d).*$",str(x))))].sample(10).sort_values(['nid','gname','year']).apply(lambda x: x.tolist(), axis=1).tolist(  
  )
  
  naks_divisions  = n27_lon_divisions[['r_eq', 'l_eq', 'r_eq1', 'l_eq1']].rename(
    columns={'r_eq':'Ādityacāra_lo', 'l_eq':'Ādityacāra_hi', 'r_eq1':'Ṛtusvabhāva_lo', 'l_eq1':'Ṛtusvabhāva_hi'}
  )

  proxy_stars = pd.merge (
    pd.merge (
    rni[['nid', 'gname']].drop_duplicates(), #.set_index('nid'),
    sens[['nid', 'gname']].drop_duplicates(), #.set_index('nid'), 
    how='left', on='nid'
  ),
    abh[['nid', 'gname']].drop_duplicates(), #.set_index('nid'),
    how='left', on='nid'
  ).rename(columns={'gname_x':'rni_proxy', 'gname_y':'sens_proxy', 'gname':'abh_yoga'})

  display (
    "Naks Span", naks_divisions,
    "================",
    "ProxyStars", proxy_stars , 
    "================",
    "Seasonal 9", bright9Naks , 
    )

def _verify_plot(rni,abh,sens, seasonal=[]):
  if seasonal :
    # print ( "Seasonal", len(seasonal), seasonal )
    rni = rni[ [n in seasonal for n in rni.nid] ]
    abh = abh[ [n in seasonal for n in abh.nid] ]
    sens = sens[ [n in seasonal for n in sens.nid] ]

  pvt=pd.pivot_table(rni, 
    index=['nid'], 
    columns=['year'], 
    values='err_lon_bounds_eq', 
    aggfunc=np.mean).T
  ax=pvt.apply(np.mean , axis=1).plot(
    figsize=(6,2), 
    lw=1 if len(seasonal)!=9 else 4,
    ls=':' if len(seasonal)!=9 else '-.',
    
    #color='pink' if len(seasonal)!=9 else 'blue',
    #legend=None
    )

  # pvt=pd.pivot_table(abh, 
  #   index=['nid'], 
  #   columns=['year'], 
  #   values='err_lon_bounds_eq', 
  #   aggfunc=np.mean).T
  # ax=pvt.apply( np.mean , axis=1).plot( 
  #   color='red', ax=ax)

  # pvt=pd.pivot_table(sens, 
  #   index=['nid'], 
  #   columns=['year'], 
  #   values='err_lon_bounds_eq', 
  #   aggfunc=np.mean).T
  # ax=pvt.apply( np.mean , axis=1).plot( 
  #   color='orange', ax=ax) 
  ax.set_title(
    f"{ 'Seasonal' if seasonal else ''} Adityachara Error\n{seasonal if seasonal else 'All 27'} \n Individual-dotted  All9-thick",
    fontsize=8
  )
  #plt.show()

def verify_plot():
  rni = n27Feb24[ 
    ( n27Feb24.year < 10000) 
    ][
      ['nid','gname', 'year', 'lon', 'err_lon_bounds_eq']
      ].sort_values(['nid', 'year'])

  sens = n27Feb24_sensitivity [ 
    ( n27Feb24_sensitivity.year < 10000) 
    ][
      ['nid','gname', 'year', 'lon', 'err_lon_bounds_eq']
      ].sort_values(['nid', 'year'])

  abh = n27Feb24_abhyankar [ 
    ( n27Feb24_abhyankar.year < 10000) 
    ][
      ['nid','gname', 'year', 'lon', 'err_lon_bounds_eq']
      ].sort_values(['nid', 'year'])
  for ss in range(1,9):
    naks_9 = rni[['nid']].drop_duplicates().sample(9).sort_values(['nid'])['nid'].tolist()
    for ss in range(1,9):
      _verify_plot(rni,abh,sens, seasonal=naks_9[ss-1:ss])
    _verify_plot(rni,abh,sens, seasonal=naks_9[:])
    plt.show()

# %%
if __name__ == "__main__":
  init_globals()
  all_plots()
  print ("****************************************************")
  spot_check()
  print ("****************************************************")
  verify_plot()
