import hashlib
import os
import time
import sys

# Standard Base58 alphabet
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def generate_private_key():
    """Generates a cryptographically secure random 256-bit Bitcoin private key."""
    return os.urandom(32)

def base58_encode_check(v_bytes):
    """Encodes bytes into a Base58Check string (includes 4-byte checksum)."""
    digest1 = hashlib.sha256(v_bytes).digest()
    digest2 = hashlib.sha256(digest1).digest()
    checksum = digest2[:4]
    
    payload = v_bytes + checksum
    num = int.from_bytes(payload, byteorder='big')
    result = []
    while num > 0:
        num, remainder = divmod(num, 58)
        result.append(BASE58_ALPHABET[remainder])
    
    for b in v_bytes:
        if b == 0:
            result.append(BASE58_ALPHABET)
        else:
            break
            
    return "".join(reversed(result))

def public_key_to_legacy_address(private_key_bytes):
    """Derives uncompressed public key and hashes it to Legacy P2PKH address."""
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization
    
    priv_key = ec.derive_private_key(
        int.from_bytes(private_key_bytes, byteorder='big'), 
        ec.SECP256K1()
    )
    pub_key = priv_key.public_key().public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )
    
    sha256_hash = hashlib.sha256(pub_key).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    
    return base58_encode_check(b'\x00' + ripemd160.digest())

def private_key_to_wif(private_key_bytes):
    """Converts private key bytes to Wallet Import Format (WIF)."""
    return base58_encode_check(b'\x80' + private_key_bytes)

def generate_instant_difficulty_1():
    print("🚀 Generating an instant address (Difficulty: 1 attempt)...")
    
    start_time = time.time()
    
    # Generate exactly one keypair
    priv_key_bytes = generate_private_key()
    address = public_key_to_legacy_address(priv_key_bytes)
    wif_key = private_key_to_wif(priv_key_bytes)
    
    elapsed_time = time.time() - start_time
    
    # Extract the natural 9-character prefix from this specific attempt
    discovered_9_chars = address[:9]
    
    log_output = (
        f"--- Instant Address Generated ---\n"
        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Address: {address}\n"
        f"Discovered 9-Char Pattern: {discovered_9_chars}\n"
        f"WIF Private Key: {wif_key}\n"
        f"Hex Private Key: {priv_key_bytes.hex()}\n"
        f"Attempts: 1\n"
        f"Time Taken: {elapsed_time:.4f} seconds\n\n"
    )

    filename = "instant_keys.txt"
    with open(filename, "a") as f:
        f.write(log_output)

    print(f"\n✨ Success! Completed in 1 attempt.")
    print(f"Address: {address}")
    print(f"9-Character Pattern: {discovered_9_chars}")
    print(f"Private Key (WIF): {wif_key}")
    print(f"Saved to: {os.path.abspath(filename)}")

if __name__ == "__main__":
    generate_instant_difficulty_1()
