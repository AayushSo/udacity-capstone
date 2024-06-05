import json
import plotly
import pandas as pd
import re

#import warnings
#warnings.filterwarnings("ignore") 

from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar,Scatter
#from plotly.graph_objs.scatter.marker import Line
#from plotly.graph_objs.scatter import Line
import joblib

import plotly.colors

app = Flask(__name__)



def prediction( energy_util,population,state, df_state_m, pipeline, n_closest = 5):
	"""
	Predict cost of energy for given data.
	Input : 
		- energy_util : tuple of energy generated in megawatt-hours for (fossil, geo, hydro, nuclear, secondary, solar, wind)
		- state
	Output :
		- pred : prediction tuple for ( all sectors, commercial, industrial, residential)
	"""
	
	X_col = ['fossil', 'geo', 'hydro', 'nuclear', 'secondary', 'solar', 'wind',
			'population', 'state_AK', 'state_AL', 'state_AR', 'state_AZ',
			'state_CA', 'state_CO', 'state_CT', 'state_DC', 'state_DE', 'state_FL',
			'state_GA', 'state_HI', 'state_IA', 'state_ID', 'state_IL', 'state_IN',
			'state_KS', 'state_KY', 'state_LA', 'state_MA', 'state_MD', 'state_ME',
			'state_MI', 'state_MN', 'state_MO', 'state_MS', 'state_MT', 'state_NC',
			'state_ND', 'state_NE', 'state_NH', 'state_NJ', 'state_NM', 'state_NV',
			'state_NY', 'state_OH', 'state_OK', 'state_OR', 'state_PA', 'state_RI',
			'state_SC', 'state_SD', 'state_TN', 'state_TX', 'state_UT', 'state_VA',
			'state_VT', 'state_WA', 'state_WI', 'state_WV', 'state_WY']
	vec_input=[i for i in energy_util]+[population,state]
	vec= vec_input # [i for i in energy_util]+[population,state]
	vec = vec[:8] + [vec[-1] in i for i in X_col[8:]]
	pred= (pipeline.predict(
			pd.DataFrame(
					data= vec,
					index = X_col).T)  ).round(2)
	
	df1 = df_state_m.loc[df_state_m.state==state]
	#df1 = df1.iloc[(df1['population']-population).abs().argsort()[:10]].fillna(0)
	
	df2 = df1.drop(['state','date'],axis=1).fillna(0)
	if 'month' in df2.columns: df2.drop('month',axis=1,inplace=True)
	a = pd.DataFrame(vec_input[:-1],index=df2.columns).T # convert input into a DF with single row so we can calcullate correlation
	a = ((a-df2.mean())/df2.std()).fillna(0) #standardize a
	df2 = ((df2 - df2.mean())/ (df2.std())).fillna(0) #standardixe df2
	corr_idx = df2.corrwith( a.iloc[0] , axis=1 ).sort_values(ascending=False).index.tolist() # these are the closes matches
	corr_idx = corr_idx[:n_closest] # select top n_closest matches
	
	df1 = df1.loc[corr_idx]
	
	#print("Closest dates match = \n",df1.date)
	#print()
	actual =  df_prices.loc[df_prices.state==state].loc[df_prices.date.isin(df1.date)] 
	
	#print("Actual generation for these dats is/are :\n",actual)
	#print("Actual prices for data are:\n",actual)
	#print()
	#print("Predicted prices are:\n",pd.DataFrame( pred,columns=['all sectors','commercial','industrial','residential']) )
	return actual, pd.DataFrame( pred,columns=['all sectors','commercial','industrial','residential'])



# load data
df_state_m = pd.read_csv('../final.csv',encoding='utf-8')
df_state_m.fillna(0,inplace=True)

df_prices = pd.read_csv('../prices.csv',encoding='utf-8')
gen_type_list = ['fossil', 'geo', 'hydro', 'nuclear', 'secondary', 'solar', 'wind']

# load model
model = joblib.load("../clf.pkl")


# index webpage displays cool visuals and receives user input text for model
@app.route('/')
@app.route('/index')
def index():
	
	# extract data needed for visuals
	#color_list = {'fossil':'gray', 'geo':'green', 'hydro':'navy', 'nuclear':'lime', 'secondary':'olive', 'solar':'#1f77b4', 'wind':'purple'}
	cmap = plotly.colors.DEFAULT_PLOTLY_COLORS
	color_list={gen_type_list[i] : cmap[i % len(cmap) ] for i in range(len(gen_type_list))}
	df_state_m['date']= pd.to_datetime(df_state_m.date)
	#print(df_state_m.info())
	#print(df_state_m.head())
	#print(df_state_m[gen_type_list[0]].tolist()[:20])
	#print(len(df_state_m[gen_type_list[0]].tolist()))
	#print("Other len = ",len(df_state_m.date.tolist()))
	# create visuals
	graphs = [
		{
			'data': [
				Bar(
					x=df_state_m.date.tolist(),
					y=df_state_m[gen_type].tolist(),
					marker = {'color':color_list[gen_type]}
				)
			],

			'layout': {
				'title': 'Generation of energy by type:'+gen_type,
				'yaxis': {
					'title': "Count (in MWh generated)"
				},
				'xaxis': {
					'title': "Date"
				}
			}
		}
	for gen_type in gen_type_list
	] 
	
	df_state_m['month'] = df_state_m.date.dt.month
	h = df_state_m[gen_type_list + ['date','population','month']].loc[df_state_m.date.dt.year>2010].drop(['date','population'],axis=1).groupby('month').sum()
	#h[gen_type_list] = (h[gen_type_list] - h[gen_type_list].mean())	 / h[gen_type_list].std()
	h[gen_type_list] = h[gen_type_list] / h[gen_type_list].max()
	
	graphs = graphs + [
		{
			'data': [
				Scatter(
					x=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
					y=h[gen_type],
					mode='lines'
				)
			],

			'layout': {
				'title': 'Generation trend for {} for each month (normalized) '.format(gen_type),
				'yaxis': {
					'title': "Normalized generation (MWh/MWh)  "
				},
				'xaxis': {
					'title': "Month"
				}
			}
		}
	for gen_type in gen_type_list
	]
	
	
	# encode plotly graphs in JSON
	ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
	graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
	
	# render web page with plotly graphs
	return render_template('master.html', ids=ids, graphJSON=graphJSON)


# web page that handles user query and displays model results
@app.route('/go')
def go():
	# save user input in query
	query_orig = request.args.get('query', '') 
	if not ',' in query_orig:
		query = query_orig.split()
	else:
		query = re.sub(r'\s','',query_orig).upper()
		query = query.split(',')
	query = [float(i) if en<len(query)-1 else i for en,i in enumerate(query)]
	actual, pred = prediction(query[:7],query[7],query[8],df_state_m,model)
	state_sel = query[8]
	#print(state_sel)
	#print(df_state_m.loc[df_state_m.state==state_sel].drop(['date','state'],axis=1))
	
	#print("ACTUAL",actual)
	try :
		typical_values= df_state_m.loc[df_state_m.state==state_sel].drop(['date','state'],axis=1).describe().loc[['mean','std']].astype(int).round(-3)
		
		#print(pred.columns.values, pred.iloc[0].tolist())
		#print(dict(zip(pred.columns.values,pred.iloc[0].tolist())))
		# This will render the go.html Please see that file. 
		return render_template(
			'go.html',
			query=query_orig,
			tables= [pred.to_html(classes='table table-hover',header='true',index=False)], #dict(zip(pred.columns.values,pred.iloc[0].tolist())),
			#titles = pred.columns.values,
			closest_match = [actual.drop('state',axis=1).to_html(classes='table table-hover',header='true',index=False)],
			state_sel=state_sel,
			typical_values = [typical_values.to_html(classes='table table-hover',header='true')],
			is_pass=1
			#closest_titles= actual.columns.values
		)
	except :
		
		return render_template(
			'go.html',
			query=query_orig,
			tables= [] , #[pred.to_html(classes='table table-hover',header='true',index=False)], #dict(zip(pred.columns.values,pred.iloc[0].tolist())),
			#titles = pred.columns.values,
			closest_match = [],#[actual.drop('state',axis=1).to_html(classes='table table-hover',header='true',index=False)],
			state_sel="",
			typical_values = [],#[typical_values.to_html(classes='table table-hover',header='true')],
			is_pass=0
			#closest_titles= actual.columns.values
		)
	


# ETL pipeline preparation HTML
@app.route('/etl-pipeline')
def etl_pipeline():
	return render_template('ETL Pipeline Preparation.html')

# ETL pipeline preparation HTML
@app.route('/ml-pipeline')
def ml_pipeline():
	return render_template('ML Pipeline Preparation.html')

# ETL pipeline preparation HTML
@app.route('/exploratory-analysis')
def exploratory_analysis():
	return render_template('Exploratory Analysis.html')


def main():
	app.run(host='0.0.0.0', port=3001, debug=True)


if __name__ == '__main__':
	main()