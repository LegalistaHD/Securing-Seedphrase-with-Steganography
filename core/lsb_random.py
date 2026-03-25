from PIL import Image
import numpy as np
import random

def embed(image: Image.Image, binary_message: str, seed_key: str) -> tuple[Image.Image, list]:
    """
    Menyisipkan pesan biner ke dalam gambar menggunakan metode LSB Random.

    Args:
        image: Objek gambar PIL (Pillow) sebagai media penampung.
        binary_message: Pesan dalam bentuk string biner ('0' dan '1').
        seed_key: Kunci (string) untuk inisialisasi Pseudo-Random Number Generator (PRNG).

    Returns:
        Tuple berisi:
        - stego_image (Image.Image): Objek gambar PIL baru yang berisi pesan.
        - coordinates (list): Daftar koordinat (x, y) yang telah dimodifikasi.

    Raises:
        ValueError: Jika pesan terlalu besar untuk disisipkan di dalam gambar.
    """
    # Pastikan gambar dalam mode RGB untuk konsistensi
    stego_image = image.convert("RGB")
    
    width, height = stego_image.size
    max_capacity = width * height
    message_length = len(binary_message)

    if message_length > max_capacity:
        raise ValueError(f"Pesan terlalu besar. Kapasitas gambar: {max_capacity} bit, Ukuran pesan: {message_length} bit.")

    # Buat daftar semua kemungkinan koordinat piksel (x, y)
    all_coordinates = [(x, y) for x in range(width) for y in range(height)]
    
    # Inisialisasi PRNG dengan seed_key
    random.seed(seed_key)
    
    # Acak urutan koordinat
    random.shuffle(all_coordinates)
    
    # Ambil koordinat yang akan digunakan sejumlah panjang pesan
    embedding_coordinates = all_coordinates[:message_length]
    
    # Muat data piksel untuk modifikasi
    pixels = stego_image.load()
    
    for i, bit in enumerate(binary_message):
        x, y = embedding_coordinates[i]
        
        # Ambil nilai RGB piksel saat ini
        r, g, b = pixels[x, y]
        
        # Ubah LSB dari kanal Biru (Blue)
        new_b = (b & 0xFE) | int(bit)
        
        # Terapkan piksel baru
        pixels[x, y] = (r, g, new_b)
        
    return stego_image, embedding_coordinates

def extract(stego_image: Image.Image, message_length: int, seed_key: str) -> str:
    """
    Mengekstrak pesan biner dari stego-image yang dibuat dengan metode LSB Random.

    Args:
        stego_image: Objek gambar PIL (Pillow) yang diduga berisi pesan.
        message_length: Panjang pesan biner yang diharapkan (jumlah bit).
        seed_key: Kunci (string) yang sama yang digunakan saat proses embedding.

    Returns:
        String pesan biner yang diekstrak.
    """
    # Pastikan gambar dalam mode RGB
    stego_image = stego_image.convert("RGB")
    width, height = stego_image.size
    
    # Buat ulang urutan koordinat acak yang sama persis seperti saat embedding
    all_coordinates = [(x, y) for x in range(width) for y in range(height)]
    random.seed(seed_key)
    random.shuffle(all_coordinates)
    
    # Ambil koordinat tempat pesan disembunyikan
    extracting_coordinates = all_coordinates[:message_length]
    
    pixels = stego_image.load()
    binary_message = []
    
    for x, y in extracting_coordinates:
        r, g, b = pixels[x, y]
        
        # Ekstrak LSB dari kanal Biru
        extracted_bit = b & 1
        binary_message.append(str(extracted_bit))
        
    return "".join(binary_message)
