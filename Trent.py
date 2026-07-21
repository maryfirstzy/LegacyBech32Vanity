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

def run_single_thread_vanity_14_char(target_string):
    if len(target_string) != 14:
        raise ValueError("Target string must be exactly 14 characters long.")
        
    # Isolate the 14th character to search for (Difficulty 1)
    target_char = target_string[-1]
    position = 13  # 14th slot in python tracking
    
    if target_char not in BASE58_ALPHABET:
        raise ValueError(f"Character '{target_char}' is not valid in Base58.")

    print(f"🚀 Running Termux-safe single-threaded generator...")
    print(f"Targeting Difficulty 1: Any address where character #14 is '{target_char}'")
    print(f"Example shape: 1XXXXXXXXXXXX{target_char}XXXX...\n")

    attempts = 0
    start_time = time.time()
    last_update_time = start_time
    last_update_attempts = 0

    while True:
        priv_key_bytes = generate_private_key()
        try:
            address = public_key_to_legacy_address(priv_key_bytes)
        except Exception as e:
            print(f"\nError deriving keys: {e}")
            return
            
        attempts += 1
        
        # Calculate and display speed every 1,000 keys to maximize performance
        if attempts % 1000 == 0:
            current_time = time.time()
            time_diff = current_time - last_update_time
            
            # Prevent division by zero if it runs ultra-fast
            if time_diff >= 0.1:
                keys_since_last = attempts - last_update_attempts
                keys_per_second = keys_since_last / time_diff
                
                # Print live status line updating in place (\r resets the line)
                sys.stdout.write(f"\r[+] Searched: {attempts:,} keys | Speed: {keys_per_second:.2f} keys/sec")
                sys.stdout.flush()
                
                last_update_time = current_time
                last_update_attempts = attempts
        
        # Check if the address matches the character at the 14th slot
        if len(address) > position and address[position] == target_char:
            break

    elapsed_time = time.time() - start_time
    wif_key = private_key_to_wif(priv_key_bytes)
    
    log_output = (
        f"--- New 14-Char Variable Address Found ---\n"
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

    # Clear the live status line and print success
    sys.stdout.write("\r" + " " * 70 + "\r")
    sys.stdout.flush()

    print(f"✨ Success! Match found.")
    print(f"Address: {address}")
    print(f"Private Key (WIF): {wif_key}")
    print(f"Saved to: {os.path.abspath(filename)}")

if __name__ == "__main__":
    run_single_thread_vanity_14_char("1SmithELGreenx")
