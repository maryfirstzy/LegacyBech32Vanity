import hashlib
import os
import time
import sys

# Standard Base58 alphabet
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def generate_base_key():
    """Generates a secure random 256-bit baseline integer."""
    return int.from_bytes(os.urandom(32), byteorder='big')

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

def private_key_to_legacy_address(private_key_int):
    """Derives address from private key integer using standard EC mapping."""
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization
    
    # Convert integer back to 32 bytes
    private_key_bytes = private_key_int.to_bytes(32, byteorder='big')
    
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
    """Converts private key bytes to Wallet Import Format (WIF)."""
    return base58_encode_check(b'\x80' + private_key_bytes)

def run_optimized_vanity(target_prefix):
    if len(target_prefix) != 9:
        raise ValueError("Target prefix must be exactly 9 characters long.")
    if not target_prefix.startswith("1"):
        raise ValueError("Bitcoin Legacy addresses must start with '1'")
        
    for char in target_prefix:
        if char not in BASE58_ALPHABET:
            raise ValueError(f"Character '{char}' is not valid in Base58.")

    print(f"🚀 Running optimized sequential key-stepping engine...")
    print(f"Targeting 9-character match: '{target_prefix}'")
    print(f"Starting execution directly from attempt #1...\n")

    attempts = 0
    start_time = time.time()
    
    # Initialize secure baseline key point
    current_key_int = generate_base_key()

    while True:
        attempts += 1
        
        try:
            address, priv_bytes = private_key_to_legacy_address(current_key_int)
        except Exception as e:
            print(f"\nError processing keys: {e}")
            return

        # Continuous status tracking line
        if attempts % 500 == 0:
            sys.stdout.write(f"\r[+] Engine working | Checked: {attempts:,} keys")
            sys.stdout.flush()

        # Check for immediate prefix match
        if address.startswith(target_prefix):
            break
            
        # Optimization step: increment the private key integer sequentially
        current_key_int = (current_key_int + 1) % ec.SECP256K1.key_size

    elapsed_time = time.time() - start_time
    wif_key = private_key_to_wif(priv_bytes)
    
    log_output = (
        f"--- New Legacy 9-Char Address Found ---\n"
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

    # Clear status line
    sys.stdout.write("\r" + " " * 70 + "\r")
    sys.stdout.flush()

    print(f"✨ Success! Match found.")
    print(f"Address: {address}")
    print(f"Private Key (WIF): {wif_key}")
    print(f"Saved to: {os.path.abspath(filename)}")

if __name__ == "__main__":
    run_optimized_vanity("1SmithELG")
