import streamlit as st
from PIL import Image
import io

# Pastikan kita bisa mengimpor dari direktori 'core'
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.bip39_utils import mnemonic_to_binary
from core.lsb_random import embed as embed_lsb
from core.edge_based import embed_edge
from core.metrics import calculate_psnr, calculate_ssim

st.set_page_config(page_title="Perbandingan Metode")

st.title("Perbandingan Kinerja Metode Steganografi")
st.write("Halaman ini memungkinkan Anda untuk menyisipkan pesan yang sama ke dalam gambar yang sama menggunakan kedua metode secara bersamaan untuk perbandingan langsung.")

# --- Global Sidebar Logic ---
with st.sidebar:
    st.header("Pengaturan Global")
    if 'shared_cover_image' in st.session_state:
        st.success("Citra Cover Tersedia")
        st.image(st.session_state['shared_cover_image'], caption="Cover Image (Global)", use_container_width=True)
    else:
        st.warning("Belum ada gambar.")
        uploaded_global = st.file_uploader("Unggah Citra Cover", type=["png"], key="compare_global_upload")
        if uploaded_global:
            st.session_state['shared_cover_image'] = Image.open(uploaded_global).convert("RGB")
            st.rerun()

# --- Helper Functions ---
def create_diff_map(image_size, coordinates):
    """Membuat gambar hitam dengan titik putih di lokasi piksel yang dimodifikasi."""
    diff_map = Image.new('RGB', image_size, 'black')
    pixels = diff_map.load()
    if coordinates:
        for x, y in coordinates:
            pixels[x, y] = (255, 255, 255) # White
    return diff_map

# --- UI Setup ---
with st.container(border=True):
    st.subheader("Citra Penampung")
    if 'shared_cover_image' in st.session_state:
        cover_image = st.session_state['shared_cover_image']
        st.image(cover_image, caption="Citra Penampung Asli (Dari Global State)")
    else:
        st.warning("Silakan unggah gambar di sidebar.")
        cover_image = None
    
    st.subheader("Data untuk Disisipkan")
    if 'default_phrase_compare' not in st.session_state:
        st.session_state.default_phrase_compare = "cube volume sleep globe color erosion mountain print below ugly section update"
    
    phrase_input = st.text_area(
        "Mnemonic Phrase (12 kata):",
        key="phrase_compare",
        value=st.session_state.default_phrase_compare,
        height=100
    )
    seed_key = st.text_input("Kunci Acak (Seed Key) untuk kedua metode:", value="kunci_rahasia_compare")

if st.button("Bandingkan Kedua Metode", type="primary", use_container_width=True):
    if cover_image and phrase_input and seed_key:
        try:
            # --- Persiapan ---
            binary_message = mnemonic_to_binary(phrase_input)
            st.info(f"Memulai perbandingan dengan pesan {len(binary_message)} bit...")

            # --- Proses Metode 1: LSB Random ---
            with st.spinner("Metode 1 (LSB Random): Menyisipkan pesan..."):
                stego_lsb, coords_lsb = embed_lsb(cover_image, binary_message, seed_key)
                psnr_lsb = calculate_psnr(cover_image, stego_lsb)
                ssim_lsb = calculate_ssim(cover_image, stego_lsb)
                diff_lsb = create_diff_map(cover_image.size, coords_lsb)

            # --- Proses Metode 2: Edge-Based ---
            with st.spinner("Metode 2 (Edge-Based): Mendeteksi tepi dan menyisipkan pesan..."):
                stego_edge, coords_edge, edge_map = embed_edge(cover_image, binary_message, seed_key)
                psnr_edge = calculate_psnr(cover_image, stego_edge)
                ssim_edge = calculate_ssim(cover_image, stego_edge)
                diff_edge = create_diff_map(cover_image.size, coords_edge)

            st.success("Perbandingan selesai!")
            st.markdown("---")

            # --- Tampilkan Hasil Perbandingan ---
            st.header("Metode 1: LSB Random")
            st.image(stego_lsb, caption="Stego-Image (LSB Random)")
            st.metric("PSNR", f"{psnr_lsb:.2f} dB")
            st.metric("SSIM", f"{ssim_lsb:.4f}")
            st.image(diff_lsb, caption="Peta Modifikasi (LSB Random)")
            st.caption("Piksel yang diubah tersebar acak di seluruh gambar.")

            st.markdown("---")

            st.header("Metode 2: Edge-Based")
            st.image(stego_edge, caption="Stego-Image (Edge-Based)")
            st.metric("PSNR", f"{psnr_edge:.2f} dB")
            st.metric("SSIM", f"{ssim_edge:.4f}")
            st.image(edge_map, caption="Peta Tepi Canny (Potensi Lokasi)")
            st.image(diff_edge, caption="Peta Modifikasi (Piksel Terpilih)")
            st.caption("Piksel yang diubah dipilih secara acak hanya dari area tepi.")

            # --- Tabel Ringkasan (Thesis Defense Enhancement) ---
            st.markdown("---")
            st.subheader("Ringkasan Kuantitatif")
            
            summary_data = [
                {"Metode": "LSB Random", "PSNR (dB)": f"{psnr_lsb:.2f}", "SSIM": f"{ssim_lsb:.4f}", "Distribusi": "Acak Uniform"},
                {"Metode": "Edge-Based", "PSNR (dB)": f"{psnr_edge:.2f}", "SSIM": f"{ssim_edge:.4f}", "Distribusi": "Adaptif (Tepi)"}
            ]
            st.table(summary_data)
            
            st.info("""
            **Analisis Singkat:**
            Metode Edge-Based biasanya menghasilkan PSNR yang sedikit lebih rendah atau setara, namun secara visual (SSIM) dan keamanan perseptual lebih unggul karena perubahan disembunyikan di area yang kompleks (tepi) di mana mata manusia kurang sensitif terhadap perubahan noise.
            """)

        except ValueError as e:
            st.error(f"Error: {e}")
        except Exception as e:
            st.error(f"Terjadi kesalahan tak terduga: {e}")
    else:
        st.warning("Mohon pastikan gambar tersedia, masukkan mnemonic, dan sediakan kunci acak.")
