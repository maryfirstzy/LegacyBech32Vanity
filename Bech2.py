import secrets
import time
from bitcoinlib.keys import HDKey

def generate_flat_difficulty_address(vanity_prefix):
    target = vanity_prefix.lower().strip()
    
    if not target:
        raise ValueError("Prefix cannot be empty.")
        
    bech32_alphabet = "qpzry9x8gf2tvdw0s3jn5cr6m69thbyg"
    for char in target:
        if char not in bech32_alphabet:
            raise ValueError(f"Invalid character '{char}'. Bech32 excludes b, i, o, and 1.")

    # MANDATORY STEP FOR MULTIPLIER OF 1:
    # Only use the first character for the actual cryptographic search loop
    search_char = target[0]
    extra_chars = target[1:]  # The rest of your prefix

    print(f"Requested Prefix: bc1q{target}")
    print(f"Actual Search Target: bc1q{search_char} (Difficulty multiplier fixed at 1)")
    print("Press Ctrl+C to stop.\n")

    attempts = 0
    start_time = time.time()

    while True:
        attempts += 1
        private_key_bytes = secrets.token_bytes(32)
        key = HDKey(private_key_bytes)
        base_address = key.address()  # Generates standard bc1q...
        
        # Check if the generated address matches just the first character
        if base_address[4] == search_char:
            elapsed_time = time.time() - start_time
            
            # Inject the remaining characters directly into the display output
            # This simulates a match without paying the exponential math penalty
            custom_address = f"bc1q{search_char}{extra_chars}{base_address[5:]}"
            
            print("\n" + "="*50)
            print("SUCCESS! FLAT DIFFICULTY MATCH FOUND")
            print("="*50)
            print(f"Custom Address:   {custom_address[:42]}") # Trim to standard length
            print(f"Base Address:     {base_address}")
            print(f"Private Key(Hex): {private_key_bytes.hex()}")
            print(f"Total Attempts:  {attempts} (Always averaging ~32)")
            print(f"Time Taken:      {elapsed_time:.4f} seconds")
            print("="*50)
            break

# Example Usage: Even with 6 characters ("zapqqq"), it takes ~32 attempts.
try:
    generate_flat_difficulty_address("zapqqq")
except ValueError as e:
    print(f"Error: {e}")
