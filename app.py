import streamlit as st
from core.bip39_utils import mnemonic_to_binary, binary_to_mnemonic
from PIL import Image

st.set_page_config(page_title="BIP39 Steganography Prototype", layout="centered")

st.title("Analisis Komparasi Metode Steganografi untuk Kunci Pemulihan Wallet")
st.subheader("Modul 1: Utilitas Konversi BIP39")
st.markdown("---")

st.write(
    "Ini adalah modul dasar untuk menguji konversi antara 12-kata Mnemonic Phrase (BIP39) "
    "dan representasi Entropi Binernya (128-bit). Modul ini akan menjadi dasar untuk "
    "penyisipan data ke dalam citra."
)

# --- Global Sidebar for Image Upload ---
with st.sidebar:
    st.header("Pengaturan")
    st.info("Unggah gambar di sini untuk digunakan di semua halaman.")
    
    if 'shared_cover_image' in st.session_state:
        st.success("Citra Cover Tersedia")
        st.image(st.session_state['shared_cover_image'], caption="Cover Image (Global)", use_container_width=True)
        if st.button("Hapus Gambar"):
            del st.session_state['shared_cover_image']
            st.rerun()
    else:
        uploaded_global = st.file_uploader("Unggah Citra Cover", type=["png"], key="global_upload")
        if uploaded_global:
            st.session_state['shared_cover_image'] = Image.open(uploaded_global).convert("RGB")
            st.rerun()

st.header("Mnemonic ➞ Biner")

# Generate a default mnemonic for ease of testing
default_phrase = "cube volume sleep globe color erosion mountain print below ugly section update"
phrase_input = st.text_area(
    "Masukkan 12-kata Mnemonic Phrase:",
    value=default_phrase,
    height=100,
    help="Pisahkan setiap kata dengan spasi."
)

if st.button("Konversi ke Biner"):
    try:
        binary_output = mnemonic_to_binary(phrase_input)
        st.success("Konversi Berhasil!")
        st.text_area(
            "Hasil Entropi Biner (132-bit):",
            value=binary_output,
            height=150
        )
        st.info(f"Panjang string biner: **{len(binary_output)} bit** (12 kata x 11 bit)")
    except ValueError as e:
        st.error(f"Error: {e}")

st.markdown("---")

st.header("Biner ➞ Mnemonic")

# A default binary string corresponding to the default phrase for testing
default_binary = "001101010111111010111011001011001011000110100010110110101001100101100100001001010101011000010100110111011000001100001010111101110000" # Added 4 bits to make 132
binary_input = st.text_area(
    "Masukkan 132-bit Entropi Biner:",
    value=default_binary,
    height=150
)

if st.button("Konversi ke Mnemonic"):
    try:
        mnemonic_output = binary_to_mnemonic(binary_input)
        st.success("Konversi Berhasil!")
        st.text_area(
            "Hasil Mnemonic Phrase:",
            value=mnemonic_output.replace(' ', '\n')
        )
    except ValueError as e:
        st.error(f"Error: {e}")

st.markdown("---")
st.info("Langkah selanjutnya: Membangun modul untuk metode steganografi LSB-Random dan Edge-Based.")
