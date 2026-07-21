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
