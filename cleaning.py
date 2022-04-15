import pandas as pd
import os
import shutil
from datetime import datetime

# read kalimati.csv
data = pd.read_csv("kalimati.csv")
for (language), group in data.groupby(['Language']):
    del group['Language']
    group.to_csv(f'{language}.csv', index=False)


# Cleaning KalimatiE
kalimatiE_df = pd.read_csv('kalimatiE.csv')
del kalimatiE_df['Nepali Name']
kalimatiE_df = kalimatiE_df.sort_values('English Name', ascending=True)
kalimatiE_df['Minimum Price'] = kalimatiE_df['Minimum Price'].apply(lambda x:x.replace('Rs. ', '')).apply(lambda x:int(x))
kalimatiE_df['Maximum Price'] = kalimatiE_df['Maximum Price'].apply(lambda x:x.replace('Rs. ', '')).apply(lambda x:int(x))
kalimatiE_df['Average Price'] = kalimatiE_df['Average Price'].apply(lambda x:float(x))

kalimatiE_df['Unit'] = kalimatiE_df['Unit'].apply(lambda x:x.replace('KG', 'Kg'))

kalimatiE_df = kalimatiE_df.rename(columns={"Minimum Price":"Minimum Price (Rs.)"})
kalimatiE_df = kalimatiE_df.rename(columns={"Maximum Price":"Maximum Price (Rs.)"})
kalimatiE_df = kalimatiE_df.rename(columns={"Average Price":"Average Price (Rs.)"})
kalimatiE_df.to_csv('pre-mergeE.csv', index=None) # for testing / for checking


# Cleaning KalimatiN
def nepali_to_english(text):
    new = ""
    for x in text:
        if x == "०":
            x = 0
        elif x == "१":
            x = 1
        elif x == "२":
            x = 2
        elif x == "३":
            x = 3
        elif x == "४":
            x = 4
        elif x == "५":
            x = 5
        elif x == "६":
            x = 6
        elif x == "७":
            x = 7
        elif x == "८":
            x = 8
        elif x == "९":
            x = 9
        x = str(x)
        new += x
    return new

kalimatiN_df = pd.read_csv('kalimatiN.csv')
del kalimatiN_df['English Name']
kalimatiN_df['Minimum Price'] = kalimatiN_df['Minimum Price'].apply(lambda x:x.replace('रू. ', ''))
kalimatiN_df['Maximum Price'] = kalimatiN_df['Maximum Price'].apply(lambda x:x.replace('रू. ', ''))

kalimatiN_df['Minimum Price'] = kalimatiN_df['Minimum Price'].apply(lambda x:nepali_to_english(x)).apply(lambda x:int(x))
kalimatiN_df['Maximum Price'] = kalimatiN_df['Maximum Price'].apply(lambda x:nepali_to_english(x)).apply(lambda x:int(x))
kalimatiN_df['Average Price'] = kalimatiN_df['Average Price'].apply(lambda x:nepali_to_english(x)).apply(lambda x:float(x))

kalimatiN_df = kalimatiN_df.rename(columns={"Minimum Price":"Minimum Price (Rs.)"})
kalimatiN_df = kalimatiN_df.rename(columns={"Maximum Price":"Maximum Price (Rs.)"})
kalimatiN_df = kalimatiN_df.rename(columns={"Average Price":"Average Price (Rs.)"})

del kalimatiN_df['Unit']
kalimatiN_df.to_csv("pre-mergeN.csv", index=None) # for testing / for checking


# updating translate.csv
translate_df = pd.read_csv('translate.csv')

up_translateE = pd.merge(kalimatiE_df, translate_df, on='English Name', how='left')
new_rowsE = up_translateE[up_translateE['Nepali Name'].isna()]
del new_rowsE['Nepali Name']

up_translateN = pd.merge(kalimatiN_df, translate_df, on='Nepali Name', how='left')
new_rowsN = up_translateN[up_translateN['English Name'].isna()]
del new_rowsN['English Name']

to_update = pd.merge(new_rowsE, new_rowsN, on=['Minimum Price (Rs.)','Maximum Price (Rs.)','Average Price (Rs.)'])
del to_update['Minimum Price (Rs.)']
del to_update['Maximum Price (Rs.)']
del to_update['Average Price (Rs.)']
del to_update['Unit']
translate_df = translate_df.append(to_update)
translate_df.to_csv('translate.csv', index=None)
# print(to_update)
# print(translate_df[-2:])


# Adding a nepali name column
new_df = pd.merge(translate_df, kalimatiE_df, on='English Name', how='inner')
new_df = new_df.sort_values('English Name', ascending=True)

# Left allignment
# new_df.style.set_properties(**{'text-align': 'Unit'})
# print(new_df)

# new_df.style.set_properties(subset=["English Name", "Nepali Name", "Unit", "Minimum Price (Rs.)", "Maximum Price (Rs.)", "Average Price (Rs.)"], **{'text-align': 'left'})
new_df.to_csv("vegetables.csv", index=None)



# Organizing the files created
current = os.getcwd()
target = os.path.join(current, 'cleaning_purpose')
daily = os.path.join(current, 'daily')

for filename in os.listdir(target):
    if '.csv' in filename:
        os.unlink(filename)

for filename in os.listdir(current):
    if '.csv' in filename:
        if filename not in ['vegetables.csv', 'translate.csv']:
            shutil.move(filename, target)

date = datetime.date(datetime.now())            
shutil.move('vegetables.csv', os.path.join(daily, f'kalimati_{date}.csv')) # just to rename 