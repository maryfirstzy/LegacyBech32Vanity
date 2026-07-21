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

def public_key_to_legacy_address(pubkey_bytes):
    """Converts a public key to a standard Legacy (P2PKH) Address."""
    sha256_hash = hashlib.sha256(pubkey_bytes).digest()
    
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256_hash)
    hashed_pubkey = ripemd160.digest()
    
    version_payload = b'\x00' + hashed_pubkey
    return base58_encode_check(version_payload)

def generate_legacy_vanity_14_char(full_target_string):
    """
    Takes a full 14-character target string starting with '1'.
    Automatically splits it into a 13-character fixed base and 
    a 1-character variable target for a Difficulty 1 search.
    """
    if not full_target_string.startswith("1"):
        raise ValueError("Bitcoin Legacy addresses must start with '1'")
    if len(full_target_string) != 14:
        raise ValueError("The target string must be exactly 14 characters long.")
        
    # Check for invalid characters and show exactly which one caused the issue
    for char in full_target_string:
        if char not in BASE58_ALPHABET:
            raise ValueError(
                f"Invalid Base58 character detected: '{char}'.\n"
                f"Bitcoin Legacy addresses cannot contain 'l' (lowercase L), 'I' (uppercase i), 'O' (uppercase o), or '0' (zero)."
            )

    variable_char = full_target_string[-1]

    print(f"Searching for 14-character Legacy vanity address matching: '{full_target_string}'")
    print(f"Difficulty 1: Actively solving for the final character '{variable_char}'...")
    
    attempts = 0
    start_time = time.time()

    while True:
        priv_key_bytes = generate_private_key()
        pub_key_bytes = private_to_uncompressed_public_key(priv_key_bytes)
        address = public_key_to_legacy_address(pub_key_bytes)
        attempts += 1
        
        if address.startswith(full_target_string):
            elapsed_time = time.time() - start_time
            print(f"\n✨ Success! Match found.")
            print(f"Address: {address}")
            print(f"Private Key (Hex): {priv_key_bytes.hex()}")
            print(f"Attempts: {attempts:,}")
            print(f"Time Taken: {elapsed_time:.4f} seconds")
            break

# EXECUTE SEARCH USING AN UPPERCASE 'L' (Valid Base58)
generate_legacy_vanity_14_char("1SmithELGreenx") 
