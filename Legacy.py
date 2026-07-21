import hashlib
import os
import time
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base58

def generate_private_key():
    """Generates a cryptographically secure random 256-bit private key."""
    return os.urandom(32)

def private_to_compressed_public_key(private_key_bytes):
    """Derives a compressed SEC1 public key from the private key using secp256k1."""
    priv_key = ec.derive_private_key(
        int.from_bytes(private_key_bytes, byteorder='big'), 
        ec.SECP256K1()
    )
    pub_key = priv_key.public_key()
    return pub_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.CompressedPoint  # Fixed here
    )

def public_key_to_legacy_address(pubkey_bytes):
    """Hashes public key and applies Base58Check encoding for a Legacy P2PKH address."""
    # 1. SHA-256 hash of the public key
    sha256_hash = hashlib.sha256(pubkey_bytes).digest()
    
    # 2. RIPEMD-160 hash of the SHA-256 hash
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    pubkey_hash = ripemd160.digest()
    
    # 3. Prepend Network Byte (0x00 for Bitcoin Mainnet Legacy addresses)
    network_payload = b'\x00' + pubkey_hash
    
    # 4. Double SHA-256 to calculate the 4-byte checksum
    checksum = hashlib.sha256(hashlib.sha256(network_payload).digest()).digest()[:4]
    
    # 5. Append checksum and encode to Base58
    final_payload = network_payload + checksum
    return base58.b58encode(final_payload).decode('utf-8')

def generate_legacy_vanity_address(prefix):
    """
    Loops until a Legacy address starting with '1' + prefix is found.
    Each character in the prefix increases complexity by exactly 58x.
    """
    # Validate that the prefix uses the legal Base58 alphabet.
    invalid_chars = ['0', 'O', 'I', 'l']
    for char in prefix:
        if char in invalid_chars:
            raise ValueError(f"Invalid character '{char}' for Base58 (Legacy) addresses.")

    full_prefix = f"1{prefix}"
    print(f"Searching for a Legacy address starting with: {full_prefix}")
    print("Press Ctrl+C to stop.\n")
    
    attempts = 0
    start_time = time.time()
    
    try:
        while True:
            attempts += 1
            
            # 1. Generate keypair
            priv_bytes = generate_private_key()
            pub_bytes = private_to_compressed_public_key(priv_bytes)
            
            # 2. Hash and Base58Check encode
            address = public_key_to_legacy_address(pub_bytes)
            
            # 3. Print benchmarking status update every 50,000 attempts
            if attempts % 50000 == 0:
                elapsed = time.time() - start_time
                speed = attempts / elapsed if elapsed > 0 else 0
                print(f"Attempts: {attempts:,} | Avg Speed: {speed:.2f} keys/sec")

            # 4. Check for case-sensitive prefix match
            if address.startswith(full_prefix):
                elapsed = time.time() - start_time
                print("\n" + "="*50)
                print("SUCCESS! MATCH FOUND")
                print("="*50)
                print(f"Address:            {address}")
                print(f"Private Key (Hex):  {priv_bytes.hex()}")
                print(f"Total Attempts:     {attempts:,}")
                print(f"Time Taken:         {elapsed:.2f} seconds")
                print("="*50)
                return priv_bytes, address
                
    except KeyboardInterrupt:
        print("\nSearch aborted by user.")
        return None, None

# Run the generator
if __name__ == "__main__":
    # Choose a short prefix to test. Every character increases difficulty by 58x.
    # Avoid: 0, O, I, l
    # Case matters: "a" is different than "A"
    TARGET_PREFIX = "Hi" 
    
    generate_legacy_vanity_address(TARGET_PREFIX)
