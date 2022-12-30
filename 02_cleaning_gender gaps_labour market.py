# Import packages
import pandas as pd
import numpy as np

# Reading in raw csv files
raw_df = pd.read_csv('./datasets_raw/Employment and activity by sex and age - annual data_eurostat_2022.csv')
print(raw_df.head())
print(raw_df.columns)

# Melting data in the correct format 
    # No need to melt the data in this dataset

# 1. Data Cleaning Step 1
# 1.1 Identify and delete columns that are not necessary for further process
raw_df.drop(columns=['DATAFLOW', 'LAST UPDATE'], axis=1, inplace=True)
print(raw_df.head())

# 1.2 Explore each column and there unique values, especially if categorical data AND Decide how to proceed with this data
# Only one value in column 'freq' (frequency) --> annually, so that we can drop this column as well
print(raw_df['freq'].unique())
raw_df.drop(columns=['freq'], axis=1, inplace=True)
print(raw_df.head())

# Indices / indic_em
# ACT: Persons in the labour force
# EMP_LFS: Total employment (resident population concept)
# We want to see data of the total employment and not only for active persons in the labour market
print(raw_df['indic_em'].unique())

# Sex
# F: Female
# M: Male
# T: Total
print(sorted(raw_df['sex'].unique()))

# Age
# Data has different age groups
# ?Since we are focusing mainly on the gender, should we get rid of the other age groups?
print(raw_df['age'].unique())

# Unit
# PC_POP: Percentage of total population
# THS_PER: Thousand persons
# We are going to work with the percentage of total population
print(raw_df['unit'].unique())

# Geo
# Working with the countries that are inside the EU27 csv from addtional data
# ?Should we keep the EU27 "Country"
print((raw_df['geo'].unique()))

# TIME_PERIOD
# Time is from 2003-2021, but maybe probably not in all countries
print(sorted(raw_df['TIME_PERIOD'].unique()))

# OBS_VALUE
# mixed values percentage and total values --> getting rid of the total values through the unit
print(sorted(raw_df['OBS_VALUE'].unique()))

# OBS_FLAG
# Deciding in a later stage what to do with the flagged rows
# b: break in time series
# d: definition differs
# nan: no flag
print((raw_df['OBS_FLAG'].unique()))

# Clean dataset STEP 1
# indic_em = EMP_LFS
# unit = PC_POP
# Drop columns after filtering
clean_df = raw_df.loc[(raw_df['indic_em'] == 'EMP_LFS')].copy()
clean_df.drop(columns=['indic_em'], axis=1, inplace=True)
print(clean_df.head())

# 1.3 Rename country column with help of the EU27.csv in additional data
# Create dictionary of EU27 countries to apply map function
countries_df = pd.read_csv("./additional_data/EU27_COUNTRY_LIST.csv")
countries = dict(zip(countries_df['Initial'].str.strip(), countries_df['Country']))
print(countries)

# Apply map function to rename the countries
new_country_column = clean_df['geo'].map(countries)
clean_df.loc[:,'geo'] = new_country_column
print((clean_df.head()))

# renaming columns
clean_df.rename(columns={"sex": "Sex", "age" : "Age", "geo": "Country", "TIME_PERIOD": "Year", "OBS_VALUE": "Total Employment in %", "OBS_FLAG" : "Flag"}, inplace=True)
print((clean_df.head()))

# reorder columns
clean_df = clean_df[['Country', 'Year', 'Sex', 'Age', 'Flag', 'Total Employment in %','unit']]
print((clean_df.head()))

# Flags
# Information to Flags, various reasons:
# https://ec.europa.eu/eurostat/cache/metadata/en/lfsi_esms.htm
# "Overall, comparability over time is considered as high."
# 'b's are most likely a change in statistical method: 
# "Methodological improvements in the underlying sampling design or changes in nomenclatura can lead to breaks in the time series."
# 'd' only in year 2021 for Spain and France
# Therefore, we can get rid of the Flag column
print(clean_df['Flag'].unique())
print(clean_df.loc[clean_df['Flag'] == 'd'])
print(clean_df.loc[clean_df['Flag'] == 'b'])
clean_df.drop(columns=['Flag'], axis=1, inplace=True)


# 2. Data Cleaning Step 2
# 2.1 Explore data with df.info() /df.describe() and clean df if necessary
# Null Values in Country column are those countries that do not belong to the EU27
# Therefore removing all rows with Country "NaN"
# Now, there are no null values in the df anymore
print(clean_df.info())
clean_df2 = clean_df[clean_df['Country'].notna()].copy()
print(clean_df2.info())

# 2.2 Compare if each country has the same number of rows
# Each item of the countries list has 234 rows
countries = list(countries_df['Country'])
for c in countries:
        print('Country: ' + str(c) + ': '+ str((clean_df2['Country'] == c).sum()))

# 2.3 Compare if each year has the same number of rows
# The years 2003 - 2008 only have 18 rows
# The years 2009 - 2021 have all 504 rows
# We want to work only with years, where each country has the same data to compare them completely
# Therefore, we are removing all rows with the years 2003-2008
for i in range(1990,2025):
    print('Year: ' + str(i) + ': '+ str((clean_df2['Year'] == i).sum()))
clean_df2.drop(clean_df2[(clean_df2['Year'] < 2009)].index, inplace=True)
print(clean_df2.info())
print(clean_df2.describe())
print(clean_df2.head())

# 3. Further individual cleaning
# Calculate percentage values
# Create one df with percentage values
# Create another df with total values --> clean_df4
clean_df3 = clean_df2.loc[(clean_df2['unit'] == 'PC_POP')].copy()
clean_df4 = clean_df2.loc[(clean_df2['unit'] == 'THS_PER')].copy()
clean_df3.drop(columns=['unit'], axis=1, inplace=True)
clean_df4.drop(columns=['unit'], axis=1, inplace=True)

clean_df3['Total Employment in %'].astype('float')
clean_df3['Total Employment in %'] = clean_df2['Total Employment in %'].div(100).round(2)
#print(clean_df3.head())

# 4. Any questions regarding cleaning decisions to discuss?
# Get Only sex of Total, Male and Female ?
# Get only one age group or multiple age groups ?

# Setting index to perform mathematical operations
clean_df3.set_index(['Country', 'Year','Age'], inplace=True)
clean_df4.set_index(['Country', 'Year','Age'], inplace=True)

# Split datasets into the Genders
fem_df = clean_df3[clean_df3['Sex'] == 'F'].copy()
mal_df = clean_df3[clean_df3['Sex'] == 'M'].copy()
tot_df = clean_df4[clean_df4['Sex'] == 'T'].copy()

# Column is not needed anymore
fem_df.drop(columns=['Sex'], axis=1, inplace=True)
mal_df.drop(columns=['Sex'], axis=1, inplace=True)
tot_df.drop(columns=['Sex'], axis=1, inplace=True)

# Calculate the employment gap between man and woman
fem_df['Employment Gap in %'] = mal_df['Total Employment in %'].sub(fem_df['Total Employment in %']).round(2)

# Add the total number of employed persons for each row
fem_df['Employed Persons in Thousands'] = fem_df.index.map(tot_df['Total Employment in %'])
fem_df['Employed Persons in Thousands'] = fem_df['Employed Persons in Thousands'].astype(int)

# Drop unnecessary columns
#print(fem_df[fem_df['Employment Gap in %'] == 0.0])
fem_df.drop(columns=['Total Employment in %'], axis=1, inplace=True)

# Reset index after finishing mathematical operations
fem_df.reset_index(inplace=True)
print(fem_df.head())

# Calculating index: (Actual value - worst value)/(Best value - worst value)
# Taking the max. employment gap from age group 15-64 since this is the age group where we are taking the index to calculate the overall index
best_value = 0
worst_value = fem_df[fem_df['Age'] == 'Y15-64']['Employment Gap in %'].max()

fem_df['IndexValueEmployment'] = (fem_df['Employment Gap in %']-worst_value)/(best_value-worst_value)
print(fem_df.head())
# 5. Save cleaned dataframe in folder datasets_cleaned 
fem_df.to_csv('./datasets_cleaned/Employment by sex and age.csv')
