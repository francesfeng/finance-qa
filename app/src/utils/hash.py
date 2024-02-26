import hashlib
import re

def text_to_hash(text):
    # Rmove special characters and convert to lowercase
    cleaned_text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    cleaned_text = cleaned_text.lower()

    # Use SHA-256 hashing algorithm
    hash_object = hashlib.sha256(text.encode())
    # Get the hexadecimal digest
    hex_dig = hash_object.hexdigest()
    # Convert hexadecimal to a decimal number

    return hex_dig
