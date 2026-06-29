import pandas as pd
import glob
import os

os.makedirs("output", exist_ok=True)

# Load, combine, and filter Listing files
all_listing_files = sorted(glob.glob("Data File/CRMLSListing*.csv"))
print(all_listing_files)
print("Listing files found:", len(all_listing_files))

listing_chunks = []
total_row_count_before_concat = 0

for file in all_listing_files:
    df = pd.read_csv(file)

    if "_filled" in file:
        df = df.iloc[:, :-2]

    total_row_count_before_concat += len(df)
    listing_chunks.append(df)

combined_listings = pd.concat(listing_chunks, ignore_index=True)

print(f"Listing row count before concatenation: {total_row_count_before_concat}")
print(f"Listing row count after concatenation: {len(combined_listings)}")

filtered_listings = combined_listings[
    combined_listings["PropertyType"] == "Residential"
]

print(f"Listing row count after Residential filter: {len(filtered_listings)}")

filtered_listings.to_csv("output/listing.csv", index=False)


# Load, combine, and filter Sold files
all_sold_files = sorted(glob.glob("Data File/CRMLSSold*.csv"))
print(all_sold_files)
print("Sold files found:", len(all_sold_files))

sold_chunks = []
total_row_count_before_concat = 0

for file in all_sold_files:
    df = pd.read_csv(file)

    if "_filled" in file:
        df = df.iloc[:, :-2]

    total_row_count_before_concat += len(df)
    sold_chunks.append(df)

combined_sold = pd.concat(sold_chunks, ignore_index=True)

print(f"Sold row count before concatenation: {total_row_count_before_concat}")
print(f"Sold row count after concatenation: {len(combined_sold)}")

filtered_sold = combined_sold[
    combined_sold["PropertyType"] == "Residential"
]

print(f"Sold row count after Residential filter: {len(filtered_sold)}")

filtered_sold.to_csv("output/sold.csv", index=False)

