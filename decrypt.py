# decrypt.py
import base64, hashlib, hmac
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

HASH_EXPECTED = "3323b032a0080f49c42db8afa0501457ba30b6db"

with open("private.pem", "rb") as f:
    priv = serialization.load_pem_private_key(f.read(), password=None)

with open("flag.enc", "r") as f:
    b64 = f.read().strip()

cipher = base64.b64decode(b64)
plaintext = priv.decrypt(
    cipher,
    padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                 algorithm=hashes.SHA256(), label=None)
)

text = plaintext.decode("utf-8", errors="ignore")
sha_plain = hashlib.sha1(text.encode()).hexdigest()
sha_newline = hashlib.sha1((text + "\n").encode()).hexdigest()

print("Decrypted plaintext:", repr(text))
print("SHA1(plain):", sha_plain)
print("SHA1(plain + newline):", sha_newline)

if hmac.compare_digest(sha_plain, HASH_EXPECTED) or hmac.compare_digest(sha_newline, HASH_EXPECTED):
    print("✔ SHA1 matches expected — flag found:", text)
else:
    print("✖ SHA1 does NOT match expected. Provided hash:", HASH_EXPECTED)
