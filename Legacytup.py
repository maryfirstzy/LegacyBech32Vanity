import hashlib
import os
import time
import multiprocessing
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Standard Base58 alphabet
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
            result.append(BASE58_ALPHABET)
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

def private_key_to_wif(private_key_bytes):
    """Converts a 256-bit private key to Wallet Import Format (WIF)."""
    wif_bytes = b'\x80' + private_key_bytes
    return base58_encode_check(wif_bytes)

def worker_search(target_prefix, result_queue, stop_event):
    """Worker loop running on an individual CPU core searching for a prefix."""
    while not stop_event.is_set():
        priv_key_bytes = generate_private_key()
        pub_key_bytes = private_to_uncompressed_public_key(priv_key_bytes)
        address = public_key_to_legacy_address(pub_key_bytes)
        
        # Check if the address explicitly starts with our target characters
        if address.startswith(target_prefix):
            wif_key = private_key_to_wif(priv_key_bytes)
            result_queue.put((address, priv_key_bytes.hex(), wif_key))
            stop_event.set()
            break

def run_multiprocess_vanity(target_prefix):
    if not target_prefix.startswith("1"):
        raise ValueError("Bitcoin Legacy addresses must start with '1'")
        
    for char in target_prefix:
        if char not in BASE58_ALPHABET:
            raise ValueError(f"Character '{char}' is not valid in Base58.")

    num_cores = multiprocessing.cpu_count()
    print(f"🚀 Testing code with {num_cores} CPU cores...")
    print(f"Searching for address starting with: '{target_prefix}'")

    result_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()
    processes = []
    start_time = time.time()

    for _ in range(num_cores):
        p = multiprocessing.Process(target=worker_search, args=(target_prefix, result_queue, stop_event))
        p.start()
        processes.append(p)

    # This will return almost instantly now
    address, priv_key_hex, wif_key = result_queue.get()

    stop_event.set()
    for p in processes:
        p.join()

    elapsed_time = time.time() - start_time
    
    log_output = (
        f"--- New Vanity Address Found ---\n"
        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Address: {address}\n"
        f"WIF Private Key: {wif_key}\n"
        f"Hex Private Key: {priv_key_hex}\n"
        f"Time Taken: {elapsed_time:.4f} seconds\n\n"
    )

    filename = "vanity_keys.txt"
    with open(filename, "a") as f:
        f.write(log_output)

    print(f"\n✨ Success! Match found instantly.")
    print(f"Address: {address}")
    print(f"Private Key (WIF): {wif_key}")
    print(f"Saved to: {os.path.abspath(filename)}")

if __name__ == "__main__":
    # '1' + 2 custom letters ('S' and 'm') = '1Sm'
    run_multiprocess_vanity("1Sm")
