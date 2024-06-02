import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from sklearn.pipeline import Pipeline

from sklearn.multioutput import MultiOutputRegressor
from sklearn.linear_model import LinearRegression

from sklearn.model_selection import train_test_split, GridSearchCV

#Generate metrics for model
from sklearn import metrics

import numpy as np
import math

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

if __name__ == '__main__' :
	show_graph=False
	
	df_prices, df_state,df_fuel,df_state_m = load_data('../data/results.xlsx')
	df_prices = df_prices.drop(['customers','revenue' ,'sales'],axis=1).loc[df_prices.price>0].loc[df_prices.sector!='other']
	df_prices=df_prices[df_prices.sector!='transportation']
	df_prices.head()
	df_prices = df_prices.pivot(columns='sector',index=['state','date'],values='price').rename_axis(columns=None).reset_index()
	df = pd.merge(df_state_m,df_prices,on=['state','date'])
	mean_std_dict={i:get_mean_std(df[i]) for i in df.drop(['state','date'],axis=1).columns}
	df=df.fillna(0)
	for i in [j for j in df.columns if not ( j=='state' or j=='date')] :
		df[i]=df[i].apply(lambda x : (x - mean_std_dict[i][0])/mean_std_dict[i][1] if x!=0 else x )
	df['month']=df.date.dt.month
	df['year']=df.date.dt.year
	df=df.drop('date',axis=1)
	df_onehot=pd.get_dummies(data=df)
	X=df_onehot.drop(['all sectors','commercial','industrial','residential'],axis=1)
	y=df_onehot[['all sectors','commercial','industrial','residential']]
	X_train, X_test, y_train, y_test = train_test_split(X, y)
	pipeline = Pipeline([
		('clf',MultiOutputRegressor(LinearRegression()))
		], verbose=True)
	print('Score =',pipeline.fit(X_train,y_train).score(X_test, y_test))
	y_pred=pipeline.predict(X_test)
	print("RMS error per category (in cents per kWh) :')
	print ( (((y_pred-y_test)*np.array([ mean_std_dict[i][1] for i in ['all sectors','commercial','industrial','residential']]) )**2).mean(axis=0)**0.5 )
	stdval = np.array([ mean_std_dict[i][1] for i in ['all sectors','commercial','industrial','residential']])
	meanval = np.array([ mean_std_dict[i][0] for i in ['all sectors','commercial','industrial','residential']])
	print("Overall MSE :",metrics.mean_squared_error(y_test*stdval,y_pred*stdval)**0.5)
	print("R2 Score = ",metrics.r2_score(y_test,y_pred))
	if show_graph:
		df_err=(y_test - y_pred).abs()/(y_test + meanval)
		df_err=df_err.melt()
		df_err['value']=df_err.value.apply(lambda x : 2+math.log10(x))
		ax = sns.histplot(data=df_err,hue='variable',x='value',bins=20)
		ax.set_xticks([-3,-2,-1,0,1])
		ax.set_xticklabels(['0.001%', '0.01%', '0.1%','1%','10%']);
		plt.show()
	with open('clf.pkl','wb') as fileh:
		pickle.dump(pipeline,fileh)