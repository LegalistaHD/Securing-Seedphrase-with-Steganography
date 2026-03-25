from PIL import Image
import numpy as np
import cv2
import random

def embed_edge(image: Image.Image, binary_message: str, seed_key: str) -> tuple[Image.Image, list, np.ndarray]:
    """
    Menyisipkan pesan biner ke dalam area tepi gambar menggunakan deteksi Canny.

    Args:
        image: Objek gambar PIL (Pillow) asli.
        binary_message: Pesan dalam bentuk string biner.
        seed_key: Kunci untuk inisialisasi PRNG.

    Returns:
        Tuple berisi:
        - stego_image (Image.Image): Objek gambar PIL baru yang berisi pesan.
        - coordinates (list): Daftar koordinat (x, y) yang telah dimodifikasi.
        - edge_map (np.ndarray): Peta tepi Canny yang dihasilkan sebagai array NumPy.

    Raises:
        ValueError: Jika jumlah piksel tepi tidak cukup untuk menampung pesan.
    """
    # 1. Konversi dari PIL Image ke OpenCV format (BGR)
    rgb_image = image.convert("RGB")
    original_cv_image = cv2.cvtColor(np.array(rgb_image), cv2.COLOR_RGB2BGR)
    stego_cv_image = original_cv_image.copy() # Bekerja pada salinan

    # 2. Deteksi tepi menggunakan Canny
    gray_image = cv2.cvtColor(original_cv_image, cv2.COLOR_BGR2GRAY)
    # Threshold (100, 200) adalah nilai umum, bisa disesuaikan
    edge_map = cv2.Canny(gray_image, 100, 200)

    # 3. Dapatkan semua koordinat piksel dari area tepi
    edge_pixels_y, edge_pixels_x = np.where(edge_map == 255)
    if not edge_pixels_y.size:
        raise ValueError("Tidak ada tepi yang terdeteksi pada gambar. Tidak bisa menyisipkan pesan.")
    
    edge_coordinates = list(zip(edge_pixels_x, edge_pixels_y))

    # 4. Periksa kapasitas
    capacity = len(edge_coordinates)
    message_length = len(binary_message)
    if message_length > capacity:
        raise ValueError(f"Pesan terlalu besar. Kapasitas area tepi: {capacity} bit, Ukuran pesan: {message_length} bit.")

    # 5. Acak urutan koordinat tepi
    random.seed(seed_key)
    random.shuffle(edge_coordinates)

    # 6. Sisipkan pesan
    embedding_coordinates = edge_coordinates[:message_length]
    for i, bit in enumerate(binary_message):
        x, y = embedding_coordinates[i]
        
        # Ambil nilai BGR dan modifikasi LSB kanal Biru (indeks 0)
        blue_val = stego_cv_image[y, x][0]
        stego_cv_image[y, x][0] = (blue_val & 0xFE) | int(bit)

    # 7. Konversi kembali dari OpenCV (BGR) ke PIL Image (RGB)
    stego_image_pil = Image.fromarray(cv2.cvtColor(stego_cv_image, cv2.COLOR_BGR2RGB))
    
    return stego_image_pil, embedding_coordinates, edge_map


def extract_edge(stego_image: Image.Image, original_image: Image.Image, message_length: int, seed_key: str) -> str:
    """
    Mengekstrak pesan dari stego-image berbasis tepi.
    Membutuhkan gambar asli untuk merekonstruksi peta tepi.

    Args:
        stego_image: Objek gambar PIL (Pillow) yang berisi pesan.
        original_image: Objek gambar PIL (Pillow) asli sebagai referensi.
        message_length: Panjang pesan biner yang diharapkan.
        seed_key: Kunci yang sama yang digunakan saat embedding.

    Returns:
        String pesan biner yang diekstrak.
        
    Raises:
        ValueError: Jika peta tepi dari gambar asli tidak dapat menampung pesan.
    """
    # 1. Regenerasi peta tepi dari GAMBAR ASLI
    original_rgb = original_image.convert("RGB")
    original_cv = cv2.cvtColor(np.array(original_rgb), cv2.COLOR_RGB2BGR)
    gray_image = cv2.cvtColor(original_cv, cv2.COLOR_BGR2GRAY)
    edge_map = cv2.Canny(gray_image, 100, 200)

    # 2. Dapatkan kembali urutan koordinat acak yang sama
    edge_pixels_y, edge_pixels_x = np.where(edge_map == 255)
    if not edge_pixels_y.size:
        raise ValueError("Tidak ada tepi yang terdeteksi pada gambar asli.")
        
    edge_coordinates = list(zip(edge_pixels_x, edge_pixels_y))
    
    capacity = len(edge_coordinates)
    if message_length > capacity:
        raise ValueError(f"Panjang pesan ({message_length}) melebihi kapasitas area tepi ({capacity}) dari gambar asli.")

    random.seed(seed_key)
    random.shuffle(edge_coordinates)
    
    extracting_coordinates = edge_coordinates[:message_length]

    # 3. Ekstrak LSB dari STEGO IMAGE pada koordinat yang ditemukan
    stego_rgb = stego_image.convert("RGB")
    stego_cv = cv2.cvtColor(np.array(stego_rgb), cv2.COLOR_RGB2BGR)
    
    binary_message = []
    for x, y in extracting_coordinates:
        blue_val = stego_cv[y, x][0]
        extracted_bit = blue_val & 1
        binary_message.append(str(extracted_bit))
        
    return "".join(binary_message)

