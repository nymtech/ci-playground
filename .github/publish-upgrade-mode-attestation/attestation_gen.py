import os
import base58
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import json 
from datetime import datetime, timezone

attester_private_key = os.getenv("ATTESTER_PRIVATE_KEY")
if not attester_private_key:
    raise ValueError("ATTESTER_PRIVATE_KEY is not set")


authorised_jwt_issuers_raw = os.getenv("AUTHORISED_JWT_ISSUERS")
if not authorised_jwt_issuers_raw:
    raise ValueError("AUTHORISED_JWT_ISSUERS is not set")


authorised_jwt_issuers = authorised_jwt_issuers_raw.split(',')

# decode passed private key
attester_private_key_decoded = base58.b58decode(attester_private_key)
ed25519_private_key = Ed25519PrivateKey.from_private_bytes(attester_private_key_decoded)

# derive corresponding public key 
ed25519_public_key = ed25519_private_key.public_key()
ed25519_public_key_bs58 = base58.b58encode(
    ed25519_public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
).decode("utf-8")

# rfc3339 formatting
starting_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

# create content we're going to sign
attestation_content = {
    "type": "upgrade_mode",
    "starting_time": starting_time,
    "attester_public_key": ed25519_public_key_bs58,
    "authorised_jwt_issuers": authorised_jwt_issuers
}
attestation_content_json = json.dumps(attestation_content, separators=(',', ':'))

print("signing the following attestation content: ", attestation_content_json)

signature = ed25519_private_key.sign(attestation_content_json.encode())
encoded_signature = base58.b58encode(signature).decode("utf-8")

attestation = attestation_content
attestation["signature"] = encoded_signature

attestation_pretty = json.dumps(attestation, indent=4)

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# Write attestation to output file
with open("output/attestation.json", "w") as f:
    f.write(attestation_pretty)

# --- Write to repo path (to be committed in PR) ---
public_path = "src/public"
os.makedirs(public_path, exist_ok=True)
with open(f"{public_path}/attestation.json", "w") as f:
    f.write(attestation_pretty)
