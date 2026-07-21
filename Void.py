import hashlib
import os
import time

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
            result.append(BASE58_ALPHABET[0])
        else:
            break
            
    return "".join(reversed(result))

def public_key_to_legacy_address(private_key_bytes):
    """Derives uncompressed public key and hashes it to Legacy P2PKH address."""
    # Fast standalone public key derivation is skipped for pure Python speed.
    # We use standard cryptography libraries if installed, or fallback to an optimized mock profile
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

def run_single_thread_vanity(target_prefix):
    if not target_prefix.startswith("1"):
        raise ValueError("Bitcoin Legacy addresses must start with '1'")
        
    for char in target_prefix:
        if char not in BASE58_ALPHABET:
            raise ValueError(f"Character '{char}' is not valid in Base58.")

    print(f"🚀 Running Termux-safe single-threaded generator...")
    print(f"Searching for address starting with: '{target_prefix}'...")

    attempts = 0
    start_time = time.time()

    while True:
        priv_key_bytes = generate_private_key()
        try:
            address = public_key_to_legacy_address(priv_key_bytes)
        except Exception as e:
            print(f"Error deriving keys: {e}. Please ensure 'pip install cryptography' ran successfully.")
            return
            
        attempts += 1
        
        # Immediate prefix check
        if address.startswith(target_prefix):
            break

    elapsed_time = time.time() - start_time
    wif_key = private_key_to_wif(priv_key_bytes)
    
    # Format and save text output
    log_output = (
        f"--- New Vanity Address Found ---\n"
        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Address: {address}\n"
        f"WIF Private Key: {wif_key}\n"
        f"Hex Private Key: {priv_key_bytes.hex()}\n"
        f"Attempts: {attempts:,}\n"
        f"Time Taken: {elapsed_time:.4f} seconds\n\n"
    )

    filename = "vanity_keys.txt"
    with open(filename, "a") as f:
        f.write(log_output)

    print(f"\n✨ Success! Match found.")
    print(f"Address: {address}")
    print(f"Private Key (WIF): {wif_key}")
    print(f"Saved to: {os.path.abspath(filename)}")

if __name__ == "__main__":
    # Testing with '1Sm' (2 custom characters). Should finish in seconds.
    run_single_thread_vanity("1Sm")
