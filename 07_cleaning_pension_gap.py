# Import packages
import pandas as pd

# Reading in raw csv files from datasets_raw
df = pd.read_csv('./datasets_raw/Pension gap raw.csv')
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

# 1. Data Cleaning Step 1
# 1.1 Identify and delete columns that are not necessary for further process
print(df.columns)

# DATAFLOW

# Contains the datasource, same for all
print('\n')
print(df['DATAFLOW'].unique())      
    
# LAST_UPDATE:

# When the dataset was last updated, 06/10/22
print('\n')
print(df['LAST UPDATE'].unique())

# Removing the columns above
df = df.loc[:, ~df.columns.isin(['DATAFLOW', 'LAST UPDATE'])]

# 1.2 Explore each column and there unique values, especially if categorical data AND Decide how to proceed with this data

# Frequency of datapoints are annual.
print('\n')
print(df['freq'].unique())

# Age:
# The data concerns pensionst between 65 and 74
print('\n')
print(df['age'].unique())

# Unit:
    
# AVG: Data is the average difference in pension between females and males as a percentage of males earnings.
# Closer to zero is therefore better
print('\n')
print(df['unit'].unique())

# Geo:

# 27 EU countries included in the dataset, abbrivated
print('\n')
print(df['geo'].unique())
print(df['geo'].value_counts())

# Time_period: 
# Annual data for the period 2012 to 2021
print('\n')
print(df['TIME_PERIOD'].unique())
print(df['TIME_PERIOD'].value_counts())

# OBS_value:

# Percentage values as float values
print('\n')
print(df['OBS_VALUE'].info())

# OBS_flag:

# comments from Eurostat on the quality of the data
# p: provisional
# b: break in time series
# Eurostat's data serves as the best available data on the topic, and these
# remarks are therfore ignored
print('\n')
print(df['OBS_FLAG'].unique())
print(df['OBS_FLAG'].value_counts())

# Removing further unnecessary columns:
df = df.loc[:, ~df.columns.isin(['freq', 'age', 'unit'])]

# Renaming columns
df.rename(columns = {'geo':'Country', 'TIME_PERIOD':'Year', 'OBS_VALUE':'Difference in pension'}, inplace = True)

# 1.3 Rename country column with help of the EU27.csv in additional data
# Mapping names to abbrivations
df['Country'] = df['Country'].map(geo_names)

print(df.columns)

# One missing value, which will be filled with zero after calculating the index
print(df['Difference in pension'].describe())

calc_df = df.pivot_table(index=['Country','Year'], values='Difference in pension')
print(calc_df)


# Calculating index: (Actual value - worst value)/(Best value - worst value)
Best_value = 0
Worst_value = 100
calc_df['Index'] = (calc_df['Difference in pension']-Worst_value)/(Best_value-Worst_value)


# 2. Data Cleaning Step 2 (handle null values, not valid rows etc.)

# Pivoting in order to fill in zeros for Nans 
fill_na_df = calc_df.pivot_table(calc_df, index=['Country'], columns=['Year'])
fill_na_df = fill_na_df.fillna(0)
# Reshaping to 'Country, Year, Average female percentage, gap, Index'
final_df = fill_na_df.stack()

# 2.1 Explore data with df.info() /df.describe() and clean df if necessary

# 270 entries
final_df.info()
print(final_df.describe())

# 2.2 Compare if each country has the same number of rows

control = final_df.pivot_table(final_df, index=['Country'], columns=['Year'])
print(control.count())
# 27 counts for every year = every country                  

# 2.3 Compare if each year has the same number of rows
control = final_df.pivot_table(final_df, index=['Year'], columns=['Country'])
print(control.count())
# 10 counts for every country = every year


# Saving output
final_df.to_csv('./datasets_cleaned/Pension gap 2012-2021')
#final_df.to_excel('Pension gap 2012-2021.xlsx')