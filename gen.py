import os

# Generate a random 16-byte secret key
secret_key = os.urandom(16)
print(secret_key)
