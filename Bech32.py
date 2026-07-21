import hashlib
import os
import time
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import bech32

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

def public_key_to_witness_program(pubkey_bytes):
    """Hashes the public key to create a 20-byte Witness Program (SHA256 + RIPEMD160)."""
    sha256_hash = hashlib.sha256(pubkey_bytes).digest()
    
    # Standard RIPEMD160 hash implementation via hashlib
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    return ripemd160.digest()

def witness_program_to_bech32_address(witness_program):
    """Encodes the witness program into a standard Native SegWit (P2WPKH) address."""
    # Convert 8-bit bytes into 5-bit groupings for Bech32 encoding
    converted = bech32.convertbits(witness_program, 8, 5)
    
    # Witness Version 0 prepended to the converted payload data
    data = [0] + converted
    
    # Encode with Human Readable Part (HRP) 'bc' for Bitcoin Mainnet
    return bech32.bech32_encode('bc', data)

def generate_vanity_address(prefix):
    """
    Loops until an address starting with 'bc1q' + prefix is found.
    Each character in the prefix increases complexity by exactly 2^1 (2x).
    """
    # Lowercase the prefix since Bech32 ignores character case
    prefix = prefix.lower()
    
    # Ensure prefix uses valid Bech32 alphabet (excludes b, i, o, 1)
    valid_chars = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    for char in prefix:
        if char not in valid_chars:
            raise ValueError(f"Invalid character '{char}' for Bech32 addresses.")

    full_prefix = f"bc1q{prefix}"
    print(f"Searching for an address starting with: {full_prefix}")
    print("Press Ctrl+C to stop.\n")
    
    attempts = 0
    start_time = time.time()
    
    try:
        while True:
            attempts += 1
            
            # 1. Generate keypair
            priv_bytes = generate_private_key()
            pub_bytes = private_to_compressed_public_key(priv_bytes)
            
            # 2. Hash and encode
            witness_prog = public_key_to_witness_program(pub_bytes)
            address = witness_program_to_bech32_address(witness_prog)
            
            # 3. Print a benchmark status update every 50,000 attempts
            if attempts % 50000 == 0:
                elapsed = time.time() - start_time
                speed = attempts / elapsed if elapsed > 0 else 0
                print(f"Attempts: {attempts:,} | Avg Speed: {speed:.2f} keys/sec")

            # 4. Check for prefix match
            if address.startswith(full_prefix):
                elapsed = time.time() - start_time
                print("\n" + "="*50)
                print("SUCCESS! MATCH FOUND")
                print("="*50)
                print(f"Address:           {address}")
                print(f"Private Key (Hex): {priv_bytes.hex()}")
                print(f"Total Attempts:    {attempts:,}")
                print(f"Time Taken:        {elapsed:.2f} seconds")
                print("="*50)
                return priv_bytes, address
                
    except KeyboardInterrupt:
        print("\nSearch aborted by user.")
        return None, None

# Run the generator
if __name__ == "__main__":
    # Choose a short prefix to test. Every added character scales difficulty by 32x.
    # Allowed alphabet characters: qpzry9x8gf2tvdw0s3jn54khce6mua7l
    TARGET_PREFIX = "r99999999" 
    
    generate_vanity_address(TARGET_PREFIX)
