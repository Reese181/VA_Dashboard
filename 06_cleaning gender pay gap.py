# Import packages
import pandas as pd

# Reading in raw csv files from datasets_raw
df = pd.read_csv('./datasets_raw/Gender pay gap raw.csv')

# 1. Data Cleaning Step 1
# 1.1 Identify and delete columns that are not necessary for further process

print(df.info())

# DATAFLOW

# Contains the datasource, same for all
print('\n')
print(df['DATAFLOW'].unique())    
    
# LAST_UPDATE:

# When the dataset was last updated, 25/02/22
print('\n')
print(df['LAST UPDATE'].unique())

# Removing the columns above

df = df.loc[:, ~df.columns.isin(['DATAFLOW', 'LAST UPDATE'])]

# 1.2 Explore each column and there unique values, especially if categorical data AND Decide how to proceed with this data

# A: Frequency of datapoints are annual.
print('\n')
print(df['freq'].unique())

# Unit:
    
# PC: Data is the difference in earninggs between females and males as a percentage of males earnings.
# Closer to zero is therefore better
print('\n')
print(df['unit'].unique())

# nace_r2
# Codenames for the different economic sectors 
print('\n')
print(df['nace_r2'].unique())

# Geo:

# EU countries included in the dataset, abbrivated
print('\n')
print(df['geo'].unique())
print(df['geo'].value_counts())

# Time_period:
 
# Annual data for the period 2009 to 2020
print('\n')
print(df['TIME_PERIOD'].unique())
print(df['TIME_PERIOD'].value_counts())

# OBS_value:

# Percentage values as float, where the percentage is the 
# difference between women and men as percentage of men's salary
print('\n')
print(df['OBS_VALUE'].unique())

# OBS_flag:

# comments from Eurostat on the quality of the data
# [nan 'p' 'u' 'd' 'b' 'c' 'pu' 'e']
# p provisional
# u low reliability
# d definition differs
# b break in time series
# c confidential
# pu provisional, low reliatbility
# e estimated

# Eurostat's data serves as the best available data on the topic, and these
# remarks are therfore ignored
print('\n')
print(df['OBS_FLAG'].unique())
print(df['OBS_FLAG'].value_counts())

''' 
sectors = df.groupby(['nace_r2'])
countries = df.groupby(['geo'])
years = df.groupby(['TIME_PERIOD'])
obs_values = df.groupby(['OBS_VALUE'])

print(sectors.describe())
print(countries.describe())
print(years.describe())
print(obs_values.describe())


Note: Since we're interested in the average gender pay gap across a country's economy, and as long as a country 
has one or more datapoints, an average will be calculated and Nans will not be replaced with zeros before at the end.'''

geo_names = {
'BE' :'Belgium',
'BG' :'Bulgaria',
'CZ' :'Czech Republic',
'DK' :'Denmark',
'DE' :'Germany',
'EE' :'Estonia',
'IE' :'Ireland',
'EL' :'Greece',
'ES' :'Spain',
'FR' :'France',
'HR' :'Croatia',
'IT' :'Italy',
'CY' :'Cyprus',
'LV' :'Latvia',
'LT' :'Lithuania',
'LU' :'Luxembourg',
'HU' :'Hungary',
'MT' :'Malta',
'NL' :'Netherlands',
'AT' :'Austria',
'PL' :'Poland',
'PT' :'Portugal',
'RO' :'Romania',
'SI' :'Slovenia',
'SK' :'Slovakia',
'FI' :'Finland',
'SE' :'Sweden'}

# A shortened list of codenames for the different sectors:
ind_names = {'Industry (1)' : 'B-S', 
             'Industry (2)' : 'B-S_X_O', 
             'Business economy' : 'B-N', 
             'Mining and quarrying' : 'B', 
             'Manufacturing' : 'C', 
             'Electricity etc supply' : 'D', 
             'Water supply' : 'E', 
             'Construction' : 'F', 
             'Wholesale and retail' : 'G', 
             'Transportation and storage' : 'H', 
             'Accommodation and food service ' : 'I', 
             'Information and communication' : 'J', 
             'Financial activities' : 'K'}

# Removing the following columns
df = df.loc[:, ~df.columns.isin(['freq', 'unit', 'OBS_FLAG'])]

# 1.3 Renaming columns and mapping country names
df.rename(columns = {'nace_r2':'Sector', 'geo':'Country', 'TIME_PERIOD':'Year', 'OBS_VALUE':'Value'}, inplace = True)

# Mapping names to abbrivations
df['Country'] = df['Country'].map(geo_names)
#df['nace_r2'] = df['nace_r2'].map(ind_names) 

# Reshaping to calculate average across all sectors
temp_df = df.pivot_table(df, index=['Year','Country'], columns=['Sector'])

temp_df['sum'] = temp_df.sum(axis=1)
temp_df['count'] = temp_df.count(axis=1)-1
temp_df['average % pay gap'] = temp_df['sum']/temp_df['count']
print(temp_df)

temp_df = temp_df.droplevel(('Sector'), axis=1)
# For selcting timeperioeds:
temp_df = temp_df.loc['2009':'2020':]
temp_df = temp_df.drop(('Value'), axis=1)
temp_df = temp_df.drop(('count'), axis=1)
temp_df = temp_df.drop(('sum'), axis=1)

# Calculating index: (Actual value - worst value)/(Best value - worst value)
Best_value = 0
Worst_value = 100
temp_df['Index'] = (temp_df['average % pay gap']-Worst_value)/(Best_value-Worst_value)

# Pivoting in order to fill in zeros for Nans where there is insufficent data to calculate
# the gap and thereby the index
filling_zeros_df = temp_df.pivot_table(temp_df, index=['Year'], columns=['Country'])
filling_zeros_df = filling_zeros_df.fillna(0)
filling_zeros_df = filling_zeros_df.stack()

# Reshaping to 'Country, Year, average % pay gap, Index'
filling_zeros_df = filling_zeros_df.pivot_table(temp_df, index=['Country'], columns=['Year'])
filling_zeros_df = filling_zeros_df.stack()
final_df = filling_zeros_df[['average % pay gap', 'Index']]


print(final_df)

final_df.to_csv('./datasets_cleaned/Gender Pay Gap 2009-2020')
#final_df.to_excel('Gender Pay Gap 2009-2020.xlsx')


# 2.2 Compare if each country has the same number of rows

control = final_df.pivot_table(final_df, index=['Country'], columns=['Year'])
print(control.count())
# 27 counts for every year                   

# 2.3 Compare if each year has the same number of rows
control = final_df.pivot_table(final_df, index=['Year'], columns=['Country'])
print(control.count())
# 12 counts for every country



