# encrypt.py
import argparse, base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

parser = argparse.ArgumentParser(description="Encrypt a message with public.pem")
parser.add_argument("message", help="Message to encrypt")
parser.add_argument("--out", default="flag.enc", help="Output file (base64)")
args = parser.parse_args()

with open("public.pem", "rb") as f:
    pub = serialization.load_pem_public_key(f.read())

cipher = pub.encrypt(
    args.message.encode("utf-8"),
    padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                 algorithm=hashes.SHA256(), label=None)
)

with open(args.out, "w") as f:
    f.write(base64.b64encode(cipher).decode())
print(f"Encrypted -> {args.out}")
