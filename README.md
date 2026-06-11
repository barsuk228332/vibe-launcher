WINE Vibe Launcher

A lightweight, modern, and high-performance game launcher for Linux built with Python and CustomTkinter. Easily manage your Windows games (.exe) using system WINE, Proton, DXVK, and VKD3D components without bloating your system.
✨ Features

    Clean System Integration: Installed locally for your user only (~/.local/bin), keeping your home directory perfectly clean.

    Proton & WINE Support: Automatically scans and utilizes installed Proton layers (Steam, PortProton, etc.) or your system WINE.

    Component Downloader: Integrated download center for the latest releases of Proton-GE, DW Proton, DXVK, and VKD3D-Proton directly from repositories.

    Built-in Linux Gaming Tweaks: Toggle performance optimizations inside a single integrated dashboard:

        MangoHud Overlay & Feral GameMode integration.

        Gamescope micro-compositor configuration.

        Esync/Fsync toggles for smooth frame rates.

        Mesa GPL shader compilation tweak for AMD graphics (fixes stutters).

        LAA (Large Address Aware) anti-crash tweak for older 32-bit games.

    Automatic Artwork: Automatically fetches and caches high-quality game covers using the SteamGridDB API with an interactive in-app poster picker.

    Playtime Tracker: Automatically monitors active game processes in a background thread and records your total pure playtime.

    Safe Session Management: Ability to safely terminate hung or frozen game processes directly from the UI.

🛠️ Installation

You don't need root (sudo) privileges to install WINE Vibe Launcher. It installs entirely inside your user space.

    Clone the repository:
    Bash

    git clone https://github.com/barsuk228332/vibe-launcher.git
    cd vibe-launcher

    Make the installer executable:
    Bash

    chmod +x install.sh

    Run the installation script:
    Bash

    ./install.sh

The script will automatically install necessary Python dependencies (customtkinter, Pillow, requests), copy the binary to your executable path, and generate a native Linux .desktop shortcut.
🚀 Usage

Once installed, you can launch the app directly from your system applications menu (search for WINE Vibe Launcher) or simply type in your terminal:
Bash

vibe-launcher

🔒 Privacy & Security

All your data, customized game configurations, and your SteamGridDB API token are safely stored locally in ~/.local/share/vibe-launcher/my_games.json. No personal data or private keys are ever uploaded to GitHub or any third-party servers.
📄 License

This project is open-source. Feel free to fork, modify, and tweak it to fit your vibe!
