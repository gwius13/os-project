import heapq
import os
import json
from collections import defaultdict, Counter

# Node class for Huffman Tree
class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

# Build Huffman Tree
def build_huffman_tree(text):
    frequency = Counter(text)
    priority_queue = [HuffmanNode(char, freq) for char, freq in frequency.items()]
    heapq.heapify(priority_queue)

    while len(priority_queue) > 1:
        left = heapq.heappop(priority_queue)
        right = heapq.heappop(priority_queue)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(priority_queue, merged)

    return heapq.heappop(priority_queue)

# Generate Huffman Codes
def generate_codes(node, prefix="", codebook={}):
    if node:
        if node.char is not None:
            codebook[node.char] = prefix
        generate_codes(node.left, prefix + "0", codebook)
        generate_codes(node.right, prefix + "1", codebook)
    return codebook

# Encode the text using Huffman codes
def huffman_encode(text, codebook):
    return ''.join(codebook[char] for char in text)

# Compress the file
def compress_file(input_file, output_file):
    with open(input_file, 'r') as file:
        text = file.read()

    if not text:
        raise ValueError("The input file is empty.")

    huffman_tree = build_huffman_tree(text)
    codebook = generate_codes(huffman_tree)
    encoded_text = huffman_encode(text, codebook)

    # Pad the encoded text to make it divisible by 8
    padding = 8 - len(encoded_text) % 8
    encoded_text += '0' * padding

    # Convert binary string to bytes
    byte_array = bytearray()
    for i in range(0, len(encoded_text), 8):
        byte = encoded_text[i:i+8]
        byte_array.append(int(byte, 2))

    # Save the codebook and padding along with the compressed data
    with open(output_file, 'wb') as file:
        # Write padding info
        file.write(bytes([padding]))
        # Write codebook (as JSON)
        codebook_json = json.dumps(codebook).encode('utf-8')
        file.write(len(codebook_json).to_bytes(4, byteorder='big'))  # Write codebook length
        file.write(codebook_json)  # Write codebook
        file.write(bytes(byte_array))  # Write encoded data

    # Get file sizes
    original_size = os.path.getsize(input_file)
    compressed_size = os.path.getsize(output_file)

    print(f"File compressed successfully: {output_file}")
    print(f"Original file size: {original_size} bytes")
    print(f"Compressed file size: {compressed_size} bytes")

# Decompress the file
def decompress_file(input_file, output_file):
    with open(input_file, 'rb') as file:
        # Read padding info
        padding = int.from_bytes(file.read(1), byteorder='big')
        # Read codebook length
        codebook_length = int.from_bytes(file.read(4), byteorder='big')
        # Read codebook
        codebook_json = file.read(codebook_length).decode('utf-8')
        codebook = json.loads(codebook_json)
        # Read encoded data
        encoded_data = file.read()

    # Convert bytes to binary string
    encoded_text = ''.join(f'{byte:08b}' for byte in encoded_data)
    encoded_text = encoded_text[:-padding]  # Remove padding

    # Decode the text using the codebook
    decoded_text = ""
    current_code = ""
    reverse_codebook = {v: k for k, v in codebook.items()}

    for bit in encoded_text:
        current_code += bit
        if current_code in reverse_codebook:
            decoded_text += reverse_codebook[current_code]
            current_code = ""

    # Write decoded text to output file
    with open(output_file, 'w') as file:
        file.write(decoded_text)

    # Get file sizes
    compressed_size = os.path.getsize(input_file)
    decompressed_size = os.path.getsize(output_file)

    print(f"File decompressed successfully: {output_file}")
    print(f"Compressed file size: {compressed_size} bytes")
    print(f"Decompressed file size: {decompressed_size} bytes")

# Main function
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python huffman_compression.py <compress|decompress> <input_file> <output_file>")
        sys.exit(1)

    operation = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]

    try:
        if operation == "compress":
            compress_file(input_file, output_file)
        elif operation == "decompress":
            decompress_file(input_file, output_file)
        else:
            print("Invalid operation. Use 'compress' or 'decompress'.")
    except Exception as e:
        print(f"Error: {e}")