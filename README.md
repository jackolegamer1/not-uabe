# 🛠️ NOT UABE

**NOT UABE** is a portable and lightweight Unity Asset Bundle editor specifically designed for Android. It allows you to view, export, and replace `Texture2D` assets directly in your smartphone's browser using Termux.

> **Why use it?** No need to transfer files to a PC just to swap a skin or texture. Mod your game assets directly on your phone.

---

## 📥 Installation Methods

### 🟢 1. The Easiest Way (One-Click Setup)
Just paste this command into Termux. It will install all dependencies, clone the repo, and start the server automatically:

```bash
pkg update && pkg install python git -y && git clone [https://github.com/jackolegamer1/not-uabe.git](https://github.com/jackolegamer1/not-uabe.git) && cd not-uabe && pip install -r requirements.txt && python uabe.py

```
*Once finished, open http://127.0.0.1:8080 in your mobile browser.*
### 🟡 2. The Standard Way (Manual Setup)
If you already have Python and Git installed, follow these steps:
 1. **Clone the repository:**
   ```bash
   git clone [https://github.com/jackolegamer1/not-uabe.git](https://github.com/jackolegamer1/not-uabe.git)
   cd not-uabe
   
   ```
 2. **Install dependencies:**
   ```bash
   pip install Flask UnityPy Pillow texture2ddecoder
   
   ```
 3. **Run the script:**
   ```bash
   python uabe.py
   
   ```
## 🚀 How to Use
 1. Start the script in Termux.
 2. Open any browser and go to: http://127.0.0.1:8080.
 3. Click **"UPLOAD BUNDLE"** and select your .bundle or .assets file.
 4. Browse the texture list with live previews:
   * **EXPORT PNG:** Saves the texture to your device.
   * **REPLACE:** Choose a custom image to overwrite the asset in the bundle.
 5. Click **"BUILD & DOWNLOAD MODDED BUNDLE"** at the bottom to get your modified file.
## 🛠️ Technical Highlights
 * **Fix Orientation:** Corrects the common Unity "flipped texture" bug; previews show assets right-side up.
 * **Auto-Decode:** Full support for ASTC, ETC1, and ETC2 formats.
 * **Mobile-First UI:** Minimalist interface optimized for vertical smartphone screens.
**Author:** @piercedpierced on tt 
