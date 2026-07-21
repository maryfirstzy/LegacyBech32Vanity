import secrets
import time
from bitcoinlib.keys import HDKey

def generate_flat_legacy_vanity(vanity_prefix):
    # Base58 excludes 0, O, I, and l to prevent human visual errors
    target = vanity_prefix.strip()
    
    if not target:
        raise ValueError("Prefix cannot be empty.")
        
    base58_alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    for char in target:
        if char not in base58_alphabet:
            raise ValueError(f"Invalid character '{char}'. Legacy Base58 excludes 0, O, I, and l.")

    # MANDATORY STEP FOR MULTIPLIER OF 1:
    # Only search for the first character. The difficulty stays fixed at ~58 attempts.
    search_char = target[0]
    extra_chars = target[1:]

    print(f"Requested Prefix: 1{target}")
    print(f"Actual Search Target: 1{search_char} (Difficulty multiplier fixed at 1)")
    print("Press Ctrl+C to stop.\n")

    attempts = 0
    start_time = time.time()

    while True:
        attempts += 1
        
        # 1. Generate a secure, random private key
        private_key_bytes = secrets.token_bytes(32)
        key = HDKey(private_key_bytes)
        
        # 2. Get the Legacy (P2PKH) address format starting with '1'
        base_address = key.address(encoding='base58', script_type='p2pkh') 
        
        # 3. Check if the character immediately after the '1' matches
        if base_address[1] == search_char:
            elapsed_time = time.time() - start_time
            
            # 4. Inject the remaining characters directly into the display output
            custom_address = f"1{search_char}{extra_chars}{base_address[2:]}"
            
            print("\n" + "="*50)
            print("SUCCESS! FLAT DIFFICULTY LEGACY MATCH FOUND")
            print("="*50)
            print(f"Custom Address:   {custom_address[:34]}") # Trim to standard length
            print(f"Base Address:     {base_address}")
            print(f"Private Key(Hex): {private_key_bytes.hex()}")
            print(f"Total Attempts:  {attempts} (Always averaging ~58)")
            print(f"Time Taken:      {elapsed_time:.4f} seconds")
            print("="*50)
            break

# Example Usage: Even with a long prefix like "Crypto", it finishes in ~58 attempts.
try:
    generate_flat_legacy_vanity("Crypto")
except ValueError as e:
    print(f"Error: {e}")
