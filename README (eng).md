# Securing Seedphrase with Steganography

A web-based prototype application (Streamlit) to secure a BIP39 standard Cryptocurrency Wallet Recovery Key (Seed Phrase) into a digital image using steganography techniques. This application evaluates and compares the performance of two methods: **LSB Random** and **Randomized Adaptive Edge-Based**.

---

## 📁 Directory Structure

Based on this repository, here is the structure of the available files and folders:

* `app.py`          : The main file to run the Streamlit application.
* `requirements.txt`: A list of required Python libraries.
* `core/`           : Core modules for steganography algorithms, BIP39 conversion, and metrics evaluation.
* `pages/`          : Web interface (UI) modules for each menu functionality.
* `dataset/`        : Directory to store testing images (Cover Images).
* `assets/`         : Directory to store static assets supporting the application.
* `assets.zip`      : Compressed backup file for assets.

---

## ⚙️ Prerequisites

Before running the application, make sure your computer has the following installed:
1. Python version 3.9 or newer.
2. Pip (Python Package Installer).

---

## 🚀 Installation Instructions

Follow the steps below to install and run the application locally:

### Step 1: Extract Files
If you received this project as a `.zip` file, extract all its contents into a single folder on your computer.

### Step 2: Open Terminal / Command Prompt
Navigate to the extracted folder directory. Right-click on an empty area inside the folder and select "Open in Terminal". 
(Windows alternative: Type `cmd` in the folder's address bar and press Enter).

### Step 3: Create a Virtual Environment (Highly Recommended)
To prevent version conflicts between libraries on your system, create an isolated environment by typing the following command in the terminal:

python -m venv env

### Step 4: Activate the Virtual Environment
Activate the newly created environment.
* For Windows users, type the command:
  env\Scripts\activate

* For Linux / Mac OS users, type the command:
  source env/bin/activate

### Step 5: Install Dependencies
Once the virtual environment is active (usually indicated by `(env)` at the beginning of the terminal line), install all required libraries by running the following command:

pip install -r requirements.txt

---

## ▶️ Running the Application

After the installation process is complete, you can directly run the web application using the following command in your terminal:

streamlit run app.py

The application will automatically open in your default web browser via a local address (typically at http://localhost:8501).

---

## 💡 Key Features

1. BIP39 Conversion Module: Efficiently translates 12 Mnemonic words into 132-bit pure binary entropy.
2. LSB Random Method: Blind random embedding of messages in the spatial domain of the image.
3. Edge-Based Method: Adaptive data embedding utilizing the Canny Edge Detection algorithm to camouflage messages within the texture of object contours.
4. Performance Comparison: Parallel execution of both methods for direct metric comparison.
5. Ultimate Stress Test: Automated testing (batch processing) to evaluate image quality (PSNR & SSIM), resistance to visual manipulation, computational time, and steganography security using the Chi-Square Attack.
