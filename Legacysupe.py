import hashlib
import os
import time
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Standard Base58 alphabet (excludes 0, O, I, l to prevent visual confusion)
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def generate_private_key():
    """Generates a cryptographically secure random 256-bit Bitcoin private key."""
    return os.urandom(32)

def private_to_uncompressed_public_key(private_key_bytes):
    """Derives an uncompressed SEC1 public key (Legacy standard)."""
    priv_key = ec.derive_private_key(
        int.from_bytes(private_key_bytes, byteorder='big'), 
        ec.SECP256K1()
    )
    pub_key = priv_key.public_key()
    return pub_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )

def base58_encode_check(v_bytes):
    """Encodes bytes into a Base58Check string (includes 4-byte checksum)."""
    # Double SHA-256 for the checksum
    digest1 = hashlib.sha256(v_bytes).digest()
    digest2 = hashlib.sha256(digest1).digest()
    checksum = digest2[:4]
    
    # Append checksum to payload
    payload = v_bytes + checksum
    
    # Convert payload bytes to a Base58 string
    num = int.from_bytes(payload, byteorder='big')
    result = []
    while num > 0:
        num, remainder = divmod(num, 58)
        result.append(BASE58_ALPHABET[remainder])
    
    # Handle leading zero bytes (which map to '1' in Base58)
    for b in v_bytes:
        if b == 0:
            result.append(BASE58_ALPHABET[0])
        else:
            break
            
    return "".join(reversed(result))

def public_key_to_legacy_address(pubkey_bytes):
    """Converts a public key to a standard Legacy (P2PKH) Address."""
    # 1. SHA-256 hash of the public key
    sha256_hash = hashlib.sha256(pubkey_bytes).digest()
    
    # 2. RIPEMD-160 hash
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    hashed_pubkey = ripemd160.digest()
    
    # 3. Prepend version byte (0x00 for Bitcoin Mainnet Legacy Address)
    version_payload = b'\x00' + hashed_pubkey
    
    # 4. Return Base58Check encoded address
    return base58_encode_check(version_payload)

def generate_legacy_vanity_14_char(fixed_base, variable_char):
    """
    Checks for a 14-character Legacy pattern.
    Fixed base must be 13 characters (starting with '1').
    Variable char is the 14th character (Difficulty 1 search).
    """
    # Validation
    if not fixed_base.startswith("1"):
        raise ValueError("Bitcoin Legacy addresses must start with '1'")
    if len(fixed_base) != 13:
        raise ValueError("The fixed base string must be exactly 13 characters long.")
    if len(variable_char) != 1:
        raise ValueError("Difficulty 1 requires exactly 1 variable character.")
    if variable_char not in BASE58_ALPHABET or not all(c in BASE58_ALPHABET for c in fixed_base):
        raise ValueError(f"Invalid Base58 character detected. Use only: {BASE58_ALPHABET}")

    target_prefix = fixed_base + variable_char
    print(f"Searching for 14-character Legacy vanity address starting with: '{target_prefix}'")
    print(f"Difficulty 1: Actively solving for the final character '{variable_char}'...")
    
    attempts = 0
    start_time = time.time()

    while True:
        priv_key_bytes = generate_private_key()
        pub_key_bytes = private_to_uncompressed_public_key(priv_key_bytes)
        address = public_key_to_legacy_address(pub_key_bytes)
        attempts += 1
        
        # Check if the generated address matches your full 14-character target
        if address.startswith(target_prefix):
            elapsed_time = time.time() - start_time
            print(f"\n✨ Success! Match found.")
            print(f"Address: {address}")
            print(f"Private Key (Hex): {priv_key_bytes.hex()}")
            print(f"Attempts: {attempts:,}")
            print(f"Time Taken: {elapsed_time:.4f} seconds")
            break

# EXAMPLE CONFIGURATION:
# '1' (1 char) + 'SmithElGree' (12 chars) = 13 characters fixed base.
# 'n' (1 char) = The 14th character to search for at Difficulty 1.
# Total string checked: '1SmithElGreen' (14 characters)
generate_legacy_vanity_14_char(fixed_base="1SmithElGree", variable_char="n")
