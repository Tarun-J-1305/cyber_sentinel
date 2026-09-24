# generate_key.py
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_and_save_keys():
    """
    Generates a new RSA key pair and saves them to 'private.pem' and 'public.pem'.
    """
    # Generate a new private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Get the corresponding public key
    public_key = private_key.public_key()

    # Serialize private key to PEM format (PKCS8, no encryption)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serialize public key to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open("private.pem", "wb") as f:
        f.write(private_pem)

    with open("public.pem", "wb") as f:
        f.write(public_pem)

    print("✅ RSA key pair generated successfully!")
    print("🔑 Private key saved to private.pem")
    print("🔑 Public key saved to public.pem")

if __name__ == "__main__":
    generate_and_save_keys()