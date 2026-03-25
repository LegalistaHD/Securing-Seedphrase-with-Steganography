from PIL import Image
import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

def calculate_psnr(original_image: Image.Image, stego_image: Image.Image) -> float:
    """
    Menghitung Peak Signal-to-Noise Ratio (PSNR) antara gambar asli dan stego.

    Args:
        original_image: Objek gambar PIL asli.
        stego_image: Objek gambar PIL hasil steganografi.

    Returns:
        Nilai PSNR dalam desibel (dB).
    """
    # Konversi gambar ke mode yang sama dan ke array NumPy
    original_array = np.array(original_image.convert("RGB"))
    stego_array = np.array(stego_image.convert("RGB"))

    # Hitung PSNR. Data range untuk gambar 8-bit adalah 255.
    return peak_signal_noise_ratio(original_array, stego_array, data_range=255)


def calculate_ssim(original_image: Image.Image, stego_image: Image.Image) -> float:
    """
    Menghitung Structural Similarity Index Measure (SSIM) antara gambar asli dan stego.

    Args:
        original_image: Objek gambar PIL asli.
        stego_image: Objek gambar PIL hasil steganografi.

    Returns:
        Nilai SSIM (antara -1 dan 1, di mana 1 berarti identik).
    """
    # Konversi gambar ke mode yang sama dan ke array NumPy
    original_array = np.array(original_image.convert("RGB"))
    stego_array = np.array(stego_image.convert("RGB"))
    
    # Hitung SSIM untuk gambar multi-channel (RGB).
    # channel_axis=-1 menunjukkan bahwa dimensi terakhir adalah channel warna.
    return structural_similarity(original_array, stego_array, channel_axis=-1, data_range=255)

