import hashlib
import os
import time
import sys
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Standard Base58 alphabet
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# Mathematical order of the secp256k1 curve
SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def generate_base_key():
    """Generates a secure random 256-bit baseline integer."""
    while True:
        key_int = int.from_bytes(os.urandom(32), byteorder='big')
        if 0 < key_int < SECP256K1_ORDER:
            return key_int

def base58_encode_check(v_bytes):
    """Encodes bytes into a Base58Check string."""
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

def private_key_to_legacy_address(private_key_int):
    """Derives genuine address from private key integer."""
    private_key_bytes = private_key_int.to_bytes(32, byteorder='big')
    
    # Mathematical curve calculation step
    priv_key = ec.derive_private_key(private_key_int, ec.SECP256K1())
    pub_key = priv_key.public_key().public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )
    
    sha256_hash = hashlib.sha256(pub_key).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    
    return base58_encode_check(b'\x00' + ripemd160.digest()), private_key_bytes

def private_key_to_wif(private_key_bytes):
    """Converts private key bytes to standard real WIF."""
    return base58_encode_check(b'\x80' + private_key_bytes)

def run_real_vanity_engine(target_prefix):
    if len(target_prefix) != 9:
        raise ValueError("Target prefix must be exactly 9 characters long.")
    if not target_prefix.startswith("1"):
        raise ValueError("Bitcoin Legacy addresses must start with '1'")
        
    for char in target_prefix:
        if char not in BASE58_ALPHABET:
            raise ValueError(f"Character '{char}' is not valid in Base58.")

    print(f"🚀 Running genuine mathematical key-stepping engine...")
    print(f"Searching for real cryptographic match starting with: '{target_prefix}'...")
    print(f"Every key generated will be a 100% genuine match for its paired address.\n")

    attempts = 0
    start_time = time.time()
    last_update_time = start_time
    last_update_attempts = 0
    
    current_key_int = generate_base_key()

    while True:
        attempts += 1
        
        try:
            address, priv_bytes = private_key_to_legacy_address(current_key_int)
        except Exception as e:
            print(f"\nError processing keys: {e}")
            return

        # Core tracker line
        if attempts % 500 == 0:
            current_time = time.time()
            time_diff = current_time - last_update_time
            if time_diff >= 0.5:
                keys_since_last = attempts - last_update_attempts
                keys_per_second = keys_since_last / time_diff
                sys.stdout.write(f"\r[+] Searched: {attempts:,} keys | Speed: {keys_per_second:.2f} keys/sec")
                sys.stdout.flush()
                last_update_time = current_time
                last_update_attempts = attempts

        # Genuine verification check
        if address.startswith(target_prefix):
            break
            
        # Move mathematically to the next sequential candidate key point
        current_key_int = (current_key_int + 1) % SECP256K1_ORDER
        if current_key_int == 0:
            current_key_int = 1

    elapsed_time = time.time() - start_time
    wif_key = private_key_to_wif(priv_bytes)
    
    log_output = (
        f"--- Real Verified Legacy 9-Char Address Found ---\n"
        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Address: {address}\n"
        f"WIF Private Key: {wif_key}\n"
        f"Hex Private Key: {priv_bytes.hex()}\n"
        f"Attempts Required: {attempts:,}\n"
        f"Time Taken: {elapsed_time:.4f} seconds\n\n"
    )

    filename = "vanity_keys.txt"
    with open(filename, "a") as f:
        f.write(log_output)

    sys.stdout.write("\r" + " " * 70 + "\r")
    sys.stdout.flush()

    print(f"✨ Success! Genuine cryptographic match found.")
    print(f"Address: {address}")
    print(f"Private Key (WIF): {wif_key}")
    print(f"Saved to: {os.path.abspath(filename)}")

if __name__ == "__main__":
    run_real_vanity_engine("1SmithELG")
