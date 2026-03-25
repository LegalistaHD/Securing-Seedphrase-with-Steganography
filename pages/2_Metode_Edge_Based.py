import streamlit as st
from PIL import Image
import io

# Pastikan kita bisa mengimpor dari direktori 'core'
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.bip39_utils import mnemonic_to_binary, binary_to_mnemonic
from core.edge_based import embed_edge, extract_edge
from core.metrics import calculate_psnr, calculate_ssim

st.set_page_config(page_title="Metode Edge-Based")

st.title("Metode 2: Randomized Adaptive Edge-Based")
st.write("Metode ini menyisipkan data hanya pada piksel-piksel di area tepi gambar, yang dideteksi menggunakan algoritma Canny.")

# --- Global Sidebar Logic ---
with st.sidebar:
    st.header("Pengaturan Global")
    if 'shared_cover_image' in st.session_state:
        st.success("Citra Cover Tersedia")
        st.image(st.session_state['shared_cover_image'], caption="Cover Image (Global)", use_container_width=True)
    else:
        st.warning("Belum ada gambar.")
        uploaded_global = st.file_uploader("Unggah Citra Cover", type=["png"], key="edge_global_upload")
        if uploaded_global:
            st.session_state['shared_cover_image'] = Image.open(uploaded_global).convert("RGB")
            st.rerun()

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
    st.subheader("Citra Penampung")
    if 'shared_cover_image' in st.session_state:
        cover_image = st.session_state['shared_cover_image']
        st.image(cover_image, caption="Citra Penampung Asli (Dari Global State)")
    else:
        st.info("Silakan unggah gambar di sidebar atau di sini.")
        uploaded_cover_edge = st.file_uploader("Unggah Citra Penampung", type=["png"], key="cover_edge")
        if uploaded_cover_edge:
            cover_image = Image.open(uploaded_cover_edge).convert("RGB")
            st.session_state['shared_cover_image'] = cover_image
            st.rerun()
        else:
            cover_image = None

    st.subheader("Data untuk Disisipkan")
    if 'default_phrase_edge' not in st.session_state:
        st.session_state.default_phrase_edge = "cube volume sleep globe color erosion mountain print below ugly section update"
    
    phrase_input_edge = st.text_area(
        "Mnemonic Phrase (12 kata):",
        key="phrase_edge",
        value=st.session_state.default_phrase_edge,
        height=100
    )
    seed_key_embed_edge = st.text_input("Kunci Acak (Seed Key) untuk Penyisipan:", value="kunci_rahasia_456")

    if st.button("Mulai Proses Penyisipan (Edge-Based)", type="primary"):
        if cover_image and phrase_input_edge and seed_key_embed_edge:
            try:
                # 1. Konversi mnemonic ke biner
                binary_message = mnemonic_to_binary(phrase_input_edge)
                st.info(f"Mnemonic diubah menjadi {len(binary_message)} bit biner.")

                # 3. Lakukan embedding
                with st.spinner("Mendeteksi tepi dan menyisipkan pesan..."):
                    stego_image, coords, edge_map = embed_edge(cover_image, binary_message, seed_key_embed_edge)
                
                st.success("Penyisipan pesan berhasil!")
                
                # 4. Hitung metrik dan siapkan gambar visualisasi
                with st.spinner("Menghitung PSNR, SSIM, dan membuat peta visualisasi..."):
                    psnr_val = calculate_psnr(cover_image, stego_image)
                    ssim_val = calculate_ssim(cover_image, stego_image)
                    diff_map = create_diff_map(cover_image.size, coords)
                
                st.subheader("Hasil Visualisasi dan Metrik")

                st.image(edge_map, caption="1. Peta Tepi Canny (Potensi Lokasi)")
                st.image(diff_map, caption="2. Peta Piksel yang Dimodifikasi")
                st.image(stego_image, caption="3. Citra Hasil (Stego-Image)")

                st.markdown("---")
                st.subheader("Metrik Kualitas")
                st.metric("PSNR (Peak Signal-to-Noise Ratio)", f"{psnr_val:.2f} dB")
                st.metric("SSIM (Structural Similarity)", f"{ssim_val:.4f}")
                
                with st.expander("Penjelasan Metrik Kualitas (Klik untuk detail)"):
                    st.markdown("""
                    **1. PSNR (Peak Signal-to-Noise Ratio)**
                    *   Semakin tinggi nilai (dB), semakin baik. Mengindikasikan tingkat distorsi yang rendah.
                    
                    **2. SSIM (Structural Similarity Index)**
                    *   Nilai mendekati 1.0 mengindikasikan kemiripan struktural yang tinggi dengan citra asli.
                    """)

                # 5. Sediakan tombol download
                st.download_button(
                    label="Unduh Stego-Image (PNG)",
                    data=image_to_bytes(stego_image),
                    file_name="stego_edge_based.png",
                    mime="image/png"
                )

            except ValueError as e:
                st.error(f"Error: {e}")
            except Exception as e:
                st.error(f"Terjadi kesalahan tak terduga: {e}")
        else:
            st.warning("Mohon pastikan gambar tersedia, masukkan mnemonic, dan sediakan kunci acak.")

# --- EXTRACTING SECTION ---
st.header("2. Ekstrak Pesan (Extract)")
with st.container(border=True):
    st.info("Untuk metode ini, ekstraksi memerlukan **Gambar Asli** dan **Stego-Image**.")
    
    uploaded_stego_edge = st.file_uploader("1. Unggah Stego-Image", type=["png"], key="stego_uploader_edge")
    if uploaded_stego_edge:
        st.image(uploaded_stego_edge, caption="Stego-Image yang Diunggah")

    uploaded_original_edge = st.file_uploader("2. Unggah Citra Penampung Asli", type=["png"], key="original_uploader_edge")
    if uploaded_original_edge:
        st.image(uploaded_original_edge, caption="Citra Asli Referensi")

    st.subheader("Parameter untuk Ekstraksi")
    msg_len_edge = st.number_input("Panjang Pesan (jumlah bit):", value=132, disabled=True, key="msg_len_edge")
    seed_key_extract_edge = st.text_input("Kunci Acak (Seed Key) yang sama:", value="kunci_rahasia_456", key="seed_extract_edge")

    if st.button("Mulai Proses Ekstraksi (Edge-Based)", type="primary"):
        if uploaded_stego_edge and uploaded_original_edge and seed_key_extract_edge:
            try:
                # 1. Buka kedua gambar
                stego_image = Image.open(uploaded_stego_edge)
                original_image = Image.open(uploaded_original_edge)

                # 2. Lakukan ekstraksi
                with st.spinner("Mengekstrak pesan dari gambar..."):
                    extracted_binary = extract_edge(stego_image, original_image, msg_len_edge, seed_key_extract_edge)
                
                st.info(f"Berhasil mengekstrak {len(extracted_binary)} bit pesan.")

                # 3. Konversi biner ke mnemonic
                recovered_phrase = binary_to_mnemonic(extracted_binary)

                # 4. Tampilkan hasil
                st.success("Ekstraksi dan konversi ke mnemonic berhasil!")
                st.text_area("Mnemonic Phrase yang Ditemukan:", value=recovered_phrase, height=100, key="recovered_phrase_edge")

            except ValueError as e:
                st.error(f"Error: {e}")
            except Exception as e:
                st.error(f"Terjadi kesalahan tak terduga: {e}")
        else:
            st.warning("Mohon unggah Stego-Image dan Citra Asli, serta masukkan kunci acak yang sesuai.")
