# This is a file to align the cleaning process
# Please do not code in heres
# Copy the empty framework, open a new .py file and paste the framework in

# Import packages
import pandas as pd
import numpy as np

# Reading in raw csv files from datasets_raw
raw_df = pd.read_csv('./datasets_raw/Members of National Parliaments by sex_EIGE.csv', sep=';', decimal=',') #decimal defined to read in the values as float and not as string)
print(raw_df.head())
print(raw_df.columns)
# Melting data in the correct format (every dimension and value in a column)
    #no need to melt data

# 1. Data Cleaning Step 1
# 1.1 Identify and delete columns that are not necessary for further process
raw_df.drop(columns=['_sex', '_UNIT', 'EGROUP','geo', 'POSITION'], axis=1, inplace=True)
print(raw_df.head())

# 1.2 Explore each column and there unique values, especially if categorical data AND Decide how to proceed with this data
# Time
# Time periods are in quarters, since we agreed to base our time series on a yearly basis, we take the values of the first quarters as yearly value
print(raw_df['time'].unique())

# Geo
print((raw_df['_geo'].unique()))

# Unit
# We are going with the percent of total, since every parliament has a different size
print((raw_df['UNIT'].unique()))

# EGROUP
# We are working the data of both parliaments upper/lower (data is more consistent)
print((raw_df['_EGROUP'].unique()))

# Position
# We are working with the values of the parliament members and not with the values of the presidents
print((raw_df['_POSITION'].unique()))

# Clean dataset STEP 1 - Filtering relevant rows
# _EGROUP = 'PARL_ALL'
# UNIT = 'Percent of total'
# _POSITION =  'MEMB_PARL'
clean_df = raw_df.loc[  (raw_df['_EGROUP'] == 'PARL_ALL') & 
                        (raw_df['UNIT'] == 'Percent of total') &
                        (raw_df['_POSITION'] == 'MEMB_PARL')
                        ].copy()
clean_df.drop(columns=['_EGROUP','UNIT','_POSITION'], axis=1, inplace=True)
print(clean_df.head())

# Filtering only first Quarter of every year
clean_df2 = clean_df[clean_df['time'].str.contains('Q1')].copy()
print(clean_df2.head())

# 1.3 Rename country column with help of the EU27.csv in additional data
# Create dictionary of EU27 countries to apply map function
countries_df = pd.read_csv("./additional_data/EU27_COUNTRY_LIST.csv")
countries = dict(zip(countries_df['Initial'].str.strip(), countries_df['Country']))
print(countries)

# Apply map function to rename the countries
new_country_column = clean_df2['_geo'].map(countries)
clean_df2.loc[:,'_geo'] = new_country_column
print((clean_df2.head()))

# renaming columns
clean_df2.rename(columns={"time": "Year", "_geo" : "Country", "value": "% of Parliaments", "sex": "Sex"}, inplace=True)
print((clean_df2.head()))

# reorder columns
clean_df2 = clean_df2[['Country', 'Year', 'Sex', '% of Parliaments']]
print((clean_df2.head()))

# 2. Data Cleaning Step 2 (handle null values, not valid rows etc.)
# 2.1 Explore data with df.info() /df.describe() and clean df if necessary
# Null Values in Country column are those countries that do not belong to the EU27
# Therefore removing all rows with Country "NaN"
# Now, there are no null values in the df anymore
print(clean_df2.info())
clean_df3 = clean_df2[clean_df2['Country'].notna()].copy()
print(clean_df3.info())
print(clean_df3.head())

# Strip the "Q1" from the year column
clean_df3['Year'] = clean_df3['Year'].str[:4].astype(int)
print(clean_df3.head())


# 2.2 Compare if each country has the same number of rows
# Each item of the countries list has 54 rows except Croatia: oly 48
countries = list(countries_df['Country'])
for c in countries:
        print('Country: ' + str(c) + ': '+ str((clean_df3['Country'] == c).sum()))

# 2.3 Compare if each year has the same number of rows
# The years 2005 and 2006 have three rows less than the other years
# These are the 6 missing rows from Croatia
# Therefore, each year before 2007 will be removed to have consistent data
for i in range(1990,2025):
    print('Year: ' + str(i) + ': '+ str((clean_df3['Year'] == i).sum()))
clean_df3.drop(clean_df3[(clean_df3['Year'] < 2007)].index, inplace=True)

print(clean_df3.info())
print(clean_df3.describe())
# 3. Further individual cleaning
# Avoided changing DType of "% of Parliaments" from string to float by passing in the 'decimal' in pd.read_csv
clean_df3['% of Parliaments'].astype(float)

# 4. Any questions regarding cleaning decisions to discuss?
# From which year on should we agree to display the data (2009/2010?)
# How do we name Sex (f/m/t - Women, Men, Total etc.)

# 5. Save cleaned dataframe in folder datasets_cleaned -- GIVE A UNIQUE NAME!
clean_df3.to_csv('./datasets_cleaned/Members of national parliaments.csv')






