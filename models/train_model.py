import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d

from sklearn.pipeline import Pipeline

from sklearn.multioutput import MultiOutputRegressor
from sklearn.linear_model import LinearRegression

from sklearn.model_selection import train_test_split, GridSearchCV

#Generate metrics for model
from sklearn import metrics

import numpy as np
import math

import joblib
import pickle

def get_mean_std(k):
    return k.mean(),k.std()


def load_data(filename):
	with pd.ExcelFile(filename) as xls:
		df_prices=pd.read_excel(xls,'prices')
		df_state=pd.read_excel(xls,'state')
		df_fuel=pd.read_excel(xls,'fuel')
		df_state_m=pd.read_excel(xls,'state monthwise')
	return df_prices, df_state,df_fuel,df_state_m

def load_metadata(filename):
	with pd.ExcelFile(filename) as xls:
		df_inflation=pd.read_excel(xls,'Sheet1')
		df_pop=pd.read_excel(xls,'Sheet2')
	return df_inflation, df_pop

    




if __name__ == '__main__' :
	show_graph = False
	print("Begin training")
	df_prices, df_state,df_fuel,df_state_m = load_data('data/results.xlsx')
	df_inflation,df_pop = load_metadata('data/metadata_energy.xlsx')
	print("Loaded dataset")
	
	infl_normalizer_dict={i['year']:i['adj'] for i in df_inflation.to_dict('records')}
	df_prices['price'] = df_prices.price / df_prices.date.dt.year.apply(lambda x : infl_normalizer_dict[x])
	
	df_prices = df_prices.drop(['customers','revenue' ,'sales'],axis=1).loc[df_prices.price>0].loc[df_prices.sector!='other']
	df_prices=df_prices[df_prices.sector!='transportation']
	df_prices = df_prices.pivot(columns='sector',index=['state','date'],values='price').rename_axis(columns=None).reset_index()

	
	# a dict of functions to interpolate with. Keys are states and funcs are interpolation functions for each state
	interpolate_func={row.tolist()[0]:interp1d([2000,2010,2020],row.tolist()[1:], bounds_error=False, fill_value='extrapolate') for index,row in df_pop.iterrows()}
	def get_iter(row): # row is {'state':'XX', 'date':datetime_obj}
		return interpolate_func[row['state']](row['date'].year + row['date'].month/12)
	
	df_state_m['population']=df_state_m[['date','state']].apply(get_iter,axis=1).astype(int)
	
	df = pd.merge(df_state_m,df_prices,on=['state','date'])
	
	print("Created df")
	
	#mean_std_dict={i:get_mean_std(df[i]) for i in df.drop(['state','date'],axis=1).columns}
	df=df.fillna(0)
	df.to_csv('prices.csv',encoding='utf-8',index=False)
	
	
	#for i in [j for j in df.columns if not ( j=='state' or j=='date')] :
	#	df[i]=df[i].apply(lambda x : (x - mean_std_dict[i][0])/mean_std_dict[i][1] if x!=0 else x )
	df['month']=df.date.dt.month
	df['year']=df.date.dt.year
	df=df.drop('date',axis=1)
	df_onehot=pd.get_dummies(data=df)
	
	X=df_onehot.drop(['all sectors','commercial','industrial','residential','year','month'],axis=1)
	y=df_onehot[['all sectors','commercial','industrial','residential']]
	X_train, X_test, y_train, y_test = train_test_split(X, y)
	
	print("Generated training and test data")
	
	
	pipeline = Pipeline([
		('clf',MultiOutputRegressor(LinearRegression()))
		], verbose=True)
	
	
	fit_pipeline = pipeline.fit(X_train,y_train)
	print('Score =',fit_pipeline.score(X_test, y_test))
	
	y_pred=pipeline.predict(X_test)
	
	print("RMS error per category (in cents per kWh) :")
	#print ( (((y_pred-y_test)*np.array([ mean_std_dict[i][1] for i in ['all sectors','commercial','industrial','residential']]) )**2).mean(axis=0)**0.5 )
	#stdval = np.array([ mean_std_dict[i][1] for i in ['all sectors','commercial','industrial','residential']])
	#meanval = np.array([ mean_std_dict[i][0] for i in ['all sectors','commercial','industrial','residential']])
	print(((y_pred-y_test)**2).mean(axis=0)**0.5)
	#print("Overall MSE :",metrics.mean_squared_error(y_test*stdval,y_pred*stdval)**0.5)
	print("R2 Score = ",metrics.r2_score(y_test,y_pred))
	
	#y_pred_all=pipeline.predict(X)
	#y_pred_all = pd.DataFrame(data=y_pred_all,columns=y.columns)
	#y_scat = pd.merge(y.melt(),y_pred_all.melt(),left_index=True,right_index=True).drop('variable_x',axis=1)
	
	
	joblib.dump(pipeline, 'clf.pkl')
	df_state_m.to_csv('final.csv',encoding='utf-8',index=False)
	
	