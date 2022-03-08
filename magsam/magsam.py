'''
## [magsam](https://github.com/suchakr/cahc-utils/tree/sunder_experiments/magsam)

- Word by word conversion of Srilankan maagadhi to samskrita using curated dictionary

'''
#%%
from IPython.display import Markdown, display
import pandas as pd
import numpy as np
import re 
from nltk.corpus import stopwords
from nltk.metrics import edit_distance
from indic_transliteration import sanscript
from indic_transliteration.sanscript import SchemeMap, SCHEMES, transliterate
#%%
class MagSam:
	'''
	MagSam class to translate Magadhi words to Samskrit
	'''
	def TypicalUse():
		ms = MagSam()
		ms.load_kosha()
		maghadhi = 'वोहारन्ति वेदितब्बं'
		samskrit = ms.translate_maghadi(maghadhi)
		print(f'{maghadhi} => {samskrit}')

	def _itransify(data): 
		return transliterate(data, sanscript.DEVANAGARI, sanscript.ITRANS).lower()

	def _i_edit_distance(a,b):
		a,b = MagSam._itransify(a), MagSam._itransify(b)
		return edit_distance(a,b)

	_split_tokens = re.compile(r'[‘;\-"\',।\s\.\*\[\]\(\)!१२३४५६७८९०॥–’]+')
	def _tokenize(text):
		try :
			ans = [ x for x in MagSam._split_tokens.split(text) if x != '']
		except Exception as e:
			print(e)
			print(text)
			ans = []
		return ans

	def _confidence(row):
		# ed = (1-row.edit_dist/len(row.m))
		# i_ed = (1-row.i_edit_dist/len(row.m))
		u_ed = row.edit_dist
		i_ed = row.i_edit_dist
		ed = (u_ed + i_ed)/2
		return 1-(ed/len(row.m))


	def __init__(self, kosha='../datasets/magsam_kosha.tsv'):
		# print(f'Training set size: {self.train_sz}')
		self.kosha_tsv = kosha
		self.pre_kosha_tsv = kosha + ".debug.tsv"
		self.kosha_df = None
		self.pre_kosha_df = None
		self.load_kosha()

	def load_kosha(self, force=False):
		'''
		Loads kosha data if it exists and regenrates it is not
		'''
		try:
			if force: raise Exception(f'Generation kosha_df. Ignoring existing {self.kosha_tsv}')
			self.kosha_df = pd.read_csv(self.kosha_tsv, sep='\t', quoting=3).set_index('m')
		except Exception as e:
			print(e)
			print(f'Generating kosha_df. {self.kosha_tsv}')
			self.generate_kosha()
			self.save_kosha()
			self.kosha_df = pd.read_csv(self.kosha_tsv, sep='\t', quoting=3).set_index('m')
			self.pre_kosha_df = pd.read_csv(self.pre_kosha_tsv, sep='\t', quoting=3)
		try:
			self.pre_kosha_df = pd.read_csv(self.pre_kosha_tsv, sep='\t', quoting=3)
		except Exception as e:
			pass

	def generate_kosha(self, training_tsv='../datasets/magsam_training.tsv', train_fraction=1):
		self.training_tsv = training_tsv
		training_df = pd.read_csv( training_tsv , sep='\t', quoting=3).dropna()
		ms ,ss = training_df.maghadi.apply(MagSam._tokenize), training_df.samskrit.apply(MagSam._tokenize)
		training_df['t_maghadi'] = ms
		training_df['t_samskrit'] = ss
		self.training_tsv = training_tsv
		self.training_df = training_df
		self.train_sz = int(training_df.shape[0]*train_fraction)
		self._generate_kosha()

	def _generate_kosha(self, step=-1, verbose=False):
		'''
		Build kosha dictionary from given training dataframe
		'''
		sz = self.train_sz 
		# get first sz rows of training dataframe 
		# are used to build the kosha dictionary
		# the rest are used for validation
		self.training_df = self.training_df.sample(frac=1).reset_index(drop=True)
		# self.training_df = self.training_df.sample(frac=1)
		self.training_df.loc[:,'trained_on'] = True
		# self.training_df.loc[:sz,'trained_on'] = True
		self.training_df.loc[sz:,'trained_on'] = False
		training_df = self.training_df
		# display(sz, training_df.trained_on.value_counts())
		training_df = training_df.head(sz)

		for n in range(0,sz,sz if step < 0 else step):
			df = training_df[n:n+step]
			ans=[ ( 
				m
				,s
				,MagSam._itransify(m)
				,MagSam._itransify(s)
				,0 # confidence
				,edit_distance(m,s)
				,MagSam._i_edit_distance(m,s)
				# ,m[0] == s[0]
				# ,m[-1] == s[-1]
				# ,(m[0] == s[0] or m[-1]  == s[-1])
				) 
				for a_m, a_s in zip(df.t_maghadi, df.t_samskrit)
				for s in a_s 
				for m in a_m
			# if edit_distance(s,m) <= 1
			]

			raw_kosha = pd.DataFrame (ans, 
				columns=[
				'm','s', 'im', 'is', 
				'confidence', 
				'edit_dist', 'i_edit_dist', 
				# 'same_start', 'same_end', 'either_start_end'
				]
			)

			raw_kosha.confidence = raw_kosha.apply( lambda x: MagSam._confidence(x) , axis=1)
			pre_kosha = raw_kosha.drop_duplicates()
			pre_kosha = pre_kosha[pre_kosha.confidence > 0].sort_values(
				by=['m', 'confidence' ,'edit_dist']
				, ascending=[True, False, True]
				).reset_index(drop=True)
			self.pre_kosha_df = pre_kosha

			kosha = pre_kosha.groupby('m').apply( lambda k: k.sort_values(by='confidence').tail(1))
			self.kosha_df = kosha
			# self.kosha_df.set_index('m', inplace=True) 
			if verbose or step==1:
				display( df[ ["maghadi", "samskrit"]].reset_index().T.to_dict(), kosha.head(40))
		return self.kosha_df, self.pre_kosha_df

	def save_kosha(self):
		self.pre_kosha_df.to_csv(self.pre_kosha_tsv, sep='\t', index=False)
		self.kosha_df.to_csv(self.kosha_tsv, sep='\t', index=False)
	
	def translate_maghadi(self, text):
		'''
		Translate a maghadi text to samskrit
		'''
		self.load_kosha()
		tokenized = MagSam._tokenize(text)
		kosha = self.kosha_df
		translated = [] 
		for m in tokenized:
			if m in kosha.index:
				translated.append( kosha.loc[m]['s'] )
			else:
				translated.append( f'*{m}*' )
		return ' '.join(translated)

	def _validate_translation(self) :
		'''
		Typical usage
		'''
		ms = self
		ms.load_kosha()
		ans=[]

		tdf = ms.training_df
		for mag,sam,train_on in zip(tdf.maghadi.values, tdf.samskrit.values, tdf.trained_on.values):
			tr = ms.translate_maghadi(mag)
			ans.append( (mag,sam,tr, (0 if '*' not in tr else 1), train_on) ) 
		result = pd.DataFrame(ans, columns=['maghadi','samskrit-human','samskrit-machine','err_flag', 'trained_on'])
		# display(result.head(10))
		# display(result.tail(10))
		train_result = result[result.trained_on==True]
		test_result = result[result.trained_on==False]
		total_samples = tdf.shape[0]
		train_samples = train_result.shape[0]
		test_samples = test_result.shape[0]
		train_errs = train_result.err_flag.sum()
		test_errs = test_result.err_flag.sum()
		train_accuracy = (train_samples - train_errs) / train_samples
		test_accuracy = (test_samples - test_errs) / (test_samples + (0 if train_samples > 0 else 1))
		# print(f'Training samples: {train_samples}')
		# print(f'Training accuracy: {train_accuracy:.2f}')
		# print(f'Testing samples: {test_samples}')
		# print(f'Testing accuracy: {test_accuracy:.2f}')
		stats_df = pd.DataFrame( 
			[(train_samples, train_accuracy, test_samples, test_accuracy)]
			, columns=[ 'train_samples', 'train_accuracy', 'test_samples', 'test_accuracy'])
		result_dfs = ( train_result, test_result, result ) 
		return stats_df, result_dfs

	def ValidateTranslation() :
		stats =[]
		for train_fraction in np.linspace(0.5,1.0,5):
			print(f'Training fraction: {train_fraction}')
			ms = MagSam()
			ms.generate_kosha(train_fraction=train_fraction)
			stats_df, result_dfs = ms._validate_translation()
			display (result_dfs[1])
			display (stats_df)
#%%
if __name__ == '__main__':
	MagSam.TypicalUse()
	MagSam.ValidateTranslation()


#%% edit distance compute - auto pilot generated
def ap_edit_distance(s1, s2):
	m = len(s1)
	n = len(s2)
	dp = np.zeros((m+1, n+1))
	for i in range(m+1):
		for j in range(n+1):
			if i == 0:
				dp[i][j] = j
			elif j == 0:
				dp[i][j] = i
			elif s1[i-1] == s2[j-1]:
				dp[i][j] = dp[i-1][j-1]
			else:
				dp[i][j] = 1 + min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1])
	return dp[m][n]
#%%
# shuffle a dataframe
def shuffle_df(df):

