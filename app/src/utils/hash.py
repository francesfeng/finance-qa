import hashlib

def text_to_hash(text):
    # Use SHA-256 hashing algorithm
    hash_object = hashlib.sha256(text.encode())
    # Get the hexadecimal digest
    hex_dig = hash_object.hexdigest()
    # Convert hexadecimal to a decimal number

    return hex_dig
