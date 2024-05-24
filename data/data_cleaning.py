import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

def extract_generation_data(start_year=2001,end_year=2023,display_stats=False):
	"""
	Extract data on energy generation for each year from individual excel files
	"""
	excel_files=[i for i in range(start_year,end_year+1)]
	fuel_types = {"WOO":"fossil","SUN":"solar","ORW":"secondary","WND":"wind","OOG":"fossil","WOC":"fossil","PC":"fossil","OTH":"secondary","MLG":"secondary","GEO":"geo","DFO":"fossil","WWW":"secondary","RFO":"fossil","HYC":"hydro","NG":"fossil","NUC":"nuclear","COL":"fossil",'HPS':'NaN'}
	
	df_bystate_collated=pd.DataFrame()
	df_bystate_detailed_collated=pd.DataFrame()
	df_byfuel_collated=pd.DataFrame()
	
	for df_year in excel_files:
		#Extract parameters that depend of year
		filename=str(df_year)
		filename_with_extension = 'dataset/'+ filename + ( '.xls' if df_year<=2010 else '.xlsx')
		skiprows=7 if df_year<=2010 else 5
		
		#Read excel file
		df = pd.read_excel(filename_with_extension,'Page 1 Generation and Fuel Data',skiprows=skiprows)
		print('Loaded DF',filename)
		
		#Standardize column names
		df.columns=df.columns.str.lower()
		df.columns=df.columns.str.replace('\n',' ')
		if 'plant state' in df.columns:
			df=df.rename(columns={'plant state':'state'})
		if not '_' in [i for i in df.columns if 'netgen' in i][0]: #style is netgen jan and not netgen_jan
			df=df.rename(columns={i:'_'.join(i.split()) for i in df.columns if 'netgen' in i})
		
		#Remove unneeded columns and standardize columns
		df = df.filter(regex=("^net.*gen|aer fuel type code|state"))
		df['fuel_category']=df['aer fuel type code'].apply(lambda x : fuel_types[x])
		df[[i for i in df.columns if 'netgen_' in i]]=df[[i for i in df.columns if 'netgen_' in i]].replace('.',0).astype(float)
		
		#Sort by fuel type
		df_byfuel=df.loc[df['aer fuel type code']!='HPS'].drop(['state','aer fuel type code'],axis=1).groupby('fuel_category',as_index=False).sum().sort_values('net generation (megawatthours)',ascending=False)
		df_byfuel = df_byfuel.filter(regex=('^netgen|fuel_cat')).melt(id_vars='fuel_category',var_name='month',value_name='units_MWHr')
		df_byfuel['month']= df_byfuel['month'].apply(lambda x : pd.to_datetime(str(int(df_year))+'-'+x.split('_')[-1]))
		df_byfuel = df_byfuel.rename(columns={'month':'date'})
		
		#Display stats
		if display_stats:
			ax = sns.lineplot(data=df_byfuel,x='date',y='units_MWHr',hue='fuel_category')
			sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
			ax.set_yscale("log")
			plt.title(filename+' Fuel Generation by Type')
			plt.show()
		
		#Sort by state
		df_bystate=df.loc[df['aer fuel type code']!='HPS'].drop('aer fuel type code',axis=1).groupby(['state','fuel_category'],as_index=False).sum().sort_values('net generation (megawatthours)',ascending=False).filter(regex=("generation|state|fuel")).rename(columns={'net generation (megawatthours)':'MWh'})
		
		#Display stats
		if display_stats:
			fig,ax=plt.subplots(figsize=(10,8))
			(df_bystate.groupby(['state','fuel_category'])['MWh'].sum()/df_bystate.groupby(['state'])['MWh'].sum()).unstack().rename_axis(columns=None).reset_index().plot(ax=ax,kind='bar',stacked=True,x='state',width=0.9)
			sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
			plt.title(filename+' Fuel Generation by state, %')
			plt.show()
		
		df_bystate=df.loc[df['aer fuel type code']!='HPS'].drop('aer fuel type code',axis=1).groupby(['state','fuel_category'],as_index=False).sum().sort_values('net generation (megawatthours)',ascending=False).filter(regex=("generation|state|fuel")).rename(columns={'net generation (megawatthours)':'MWh'})
		df_bystate = df_bystate.pivot(columns='fuel_category',index='state',values='MWh').rename_axis(columns=None).reset_index()
		
		if display_stats:
			fig,ax=plt.subplots(figsize=(10,8))
			df_bystate.plot(ax=ax,kind='bar', stacked=True, width=0.9,x='state')
			plt.title(filename+' Fuel Generation by state, absolute')
			plt.show()
		
		df_bystate['year']=df_year
		
		df_bystate_detailed = df.loc[df['aer fuel type code']!='HPS'].drop('aer fuel type code',axis=1).groupby(['state','fuel_category'],as_index=False).sum().sort_values('net generation (megawatthours)',ascending=False).filter(regex=("netgen|state|fuel")).melt(id_vars=['state','fuel_category'],var_name='month',value_name='units_MWHr')
		try :
			df_bystate_detailed['date']=pd.to_datetime(filename + '-' + df_bystate_detailed.month.apply(lambda x : x.split('_')[1]) , format="%Y-%b")
		except:
			df_bystate_detailed['date']=pd.to_datetime(filename + '-' + df_bystate_detailed.month.apply(lambda x : x.split('_')[1]) , format="%Y-%B")
		df_bystate_detailed=df_bystate_detailed.drop('month',axis=1).sort_values(by=['state','date','fuel_category'])
		df_bystate_detailed=df_bystate_detailed.pivot(columns='fuel_category',index=['state','date'],values='units_MWHr').rename_axis(columns=None).reset_index()
		
		#Append to master df's
		df_bystate_collated=pd.concat([df_bystate_collated, df_bystate], ignore_index=True, sort=False)
		df_byfuel_collated=pd.concat([df_byfuel_collated, df_byfuel], ignore_index=True, sort=False)
		df_bystate_detailed_collated=pd.concat([df_bystate_detailed_collated, df_bystate_detailed], ignore_index=True, sort=False)
    
	return df_byfuel_collated, df_bystate_collated,df_bystate_detailed_collated

def write_to_excel(filename,df_dict):
	"""
	write set of df's to excel file
	Input :
		- filename
		- df_dict which is of the format : {'sheetname1':df1,'sheetname2':df2,...}
	"""
	with pd.ExcelWriter(filename) as writer:
		for df_sheet in df_dict : 
			df=df_dict[df_sheet]
			df.to_excel(writer,sheet_name=df_sheet,index=False)

def extract_price_data(filename,end_year=2024):
	"""
	Extract price points by state and sector
	Convert state name from absolute name to postal-abbreviation
	"""
	xls = pd.ExcelFile(filename)
	df_prices=pd.read_excel(xls,'prices')
	df_codes=pd.read_excel(xls,'codes')
	print("Loaded price DF")
	
	#Convert state codes into a dict
	state_codes_dict = df_codes.set_index('State').T.to_dict('records')[0]
	
	#Remove region data. We are noly interested in state data
	df_prices  = df_prices.loc[df_prices.stateDescription.isin(df_codes.State.unique())]
	
	#Convert statename into abbr
	df_prices=df_prices.replace({'stateDescription':state_codes_dict})
	df_prices=df_prices.rename(columns={'stateDescription':'state'})
	
	#Convert year and month into date
	df_prices['date']=pd.to_datetime(df_prices.year.astype('str')+'-'+df_prices.month.astype('str'))
	df_prices=df_prices.loc[df_prices.year<end_year].drop(['year','month'],axis=1).rename(columns={'sectorName':'sector'})
	return df_prices

if __name__ == '__main__':
	df_prices=extract_price_data('electricity_prices.xlsx')
	df_fuel,df_state, df_state_monthwise = extract_generation_data()
	print("Loading DF complete")
	write_to_excel('results.xlsx',{'state':df_state, 'state monthwise':df_state_monthwise, 'fuel':df_fuel, 'prices':df_prices})
	print("Write to xls file complete")
	