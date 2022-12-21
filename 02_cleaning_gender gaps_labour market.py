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
clean_df = raw_df.loc[(raw_df['indic_em'] == 'EMP_LFS') & (raw_df['unit'] == 'PC_POP')].copy()
clean_df.drop(columns=['indic_em','unit'], axis=1, inplace=True)
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
clean_df.rename(columns={"sex": "Sex", "age" : "Age", "geo": "Country", "TIME_PERIOD": "Year", "OBS_VALUE": "% of Total Employment", "OBS_FLAG" : "Flag"}, inplace=True)
print((clean_df.head()))

# reorder columns
clean_df = clean_df[['Country', 'Year', 'Sex', 'Age', 'Flag', '% of Total Employment']]
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
clean_df2 = clean_df[clean_df['Country'].notna()]
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
    # -

# 4. Any questions regarding cleaning decisions to discuss?
# Get Only sex of Total, Male and Female ?
# Get only one age group or multiple age groups ?

# 5. Save cleaned dataframe in folder datasets_cleaned 
clean_df2.to_csv('./datasets_cleaned/Employment by sex and age.csv')
