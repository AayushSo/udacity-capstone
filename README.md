# Trends and Estimations of US Energy generation and prices

## Overview
The quest for sustainable energy sources has never been more critical. However, the transitions towards a greener energy utilization landscape brings forth its own set of challenges, and understanding energy generation and consumption patterns becomes paramount. 
In this project, I shall look into the production and utilization of energy across the United States to uncover insights and identify trends. I also implement a basic ML pipeline to estimate costs of energy for different sectors based on energy and demoraphic statistics for the different states.
The project deals with the following parts:
>	1. **Data Gathering and data cleaning** : Gathering, preliminary processing and condesnsing of various datasets
>	2. **Data Exploratory Analysis** : A deeper look into our data to understand informatino provided and uncover intersting questions to ask
>	3. **Machine Learning Pipeline** : Creating a Regression pipeline to process and estimate electricity costs.
>	4. **Creating Web App** :  Creating a basic web app to highlight our learnings 

## Instructions to run the webapp:
1. Run the following commands in the project's root directory to set up your database and model.

    - To run ETL pipeline that cleans data and stores in database 
        `python data/data_cleaning.py`
    - To run ML pipeline that trains classifier and saves 
        `python models/train_model.py`

2. Run the following command in the app's directory to run your web app.
    `cd app`
	`python run.py`

3. Go to  http://127.0.0.1:3001

## Project Analysis

### Step 1 - Data gathering and data cleaning

The aim of the project was to observe trends in energy generation for United States over the last 2 decades. Energy generation data used to explore this was downloaded from [The US Energy Information Administration]( https://www.eia.gov/electricity/data/eia923/), while the energy prices dataset was downloaded from [ this Kaggle link by user Alistair King](https://www.kaggle.com/datasets/alistairking/electricity-prices)

This data was not available in the format I needed - the monthly data for each year was given separately. Also - the xls files had a lot of other information as well - useful for a later, in-depth analysis perhaps, but discarded for now!

So - the first step was to download each individual file, separate the information of most importance for our project, and store this data in another excel file for later usage.

Second - after a preliminary analysis, I realized it would be important to have two other pieces of information which would be relevant for analysis of energy trends and prices - how the population of each state increased over time, and how the dollar value has been impacted by inflation. Population information is unfortunately only available for once every decade when the census is performed. However trends in population for this short duration are approximately linear for all states, and so I have used a linear interpolation to estimate "monthly" population figues which are used further for analysis.
Population data was copied from [the Wikipedia page on historical US statewise population data ] https://en.wikipedia.org/wiki/List_of_U.S._states_and_territories_by_historical_population#1960%E2%80%932020,_census_data) while the inflation data was downloaded from [ this site and manually converted to show dollar value with respect to 2010 dollar value] (https://www.in2013dollars.com/us/inflation/2001?amount=1)
