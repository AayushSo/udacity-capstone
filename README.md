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
Population data was copied from [the Wikipedia page on historical US statewise population data ](https://en.wikipedia.org/wiki/List_of_U.S._states_and_territories_by_historical_population#1960%E2%80%932020,_census_data) while the inflation data was downloaded from [ this site and manually converted to show dollar value with respect to 2010 dollar value](https://www.in2013dollars.com/us/inflation/2001?amount=1)

All the data is combined by month and state and stored as a single dataset. 

### Step 2 - Data Exploratory Analysis

In this step I have tried to explore the data form different angles and used different types of visualizations to glean useful questions and interesting datapoints from the dataset.
Some interesting questions included:
> * How has the energy production increased over time?
> * How has the energy production per person chanegd over time?
> * How has the proportion of energy production for different states / over all of US changed over time?
> * Which states have the highest/lowest domestic cost of electricity? Which have the highest/ lowest cost industrial of electricity?
> * How has the proportion of non-fossil fuel based energy production changed over time? Which states are responsible for the biggest increase in green energy ? How has this impacted the price of energy in that state?

The details for this analysis can be found in my ipynb html file.

### Step 3 - Machine Learning Pipeline

Once the data is analyzed - the main objective I realized was the importance of being able to estimate energy prices to consumers, e.g. if a company desired to enter into the green energy market, how would it impact the energy market, and thus can they estimate in which state to setup their facilities to maximize profits?

The ML model selected was a Linear Regression Model. The variables passed to the dataset included:
> * Energy production in a particular state for fossil fuels
> * Energy production in a particular state for geothermal energy generation
> * Energy production in a particular state for nuclear power 
> * Energy production in a particular state for secondary carbon-based fuels 
> * Energy production in a particular state for hydro power 
> * Energy production in a particular state for solar power 
> * Energy production in a particular state for wind power 
> * Population of a state (estimated usig linear interpolation)

Date is not included as a variable as we want to estimate price based solely on existing population and energy generation and remain time-agnostic. This is also the reason why prices calculated are inflation-adjusted.

The labels we want to estimate are:
> * Inflation-adjusted price of electricity for commercial customers ( cents/kWh of electricity) 
> * Inflation-adjusted price of electricity for industrial customers ( cents/kWh ) 
> * Inflation-adjusted price of electricity for residential customers ( cents/kWh ) 
> * Inflation-adjusted price of electricity for all sectors( cents/kWh ) 

Since we are predicting multiple targets, we used a MultiOutputRegressor in our ML pipeline to estimate all 4 labels at once.

The ML model trained has an RMSE score of ~1.3 cents/kWh and an R2 score of around 0.868

### Step 4 - Creating Web App

In the final step, I have deployed a webapp using Bootstrap as a front-end and Flask for backend processing along with Plotly for generating graphs. 
The webapp includes a few charts regarding energy generation. The site also loads the trained ML model which accepts use
r input of the format :
**fossil, geo, hydro, nuclear, secondary, solar, wind, population, state** where 
> * *fossil,geo, ..., wind* represent total energy generation in a given month (in MWh), 
> * *population* represents estimate of the absolute population in a state, and 
> * *state* represens a 2-character representation of the state in which to estimate cost.
xls

## Dataset list and other important files
### Datasets and links
> 1. [Energy Generation Data from The US Energy Information Administration]( https://www.eia.gov/electricity/data/eia923/)
> 2. [Energy Prices Dataset from Kaggle](https://www.kaggle.com/datasets/alistairking/electricity-prices)
> 3. [US Census data from Wikipedia](https://en.wikipedia.org/wiki/List_of_U.S._states_and_territories_by_historical_population#1960%E2%80%932020,_census_data)
> 4. [Inflation Adjusted Dollar Value](https://www.in2013dollars.com/us/inflation/2001?amount=1)
> 5. [US two-letter state and territory abbreviations from the FAA](https://www.faa.gov/air_traffic/publications/atpubs/cnt_html/appendix_a.html)

### Important files 
> 1. data_cleaning.py - ETL pipeline for gathering, assimilating, cleaning and storing data back in an xls file.
> 2. train_model.py - ML pipeline. USed to setup pipeline, load and train on processed data, calculate stats on performance and store the model for further predictions on webapp.
> 3. run.py - The main backend script for the site. Includes scripts to load the homepage, as well as run the query through MP model to generate estimates of prices.
