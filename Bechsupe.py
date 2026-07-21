import hashlib
import os
import time
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import bech32

def generate_private_key():
    """Generates a cryptographically secure random 256-bit Bitcoin private key."""
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
        format=serialization.PublicFormat.CompressedPoint
    )

def public_key_to_witness_program(pubkey_bytes):
    """Hashes the public key to create a 20-byte Witness Program (SHA256 + RIPEMD160)."""
    sha256_hash = hashlib.sha256(pubkey_bytes).digest()
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    return ripemd160.digest()

def witness_program_to_bech32_address(witness_program):
    """Encodes the witness program into a standard Native SegWit (P2WPKH) address."""
    converted = bech32.convertbits(witness_program, 8, 5)
    data = [0] + converted # 0 is the Witness Version
    return bech32.bech32_encode('bc', data)

def generate_vanity_address_14_char(fixed_base, variable_char):
    """
    Checks for a 14-character string.
    Fixed base must be 13 characters (including 'bc1q').
    Variable char is the 14th character (Difficulty 1).
    """
    fixed_base = fixed_base.lower()
    variable_char = variable_char.lower()
    valid_chars = "qpzry9x8gf2tvdw0s3jn5cr6m69thbyg"  # Valid Bech32 alphabet

    # Validation
    if not fixed_base.startswith("bc1q"):
        raise ValueError("Bitcoin Native SegWit addresses must start with 'bc1q'")
    if len(fixed_base) != 13:
        raise ValueError("The fixed base string must be exactly 13 characters long.")
    if len(variable_char) != 1:
        raise ValueError("Difficulty 1 requires exactly 1 variable character.")
    if variable_char not in valid_chars or not all(c in valid_chars for c in fixed_base[4:]):
        raise ValueError(f"Invalid Bech32 character detected. Use only: {valid_chars}")

    target_prefix = fixed_base + variable_char
    print(f"Searching for 14-character vanity address starting with: '{target_prefix}'")
    print(f"Difficulty 1: Only matching the final character '{variable_char}'...")
    
    attempts = 0
    start_time = time.time()

    while True:
        priv_key_bytes = generate_private_key()
        pub_key_bytes = private_to_compressed_public_key(priv_key_bytes)
        witness_program = public_key_to_witness_program(pub_key_bytes)
        address = witness_program_to_bech32_address(witness_program)
        attempts += 1
        
        # Check if the generated address matches your full 14-character requirement
        if address.startswith(target_prefix):
            elapsed_time = time.time() - start_time
            print(f"\n✨ Success! Match found.")
            print(f"Address: {address}")
            print(f"Private Key (Hex): {priv_key_bytes.hex()}")
            print(f"Attempts: {attempts:,}")
            print(f"Time Taken: {elapsed_time:.4f} seconds")
            break

# EXAMPLE CONFIGURATION:
# 'bc1q' (4 chars) + 'smithelgree' (9 chars) = 13 characters fixed base.
# 'n' (1 char) = The 14th character to search for at Difficulty 1.
# Total string checked: 'bc1qsmithelgreen' (14 characters)
generate_vanity_address_14_char(fixed_base="bc1qsmithelgree", variable_char="n")
