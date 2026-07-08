# Used Car Price EDA

Exploratory data analysis of used car listings, looking at how price relates to a vehicle's age, brand, and mileage — and along the way, catching a couple of data quality issues that would have quietly skewed the results if left unchecked.

## Data

- **Source**: [Used Car Price Prediction Dataset](https://www.kaggle.com/datasets/taeefnajib/used-car-price-prediction-dataset) by Taeef Najib (Kaggle), scraped from cars.com listings.
- **Size**: 4,009 rows, 12 original columns (`used_cars.csv`).
- **Columns used**: brand, model, model_year, mileage, price, fuel_type, engine, transmission, accident, clean_title. (`ext_col` and `int_col` were dropped — not relevant to price analysis.)

## Tools

Python, pandas, NumPy, matplotlib, seaborn.

## Cleaning

The raw data had several problems that needed resolving before any analysis could be trusted:

- **Price and mileage were text, not numbers.** Both came in as strings (`"$32,000"`, `"45,000 mi."`). Stripped the symbols/units and cast to float.
- **Duplicate listings.** Removed rows that matched on brand, model, year, and mileage.
- **Engine specs were buried in a free-text field.** Used regex to pull `horsepower` and `engine_liters` out of the messy `engine` string into their own numeric columns.
- **Missing fuel type wasn't random.** ~163 rows with no `fuel_type` turned out to be electric vehicles that just weren't labeled as such — their `engine` field mentioned "Electric" instead of a displacement. Recoded those rows to `fuel_type = 'Electric'`, which resolved all but 5 genuinely unexplained gaps.
- **`clean_title` had no "No" value.** The column only ever contained `"Yes"` or blank — there was no explicit "No" in the source data. Since a blank almost certainly means the title isn't clean (sellers have no reason to omit a clean title), missing values were recoded to `"No"`.
- **One clear data entry error.** A Maserati Quattroporte was listed at $2,954,083 — roughly 20x what that car is realistically worth. Before dropping it, checked every other listing above $500k to make sure this wasn't part of a wider pattern of bad data. Those turned out to be legitimate exotic cars (Bugatti Veyron, Rolls-Royce Cullinan/Phantom, Lamborghini Aventador SVJ, Porsche Carrera GT), so only the one Maserati row was removed.

## Analysis

- **Depreciation curves.** Built average price by age for the top 8 brands by listing count, to see how value holds up over time.
- **Porsche and Mercedes-Benz command a premium** over brands like Toyota and Chevrolet at comparable ages.
- **Investigated a spike in the Porsche curve at 17 years old.** Rather than take it at face value, checked the underlying sample size and found only 4 listings at that age, one of them a high-value 911 Turbo Cabriolet pulling the average up. Documented as a small-sample artifact, not a real trend.
- **Brand-level summary stats** (average price, age, mileage) restricted to brands with 20+ listings, to avoid low-sample-size brands distorting the comparison.

## Running it

```bash
pip install pandas numpy matplotlib seaborn
python eda.py
```

Requires `used_cars.csv` in the same directory.
