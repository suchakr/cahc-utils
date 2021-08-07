#%%
import pandas as pd
import numpy as np
from datetime import datetime
import re
import matplotlib.pyplot as plt

#%%
# dtypes = [str, str, float, float, float]
mr = pd.read_csv("../datasets/mars-retro.txt", sep="\t").drop(columns=['hhmm'])
mr.date = pd.to_datetime(mr.date)
mr = mr.set_index('date')
mr

# %%
ax = mr.plot()
ax.grid()
# %%

mr.plot(kind='scatter', x="lon", y="lat")

# %%
f=0
ans =[]
for d ,l in zip(mr.lon.diff() , mr.lon) :
  if d < -300 : f+=1
  ans.append( l + f*360)

mr['lona'] = ans
mr[300:450].plot(kind='scatter', x="lona", y="lat", marker='.')
# %%
mr[450:500].plot(kind='scatter', x="lona", y="lat", marker='.')

# %%
mr['ldiff'] = mr.lon.diff()
mr['retro'] = mr.ldiff.apply( lambda x: 1 if x < -1 and x >-300 else 0)
mr1 = mr.reset_index()
mr1 = mr1[mr1.retro==1]
idx = pd.Series(mr1.index)
idxd = idx.diff()
idx[idxd>1].shape

#%%
fig, axs = plt.subplots(3,7, figsize=(25,16))
fig.tight_layout(pad=3.0)


for span,ax in zip(idx[idxd>1], axs.flatten()) :
  mrx = mr[span-50:span+50]
  mrx.plot(ax=ax, kind='scatter', 
  x="lona", y="lat", marker='.', 
  sharey=True,
  title=re.sub(".\d\d\s00:00:00","",str(mrx.index[0]))) 
  ax.set_xlabel("")
  # ax.set_xticklabels([ t.get_text() for t in ax.get_xticklabels()])
  print([ int(t%360) for t in ax.get_xticks()])
  ax.set_xticklabels([ int(t%360) for t in ax.get_xticks()])

# %%
