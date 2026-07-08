import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import seaborn as sns
plt.style.use('ggplot')
pd.set_option('display.max_columns', 100)
#since theres a lot of very large and very small numbers, this prevents scientific notation from being used.
pd.options.display.float_format = '{:.2f}'.format
df = pd.read_csv('used_cars.csv')

print(df.shape) 
print(df.dtypes)
#milage and price columns have $ and , in them, so need to clean them up to be able to use them for analysis.
df['price_clean'] = df['price'].str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)
df['milage_clean'] = df['milage'].str.replace('mi.','', regex=False).str.replace(',','', regex=False).astype(float)

#check to see if cleaning worked on columns 'milage' and 'price'
print(df[['price', 'price_clean', 'milage', 'milage_clean']].head())

#excluding interior/exterior color, not relevant, should have 10 columns not 12 now
df = df[[
    'brand',
    'model',
    'model_year',
    'milage_clean',
    'price_clean',
    'fuel_type',
    'engine',
    'transmission',
    # 'ext_col',
    # 'int_col',
    'accident',
    'clean_title',
#copy() ensures that we work with independent object, not window at original set
]].copy()

#fixes any duplicates in dataset
df = df.loc[~df.duplicated(subset=['brand', 'model', 'model_year', 'milage_clean'])] \
    .reset_index(drop=True).copy()

#original dataset had typo in 'milage' column, which is bad 
df = df.rename(columns={'milage_clean': 'mileage_clean'})

df['horsepower'] = df['engine'].str.extract(r'(\d+\.?\d*)HP').astype(float)
df['engine_liters'] = df['engine'].str.extract(r'(\d+\.?\d*)L').astype(float)

#need to better review how this line works in the future, but this is to determine whether the missing engine values are electric cars or not. If they are electric, then the engine value is not applicable, so we can leav it as NaN.
print(f"number of missing engines: {df[df['fuel_type'].isna()]['engine'].str.contains('Electric', na=False).sum()}")

df.loc[df['fuel_type'].isna() & df['engine'].str.contains('Electric', na=False), 'fuel_type'] = 'Electric'
print(f"remaining missing fuel_type: {df['fuel_type'].isna().sum()}")

print(df['clean_title'].value_counts(dropna=False))
#clean_title only shows yes or NaN so no "no" option exists, fixed
df['clean_title_flag'] = df['clean_title'].fillna('No')
print(df[['price_clean', 'mileage_clean', 'model_year', 'horsepower', 'engine_liters']].describe())

#describe() showed a max price of 2.5 million, which is an error, as the Maserati it is associated with is generally listed at 150k new.
print(f"Excluding likely data error: {df.loc[df['price_clean'].idxmax(), 'model']} listed at ${df['price_clean'].max():,.0f}")

#see what else gets caught by the filter
print(df[df['price_clean'] >= 500000][['brand', 'model', 'model_year', 'mileage_clean', 'price_clean']])

#dropping only the specific row identified as a data entry error (Maserati Quattroporte listed at $2,954,083), keeping other legitimate high-value exotic listings
df = df[df['price_clean'] != 2954083.00]
print(df[['price_clean', 'mileage_clean', 'model_year', 'horsepower', 'engine_liters']].describe())


#Step 3: Feature Understanding
#creating an age column to make brand comparisons easier to reason about than raw model year
df['age'] = 2026 - df['model_year']

#looking at price vs age for the top 8 brands by listing count, to see which brands hold value better as cars get older
top_brands = df['brand'].value_counts().head(8).index
df_top = df[df['brand'].isin(top_brands)]

#restricting range to cut out extreme outliers stretching the axes
df_top_clean = df_top[(df_top['age'] <= 20) & (df_top['price_clean'] <= 200000)]

#average price by brand and age, to build a depreciation curve per brand
depreciation = df_top_clean.groupby(['brand', 'age'])['price_clean'].mean().reset_index()

plt.figure(figsize=(10, 6))
sns.lineplot(x='age', y='price_clean', hue='brand', data=depreciation, marker='o')
plt.title('Average Price by Age, by Brand')
plt.xlabel('Age (years)')
plt.ylabel('Average Price ($)')
plt.show()

#grouped comparison, restricted to brands with at least 20 listings so small samples don't skew the picture
brand_summary = df.groupby('brand').agg(
    avg_price=('price_clean', 'mean'),
    avg_age=('age', 'mean'),
    avg_mileage=('mileage_clean', 'mean'),
    count=('price_clean', 'size')
).query('count >= 20').sort_values('avg_price', ascending=False)

print(brand_summary)

print(df_top_clean[(df_top_clean['brand'] == 'Porsche') & (df_top_clean['age'] == 17)][['model', 'model_year', 'price_clean', 'mileage_clean']])

print(df_top_clean[(df_top_clean['brand'] == 'Porsche') & (df_top_clean['age'] == 17)][['model', 'model_year', 'price_clean', 'mileage_clean']])

#checking listing counts behind each age point on the Porsche line, to confirm how much sample size is driving the volatility in the curve
age_counts = df_top_clean.groupby(['brand', 'age']).size().reset_index(name='count')
print(age_counts[age_counts['brand'] == 'Porsche'].sort_values('age'))