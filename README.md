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
