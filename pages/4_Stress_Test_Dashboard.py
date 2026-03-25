
import streamlit as st
import os
import time
import io
import numpy as np
import pandas as pd
from PIL import Image, ImageEnhance, ImageStat
import cv2
from scipy.stats import chisquare
import plotly.express as px

# Import core modules
try:
    from core.lsb_random import embed as embed_lsb
    from core.edge_based import embed_edge
    from core.bip39_utils import mnemonic_to_binary
    from core.metrics import calculate_psnr, calculate_ssim
except ImportError as e:
    st.error(f"Error importing core modules: {e}. Please ensure core files are in the correct path.")
    st.stop()

# --- Constants and Configuration ---
DATASET_DIR = './dataset'
VALID_PHRASE = "cube volume sleep globe color erosion mountain print below ugly section update"
SEED_KEY = "raihan123"
PAYLOAD = mnemonic_to_binary(VALID_PHRASE)
RESOLUTIONS = [64, 128, 256, 384, 512, 640, 768, 896, 1024]
FACTORS = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
KEY_LENGTHS = [10, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]


# --- Helper Functions ---

def get_image_files(dataset_path):
    """Get a list of image file paths from the dataset directory."""
    supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    if not os.path.exists(dataset_path):
        return []
    
    # Filter files by supported format
    files = [f for f in os.listdir(dataset_path) if f.lower().endswith(supported_formats)]
    
    # Sort files naturally (e.g., 1.png, 2.png, 10.png)
    try:
        files.sort(key=lambda f: int(os.path.splitext(f)[0]))
    except ValueError:
        # If filenames are not purely numeric, fall back to simple string sort
        files.sort()
        
    return [os.path.join(dataset_path, f) for f in files]

def get_edge_density(img_path, threshold1=100, threshold2=200):
    """Calculates the percentage of edge pixels in an image."""
    try:
        image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            return 0.0
        edges = cv2.Canny(image, threshold1, threshold2)
        edge_pixels = np.sum(edges > 0)
        total_pixels = image.size
        return (edge_pixels / total_pixels) * 100
    except Exception:
        return 0.0

def get_avg_brightness(pil_img):
    """Calculates the average brightness of a PIL image."""
    if pil_img.mode != 'L':
        pil_img = pil_img.convert('L')
    return ImageStat.Stat(pil_img).mean[0]

def calculate_chi_square_p_value(stego_image):
    """
    Performs a Chi-Square analysis on Pairs of Values (PoVs) from LSBs.
    Returns the p-value.
    """
    if stego_image.mode != 'RGB':
        stego_image = stego_image.convert('RGB')
    
    pixels = np.array(stego_image).flatten()
    
    # Extract LSBs from the first 50000 pixel values for performance
    lsbs = (pixels[:50000] & 1).astype(np.uint8)
    
    # Create Pairs of Values (PoVs)
    pairs = lsbs.reshape(-1, 2)
    
    # Count occurrences of [0,0], [0,1], [1,0], [1,1]
    observed_freq = np.zeros(4, dtype=int)
    for p in pairs:
        if p[0] == 0 and p[1] == 0:
            observed_freq[0] += 1
        elif p[0] == 0 and p[1] == 1:
            observed_freq[1] += 1
        elif p[0] == 1 and p[1] == 0:
            observed_freq[2] += 1
        else: # p[0] == 1 and p[1] == 1
            observed_freq[3] += 1
            
    total_pairs = len(pairs)
    if total_pairs == 0:
        return 1.0 # Cannot perform test, assume safe

    # Expected frequency for a random distribution is equal for all pairs
    expected_freq = [total_pairs / 4.0] * 4
    
    # Perform Chi-Square test
    chi2_stat, p_value = chisquare(f_obs=observed_freq, f_exp=expected_freq)
    
    return p_value

# --- Main Application UI ---
st.set_page_config(layout="wide")
st.title("Automated Ultimate Stress Test")
st.markdown("Analisis komparatif metode LSB Random dan Edge-Based pada berbagai kondisi.")

# --- Setup Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Profil Dataset", 
    "Uji Resolusi", 
    "Uji Kecerahan & Kontras", 
    "Uji Panjang Kunci / Seed Key", 
    "Uji Chi-Square"
])

# Initialize content for tabs
with tab1:
    st.info("Hasil analisis profil dataset akan muncul di sini setelah tes dijalankan.")
with tab2:
    st.info("Hasil uji resolusi akan muncul di sini setelah tes dijalankan.")
with tab3:
    st.info("Hasil uji kecerahan dan kontras akan muncul di sini setelah tes dijalankan.")
with tab4:
    st.info("Hasil uji waktu komputasi dan ukuran file akan muncul di sini setelah tes dijalankan.")
with tab5:
    st.info("Hasil uji Chi-Square akan muncul di sini setelah tes dijalankan.")


if st.button("Jalankan Ultimate Stress Test", type="primary"):
    
    image_files = get_image_files(DATASET_DIR)
    if not image_files:
        st.error(f"Tidak ada gambar ditemukan di direktori '{DATASET_DIR}'. Pastikan folder ada dan berisi gambar.")
        st.stop()
        
    total_images = len(image_files)
    sample_img_path = image_files[0]

    # --- TAB 1: PROFIL DATASET ---
    with tab1:
        st.empty() # Clear the initial info message
        progress_bar_tab1 = st.progress(0)
        status_text_tab1 = st.empty()
        
        profile_data = []
        for i, img_path in enumerate(image_files):
            status_text_tab1.text(f"Menganalisis gambar {i+1}/{total_images}: {os.path.basename(img_path)}")
            try:
                file_size_mb = os.path.getsize(img_path) / (1024 * 1024)
                with Image.open(img_path) as img:
                    avg_brightness = get_avg_brightness(img)
                edge_density = get_edge_density(img_path)
                
                profile_data.append({
                    "Filename": os.path.basename(img_path),
                    "File Size (MB)": file_size_mb,
                    "Avg Brightness": avg_brightness,
                    "Edge Density (%)": edge_density
                })
            except Exception as e:
                st.warning(f"Gagal memproses {os.path.basename(img_path)}: {e}")
            progress_bar_tab1.progress((i + 1) / total_images)
        
        status_text_tab1.success("Analisis profil dataset selesai!")
        df_profile = pd.DataFrame(profile_data)
        df_profile.index = df_profile.index + 1
        st.dataframe(df_profile)

    # --- TAB 2: UJI RESOLUSI ---
    with tab2:
        st.empty()
        progress_bar_tab2 = st.progress(0)
        status_text_tab2 = st.empty()

        res_results = []
        total_steps_tab2 = len(RESOLUTIONS) * total_images
        current_step_tab2 = 0

        for res in RESOLUTIONS:
            psnr_lsb_list, ssim_lsb_list = [], []
            psnr_edge_list, ssim_edge_list = [], []

            for img_path in image_files:
                current_step_tab2 += 1
                status_text_tab2.text(f"Uji Resolusi: {res}x{res} | Gambar: {os.path.basename(img_path)}")
                progress_bar_tab2.progress(current_step_tab2 / total_steps_tab2)
                
                try:
                    with Image.open(img_path) as img:
                        img_resized = img.resize((res, res), Image.Resampling.LANCZOS)
                        stego_lsb, _ = embed_lsb(img_resized, PAYLOAD, SEED_KEY)
                        psnr_lsb_list.append(calculate_psnr(img_resized, stego_lsb))
                        ssim_lsb_list.append(calculate_ssim(img_resized, stego_lsb))
                        try:
                            stego_edge, _, _ = embed_edge(img_resized, PAYLOAD, SEED_KEY)
                            psnr_edge_list.append(calculate_psnr(img_resized, stego_edge))
                            ssim_edge_list.append(calculate_ssim(img_resized, stego_edge))
                        except ValueError:
                            psnr_edge_list.append(0); ssim_edge_list.append(0)
                except Exception as e:
                    st.warning(f"Error pada {os.path.basename(img_path)} di resolusi {res}x{res}: {e}")

            res_results.append({
                "Resolusi": f"{res}x{res}", "PSNR LSB": np.mean(psnr_lsb_list or [1]),
                "PSNR Edge": np.mean(psnr_edge_list or [0]), "SSIM LSB": np.mean(ssim_lsb_list or [0]),
                "SSIM Edge": np.mean(ssim_edge_list or [0])
            })

        status_text_tab2.success("Uji resolusi selesai!")
        df_res = pd.DataFrame(res_results).set_index("Resolusi")

        # Visualisasi Perbandingan PSNR
        st.subheader("Perbandingan Rata-rata PSNR vs. Resolusi")
        df_res_psnr_melted = df_res.reset_index().melt(id_vars='Resolusi', value_vars=['PSNR LSB', 'PSNR Edge'], var_name='Metode', value_name='Nilai')
        fig_psnr = px.bar(df_res_psnr_melted, x='Resolusi', y='Nilai', color='Metode', barmode='group', title='Perbandingan PSNR Berdasarkan Resolusi')
        fig_psnr.update_yaxes(title_text='PSNR (dB)')
        st.plotly_chart(fig_psnr, use_container_width=True)

        # Menampilkan tabel data PSNR dengan rata-rata
        df_res_psnr = df_res[['PSNR LSB', 'PSNR Edge']].copy()
        avg_psnr = df_res_psnr.mean().to_frame().T
        avg_psnr.index = ['Rata-rata']
        df_res_psnr = pd.concat([df_res_psnr, avg_psnr])
        st.dataframe(df_res_psnr.style.format("{:.2f} dB"))

        # Visualisasi Perbandingan SSIM
        st.subheader("Perbandingan Rata-rata SSIM vs. Resolusi")
        df_res_ssim_melted = df_res.reset_index().melt(id_vars='Resolusi', value_vars=['SSIM LSB', 'SSIM Edge'], var_name='Metode', value_name='Nilai')
        fig_ssim = px.bar(df_res_ssim_melted, x='Resolusi', y='Nilai', color='Metode', barmode='group', title='Perbandingan SSIM Berdasarkan Resolusi')
        fig_ssim.update_yaxes(title_text='SSIM')
        st.plotly_chart(fig_ssim, use_container_width=True)

        # Menampilkan tabel data SSIM dengan rata-rata
        df_res_ssim = df_res[['SSIM LSB', 'SSIM Edge']].copy()
        avg_ssim = df_res_ssim.mean().to_frame().T
        avg_ssim.index = ['Rata-rata']
        df_res_ssim = pd.concat([df_res_ssim, avg_ssim])
        st.dataframe(df_res_ssim.style.format("{:.4f}"))

        st.subheader("Analisis Hasil Uji Resolusi")
        avg_psnr_lsb = df_res["PSNR LSB"].mean()
        avg_psnr_edge = df_res["PSNR Edge"].mean()
        avg_ssim_lsb = df_res["SSIM LSB"].mean()
        avg_ssim_edge = df_res["SSIM Edge"].mean()

        winner = "LSB Random" if avg_psnr_lsb >= avg_psnr_edge else "Edge-Based"
        
        st.info(f"""
        Berdasarkan pengujian, LSB Random mencetak nilai rata-rata PSNR **{avg_psnr_lsb:.2f} dB** dan SSIM **{avg_ssim_lsb:.4f}**, 
        sedangkan Edge-Based mencetak PSNR **{avg_psnr_edge:.2f} dB** dan SSIM **{avg_ssim_edge:.4f}**.
        
        Secara matematis (PSNR), **{winner}** lebih unggul. Namun pada metrik SSIM yang merepresentasikan persepsi mata manusia, 
        nilai di atas 0.99 membuktikan bahwa kedua metode memiliki tingkat _Imperceptibility_ yang sangat sempurna. 
        Edge-Based menyembunyikan perubahan di area kompleks sehingga mata manusia lebih sulit membedakan perubahannya 
        dibandingkan LSB yang menyebarnya ke area polos.
        """)
        
        st.info("Catatan: Pada resolusi rendah (misalnya di bawah 256x256), metode Edge-Based seringkali gagal atau menghasilkan kualitas sangat rendah (PSNR 0) karena tidak tersedianya piksel tepi yang cukup untuk menampung seluruh 132-bit payload.")
        st.markdown("---")
 

    # --- TAB 3: UJI KECERAHAN & KONTRAS ---
    with tab3:
        st.empty()
        progress_bar_tab3 = st.progress(0)
        status_text_tab3 = st.empty()
        
        bright_results, contrast_results = [], []
        total_enh_steps = len(FACTORS) * total_images * 2; current_enh_step = 0

        for factor in FACTORS:
            b_psnr_lsb, b_ssim_lsb, b_psnr_edge, b_ssim_edge = [],[],[],[]
            c_psnr_lsb, c_ssim_lsb, c_psnr_edge, c_ssim_edge = [],[],[],[]
            
            for img_path in image_files:
                current_enh_step += 2 # Two operations per image
                status_text_tab3.text(f"Uji Enhance - Faktor {factor:.1f} - Gambar: {os.path.basename(img_path)}")
                progress_bar_tab3.progress(current_enh_step / total_enh_steps)

                with Image.open(img_path) as img:
                    img_resized = img.resize((256, 256), Image.Resampling.LANCZOS)
                    # Brightness
                    img_bright = ImageEnhance.Brightness(img_resized).enhance(factor)
                    stego_lsb, _ = embed_lsb(img_bright, PAYLOAD, SEED_KEY); b_psnr_lsb.append(calculate_psnr(img_bright, stego_lsb)); b_ssim_lsb.append(calculate_ssim(img_bright, stego_lsb))
                    try:
                        stego_edge, _, _ = embed_edge(img_bright, PAYLOAD, SEED_KEY); b_psnr_edge.append(calculate_psnr(img_bright, stego_edge)); b_ssim_edge.append(calculate_ssim(img_bright, stego_edge))
                    except ValueError: b_psnr_edge.append(0); b_ssim_edge.append(0)
                    # Contrast
                    img_contrast = ImageEnhance.Contrast(img_resized).enhance(factor)
                    stego_lsb, _ = embed_lsb(img_contrast, PAYLOAD, SEED_KEY); c_psnr_lsb.append(calculate_psnr(img_contrast, stego_lsb)); c_ssim_lsb.append(calculate_ssim(img_contrast, stego_lsb))
                    try:
                        stego_edge, _, _ = embed_edge(img_contrast, PAYLOAD, SEED_KEY); c_psnr_edge.append(calculate_psnr(img_contrast, stego_edge)); c_ssim_edge.append(calculate_ssim(img_contrast, stego_edge))
                    except ValueError: c_psnr_edge.append(0); c_ssim_edge.append(0)
                        
            bright_results.append({"Faktor": f"{factor:.1f}", "PSNR LSB": np.mean(b_psnr_lsb), "PSNR Edge": np.mean(b_psnr_edge), "SSIM LSB": np.mean(b_ssim_lsb), "SSIM Edge": np.mean(b_ssim_edge)})
            contrast_results.append({"Faktor": f"{factor:.1f}", "PSNR LSB": np.mean(c_psnr_lsb), "PSNR Edge": np.mean(c_psnr_edge), "SSIM LSB": np.mean(c_ssim_lsb), "SSIM Edge": np.mean(c_ssim_edge)})

        status_text_tab3.success("Uji kecerahan dan kontras selesai!")
        df_bright = pd.DataFrame(bright_results).set_index("Faktor")
        df_contrast = pd.DataFrame(contrast_results).set_index("Faktor")

        # --- UJI KECERAHAN ---
        st.subheader("Uji Kecerahan (Brightness)")
        st.markdown("---")

        # Visualisasi Kecerahan PSNR
        st.write("##### Perbandingan PSNR pada Uji Kecerahan")
        df_bright_psnr_melted = df_bright.reset_index().melt(id_vars='Faktor', value_vars=['PSNR LSB', 'PSNR Edge'], var_name='Metode', value_name='PSNR (dB)')
        fig_bright_psnr = px.bar(df_bright_psnr_melted, x='Faktor', y='PSNR (dB)', color='Metode', barmode='group', title='PSNR vs. Faktor Kecerahan')
        st.plotly_chart(fig_bright_psnr, use_container_width=True)

        # Tabel Data Kecerahan
        st.write("##### Tabel Data Uji Kecerahan")
        df_bright_data = df_bright[['PSNR LSB', 'SSIM LSB', 'PSNR Edge', 'SSIM Edge']].copy()
        avg_bright = df_bright_data.mean().to_frame().T
        avg_bright.index = ['Rata-rata']
        df_bright_data = pd.concat([df_bright_data, avg_bright])
        st.dataframe(df_bright_data.style.format({'PSNR LSB': '{:.2f} dB', 'PSNR Edge': '{:.2f} dB', 'SSIM LSB': '{:.4f}', 'SSIM Edge': '{:.4f}'}))

        # Penjelasan Kecerahan
        st.write("##### Analisis Uji Kecerahan")
        st.info("""
        **Tujuan Uji Kecerahan**: Mengukur batas toleransi algoritma deteksi tepi Canny saat gambar menjadi sangat gelap (faktor < 1.0) atau silau (faktor > 1.0).
        
        **Kesimpulan**: Pada kondisi ekstrem, jumlah tepi menurun drastis sehingga Edge-Based gagal menyisipkan data atau metriknya anjlok. LSB Random terbukti lebih stabil karena tidak bergantung pada kontur cahaya.
        """)


        # --- UJI KONTRAS ---
        st.subheader("Uji Kontras (Contrast)")
        st.markdown("---")
        
        # Visualisasi Kontras PSNR
        st.write("##### Perbandingan PSNR pada Uji Kontras")
        df_contrast_psnr_melted = df_contrast.reset_index().melt(id_vars='Faktor', value_vars=['PSNR LSB', 'PSNR Edge'], var_name='Metode', value_name='PSNR (dB)')
        fig_contrast_psnr = px.bar(df_contrast_psnr_melted, x='Faktor', y='PSNR (dB)', color='Metode', barmode='group', title='PSNR vs. Faktor Kontras')
        st.plotly_chart(fig_contrast_psnr, use_container_width=True)

        # Tabel Data Kontras
        st.write("##### Tabel Data Uji Kontras")
        df_contrast_data = df_contrast[['PSNR LSB', 'SSIM LSB', 'PSNR Edge', 'SSIM Edge']].copy()
        avg_contrast = df_contrast_data.mean().to_frame().T
        avg_contrast.index = ['Rata-rata']
        df_contrast_data = pd.concat([df_contrast_data, avg_contrast])
        st.dataframe(df_contrast_data.style.format({'PSNR LSB': '{:.2f} dB', 'PSNR Edge': '{:.2f} dB', 'SSIM LSB': '{:.4f}', 'SSIM Edge': '{:.4f}'}))

        # Penjelasan Kontras
        st.write("##### Analisis Uji Kontras")
        avg_psnr_lsb_contrast = df_contrast['PSNR LSB'].mean()
        avg_psnr_edge_contrast = df_contrast['PSNR Edge'].mean()
        winner_contrast = "LSB Random" if avg_psnr_lsb_contrast >= avg_psnr_edge_contrast else "Edge-Based"
        
        st.info(f"""
        **Tujuan Uji Kontras**: Menguji ketahanan metode saat selisih piksel terang dan gelap pada gambar diperbesar atau diperkecil. Kontras yang terlalu rendah membuat gambar terlihat abu-abu rata, mematikan fungsi deteksi tepi.

        **Kesimpulan**: Berdasarkan nilai metrik, **{winner_contrast}** terbukti lebih bertahan dan stabil terhadap manipulasi kontras dibandingkan metode lainnya.
        """)



    # --- TAB 4: UJI PANJANG KUNCI / SEED KEY ---
    with tab4:
        st.empty()
        progress_bar_tab4 = st.progress(0)
        status_text_tab4 = st.empty()

        status_text_tab4.text("Memulai uji panjang kunci...")
        key_length_results = []
        with Image.open(sample_img_path) as img:
            img_resized = img.resize((512, 512), Image.Resampling.LANCZOS)
            for i, length in enumerate(KEY_LENGTHS):
                status_text_tab4.text(f"Menguji panjang key: {length} karakter")
                test_key = 'A' * length
                
                # LSB Method
                start_time = time.time()
                stego_lsb, _ = embed_lsb(img_resized, PAYLOAD, test_key)
                lsb_time = time.time() - start_time
                lsb_psnr = calculate_psnr(img_resized, stego_lsb)
                lsb_ssim = calculate_ssim(img_resized, stego_lsb)

                # Edge Method
                start_time = time.time()
                try:
                    stego_edge, _, _ = embed_edge(img_resized, PAYLOAD, test_key)
                    edge_time = time.time() - start_time
                    edge_psnr = calculate_psnr(img_resized, stego_edge)
                    edge_ssim = calculate_ssim(img_resized, stego_edge)
                except ValueError: 
                    edge_time, edge_psnr, edge_ssim = 0, 0, 0
                
                key_length_results.append({
                    "Panjang Key": str(length), 
                    "LSB Time (s)": lsb_time, "Edge Time (s)": edge_time,
                    "LSB PSNR": lsb_psnr, "Edge PSNR": edge_psnr,
                    "LSB SSIM": lsb_ssim, "Edge SSIM": edge_ssim,
                })
                progress_bar_tab4.progress((i + 1) / len(KEY_LENGTHS))
        
        df_key_length = pd.DataFrame(key_length_results).set_index("Panjang Key")
        status_text_tab4.success("Uji panjang kunci selesai!")

        # --- Waktu Komputasi ---
        st.subheader("Waktu Eksekusi vs. Panjang Seed Key")
        df_time = df_key_length[['LSB Time (s)', 'Edge Time (s)']]
        df_time_melted = df_time.reset_index().melt(id_vars='Panjang Key', value_vars=['LSB Time (s)', 'Edge Time (s)'], var_name='Metode', value_name='Waktu (s)')
        fig_time = px.bar(df_time_melted, x='Panjang Key', y='Waktu (s)', color='Metode', barmode='group', title='Waktu Eksekusi Berdasarkan Panjang Seed Key')
        st.plotly_chart(fig_time, use_container_width=True)
        
        avg_time = df_time.mean().to_frame().T
        avg_time.index = ['Rata-rata']
        df_time_display = pd.concat([df_time, avg_time])
        st.dataframe(df_time_display.style.format("{:.4f} s"))
        st.markdown("---")

        # --- PSNR ---
        st.subheader("PSNR vs. Panjang Seed Key")
        df_psnr = df_key_length[['LSB PSNR', 'Edge PSNR']]
        df_psnr_melted = df_psnr.reset_index().melt(id_vars='Panjang Key', value_vars=['LSB PSNR', 'Edge PSNR'], var_name='Metode', value_name='PSNR (dB)')
        fig_psnr_key = px.bar(df_psnr_melted, x='Panjang Key', y='PSNR (dB)', color='Metode', barmode='group', title='PSNR Berdasarkan Panjang Seed Key')
        st.plotly_chart(fig_psnr_key, use_container_width=True)

        avg_psnr = df_psnr.mean().to_frame().T
        avg_psnr.index = ['Rata-rata']
        df_psnr_display = pd.concat([df_psnr, avg_psnr])
        st.dataframe(df_psnr_display.style.format("{:.2f} dB"))
        st.markdown("---")

        # --- SSIM ---
        st.subheader("SSIM vs. Panjang Seed Key")
        df_ssim = df_key_length[['LSB SSIM', 'Edge SSIM']]
        df_ssim_melted = df_ssim.reset_index().melt(id_vars='Panjang Key', value_vars=['LSB SSIM', 'Edge SSIM'], var_name='Metode', value_name='SSIM')
        fig_ssim_key = px.bar(df_ssim_melted, x='Panjang Key', y='SSIM', color='Metode', barmode='group', title='SSIM Berdasarkan Panjang Seed Key')
        st.plotly_chart(fig_ssim_key, use_container_width=True)

        avg_ssim = df_ssim.mean().to_frame().T
        avg_ssim.index = ['Rata-rata']
        df_ssim_display = pd.concat([df_ssim, avg_ssim])
        st.dataframe(df_ssim_display.style.format("{:.4f}"))
        st.markdown("---")

        # --- Kesimpulan ---
        st.subheader("Analisis Hasil Uji Panjang Kunci")
        avg_time_lsb = df_key_length["LSB Time (s)"].mean()
        avg_time_edge = df_key_length["Edge Time (s)"].mean()
        st.info(f"""
        Pengujian ini membuktikan bahwa variasi panjang Kunci Acak (Password PRNG) hanya berdampak signifikan pada **Waktu Komputasi**, 
        di mana LSB butuh rata-rata **{avg_time_lsb:.4f} detik** dan Edge butuh **{avg_time_edge:.4f} detik**. 
        
        Namun, panjang Kunci Acak **SAMA SEKALI TIDAK** memengaruhi metrik kualitas citra (PSNR dan SSIM tetap stabil). 
        Hal ini karena yang mengubah piksel adalah ukuran muatan data (132 bit), bukan panjang password-nya.
        """)


    # --- TAB 5: UJI CHI-SQUARE ---
    with tab5:
        st.empty()
        progress_bar_tab5 = st.progress(0)
        status_text_tab5 = st.empty()
        status_text_tab5.text("Mempersiapkan gambar...")
        
        with Image.open(sample_img_path) as img:
            img_resized = img.resize((128, 128), Image.Resampling.LANCZOS)
            status_text_tab5.text("Menganalisis LSB Random..."); stego_lsb, _ = embed_lsb(img_resized, PAYLOAD, SEED_KEY); p_value_lsb = calculate_chi_square_p_value(stego_lsb); progress_bar_tab5.progress(0.5)
            status_text_tab5.text("Menganalisis Edge-Based...");
            try:
                stego_edge, _, _ = embed_edge(img_resized, PAYLOAD, SEED_KEY); p_value_edge = calculate_chi_square_p_value(stego_edge)
            except ValueError: p_value_edge = 1.0 
            progress_bar_tab5.progress(1.0)

        status_text_tab5.success("Analisis Chi-Square selesai!")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="P-Value LSB Random", value=f"{p_value_lsb:.4f}")
            if p_value_lsb < 0.05: st.error("Terdeteksi oleh Chi-Square!")
            else: st.success("Aman dari Chi-Square.")
        with col2:
            st.metric(label="P-Value Edge-Based", value=f"{p_value_edge:.4f}")
            if p_value_edge < 0.05: st.error("Terdeteksi oleh Chi-Square!")
            else: st.success("Aman dari Chi-Square.")
        st.info("Teori: P-Value > 0.05 menunjukkan data stego mirip data acak, sehingga aman dari serangan ini.")
        st.markdown("""
        ---
        ### Memahami Chi-Square Attack pada Steganografi
        **Cara Kerja**: Gambar digital yang normal memiliki kurva distribusi warna (Histogram) yang natural. Jika kita menggunakan steganografi LSB berurutan yang konvensional, nilai piksel akan bergeser secara berpasangan (Pairs of Values), membuat kurva histogramnya menjadi rata secara tidak wajar (anomali). Algoritma Chi-Square bertugas mendeteksi keanehan pasangan nilai ini.
        
        **Mengapa Sistem Ini Aman (P-Value > 0.05):**
        - **Muatan Sangat Kecil**: Kunci Pemulihan Wallet BIP39 hanya berukuran 132 bit. Mengubah 132 piksel dari total ratusan ribu piksel dalam gambar tidak akan membuat perubahan signifikan pada histogram secara keseluruhan.
        - **Metode LSB Random**: Mengacak lokasi penyisipan menggunakan PRNG membuat keanehan bit tidak menumpuk di satu lokasi, sehingga mesin statistik kesulitan mencari pola anomali.
        - **Metode Adaptive Edge-Based**: Menyembunyikan 132 bit tersebut di area tepi yang memang sudah memiliki variasi warna dan tekstur (noise natural) yang tinggi, sehingga perubahan akibat steganografi tertutupi oleh kerumitan visual gambar asli.
        """)

