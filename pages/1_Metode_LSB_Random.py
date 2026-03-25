import streamlit as st
from PIL import Image
import io

# Pastikan kita bisa mengimpor dari direktori 'core'
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.bip39_utils import mnemonic_to_binary, binary_to_mnemonic
from core.lsb_random import embed, extract
from core.metrics import calculate_psnr, calculate_ssim

st.set_page_config(page_title="Metode LSB Random")

st.title("Metode 1: LSB Random")
st.write("Halaman ini mengimplementasikan penyisipan dan ekstraksi pesan menggunakan metode LSB pada kanal Biru dengan posisi piksel yang diacak.")

# Fungsi bantuan untuk download gambar
def image_to_bytes(image: Image.Image):
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

def create_diff_map(image_size, coordinates):
    """Membuat gambar hitam dengan titik putih di lokasi piksel yang dimodifikasi."""
    diff_map = Image.new('RGB', image_size, 'black')
    pixels = diff_map.load()
    if coordinates:
        for x, y in coordinates:
            pixels[x, y] = (255, 255, 255) # White
    return diff_map

# --- EMBEDDING SECTION ---
st.header("1. Sisipkan Pesan (Embed)")
with st.container(border=True):
    uploaded_cover = st.file_uploader("Unggah Citra Penampung (Cover Image)", type=["png"])
    if uploaded_cover:
        st.image(uploaded_cover, caption="Citra Penampung Asli")

    st.subheader("Data untuk Disisipkan")
    # Menggunakan session state untuk menyimpan nilai default
    if 'default_phrase_lsb' not in st.session_state:
        st.session_state.default_phrase_lsb = "cube volume sleep globe color erosion mountain print below ugly section update"
    
    phrase_input = st.text_area(
        "Mnemonic Phrase (12 kata):",
        key="phrase_lsb",
        value=st.session_state.default_phrase_lsb,
        height=100
    )
    seed_key_embed = st.text_input("Kunci Acak (Seed Key) untuk Penyisipan:", value="kunci_rahasia_123")

    if st.button("Mulai Proses Penyisipan", type="primary"):
        if uploaded_cover and phrase_input and seed_key_embed:
            try:
                # 1. Konversi mnemonic ke biner
                binary_message = mnemonic_to_binary(phrase_input)
                st.info(f"Mnemonic berhasil diubah menjadi {len(binary_message)} bit biner.")

                # 2. Buka gambar
                cover_image = Image.open(uploaded_cover)

                # 3. Lakukan embedding
                with st.spinner("Menyisipkan pesan ke dalam gambar..."):
                    stego_image, coords = embed(cover_image, binary_message, seed_key_embed)

                # 4. Tampilkan hasil dan hitung metrik
                st.success("Penyisipan pesan berhasil!")
                
                with st.spinner("Menghitung PSNR, SSIM, dan membuat peta modifikasi..."):
                    psnr_val = calculate_psnr(cover_image, stego_image)
                    ssim_val = calculate_ssim(cover_image, stego_image)
                    diff_map = create_diff_map(cover_image.size, coords)

                st.subheader("Hasil dan Metrik Kualitas")

                st.image(stego_image, caption="Citra Hasil (Stego-Image)")
                st.image(diff_map, caption="Peta Piksel yang Dimodifikasi")

                st.metric("PSNR (Peak Signal-to-Noise Ratio)", f"{psnr_val:.2f} dB")
                st.metric("SSIM (Structural Similarity)", f"{ssim_val:.4f}")
                
                st.caption("""
                **PSNR** mengukur rasio antara kekuatan maksimum sinyal (piksel gambar) dan 'noise' (gangguan/perubahan) yang memengaruhinya. Semakin tinggi nilainya (dalam dB), semakin sedikit 'noise' atau kerusakan pada gambar. Nilai di atas 30-40 dB umumnya dianggap sangat baik, di mana perbedaan hampir tidak terlihat.
                
                **SSIM** mengukur kesamaan struktural (pola, kontras, pencahayaan) antara dua gambar, yang lebih sesuai dengan persepsi mata manusia. Nilai berkisar antara -1 hingga 1. Nilai 1 berarti kedua gambar identik secara struktural.
                """)

                # 5. Sediakan tombol download
                st.download_button(
                    label="Unduh Stego-Image (PNG)",
                    data=image_to_bytes(stego_image),
                    file_name="stego_lsb_random.png",
                    mime="image/png"
                )

            except ValueError as e:
                st.error(f"Error: {e}")
            except Exception as e:
                st.error(f"Terjadi kesalahan tak terduga: {e}")
        else:
            st.warning("Mohon lengkapi semua input: unggah gambar, masukkan mnemonic, dan sediakan kunci acak.")

# --- EXTRACTING SECTION ---
st.header("2. Ekstrak Pesan (Extract)")
with st.container(border=True):
    uploaded_stego = st.file_uploader("Unggah Stego-Image", type=["png"], key="stego_uploader")
    if uploaded_stego:
        st.image(uploaded_stego, caption="Stego-Image yang Diunggah")

    st.subheader("Parameter untuk Ekstraksi")
    # Panjang pesan untuk BIP39 adalah 128 bit
    msg_len = st.number_input("Panjang Pesan (jumlah bit):", value=132, disabled=True)
    seed_key_extract = st.text_input("Kunci Acak (Seed Key) yang sama:", value="kunci_rahasia_123")

    if st.button("Mulai Proses Ekstraksi", type="primary"):
        if uploaded_stego and seed_key_extract:
            try:
                # 1. Buka stego-image
                stego_image = Image.open(uploaded_stego)

                # 2. Lakukan ekstraksi
                with st.spinner("Mengekstrak pesan dari gambar..."):
                    extracted_binary = extract(stego_image, msg_len, seed_key_extract)
                
                st.info(f"Berhasil mengekstrak {len(extracted_binary)} bit pesan.")

                # 3. Konversi biner ke mnemonic
                recovered_phrase = binary_to_mnemonic(extracted_binary)

                # 4. Tampilkan hasil
                st.success("Ekstraksi dan konversi ke mnemonic berhasil!")
                st.text_area("Mnemonic Phrase yang Ditemukan:", value=recovered_phrase, height=100)

            except ValueError as e:
                st.error(f"Error: {e}")
            except Exception as e:
                st.error(f"Terjadi kesalahan tak terduga: {e}")
        else:
            st.warning("Mohon unggah stego-image dan masukkan kunci acak yang sesuai.")
