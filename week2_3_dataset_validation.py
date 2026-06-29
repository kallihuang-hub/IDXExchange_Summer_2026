import pandas as pd
import glob
import os

# =========================
# 1. Load and combine files
# =========================

input_folder = "Data File"
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)

all_listing_files = sorted(glob.glob(f"{input_folder}/CRMLSListing*.csv"))

print("Files found:", len(all_listing_files))
print(all_listing_files)

listing_chunks = []

for file in all_listing_files:
    df = pd.read_csv(file, low_memory=False)

    # Drop extra columns in filled files if needed
    if "_filled" in file:
        df = df.iloc[:, :-2]

    listing_chunks.append(df)

sold = pd.concat(listing_chunks, ignore_index=True)

print("\n===== Dataset Structure Before Filtering =====")
print("Rows, Columns:", sold.shape)
print("\nColumn Names:")
print(sold.columns.tolist())

print("\nData Types:")
print(sold.dtypes)

print("\nFirst 5 Rows:")
print(sold.head())


# =========================
# 2. Property Type Review
# =========================

print("\n===== Unique Property Types =====")
property_types = sold["PropertyType"].value_counts(dropna=False)
print(property_types)

property_types.to_csv(f"{output_folder}/property_type_counts.csv")


# =========================
# 3. Residential Filtering
# =========================

print("\n===== Filtering Logic =====")
print("Keeping only records where PropertyType == 'Residential'")

residential_sold = sold[sold["PropertyType"] == "Residential"].copy()

print("Rows before filtering:", len(sold))
print("Rows after filtering:", len(residential_sold))
print("Residential share:", len(residential_sold) / len(sold) * 100, "%")


# =========================
# 4. Missing Value Analysis
# =========================

missing_report = pd.DataFrame({
    "missing_count": residential_sold.isnull().sum(),
    "missing_percent": residential_sold.isnull().mean() * 100,
    "dtype": residential_sold.dtypes
})

missing_report["above_90_percent_missing"] = missing_report["missing_percent"] > 90

missing_report = missing_report.sort_values(
    by="missing_percent",
    ascending=False
)

print("\n===== Missing Value Report =====")
print(missing_report)

missing_report.to_csv(f"{output_folder}/missing_value_report.csv")


# =========================
# 5. Numeric Distribution Summary
# =========================

numeric_fields = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt"
]

available_numeric_fields = [
    col for col in numeric_fields if col in residential_sold.columns
]

for col in available_numeric_fields:
    residential_sold[col] = pd.to_numeric(residential_sold[col], errors="coerce")

numeric_summary = residential_sold[available_numeric_fields].describe(
    percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
).T

print("\n===== Numeric Distribution Summary =====")
print(numeric_summary)

numeric_summary.to_csv(f"{output_folder}/numeric_distribution_summary.csv")


# Required deliverable summary for selected fields
required_fields = ["ClosePrice", "LivingArea", "DaysOnMarket"]

required_available = [
    col for col in required_fields if col in residential_sold.columns
]

required_summary = residential_sold[required_available].describe(
    percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
).T

required_summary.to_csv(f"{output_folder}/required_numeric_summary.csv")


# =========================
# 6. Suggested EDA Questions
# =========================

print("\n===== Suggested EDA Questions =====")

if "ClosePrice" in residential_sold.columns:
    print("Average ClosePrice:", residential_sold["ClosePrice"].mean())
    print("Median ClosePrice:", residential_sold["ClosePrice"].median())

if "DaysOnMarket" in residential_sold.columns:
    print("Average DaysOnMarket:", residential_sold["DaysOnMarket"].mean())
    print("Median DaysOnMarket:", residential_sold["DaysOnMarket"].median())

if {"ClosePrice", "ListPrice"}.issubset(residential_sold.columns):
    sold_above_list = residential_sold[
        residential_sold["ClosePrice"] > residential_sold["ListPrice"]
    ]

    sold_below_list = residential_sold[
        residential_sold["ClosePrice"] < residential_sold["ListPrice"]
    ]

    valid_price_rows = residential_sold[
        residential_sold["ClosePrice"].notna() &
        residential_sold["ListPrice"].notna()
    ]

    print(
        "Percent sold above list price:",
        len(sold_above_list) / len(valid_price_rows) * 100
    )

    print(
        "Percent sold below list price:",
        len(sold_below_list) / len(valid_price_rows) * 100
    )

if {"CloseDate", "ListingContractDate"}.issubset(residential_sold.columns):
    residential_sold["CloseDate"] = pd.to_datetime(
        residential_sold["CloseDate"],
        errors="coerce"
    )

    residential_sold["ListingContractDate"] = pd.to_datetime(
        residential_sold["ListingContractDate"],
        errors="coerce"
    )

    date_issues = residential_sold[
        residential_sold["CloseDate"] < residential_sold["ListingContractDate"]
    ]

    print("Close date before listing date issue count:", len(date_issues))
    date_issues.to_csv(f"{output_folder}/date_consistency_issues.csv", index=False)

if {"CountyOrParish", "ClosePrice"}.issubset(residential_sold.columns):
    county_median_prices = (
        residential_sold
        .groupby("CountyOrParish")["ClosePrice"]
        .median()
        .sort_values(ascending=False)
    )

    print("\nCounties with highest median ClosePrice:")
    print(county_median_prices.head(10))

    county_median_prices.to_csv(f"{output_folder}/county_median_prices.csv")


# =========================
# 7. Save Filtered Dataset
# =========================

residential_sold.to_csv(
    f"{output_folder}/residential_filtered_sold.csv",
    index=False
)

print("\nFiltered residential dataset saved to:")
print(f"{output_folder}/residential_filtered_sold.csv")

