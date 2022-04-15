import pandas as pd
from pandas.core.indexes.base import Index
from tabulate import tabulate
import os
import datetime
from xlsxwriter import Workbook
import plotly.express as px
import matplotlib.pyplot as plt
from dateutil import parser


#location of all essential csv files
home = os.getcwd()
print(home)
os.chdir('daily')
today = datetime.date.today().strftime("%Y-%m-%d")
yesterday = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
today_file = f'kalimati_{today}.csv'
yesterday_file = f'kalimati_{yesterday}.csv'
today_df = pd.read_csv(today_file)
try:
    yesterday_df = pd.read_csv(yesterday_file)
except FileNotFoundError:
    csv_location = os.path.join(home, 'daily')
    yesterday_file = sorted(os.listdir(csv_location))[-3]
    yesterday_df = pd.read_csv(yesterday_file)

# removing nepali name column from the dataframe: ADD THIS COLUMN LATER along with others below when needed
nepali_name = list(today_df['Nepali Name'])
maximum = list(today_df['Maximum Price (Rs.)'])  
minimum = list(today_df['Minimum Price (Rs.)']) 
# del today_df['Nepali Name']
del today_df['Minimum Price (Rs.)']
del today_df['Maximum Price (Rs.)']

yesterday_nepali_name = list(yesterday_df['Nepali Name'])
yesterday_maximum = list(yesterday_df['Maximum Price (Rs.)'])  
yesterday_minimum = list(yesterday_df['Minimum Price (Rs.)']) 
del yesterday_df['Nepali Name']
del yesterday_df['Minimum Price (Rs.)']
del yesterday_df['Maximum Price (Rs.)']


# Total Number of vegetables today
vegetable_count = today_df.shape[0]

# Average Price of vegetables/fruits per kg/Pc/Doz [Avergae Kalimati Price]---VISUALIZATION REMAINING
today_df['Average Kalimati Price (Rs.)'] = today_df['Average Price (Rs.)'].mean() # plot a single graph of this comparing with the one below
yesterday_df['Average Kalimati Price (Rs.)'] = yesterday_df['Average Price (Rs.)'].mean() # plot a single graph of this comparing with the one above


                                        # PART 1: Intraday
# Relatively Cheap
below_avg_price = today_df['Average Price (Rs.)'] < today_df['Average Kalimati Price (Rs.)']
cheap_df = today_df[below_avg_price].sort_values('Average Price (Rs.)')
cheap_df['Average Kalimati Price'] = round(today_df['Average Price (Rs.)'].mean(), 2)
cheap_df['Less than Average Kalimati Price by (Rs.)'] = round(cheap_df['Average Kalimati Price (Rs.)'] - cheap_df['Average Price (Rs.)'], 2)
del cheap_df['Average Kalimati Price (Rs.)']
# print(cheap_df)


# Relatviely Expensive
above_avg_price = today_df['Average Price (Rs.)'] > today_df['Average Kalimati Price (Rs.)']
expensive_df = today_df[above_avg_price].sort_values('Average Price (Rs.)', ascending=False)
expensive_df['Average Kalimati Price'] = round(today_df['Average Price (Rs.)'].mean(), 2)
expensive_df['More than Average Kalimati Price by (Rs.)'] = round(expensive_df['Average Price (Rs.)'] - expensive_df['Average Kalimati Price (Rs.)'], 2)
del expensive_df['Average Kalimati Price (Rs.)']
# print(expensive_df)



                                    # PART 2: Interday
with_yesterday_df = pd.merge(today_df, yesterday_df, on='English Name')
del with_yesterday_df['Unit_x']
del with_yesterday_df['Unit_y']
with_yesterday_df['Change in Average Price (Rs.)'] = with_yesterday_df['Average Price (Rs.)_x'] - with_yesterday_df['Average Price (Rs.)_y']
with_yesterday_df['Change in Average Price (%)'] =  round(with_yesterday_df['Change in Average Price (Rs.)']/with_yesterday_df['Average Price (Rs.)_y'] * 100, 2)
del with_yesterday_df['Average Kalimati Price (Rs.)_x']
del with_yesterday_df['Average Kalimati Price (Rs.)_y']


# All Positive Change in Price
positive_change = with_yesterday_df['Average Price (Rs.)_x'] > with_yesterday_df['Average Price (Rs.)_y']
top_positive_change = with_yesterday_df[positive_change].sort_values('Change in Average Price (%)', ascending=False)
top_positive_change = top_positive_change.rename(columns={'Average Price (Rs.)_x': "Average Price (Rs.)"})
top_positive_change = top_positive_change.rename(columns={'Change in Average Price (%)': "Average Price increased by (%)"})
top_positive_change = top_positive_change.rename(columns={'Change in Average Price (Rs.)': "Average Price increased by (Rs.)"})
del top_positive_change['Average Price (Rs.)_y']
# print(top_positive_change)


# All Negative Change in Price
negative_change = with_yesterday_df['Average Price (Rs.)_x'] < with_yesterday_df['Average Price (Rs.)_y']
top_negative_change = with_yesterday_df[negative_change].sort_values('Change in Average Price (%)')
top_negative_change = top_negative_change.rename(columns={'Average Price (Rs.)_x': "Average Price (Rs.)"})
top_negative_change = top_negative_change.rename(columns={'Change in Average Price (%)': "Average Price decreased by (%)"})
top_negative_change["Average Price decreased by (%)"] = top_negative_change["Average Price decreased by (%)"].abs()
top_negative_change = top_negative_change.rename(columns={'Change in Average Price (Rs.)': "Average Price decreased by (Rs.)"})
top_negative_change["Average Price decreased by (Rs.)"] = top_negative_change["Average Price decreased by (Rs.)"].abs()
del top_negative_change['Average Price (Rs.)_y']
# print(top_negative_change)


# Change in Average kalimati Price - - CONSOLE ONLY
change_in_avg_kalimati_price = today_df['Average Price (Rs.)'].mean() - yesterday_df['Average Price (Rs.)'].mean()
percent_change = change_in_avg_kalimati_price.item()/yesterday_df['Average Price (Rs.)'].mean()*100
print("Today's Average Kalimati Price is Rs.", round(today_df['Average Price (Rs.)'].mean(), 2))
print("Last day's Average Kalimati Price was Rs.",round(yesterday_df['Average Price (Rs.)'].mean(), 2))
if change_in_avg_kalimati_price.item() < 0:  # although not needed here, .item() converts numpy type to python type
    print('Average kalimati Price decreased by Rs.', str(round(change_in_avg_kalimati_price, 2))[1:])
    print("Average kalimati Price decreased by ", str(round(percent_change,2))[1:], '%')
elif change_in_avg_kalimati_price.item() > 0:  # although not needed here, .item() converts numpy type to python type
    print('Average kalimati Price increased by Rs.', str(round(change_in_avg_kalimati_price, 2)))
    print("Average kalimati Price increased by", str(round(percent_change,2)), '%')


# Writing to an excel file:
os.chdir(home)
os.chdir('daily analysis')

writer = pd.ExcelWriter(f'{today}.xlsx', engine='xlsxwriter')
workbook  = Workbook(f'{today}.xlsx')

worksheet1 = 'Items costing<Average Price'
worksheet2 = 'Items costing>Average Price'
worksheet3 = 'Items whose price increased'
worksheet4 = 'Items whose price decreased'
cheap_df.to_excel(writer, sheet_name=worksheet1, index=None)
expensive_df.to_excel(writer, sheet_name=worksheet2, index=None)
top_positive_change.to_excel(writer, sheet_name=worksheet3, index=None)
top_negative_change.to_excel(writer, sheet_name=worksheet4, index=None)
writer.save()



                                            # Part 3: Date wise columns 
# The code below is for merging all the daily kalimati files at once. However, for now, this is commented out since it will only be required
# to run a shorter version of code to update (merging) each day's data at a time everyday. 

# all_files = os.chdir('/Users/birajaryal/virtual_workspace/vegetables/daily')
# list_of_dfs = []
# all_df = {}
# for file in os.listdir(all_files):
#     if file.endswith('.csv'):
#         date = file.split('_')[-1][:-4]
#         df = date
#         df_value = pd.read_csv(file)
#         del df_value['Maximum Price (Rs.)']
#         del df_value['Minimum Price (Rs.)']
#         del df_value['Nepali Name']
#         df_value = df_value.rename(columns={'English Name': "Name"})
#         df_value = df_value.rename(columns={'Average Price (Rs.)': date}) 
#         all_df[df] = df_value

# list_of_dfs = sorted(all_df.keys())
# count = len(list_of_dfs)
# count_duplicate = count
# for i in list_of_dfs:
#     i = parser.parse(i)
#     j = i + datetime.timedelta(1)
#     i = i.strftime("%Y-%m-%d")
#     j = j.strftime("%Y-%m-%d")
#     del all_df[j]['Unit']
#     if count == count_duplicate:
#         complete_df = pd.merge(all_df[i], all_df[j], on='Name', how='outer')
#     else:
#         complete_df = pd.merge(complete_df, all_df[j], on="Name", how='outer')
#     count -= 1
#     if count == 1:
#         break
# del complete_df['Unit']
# nepali_name_df = pd.read_csv('/Users/birajaryal/virtual_workspace/vegetables/translate.csv')
# nepali_name_df = nepali_name_df.rename(columns={'English Name': 'Name'})
# complete_df = pd.merge(nepali_name_df, complete_df, on='Name')
# complete_df = complete_df.sort_values('Name', ascending=True)


# Use the above code to merge a lot of daily kalimati files at once. 
# However once we've done this, which we have, it's better to just merge the df from "up_to_date.xlsx" with today's df


# Thus, from now onwards, it's okay to use the following code:
del today_df['Nepali Name']
del today_df['Average Kalimati Price (Rs.)']
del today_df['Unit']
today_df = today_df.rename(columns={'Average Price (Rs.)': today})
today_df = today_df.rename(columns={'English Name': 'Name'})
print(os.getcwd())
os.chdir('/Users/birajaryal/virtual_workspace/vegetables/daily')
complete_df = pd.read_excel('up_to_date.xlsx')
del complete_df['Nepali Name']
complete_df = pd.merge(complete_df, today_df, on='Name', how='outer')
nepali_name_df = pd.read_csv('/Users/birajaryal/virtual_workspace/vegetables/translate.csv')
nepali_name_df = nepali_name_df.rename(columns={'English Name': 'Name'})
complete_df = pd.merge(nepali_name_df, complete_df, on='Name')
complete_df = complete_df.sort_values('Name', ascending=True)

complete_df.to_excel("up_to_date.xlsx", sheet_name='daily', index=None)


                                                # Part 4: Visualizations
# today_df['Maximum Price (Rs.)'] = maximum
# today_df['Minimum Price (Rs.)'] = minimum
# #All items alphabetically
# complete_chart = px.scatter(data_frame=today_df.sort_values('English Name'), x="English Name", title='All items alphabetically', y=['Average Price (Rs.)', 'Minimum Price (Rs.)','Maximum Price (Rs.)'], color="Unit")
# complete_chart.update_layout(xaxis=dict(rangeslider=dict(visible=True)))
# complete_chart.show()

# #All items price-wise
# complete_chart = px.line(data_frame=today_df.sort_values('Average Price (Rs.)'), x="English Name", title='All items: cheap to expensive', y='Average Price (Rs.)')
# complete_chart.show()

# #Visualization of Part 1: Intraday
# expensive_graph = px.scatter(data_frame=expensive_df.sort_values('Average Price (Rs.)', ascending=True), x='English Name', title='Items costing more than Average Kalimati Price', y=['Average Price (Rs.)','Average Kalimati Price'])
# expensive_graph.show()
# cheap_graph = px.scatter(data_frame=cheap_df.sort_values('Average Price (Rs.)', ascending=True), x='English Name', title='Items costing less than Average Kalimati Price', y=['Average Price (Rs.)','Average Kalimati Price'])
# cheap_graph.show()

# # Visualization of Part 2: Interday
# positive_change_percent = px.line(data_frame=top_positive_change.sort_values('Average Price increased by (%)', ascending=True), x='English Name', title='Increase in Average Price (%)', y='Average Price increased by (%)')
# positive_change_percent.show()
# positive_change_rupees = px.line(data_frame=top_positive_change.sort_values('Average Price increased by (Rs.)', ascending=True), x='English Name', title='Increase in Average Price (Rs.)', y='Average Price increased by (Rs.)')
# positive_change_rupees.show()
# negative_change_percent = px.line(data_frame=top_negative_change.sort_values('Average Price decreased by (%)', ascending=False), x='English Name', title='Decrease in Average Price (%)', y='Average Price decreased by (%)')
# negative_change_percent.show()
# negative_change_rupees = px.line(data_frame=top_negative_change.sort_values('Average Price decreased by (Rs.)', ascending=False), x='English Name', title='Decrease in Average Price (Rs.)', y='Average Price decreased by (Rs.)')
# negative_change_rupees.show()
