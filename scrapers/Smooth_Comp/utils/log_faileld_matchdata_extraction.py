import pandas as pd
import os
from datetime import datetime

date_stamp = datetime.now().strftime("%Y-%m-%d")
parent_dir = os.path.abspath(os.getcwd())
data_dir = os.path.join(parent_dir, "data")
raw_data_dir = os.path.join(data_dir, "raw")
test_dir = os.path.join(data_dir, "test")

failed_match_data_extracts_csv = os.path.join(data_dir, f"failed_match_data_extractions.csv")

def log_failed_matchdata_extract(event_id, match_id):
    """Logs a failed bracket match extraction only if it's not already logged."""
    
    # Load existing failed brackets
    if os.path.exists(failed_match_data_extracts_csv):
        faield_match_extract_df = pd.read_csv(failed_match_data_extracts_csv)
    else:
        faield_match_extract_df = pd.DataFrame(columns=["event_id", "bracket_bundle_id","match_id", "attempts", "last_failed"])

    # Check if this bracket ID already failed before
    if ((faield_match_extract_df["event_id"] == event_id) & (faield_match_extract_df["match_id"]== match_id)).any():
        print(f"⚠️ Match ID:{match_id} for event {event_id} is already in the failure log.")
        
        # Increment attempt count
        faield_match_extract_df.loc[
            (faield_match_extract_df["event_id"] == event_id) & (faield_match_extract_df["match_id"]== match_id),
            ["attempts", "last_failed"]
        ] = [faield_match_extract_df["attempts"] + 1, date_stamp]
    else:
        # Add new failed record
        new_failed_bracket = pd.DataFrame([{
            "event_id": event_id,
            "match_id": match_id,
            "attempts": 1,
            "last_failed": date_stamp
        }])
        
        faield_match_extract_df = pd.concat([faield_match_extract_df, new_failed_bracket], ignore_index=True)

    # Save updated failure log
    faield_match_extract_df.to_csv(failed_match_data_extracts_csv, index=False)
    print(f"🚨 Logged failed MatchID:{match_id} for event {event_id}. Attempt #{faield_match_extract_df.loc[faield_match_extract_df['match_id'] == match_id, 'attempts'].values[0]}")
