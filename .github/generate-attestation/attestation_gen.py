import os

attester_private_key = os.getenv("ATTESTER_PRIVATE_KEY")
if not attester_private_key:
    raise ValueError("ATTESTER_PRIVATE_KEY is not set")


# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# Write hash to output file
with open("output/test.txt", "w") as f:
    f.write(attester_private_key)

# --- Write to repo path (to be committed in PR) ---
public_path = "src/public"
os.makedirs(public_path, exist_ok=True)
with open(f"{public_path}/test.txt", "w") as f:
    f.write(hash_value)

print("written to output/test.txt")