# 🎮 WINE Vibe Launcher

A lightweight, fast, and stylish launcher for WINE and Proton games on Linux, featuring a custom modern dark user interface built with `customtkinter`.

Designed specifically for Linux gamers who want maximum performance without heavy background overlays, providing easy component management right out of the box.

---

## ✨ Features

* **System Menu Integration**: Automatically creates a `.desktop` shortcut in your applications menu (perfect for KDE and other desktop environments) upon first launch.
* **Component Center**: Download and manage compatibility layers with a single click:
  * **Proton-GE** (Official builds by GloriousEggroll)
  * **DW Proton** (Custom builds optimized for anime and gacha games, fetched seamlessly via Forgejo API)
  * **DXVK** (DirectX 9/10/11 to Vulkan translation)
  * **VKD3D** (DirectX 12 to Vulkan translation)
* **Gaming Optimizations**: Toggle **MangoHud** (performance overlay) and **Gamescope** (micro-compositor with FSR upscale support) instantly using simple checkboxes.
* **Isolated Wine Prefixes**: Manage dedicated `WINEPREFIX` paths for each game to keep your configurations clean and isolated.
* **Smart Search**: Quickly filter through your entire game library instantly.

---

## 🚀 Requirements & Dependencies

To ensure everything runs smoothly, make sure you have the following installed on your system:
* **Python 3**
* UI library: `pip install customtkinter`
* System utilities: `tar` (required for extracting downloaded components)
* Gaming tools (Optional but recommended): `mangohud`, `gamescope`, `wine`

---

## 🛠️ Installation & Usage

1. Clone the repository:
```bash
git clone [https://github.com/barsuk228332/vibe-launcher.git](https://github.com/barsuk228332/vibe-launcher.git)
cd vibe-launcher
