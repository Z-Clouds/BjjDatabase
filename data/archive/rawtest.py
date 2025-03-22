import pandas as pd
import os 

df = pd.read_csv("cleaned_match_data.csv")

df = df["match_id"]
print(df)
# Get the parent directory
parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))

# Define the file path in the parent directory
file_path = os.path.join(parent_dir, "SC_master_match_ids_scraped.csv")

# Save the DataFrame as a CSV
df.to_csv(file_path, index=False)

print(f"CSV saved to: {file_path}")