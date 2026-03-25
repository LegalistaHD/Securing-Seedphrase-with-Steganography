from mnemonic import Mnemonic

WORD_COUNT = 12
BITS_PER_WORD = 11
TOTAL_BITS = WORD_COUNT * BITS_PER_WORD  # 12 * 11 = 132 bits

def mnemonic_to_binary(phrase: str) -> str:
    """
    Converts a 12-word BIP39 mnemonic phrase into its binary entropy string.

    Args:
        phrase: A string containing 12 words separated by spaces.

    Returns:
        A 132-bit binary string (concatenation of 11-bit word indices).

    Raises:
        ValueError: If the phrase is not 12 words long, is invalid, or fails the checksum.
    """
    words = phrase.strip().split()
    if len(words) != WORD_COUNT:
        raise ValueError(f"Invalid phrase: Must contain exactly {WORD_COUNT} words.")

    mnemo = Mnemonic("english")
    
    # The library's check() method implicitly validates the checksum.
    if not mnemo.check(phrase):
        raise ValueError("Invalid mnemonic phrase: Checksum failed or words are incorrect.")

    try:
        # Convert each word to its 11-bit index in the wordlist
        binary_chunks = []
        for word in words:
            index = mnemo.wordlist.index(word)
            binary_chunks.append(format(index, f'0{BITS_PER_WORD}b'))
            
        binary_string = "".join(binary_chunks)
        return binary_string
    except Exception as e:
        raise ValueError(f"An error occurred during conversion: {e}")


def binary_to_mnemonic(binary_string: str) -> str:
    """
    Converts a 132-bit binary string back into a 12-word BIP39 mnemonic phrase.

    Args:
        binary_string: A 132-bit binary string ('0's and '1's).

    Returns:
        A string containing the 12-word mnemonic phrase.

    Raises:
        ValueError: If the binary string is not 128 bits long.
    """
    if len(binary_string) != TOTAL_BITS:
        raise ValueError(f"Invalid binary string: Must be {TOTAL_BITS} bits long.")
    if not all(c in '01' for c in binary_string):
        raise ValueError("Invalid binary string: Must only contain '0' or '1'.")

    try:
        mnemo = Mnemonic("english")
        words = []
        
        # Split into 11-bit chunks and convert to words
        for i in range(0, TOTAL_BITS, BITS_PER_WORD):
            chunk = binary_string[i:i+BITS_PER_WORD]
            index = int(chunk, 2)
            words.append(mnemo.wordlist[index])
        
        phrase = " ".join(words)
        # Optional: Check checksum again (though we just reconstructed it)
        if not mnemo.check(phrase):
            raise ValueError("Restored mnemonic has invalid checksum.")
            
        return phrase
    except Exception as e:
        raise ValueError(f"An error occurred during conversion: {e}")
