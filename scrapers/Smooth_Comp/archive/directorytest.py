import os

parent_dir = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))
print (parent_dir)
data_dir = os.path.join(parent_dir, "data")
print (data_dir)
raw_data_dir = os.path.join(data_dir,"raw")
print (raw_data_dir)
test_dir = os.path.join(data_dir, "test")
print (test_dir)
import os

# Ensure directories exist
print(f"Checking if directories exist...")
print(f"Exists - {raw_data_dir}: {os.path.exists(raw_data_dir)}")
print(f"Exists - {test_dir}: {os.path.exists(test_dir)}")

# Create directories if missing
os.makedirs(raw_data_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)

print("✅ Directories should now exist.")
