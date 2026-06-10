# 🎮 WINE Vibe Launcher

A lightweight, fast, and stylish launcher for WINE and Proton games on Linux, featuring a custom modern dark user interface built with `customtkinter`.

Designed specifically for Linux gamers who want maximum performance without heavy background overlays, providing easy component management right out of the box.

---

## ✨ Features

* **Grid View Library**: A sleek, adaptive grid layout that displays your games as beautiful cards with smooth hover effects instead of boring text lists.
* **Steam Cover Auto-Downloader**: Automatically searches and downloads official vertical game covers directly from the Steam database in one click.
* **System Menu Integration**: Automatically creates a `.desktop` shortcut in your applications menu (perfect for KDE and other desktop environments) upon first launch to run the app flawlessly from any workspace.
* **Component Center**: Download and manage compatibility layers with a single click, featuring a real-time visual progress bar and automatic list refresh:
  * **Proton-GE** (Official builds by GloriousEggroll)
  * **DW Proton** (Custom builds optimized for anime and gacha games, fetched seamlessly via Forgejo API)
  * **DXVK** (DirectX 9/10/11 to Vulkan translation)
  * **VKD3D** (DirectX 12 to Vulkan translation)
* **Built-in Wine Utilities**: Launch `Winecfg` and `Winetricks` directly inside the dedicated environment of your selected game in one click.
* **Gaming Optimizations**: Instantly toggle powerful Linux gaming tools using simple checkboxes:
  * **Feral GameMode** (Optimizes CPU governor, GPU clocks, and process priorities)
  * **MangoHud** (Advanced performance, FPS, and hardware monitoring overlay)
  * **Gamescope** (Micro-compositor with built-in AMD FSR upscaling support)
* **Advanced Launch Tweaks**: Add custom game launch arguments (e.g., `-skipintro`) and pass custom environment variables (ENV) on the fly.
* **Isolated Wine Prefixes**: Manage dedicated `WINEPREFIX` paths for each game to keep your configurations clean, portable, and isolated.
* **Smart Search**: Quickly filter through your entire game library instantly as you type.

---

## 🚀 Requirements & Dependencies

To ensure everything runs smoothly, make sure you have the following installed on your system:

* **Python 3**
* Python libraries:
  ```bash
  pip install customtkinter Pillow

    System utilities: tar (required for extracting downloaded components)

    Gaming tools (Optional but highly recommended): wine, winetricks, gamemode, mangohud, gamescope

🛠️ Installation & Usage

    Clone the repository:

Bash

git clone [https://github.com/barsuk228332/vibe-launcher.git](https://github.com/barsuk228332/vibe-launcher.git)
cd vibe-launcher

    Install python dependencies:

Bash

pip install -r requirements.txt

(Or install them manually using: pip install customtkinter Pillow)

    Run the launcher:

Bash

python3 wine-gui.py

On the very first launch, the app will automatically integrate itself into your system applications menu for quick access!
📦 Project Structure

If you want to contribute or tweak the paths, here is where the launcher stores its assets:

    Config & Database: ~/.local/share/vibe-launcher/my_games.json

    Downloaded Covers: ~/.local/share/vibe-launcher/covers/

    Compatibility Layers: ~/.local/share/vibe-launcher/runners/
