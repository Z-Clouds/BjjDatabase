import pandas as pd
import os
from datetime import datetime

date_stamp = datetime.now().strftime("%Y-%m-%d")
parent_dir = os.path.abspath(os.getcwd())
data_dir = os.path.join(parent_dir, "data")
raw_data_dir = os.path.join(data_dir, "raw")
test_dir = os.path.join(data_dir, "test")

failed_event_bracket_bundle_extracts_csv = os.path.join(data_dir,"failed_event_bracket_bundle_extractions.csv")

def log_failed_event_bracket_extract(event_id):
    """Logs a failed bracket bundle extraction only if it's not already logged."""
    
    # Load existing failed brackets
    if os.path.exists(failed_event_bracket_bundle_extracts_csv):
        failed_brackets_df = pd.read_csv(failed_event_bracket_bundle_extracts_csv)
    else:
        failed_brackets_df = pd.DataFrame(columns=["event_id", "attempts", "last_failed"])

    # Check if this bracket ID already failed before
    if ((failed_brackets_df["event_id"] == event_id)).any():
        print(f"⚠️ Bracket bundle failure for event {event_id} is already in the failure log.")
        
        # Increment attempt count
        failed_brackets_df.loc[
            (failed_brackets_df["event_id"] == event_id),
            ["attempts", "last_failed"]
        ] = [failed_brackets_df["attempts"] + 1, date_stamp]
    else:
        # Add new failed record
        new_failed_bracket = pd.DataFrame([{
            "event_id": event_id,
            "attempts": 1,
            "last_failed": date_stamp
        }])
        
        failed_brackets_df = pd.concat([failed_brackets_df, new_failed_bracket], ignore_index=True)

    # Save updated failure log
    failed_brackets_df.to_csv(failed_event_bracket_bundle_extracts_csv, index=False)
    print(f"🚨 Logged failed bracket bundle extract for event {event_id}. Attempt #{failed_brackets_df.loc[failed_brackets_df['event_id'] == event_id, 'attempts'].values[0]}")
