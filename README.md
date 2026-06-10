# 🎮 WINE Vibe Launcher

A lightweight, blazing-fast, and visually stunning custom launcher for WINE and Proton games on Linux. Built using `customtkinter`, it provides an elegant dark-themed dashboard to manage your Windows gaming library natively, without the overhead of heavy background game clients or stores.

Designed from scratch for Linux enthusiasts and gamers who demand absolute performance, granular prefix control, and an interface that looks like a premium gaming client.

---

## ✨ Full Feature Overview

* **🖼️ Smooth Grid View Library**: Say goodbye to boring text lists and basic dropdowns. Your game library is rendered as a clean, responsive grid of gaming cards featuring dynamic borders, highlight selections, and integrated visual indicators.

* **🔍 Steam Cover Auto-Downloader**: No manual image hunting required. When you select a game, the launcher uses the Steam Store API to look up the game's official AppID and pulls down high-resolution vertical cover art directly into your local storage with one click.

* **⚙️ One-Click Wine Utilities**: Need to tweak libraries or install a font? The interface dynamically hooks into the environment variables of your selected game, allowing you to launch isolated instances of `Winecfg` and `Winetricks` targeted directly at that specific game's `WINEPREFIX`.

* **🛠️ Native System Menu Integration**: Upon its very first execution, the launcher automatically compiles and deploys a standalone `.desktop` environment entry inside your user applications directory (`~/.local/share/applications`). This fully integrates Vibe Launcher into system application menus (KDE Kickoff, Rofi, GNOME, etc.) with proper categorization.

* **🌍 Dynamic Component Center**: An all-in-one hub to download and maintain compatibility translations. It fetches release manifests directly via the GitHub and Forgejo APIs, providing a visual download progress bar:
  * **Proton-GE** (Official bleeding-edge optimization layers by GloriousEggroll)
  * **DW Proton** (Custom wine-distributions fine-tuned for anime, gacha, and modern anti-cheat gaming layers via Dawn Winery API)
  * **DXVK** (High-performance DirectX 9/10/11 to Vulkan translation)
  * **VKD3D** (DirectX 12 to Vulkan translation layers)

* **🚀 Linux Gaming Performance Toggles**: Instantly stack the best open-source performance tools before spinning up your titles via simple checkboxes:
  * **Feral GameMode**: Automatically forces CPU governors to performance mode, optimizes process scheduling niceness, and raises GPU power profiles.
  * **MangoHud**: Displays full system telemetry, framing times, CPU/GPU utilization, temperatures, and live FPS counters.
  * **Gamescope**: Runs the game inside an isolated micro-compositor instance, unlocking system-level AMD FSR upscaling, resolution forcing, and seamless refresh rate containerization.

* **🔒 Strict Prefix Isolation & Custom Parameters**: Every single entry features independent arguments, separate system environment overrides (`ENV_VARIABLES`), and custom sandbox locations for individual `WINEPREFIX` virtual filesystems.

---

## 🚀 Requirements & Dependencies

To ensure all engines and visual elements load correctly, verify your Linux environment contains the following blocks:

### 1. Base Runtime
* **Python 3.10+** (Core programming runtime)

### 2. Python Packages
* `customtkinter` (Modern UI elements)
* `Pillow` (Advanced image processing for covers)

### 3. System Packages & Tools
Install these via your native package manager (e.g., `pacman -S`, `apt install`):
* `wine` / `wine-staging` (Core execution layers)
* `winetricks` (Windows DLL/font deployment engine)
* `tar` (Required by the Component Manager to decompress downloaded layers)
* `gamemode` / `lib32-gamemode` (For Feral GameMode support)
* `mangohud` / `lib32-mangohud` (For overlay rendering)
* `gamescope` (For the micro-compositor runtime environment)

---

## 🛠️ Installation & Usage Guide

Follow these exact steps to deploy, install dependencies, and launch the application cleanly on your Linux system.

### Step 1: Clone the Repository
Open your terminal and clone the codebase down to your local directory:

```bash
git clone [https://github.com/barsuk228332/vibe-launcher.git](https://github.com/barsuk228332/vibe-launcher.git)
cd vibe-launcher

Step 2: Install Python Dependencies

Use pip to automatically install the required layout and image libraries specified in the project requirements:
Bash

pip install -r requirements.txt

(Alternatively, you can install the packages manually if you don't use a requirements file):
Bash

pip install customtkinter Pillow

Step 3: Run the Launcher

Execute the application Python script:
Bash

python3 wine-gui.py

Note: On your very first startup, the app automatically creates its system desktop shortcut. You can then completely close the terminal and comfortably run WINE Vibe Launcher straight from your system desktop application grid or KDE application menu!
📦 Project Structure & Storage Paths

The launcher adheres to the XDG Base Directory Specification, keeping your user directories completely clean. All assets and configurations are isolated within your user space:
Plaintext

📁 Configuration Directory:  ~/.local/share/vibe-launcher/
├── 📄 my_games.json         <- JSON database containing your custom game configurations
├── 📁 covers/               <- Local caching directory for downloaded Steam cover art
└── 📁 runners/              <- Extracted custom compatibility tools (Proton-GE, DW-Proton)
    ├── 📁 dxvk/             <- Local folders storing explicit DXVK translator versions
    └── 📁 vkd3d/            <- Local folders storing explicit VKD3D translator versions

💡 How to Add and Run Your First Game

    Launch the Client: Open Vibe Launcher from your applications panel.

    Add Entry: Click on the + Добавить игру button at the top left.

    Configure Paths:

        Use Обзор файла to select your target game's .exe executable.

        Provide a clean name for the library (e.g., Project Zomboid or Geometry Dash).

        Leave the cover entry blank to use automatic search, or supply a custom path.

    Choose Optimization: Toggle GameMode, MangoHud or Gamescope depending on your performance preferences.

    Save & Play: Click СОХРАНИТЬ ИГРУ. Back on the home screen, select your newly created game card, click the blue Скачать обложку button to automatically fetch your artwork from Steam, and smash that green ИГРАТЬ button!
