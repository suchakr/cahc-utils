'''
Surya Chandra Prajaptin -:- The Astrological Algorithms of SuryaChandra.
'''
#%%
import NaksUtils
from IPython.display import display
from sympy import *
import pandas as pd
import numpy as np
class SCP :
	'''
	Observational data of Sun and Moon transit through Nakshatra
	'''
	def __init__(self, **kwargs) :
		nu = NaksUtils.NaksUtils()
		
		pass

	def TestSCP() :
		pass
#%%
if __name__ == '__main__' :
	nu = NaksUtils.NaksUtils()
	display(nu.df)
	SCP.TestSCP()
# %%
help(sympy)

# %%
 (x, y, K) = symbols('x y K')
 solve([K - x/y, x -21, y - 67])

# %%
(hh, mm, d, m , y ) = symbols('hh mm d m y')
ans = solve([
  hh - mm/60,
  d - hh/24,
  m - d/30,
  y - m/12,
  d - 365
])
ans
#%%
ans = pd.DataFrame(ans, index=['d']).T
ans
#%%
ans['dec'] = ans.val.apply( lambda x: '%0.2f' %eval(str(x)))
ans

# %%
