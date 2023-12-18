#%%
import pandas as pd 
import generate_counts as gmc   # gmc = generate matra counts
import numpy as np 
import sys
import re
from glob import glob

def warn(*args, **kwargs): print(*args, file=sys.stderr, **kwargs)

def rv_count() :
  # for csv in [ x for x in sys.argv if re.match( ".*csv$", x) ] :
  for csv in [ x for x in glob("v*csv") if re.match( ".*csv$", x) ] :
    print(csv)
    rgdf = pd.read_csv(csv)#.head(2)
    display(rgdf.head())
    #rgdf = pd.read_csv("./rgveda.csv")
    num_mantras , _  = rgdf.shape

    scores =[]
    counts = []
    durations = []
    padded_double_virama = [ 2 ,'|']
    N=0
    F=0
    for n in range(num_mantras) :
      mantra = rgdf["Mantra"][n]
      try:
        N=N+1
        score = gmc.countMatras(input_mantra= mantra)
        _score = map( lambda x : [] if x == padded_double_virama else x, score)
        count, duration = gmc.summmarizeMatras( _score)
        scores.append(score)
        counts.append(count)
        durations.append(duration)
      except:
        F=F+1
        warn("%s as position %d failed" %  (mantra,n) )
        scores.append( [ [-1] ])
        counts.append(-1)
        durations.append(-1)

    rgdf['counts'] = counts
    rgdf['durations'] = durations
    rgdf['scores'] = scores

    tsv = csv.replace(".csv" , "_score~.tsv")
    rgdf.to_csv (tsv, index=False, sep="\t")
    #rgdf.to_csv ("./rgveda_score.tsv", index=False, sep="\t")
    print ("=========================")
    print ( '%s => %s ; Mantras(Total=%6d; Exceptions=%6d)' % (csv, tsv, N,F))
    print (rgdf.head())
    #print(rgdf.info())
    #print(rgdf.durations.value_counts().sort_index())
    print ("Mantras that could not be scored")
    print (rgdf[rgdf.durations == -1].durations.value_counts())
    print (rgdf[rgdf.durations == -1].head().Mantra)
    print ("=========================")
#%%
if __name__ == "__main__" :
  rv_count()


# %%
