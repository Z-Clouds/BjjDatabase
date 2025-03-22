import pandas as pd
import ast  # Safely evaluates JSON stored as strings

# 📌 Step 1: Load the CSV file
df = pd.read_csv("match_data.csv")
print(df.head())
# 📌 Step 2: Convert JSON-like strings into dictionaries
def parse_json(text):
    """Safely parse JSON-like strings into dictionaries."""
    try:
        return ast.literal_eval(text)  # Converts JSON strings to Python dicts
    except (ValueError, SyntaxError):
        return {}  # Return empty dict if parsing fails

# Apply function to the nested JSON columns
nested_columns = ["left", "right", "matchInfo"]
for col in nested_columns:
    df[col] = df[col].apply(parse_json)

# 📌 Step 3: Expand JSON fields into separate columns
df_left = df["left"].apply(pd.Series).add_prefix("left_")
df_right = df["right"].apply(pd.Series).add_prefix("right_")
df_matchinfo = df["matchInfo"].apply(pd.Series).add_prefix("match_")

# 📌 Step 4: Combine all expanded columns with match_id
final_df = pd.concat([df["match_id"], df_left, df_right, df_matchinfo], axis=1)

# 📌 Step 5: Save to a new structured CSV file
final_df.to_csv("cleaned_match_data.csv", index=False)

print("✅ Successfully converted nested JSON into structured CSV!")
