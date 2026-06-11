import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import subprocess
import json
import os
import urllib.request
import urllib.parse
import threading
import tarfile
import sys
import shlex
import shutil
import time
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class WineLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("WINE Vibe Launcher")
        self.geometry("720x850")
        
        self.resizable(True, True)
        self.minsize(550, 600)

        self.app_dir = os.path.expanduser("~/.local/share/vibe-launcher")
        self.runners_dir = os.path.join(self.app_dir, "runners")
        self.dxvk_dir = os.path.join(self.app_dir, "dxvk")
        self.vkd3d_dir = os.path.join(self.app_dir, "vkd3d")
        self.covers_dir = os.path.join(self.app_dir, "covers")
        
        os.makedirs(self.runners_dir, exist_ok=True)
        os.makedirs(self.dxvk_dir, exist_ok=True)
        os.makedirs(self.vkd3d_dir, exist_ok=True)
        os.makedirs(self.covers_dir, exist_ok=True)

        self.config_file = os.path.join(self.app_dir, "my_games.json")
        old_config = "my_games.json"
        if os.path.exists(old_config) and not os.path.exists(self.config_file):
            shutil.copy(old_config, self.config_file)

        self.config_data = self.load_config_data()
        self.games = self.config_data.get("games", [])
        
        self.sgdb_key = self.config_data.get("sgdb_key", "")

        self.create_desktop_shortcut()

        if "--headless-init" in sys.argv:
            sys.exit(0)

        self.search_query = ""
        self.selected_game = None
        self.game_cards = []
        self.is_editing = False
        
        self.current_process = None
        self.is_game_running = False
        
        self.game_start_time = 0
        self._resize_timer_id = None

        self.view_mode = "normal" 

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.main_screen = ctk.CTkFrame(self.container, fg_color="transparent")
        self.add_screen = ctk.CTkFrame(self.container, fg_color="transparent")
        self.settings_screen = ctk.CTkFrame(self.container, fg_color="transparent")

        self.init_main_screen()
        self.init_add_screen()
        self.init_settings_screen()

        self.show_screen(self.main_screen)
        
        self.bind("<Configure>", self.on_window_resize)

    def create_desktop_shortcut(self):
        apps_dir = os.path.expanduser("~/.local/share/applications")
        os.makedirs(apps_dir, exist_ok=True)
        shortcut_path = os.path.join(apps_dir, "vibe-launcher.desktop")

        if not os.path.exists(shortcut_path):
            target_exec = os.path.expanduser("~/.local/bin/vibe-launcher")
            if not os.path.exists(target_exec):
                target_exec = f"{sys.executable} {os.path.abspath(sys.argv[0])}"
            else:
                target_exec = f"python3 {target_exec}"

            desktop_entry = f"""[Desktop Entry]
Type=Application
Name=WINE Vibe Launcher
Comment=Управление WINE играми, Proton, DXVK и VKD3D
Exec={target_exec}
Icon=applications-games
Terminal=false
Categories=Game;Utility;
StartupNotify=true
"""
            try:
                with open(shortcut_path, "w", encoding="utf-8") as f:
                    f.write(desktop_entry)
            except Exception as e:
                print(f"Не удалось создать ярлык: {e}")

    def show_screen(self, screen):
        self.main_screen.pack_forget()
        self.add_screen.pack_forget()
        self.settings_screen.pack_forget()
        
        if screen == self.add_screen:
            self.refresh_runner_dropdown()
            self.refresh_dxvk_vkd3d_dropdowns()
            
        screen.pack(fill="both", expand=True, padx=20, pady=20)

    def init_main_screen(self):
        self.top_box = ctk.CTkFrame(self.main_screen, fg_color="transparent")
        self.top_box.pack(fill="x", pady=(0, 10))

        self.add_btn = ctk.CTkButton(self.top_box, text="+ Добавить игру", font=("Arial", 13, "bold"), command=self.open_add_new)
        self.add_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.settings_btn = ctk.CTkButton(self.top_box, text="⚙️ Настройки", width=110, fg_color="#333", hover_color="#444", command=lambda: self.show_screen(self.settings_screen))
        self.settings_btn.pack(side="right", padx=(5, 0))

        self.search_view_box = ctk.CTkFrame(self.main_screen, fg_color="transparent")
        self.search_view_box.pack(pady=(0, 10), fill="x")

        self.search_entry = ctk.CTkEntry(self.search_view_box, placeholder_text="Поиск в библиотеке...", text_color=("#ffffff", "#ffffff"), placeholder_text_color="#aaaaaa")
        self.search_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.filter_games)

        self.size_normal_btn = ctk.CTkButton(self.search_view_box, text="■ Крупные", width=80, height=28, fg_color="#1f538d", command=lambda: self.set_view_mode("normal"))
        self.size_normal_btn.pack(side="right", padx=2)
        
        self.size_small_btn = ctk.CTkButton(self.search_view_box, text="⁝⁝ Мелкие", width=80, height=28, fg_color="#333", hover_color="#444", command=lambda: self.set_view_mode("small"))
        self.size_small_btn.pack(side="right", padx=2)

        self.scroll_frame = ctk.CTkScrollableFrame(self.main_screen, label_text="ВАША ИГРОВАЯ БИБЛИОТЕКА", label_font=("Arial", 11, "bold"))
        self.scroll_frame.pack(fill="both", expand=True, pady=5)

        self.info_panel = ctk.CTkFrame(self.main_screen, fg_color="#1e1e24", border_width=1, border_color="#333", height=165)
        self.info_panel.pack(fill="x", pady=10)
        self.info_panel.pack_propagate(False)
        
        self.info_label = ctk.CTkLabel(self.info_panel, text="Выберите игру из библиотеки выше", justify="left", font=("Arial", 13), text_color="gray", anchor="nw")
        self.info_label.pack(side="left", fill="both", expand=True, padx=15, pady=12)

        self.tools_frame = ctk.CTkFrame(self.info_panel, fg_color="transparent", width=130)
        self.tools_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        self.btn_winecfg = ctk.CTkButton(self.tools_frame, text="Winecfg", width=120, height=26, fg_color="#444", hover_color="#555", command=lambda: self.run_wine_tool("winecfg"))
        self.btn_winecfg.pack(pady=2)
        self.btn_winetricks = ctk.CTkButton(self.tools_frame, text="Winetricks", width=120, height=26, fg_color="#444", hover_color="#555", command=lambda: self.run_wine_tool("winetricks"))
        self.btn_winetricks.pack(pady=2)
        
        self.btn_get_cover = ctk.CTkButton(self.tools_frame, text="Скачать обложку", width=120, height=26, fg_color="#1f538d", hover_color="#296cb8", command=self.download_cover_auto)
        self.btn_get_cover.pack(pady=2)

        self.main_btn_box = ctk.CTkFrame(self.main_screen, fg_color="transparent")
        self.main_btn_box.pack(fill="x", pady=(5, 0))

        self.delete_btn = ctk.CTkButton(self.main_btn_box, text="Удалить", command=self.delete_game, fg_color="#721c24", hover_color="#af2331", width=90, height=45)
        self.delete_btn.pack(side="left", padx=(0, 5))

        self.edit_btn = ctk.CTkButton(self.main_btn_box, text="ИЗМЕНИТЬ", command=self.open_edit_existing, fg_color="#444", hover_color="#555", width=110, height=45)
        self.edit_btn.pack(side="left", padx=5)

        self.run_btn = ctk.CTkButton(self.main_btn_box, text="ИГРАТЬ", command=self.handle_game_button, fg_color="#28a745", hover_color="#218838", font=("Arial", 15, "bold"), height=45)
        self.run_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

        self.update_list()

    def set_view_mode(self, mode):
        self.view_mode = mode
        if mode == "normal":
            self.size_normal_btn.configure(fg_color="#1f538d")
            self.size_small_btn.configure(fg_color="#333")
        else:
            self.size_normal_btn.configure(fg_color="#333")
            self.size_small_btn.configure(fg_color="#1f538d")
        self.update_list()

    def on_window_resize(self, event):
        if hasattr(self, 'scroll_frame') and event.widget == self:
            if self._resize_timer_id is not None:
                self.after_cancel(self._resize_timer_id)
            self._resize_timer_id = self.after(200, self.safe_update_list)

    def safe_update_list(self):
        self._resize_timer_id = None
        self.update_list()

    def open_add_new(self):
        self.is_editing = False
        self.clear_add_inputs()
        self.show_screen(self.add_screen)

    def open_edit_existing(self):
        if not self.selected_game:
            self.info_label.configure(text="⚠️ Сначала выберите игру для изменения!", text_color="#ff4444")
            return
        
        self.is_editing = True
        game = self.selected_game
        self.clear_add_inputs()
        
        self.exe_entry.insert(0, game.get("exe_path", ""))
        self.name_entry.insert(0, game.get("name", ""))
        self.args_entry.insert(0, game.get("launch_args", ""))
        self.env_entry.insert(0, game.get("custom_env", ""))
        self.icon_entry.insert(0, game.get("icon_path", ""))
        
        self.refresh_runner_dropdown()
        found_runner = False
        for opt in self.runner_options:
            if game.get("runner_type") == "proton" and game.get("proton_path") in opt:
                self.runner_dropdown.set(opt)
                found_runner = True
                break
        if not found_runner: self.runner_dropdown.set("Системный WINE")
        self.on_runner_changed(self.runner_dropdown.get())

        self.prefix_entry.insert(0, game.get("wineprefix", ""))
        self.dxvk_dropdown.set(game.get("dxvk_version", "[ Отключено ]"))
        self.vkd3d_dropdown.set(game.get("vkd3d_version", "[ Отключено ]"))
        
        self.mangohud_var.set(game.get("use_mangohud", False))
        self.gamescope_var.set(game.get("use_gamescope", False))
        self.gamemode_var.set(game.get("use_gamemode", False))
        
        self.esync_var.set(game.get("use_esync", True))
        self.gpl_var.set(game.get("use_gpl", False))
        self.large_address_var.set(game.get("use_large_address", True))
        
        self.show_screen(self.add_screen)

    def scan_runners(self):
        runners = [("Системный WINE", "wine", "")]
        paths_to_scan = [
            self.runners_dir,
            os.path.expanduser("~/.local/share/Steam/compatibilitytools.d"),
            os.path.expanduser("~/.local/share/Steam/steamapps/common"),
            os.path.expanduser("~/PortProton/data/dist")
        ]
        for p in paths_to_scan:
            if os.path.exists(p):
                try:
                    for item in os.listdir(p):
                        full_path = os.path.join(p, item)
                        if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, "proton")):
                            runners.append((f"Proton: {item}", "proton", full_path))
                except Exception: pass
        return runners

    def scan_local_components(self, target_dir):
        components = ["[ Отключено ]"]
        if os.path.exists(target_dir):
            try:
                for item in os.listdir(target_dir):
                    if os.path.isdir(os.path.join(target_dir, item)): components.append(item)
            except Exception: pass
        return components

    def init_add_screen(self):
        ctk.CTkLabel(self.add_screen, text="Параметры игры", font=("Arial", 16, "bold")).pack(pady=(0, 10))
        
        self.exe_entry = ctk.CTkEntry(self.add_screen, placeholder_text="Путь к исполняемому файлу (.exe)...", text_color=("#ffffff", "#ffffff"), placeholder_text_color="#aaaaaa")
        self.exe_entry.pack(fill="x", pady=2)
        ctk.CTkButton(self.add_screen, text="Обзор файла", height=25, fg_color="#444", command=self.choose_exe).pack(anchor="e", pady=(0, 5))
        
        self.name_entry = ctk.CTkEntry(self.add_screen, placeholder_text="Название игры в библиотеке...", text_color=("#ffffff", "#ffffff"), placeholder_text_color="#aaaaaa")
        self.name_entry.pack(fill="x", pady=(2, 5))

        self.icon_entry = ctk.CTkEntry(self.add_screen, placeholder_text="Путь к обложке игры (Оставьте пустым для автопоиска)...", text_color=("#ffffff", "#ffffff"), placeholder_text_color="#aaaaaa")
        self.icon_entry.pack(fill="x", pady=2)
        ctk.CTkButton(self.add_screen, text="Выбрать обложку вручную", height=25, fg_color="#444", command=self.choose_icon).pack(anchor="e", pady=(0, 5))
        
        self.args_entry = ctk.CTkEntry(self.add_screen, placeholder_text="Аргументы запуска (например: -skipintro -windowed)", text_color=("#ffffff", "#ffffff"), placeholder_text_color="#aaaaaa")
        self.args_entry.pack(fill="x", pady=2)
        
        self.env_entry = ctk.CTkEntry(self.add_screen, placeholder_text="Переменные окружения (например: DXVK_HUD=1 WINEESYNC=1)", text_color=("#ffffff", "#ffffff"), placeholder_text_color="#aaaaaa")
        self.env_entry.pack(fill="x", pady=(2, 5))

        self.runner_dropdown = ctk.CTkOptionMenu(self.add_screen, values=["Системный WINE"], command=self.on_runner_changed)
        self.runner_dropdown.pack(fill="x", pady=2)
        
        self.proton_frame = ctk.CTkFrame(self.add_screen, fg_color="transparent")
        self.proton_frame.pack(fill="x", pady=2)
        self.proton_entry = ctk.CTkEntry(self.proton_frame, placeholder_text="Путь к Proton слою...", text_color=("#ffffff", "#ffffff"), placeholder_text_color="#aaaaaa")
        self.proton_entry.pack(fill="x", side="left", expand=True, padx=(0, 5))
        
        self.prefix_entry = ctk.CTkEntry(self.add_screen, placeholder_text="Кастомный путь к префиксу (WINEPREFIX)...", text_color=("#ffffff", "#ffffff"), placeholder_text_color="#aaaaaa")
        self.prefix_entry.pack(fill="x", pady=2)
        
        lib_box = ctk.CTkFrame(self.add_screen, fg_color="transparent")
        lib_box.pack(fill="x", pady=5)
        self.dxvk_dropdown = ctk.CTkOptionMenu(lib_box, values=["[ Отключено ]"])
        self.dxvk_dropdown.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.vkd3d_dropdown = ctk.CTkOptionMenu(lib_box, values=["[ Отключено ]"])
        self.vkd3d_dropdown.pack(side="right", expand=True, fill="x", padx=(5, 0))

        tweak_box = ctk.CTkFrame(self.add_screen, fg_color="#1a1a1a", border_width=1, border_color="#333", corner_radius=6)
        tweak_box.pack(fill="x", pady=10, padx=2)
        
        ctk.CTkLabel(tweak_box, text="⚙️ Встроенные твики и утилиты оптимизации Linux Gaming:", font=("Arial", 11, "bold"), text_color="#1f538d").pack(anchor="w", padx=12, pady=(8, 4))
        
        tweak_grid = ctk.CTkFrame(tweak_box, fg_color="transparent")
        tweak_grid.pack(fill="x", padx=10, pady=(0, 10))
        
        tweak_grid.grid_columnconfigure(0, weight=1)
        tweak_grid.grid_columnconfigure(1, weight=1)
        tweak_grid.grid_columnconfigure(2, weight=1)

        # ИСПРАВЛЕНО: Текст чекбоксов слегка укорочен, а размер шрифта уменьшен до 11, чтобы он идеально сидел без ресайза
        tweak_font = ("Arial", 11)

        self.mangohud_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(tweak_grid, text="MangoHud Overlay", font=tweak_font, variable=self.mangohud_var).grid(row=0, column=0, padx=8, pady=6, sticky="w")
        
        self.gamescope_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(tweak_grid, text="Gamescope", font=tweak_font, variable=self.gamescope_var).grid(row=0, column=1, padx=8, pady=6, sticky="w")

        self.gamemode_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(tweak_grid, text="Feral GameMode", font=tweak_font, variable=self.gamemode_var).grid(row=0, column=2, padx=8, pady=6, sticky="w")

        self.esync_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(tweak_grid, text="Esync/Fsync твик", font=tweak_font, variable=self.esync_var).grid(row=1, column=0, padx=8, pady=6, sticky="w")

        self.gpl_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(tweak_grid, text="Mesa GPL (AMD)", font=tweak_font, variable=self.gpl_var).grid(row=1, column=1, padx=8, pady=6, sticky="w")

        self.large_address_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(tweak_grid, text="LAA анти-краш", font=tweak_font, variable=self.large_address_var).grid(row=1, column=2, padx=8, pady=6, sticky="w")

        btn_box = ctk.CTkFrame(self.add_screen, fg_color="transparent")
        btn_box.pack(fill="x", side="bottom", pady=5)
        ctk.CTkButton(btn_box, text="ОТМЕНА", fg_color="#444", hover_color="#555", command=self.cancel_add).pack(side="left", expand=True, padx=(0,5))
        ctk.CTkButton(btn_box, text="СОХРАНИТЬ ИГРУ", fg_color="#28a745", hover_color="#218838", font=("Arial", 12, "bold"), command=self.save_new_game).pack(side="right", expand=True, padx=(5,0))

    def on_runner_changed(self, choice):
        for name, r_type, r_path in self.scanned_runners:
            if name == choice:
                self.proton_entry.configure(state="normal")
                self.proton_entry.delete(0, tk.END)
                if r_type == "proton": self.proton_entry.insert(0, r_path)
                self.proton_entry.configure(state="disabled")
                break

    def refresh_runner_dropdown(self):
        self.scanned_runners = self.scan_runners()
        self.runner_options = [r[0] for r in self.scanned_runners]
        self.runner_dropdown.configure(values=self.runner_options)

    def refresh_dxvk_vkd3d_dropdowns(self):
        self.dxvk_dropdown.configure(values=self.scan_local_components(self.dxvk_dir))
        self.vkd3d_dropdown.configure(values=self.scan_local_components(self.vkd3d_dir))

    def choose_exe(self):
        p = filedialog.askopenfilename(filetypes=[("Исполняемые файлы", "*.exe")])
        if p:
            self.exe_entry.delete(0, tk.END); self.exe_entry.insert(0, p)
            if not self.name_entry.get():
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, os.path.splitext(os.path.basename(p))[0])

    def choose_icon(self):
        p = filedialog.askopenfilename(filetypes=[("Изображения", "*.png *.jpg *.jpeg")])
        if p:
            self.icon_entry.delete(0, tk.END); self.icon_entry.insert(0, p)

    def cancel_add(self):
        self.is_editing = False
        self.show_screen(self.main_screen)

    def clear_add_inputs(self):
        for e in [self.exe_entry, self.name_entry, self.prefix_entry, self.args_entry, self.env_entry, self.icon_entry]: 
            e.delete(0, tk.END)
        self.mangohud_var.set(False); self.gamescope_var.set(False); self.gamemode_var.set(False)
        self.esync_var.set(True); self.gpl_var.set(False); self.large_address_var.set(True)

    def save_new_game(self):
        exe = self.exe_entry.get().strip(); name = self.name_entry.get().strip()
        if not exe or not name: return
        
        choice = self.runner_dropdown.get(); r_type = "wine"; prot_p = ""
        for r_name, t, p in self.scanned_runners:
            if r_name == choice: r_type = t; prot_p = p; break

        new_data = {
            "name": name, "exe_path": exe, "runner_type": r_type, "proton_path": prot_p,
            "wineprefix": self.prefix_entry.get().strip(), 
            "launch_args": self.args_entry.get().strip(),
            "custom_env": self.env_entry.get().strip(),
            "icon_path": self.icon_entry.get().strip(),
            "dxvk_version": self.dxvk_dropdown.get(),
            "vkd3d_version": self.vkd3d_dropdown.get(), 
            "use_mangohud": self.mangohud_var.get(),
            "use_gamescope": self.gamescope_var.get(),
            "use_gamemode": self.gamemode_var.get(),
            "use_esync": self.esync_var.get(),
            "use_gpl": self.gpl_var.get(),
            "use_large_address": self.large_address_var.get(),
            "launch_count": self.selected_game["launch_count"] if self.is_editing else 0,
            "total_playtime_seconds": self.selected_game.get("total_playtime_seconds", 0) if self.is_editing else 0
        }

        if self.is_editing:
            for i, g in enumerate(self.games):
                if g == self.selected_game: self.games[i] = new_data; break
        else:
            self.games.append(new_data)
            
        self.save_config(); self.update_list(); self.cancel_add()

    def delete_game(self):
        if self.selected_game: 
            self.games.remove(self.selected_game)
            self.selected_game = None
            self.info_label.configure(text="Выберите игру из библиотеки выше", text_color="gray")
            self.save_config(); self.update_list()

    def load_config_data(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict): return data
            except: pass
        return {"games": [], "sgdb_key": ""}

    def save_config(self):
        self.config_data["games"] = self.games
        self.config_data["sgdb_key"] = self.sgdb_key
        with open(self.config_file, "w") as f: json.dump(self.config_data, f, indent=4)

    def update_list(self):
        for w in self.scroll_frame.winfo_children(): 
            w.destroy()
        self.game_cards = []
        
        if self.view_mode == "normal":
            card_w, card_h = 155, 245
            img_w, img_h = 153, 205
            pady_text = 20
        else:
            card_w, card_h = 105, 175
            img_w, img_h = 103, 140
            pady_text = 10

        self.update_idletasks()
        frame_width = self.scroll_frame.winfo_width() - 30
        if frame_width < 100: 
            frame_width = 650
            
        max_cols = max(1, frame_width // (card_w + 12))
        
        row, col = 0, 0
        for g in self.games:
            if self.search_query.lower() in g["name"].lower():
                card = ctk.CTkFrame(self.scroll_frame, width=card_w, height=card_h, fg_color="#1a1a1a", border_width=1, border_color="#333", corner_radius=8)
                card.grid(row=row, column=col, padx=6, pady=8)
                card.grid_propagate(False)

                img_path = g.get("icon_path", "")
                has_img = False
                
                if img_path and os.path.exists(img_path):
                    try:
                        with Image.open(img_path) as open_img:
                            pil_img = open_img.copy().resize((img_w, img_h), Image.Resampling.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(img_w, img_h))
                        lbl_img = ctk.CTkLabel(card, image=ctk_img, text="")
                        lbl_img.pack(side="top", fill="both", expand=True)
                        has_img = True
                    except Exception as e:
                        print(f"Ошибка вывода картинки: {e}")

                if not has_img:
                    lbl_img = ctk.CTkLabel(card, text=g['name'][:10] + '...' if len(g['name']) > 10 else g['name'], font=("Arial", 11, "bold"), text_color="#1f538d", anchor="center")
                    lbl_img.pack(side="top", fill="both", expand=True, pady=pady_text)

                lbl_name = ctk.CTkLabel(card, text=g['name'], font=("Arial", 10, "bold") if self.view_mode=="small" else ("Arial", 11, "bold"), anchor="w", padx=6)
                lbl_name.pack(side="bottom", fill="x", pady=(2, 5))

                for widget in [card, lbl_img, lbl_name]:
                    widget.bind("<Button-1>", lambda e, game=g: self.select_game(game))
                
                if self.selected_game and g["name"] == self.selected_game["name"]:
                    card.configure(border_color="#1f538d", fg_color="#222")
                
                self.game_cards.append((g, card))
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

    def filter_games(self, event):
        self.search_query = self.search_entry.get()
        self.update_list()

    def format_playtime(self, total_seconds):
        if not total_seconds:
            return "0 мин."
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if hours > 0:
            return f"{hours} ч. {minutes} мин."
        return f"{minutes} мин."

    def select_game(self, game):
        self.selected_game = game
        
        for g, card in self.game_cards:
            if g["name"] == game["name"]:
                card.configure(border_color="#1f538d", fg_color="#222")
            else:
                card.configure(border_color="#333", fg_color="#1a1a1a")
                
        time_text = self.format_playtime(game.get("total_playtime_seconds", 0))

        info = f"Игра: {game.get('name')}\n"
        info += f"Раннер: {game.get('runner_type','wine').upper()} | Префикс: {game.get('wineprefix') or 'Default'}\n"
        info += f"Трансляторы: DXVK: {game.get('dxvk_version','None')} | VKD3D: {game.get('vkd3d_version','None')}\n"
        opts = []
        if game.get('use_gamemode'): opts.append("GameMode")
        if game.get('use_gamescope'): opts.append("Gamescope")
        if game.get('use_mangohud'): opts.append("MangoHud")
        if game.get('use_esync', True): opts.append("Esync")
        if game.get('use_gpl', False): opts.append("MesaGPL")
        
        info += f"Оптимизации: {', '.join(opts) if opts else 'Нет'}\n"
        info += f"Запусков: {game.get('launch_count',0)} | Время в игре: {time_text}"
        self.info_label.configure(text=info, text_color="white")

        if self.is_game_running:
            self.run_btn.configure(text="ЗАКРЫТЬ ИГРУ", fg_color="#af2331", hover_color="#721c24")
        else:
            self.run_btn.configure(text="ИГРАТЬ", fg_color="#28a745", hover_color="#218838")

    def download_cover_auto(self):
        if not self.selected_game:
            self.info_label.configure(text="⚠️ Сначала выберите игру для скачивания обложки!", text_color="#ff4444")
            return

        if not self.sgdb_key:
            self.info_label.configure(text="⚠️ Ошибка: SteamGridDB API Key не задан в Настройках!", text_color="#ff4444")
            return

        game = self.selected_game
        game_name = game["name"]
        
        self.info_label.configure(text=f"🔍 Ищем варианты обложек для '{game_name}' на SteamGridDB...", text_color="cyan")
        
        def worker():
            try:
                encoded_name = urllib.parse.quote(game_name.strip())
                search_url = f"https://www.steamgriddb.com/api/v2/search/autocomplete/{encoded_name}"
                
                req = urllib.request.Request(search_url, headers={
                    "Authorization": f"Bearer {self.sgdb_key.strip()}",
                    "User-Agent": "VibeLauncher"
                })
                
                with urllib.request.urlopen(req) as resp:
                    res_data = json.loads(resp.read().decode())
                
                if res_data and res_data.get("success") and res_data.get("data") and len(res_data["data"]) > 0:
                    sgdb_game_id = res_data["data"][0]["id"]
                    found_name = res_data["data"][0]["name"]
                    
                    grids_url = f"https://www.steamgriddb.com/api/v2/grids/game/{sgdb_game_id}"
                    
                    req_grids = urllib.request.Request(grids_url, headers={
                        "Authorization": f"Bearer {self.sgdb_key.strip()}",
                        "User-Agent": "VibeLauncher"
                    })
                    
                    with urllib.request.urlopen(req_grids) as resp_grids:
                        grids_data = json.loads(resp_grids.read().decode())
                        
                    if grids_data and grids_data.get("success") and grids_data.get("data") and len(grids_data["data"]) > 0:
                        cover_urls = []
                        for item in grids_data["data"]:
                            current_url = item.get("url", "")
                            if any(current_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
                                cover_urls.append(current_url)
                        
                        if cover_urls:
                            self.after(0, lambda: self.info_label.configure(text=f"✨ Найдено {len(cover_urls)} вариантов для '{found_name}'. Открываем окно выбора...", text_color="cyan"))
                            self.after(0, lambda: self.create_cover_picker_window(game, cover_urls))
                        else:
                            self.after(0, lambda: self.info_label.configure(text=f"❌ На сервере нет статичных картинок для '{game_name}'.", text_color="red"))
                    else:
                        self.after(0, lambda: self.info_label.configure(text=f"❌ Для ID {sgdb_game_id} не найдено обложек.", text_color="red"))
                else:
                    self.after(0, lambda: self.info_label.configure(text=f"❌ Игра '{game_name}' не найдена в базе SteamGridDB.", text_color="red"))
            except Exception as e:
                self.after(0, lambda: self.info_label.configure(text=f"❌ Ошибка API: {e}", text_color="red"))
                
        threading.Thread(target=worker, daemon=True).start()

    def create_cover_picker_window(self, game, cover_urls):
        game_name = game["name"]
        
        picker_win = ctk.CTkToplevel(self)
        picker_win.title(f"Выбор обложки: {game_name}")
        picker_win.geometry("520x650")
        picker_win.resizable(False, False)
        picker_win.attributes("-topmost", True)

        ctk.CTkLabel(picker_win, text=f"Выберите обложку для '{game_name}'", font=("Arial", 14, "bold")).pack(pady=10)
        
        status_lbl = ctk.CTkLabel(picker_win, text="Загрузка миниатюр...", text_color="gray")
        status_lbl.pack(pady=(0, 10))

        scroll_thumbs = ctk.CTkScrollableFrame(picker_win, width=500, height=500, fg_color="transparent")
        scroll_thumbs.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.thumbs_cache = []

        def load_thumbnails():
            row, col = 0, 0
            for url in cover_urls[:16]: 
                try:
                    img_req = urllib.request.Request(url, headers={
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    })
                    
                    with urllib.request.urlopen(img_req) as response:
                        pil_raw = Image.open(response)
                        pil_thumb = pil_raw.resize((100, 150), Image.Resampling.LANCZOS)
                        ctk_thumb = ctk.CTkImage(light_image=pil_thumb, dark_image=pil_thumb, size=(100, 150))
                        
                        self.thumbs_cache.append(ctk_thumb)

                        lbl_thumb = ctk.CTkLabel(scroll_thumbs, image=ctk_thumb, text="", cursor="hand2")
                        lbl_thumb.grid(row=row, column=col, padx=10, pady=10)
                        
                        lbl_thumb.bind("<Button-1>", lambda e, u=url, w=picker_win, s=status_lbl, g=game: self.finish_download_selected_cover(g, u, w, s))

                        col += 1
                        if col > 3: 
                            col = 0
                            row += 1
                except Exception as e:
                    print(f"Ошибка миниатюры: {e}")
            
            self.after(0, lambda: status_lbl.configure(text="Кликните на постер для выбора", text_color="gray"))

        threading.Thread(target=load_thumbnails, daemon=True).start()

    def finish_download_selected_cover(self, game, cover_url, picker_win, status_lbl):
        game_name = game["name"]
        status_lbl.configure(text=f"🔄 Скачиваем оригинал...", text_color="cyan")
        
        def worker():
            try:
                clean_name = "".join([c for c in game_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                save_path = os.path.join(self.covers_dir, f"{clean_name}_sgdb.jpg")
                
                if os.path.exists(save_path):
                    try: os.remove(save_path)
                    except: pass
                
                img_req = urllib.request.Request(cover_url, headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                })
                with urllib.request.urlopen(img_req) as response, open(save_path, 'wb') as out_file:
                    out_file.write(response.read())
                
                game["icon_path"] = save_path
                self.save_config()
                
                self.after(0, lambda: self.info_label.configure(text=f"✨ Обложка для '{game_name}' успешно изменена!", text_color="green"))
                self.after(0, self.update_list)
                self.after(50, lambda: self.select_game(game))
                self.after(100, picker_win.destroy)
                
            except Exception as e:
                self.after(0, lambda: status_lbl.configure(text=f"❌ Ошибка скачивания: {e}", text_color="red"))
                
        threading.Thread(target=worker, daemon=True).start()

    def run_wine_tool(self, tool_name):
        if not self.selected_game: return
        game = self.selected_game
        env = os.environ.copy()
        
        if game.get("wineprefix"): 
            env["WINEPREFIX"] = game["wineprefix"]
            
        if game["runner_type"] == "proton":
            env["STEAM_COMPAT_DATA_PATH"] = game.get("wineprefix") or os.path.join(os.path.dirname(game["exe_path"]), "prefix")
            env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = os.path.expanduser("~/.local/share/Steam")
            os.makedirs(env["STEAM_COMPAT_DATA_PATH"], exist_ok=True)
            cmd = [os.path.join(game["proton_path"], "proton"), "run", tool_name]
        else:
            cmd = [tool_name]
            
        subprocess.Popen(cmd, env=env)

    def handle_game_button(self):
        if self.is_game_running:
            self.stop_game()
        else:
            self.run_game()

    def run_game(self):
        if not self.selected_game: return
        game = self.selected_game; env = os.environ.copy(); ld_paths = []
        
        for v, d in [(game.get("dxvk_version"), self.dxvk_dir), (game.get("vkd3d_version"), self.vkd3d_dir)]:
            if v and v != "[ Отключено ]":
                base = os.path.join(d, v)
                for s in ["x64", "x32", "x86"]:
                    if os.path.exists(os.path.join(base, s)): ld_paths.append(os.path.join(base, s))
        if ld_paths: env["WINE_DLL_PATH"] = ":".join(ld_paths)
        
        custom_env_str = game.get("custom_env", "").strip()
        if custom_env_str:
            for pair in custom_env_str.split():
                if "=" in pair:
                    k, v = pair.split("...", 1) if "..." in pair else pair.split("=", 1)
                    env[k] = v
        
        if game.get("use_esync", True):
            env["WINEESYNC"] = "1"
            env["WINEFSYNC"] = "1"
        if game.get("use_gpl", False):
            env["RADV_PERFTEST"] = "gpl"
        if game.get("use_large_address", True):
            env["WINE_LARGE_ADDRESS_AWARE"] = "1"

        cmd = []
        if game.get("use_gamemode"): cmd += ["gamemoderun"]
        if game.get("use_gamescope"): cmd += ["gamescope", "-f", "-F", "fsr", "--"]
        if game.get("use_mangohud"): cmd += ["mangohud"]
        
        if game["runner_type"] == "proton":
            env["STEAM_COMPAT_DATA_PATH"] = game.get("wineprefix") or os.path.join(os.path.dirname(game["exe_path"]), "prefix")
            env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = os.path.expanduser("~/.local/share/Steam")
            os.makedirs(env["STEAM_COMPAT_DATA_PATH"], exist_ok=True)
            cmd += [os.path.join(game["proton_path"], "proton"), "run", game["exe_path"]]
        else:
            if game.get("wineprefix"): env["WINEPREFIX"] = game["wineprefix"]
            cmd += ["wine", game["exe_path"]]
            
        args_str = game.get("launch_args", "").strip()
        if args_str:
            cmd += shlex.split(args_str)
            
        try:
            self.game_start_time = time.time()
            
            self.current_process = subprocess.Popen(cmd, env=env, cwd=os.path.dirname(game["exe_path"]))
            self.is_game_running = True
            
            self.run_btn.configure(text="ЗАКРЫТЬ ИГРУ", fg_color="#af2331", hover_color="#721c24")
            
            threading.Thread(target=self.monitor_game_process, daemon=True).start()
            
            game["launch_count"] = game.get("launch_count", 0) + 1
            self.save_config(); self.select_game(game)
        except Exception as e:
            messagebox.showerror("WINE Vibe Launcher", f"Не удалось запустить игру:\n{e}")

    def monitor_game_process(self):
        if self.current_process:
            self.current_process.wait()
            
            if self.is_game_running and self.game_start_time > 0:
                elapsed_seconds = int(time.time() - self.game_start_time)
                if self.selected_game:
                    old_playtime = self.selected_game.get("total_playtime_seconds", 0)
                    self.selected_game["total_playtime_seconds"] = old_playtime + elapsed_seconds
                    self.save_config()

            self.is_game_running = False
            self.current_process = None
            self.game_start_time = 0
            self.after(0, self.reset_game_button)

    def stop_game(self):
        if self.current_process and self.is_game_running:
            if messagebox.askyesno("WINE Vibe Launcher", "Вы действительно хотите принудительно завершить игру?"):
                try:
                    if self.game_start_time > 0:
                        elapsed_seconds = int(time.time() - self.game_start_time)
                        if self.selected_game:
                            old_playtime = self.selected_game.get("total_playtime_seconds", 0)
                            self.selected_game["total_playtime_seconds"] = old_playtime + elapsed_seconds
                            self.save_config()

                    self.current_process.terminate()
                    self.is_game_running = False
                    self.current_process = None
                    self.game_start_time = 0
                    self.reset_game_button()
                except Exception as e:
                    print(f"Не удалось остановить процесс: {e}")

    def reset_game_button(self):
        self.run_btn.configure(text="ИГРАТЬ", fg_color="#28a745", hover_color="#218838")
        if self.selected_game:
            self.select_game(self.selected_game)

    def init_settings_screen(self):
        ctk.CTkLabel(self.settings_screen, text="Центр загрузки компонентов", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.dl_status_label = ctk.CTkLabel(self.settings_screen, text="", text_color="cyan")
        self.dl_status_label.pack(fill="x")
        self.progress_bar = ctk.CTkProgressBar(self.settings_screen)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.pack_forget()
        
        self.tabview = ctk.CTkTabview(self.settings_screen, height=400)
        self.tabview.pack(fill="both", expand=True)
        
        self.tab_configs = {
            "runners": {"title": "Движки (Proton-GE)", "repo": "GloriousEggroll/proton-ge-custom", "is_forgejo": False},
            "dwproton": {"title": "DW Proton (Гача)", "repo": "dawn-winery/dwproton", "is_forgejo": True},
            "dxvk": {"title": "DXVK (DX9/10/11)", "repo": "doitsujin/dxvk", "is_forgejo": False},
            "vkd3d": {"title": "VKD3D (DX12)", "repo": "HansKristian-Work/vkd3d-proton", "is_forgejo": False}
        }
        
        for key, conf in self.tab_configs.items():
            tab = self.tabview.add(conf["title"])
            scroll = ctk.CTkScrollableFrame(tab, height=240); scroll.pack(fill="x", pady=5)
            ctk.CTkButton(tab, text=f"Обновить список релизов", font=("Arial", 12, "bold"), fg_color="#333", hover_color="#444", command=lambda c=conf, s=scroll, k=key: self.load_data_thread(c, s, k)).pack(fill="x", pady=5)
            
        api_box = ctk.CTkFrame(self.settings_screen, fg_color="#1a1a1a", border_width=1, border_color="#333", corner_radius=6)
        api_box.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(api_box, text="SteamGridDB API Key:", font=("Arial", 11, "bold")).pack(side="left", padx=10, pady=10)
        
        self.api_entry = ctk.CTkEntry(api_box, placeholder_text="Вставьте токен...", show="*", text_color=("#ffffff", "#ffffff"), placeholder_text_color="#aaaaaa")
        self.api_entry.pack(side="left", fill="x", expand=True, padx=5, pady=10)
        if self.sgdb_key:
            self.api_entry.insert(0, self.sgdb_key)
            
        save_api_btn = ctk.CTkButton(api_box, text="Сохранить ключ", width=110, fg_color="#1f538d", hover_color="#296cb8", command=self.save_api_key_local)
        save_api_btn.pack(side="right", padx=10, pady=10)

        ctk.CTkButton(self.settings_screen, text="ВЕРНУТЬСЯ В ГЛАВНОЕ МЕНЮ", fg_color="#444", hover_color="#555", command=lambda: self.show_screen(self.main_screen)).pack(fill="x", side="bottom", pady=10)

    def save_api_key_local(self):
        new_key = self.api_entry.get().strip()
        self.sgdb_key = new_key
        self.save_config()
        messagebox.showinfo("WINE Vibe Launcher", "API-ключ SteamGridDB успешно сохранен!")

    def load_data_thread(self, conf, scroll, component_type):
        def worker():
            try:
                if conf["is_forgejo"]:
                    url = f"https://dawn.wine/api/v1/repos/{conf['repo']}/releases?per_page=5"
                else:
                    url = f"https://api.github.com/repos/{conf['repo']}/releases?per_page=5"
                    
                req = urllib.request.Request(url, headers={"User-Agent": "VibeLauncher"})
                with urllib.request.urlopen(req) as resp:
                    data = json.loads(resp.read().decode())
                    self.after(0, lambda: self.render_list(data, scroll, component_type))
            except Exception as e: 
                print(f"Ошибка загрузки данных релизов ({component_type}): {e}")
        threading.Thread(target=worker, daemon=True).start()

    def render_list(self, data, scroll, component_type):
        for w in scroll.winfo_children(): w.destroy()
        for rel in data:
            f = ctk.CTkFrame(scroll, fg_color="transparent"); f.pack(fill="x", pady=2)
            tag = rel.get("name") or rel.get("tag_name")
            ctk.CTkLabel(f, text=tag).pack(side="left", padx=5)
            
            dl_url = ""
            for a in rel.get("assets", []):
                a_name = a.get("name", "")
                if component_type in ["vkd3d", "dwproton"]:
                    if any(a_name.endswith(ext) for ext in [".tar.xz", ".tar.zst", ".tar.gz"]):
                        dl_url = a.get("browser_download_url"); break
                else:
                    if a_name.endswith(".tar.gz") and not "native" in a_name:
                        dl_url = a.get("browser_download_url"); break
                        
            if dl_url: 
                ctk.CTkButton(f, text="Скачать", width=70, command=lambda u=dl_url, t=tag, k=component_type: self.start_download(u, t, k)).pack(side="right")

    def update_progress(self, count, block_size, total_size, tag):
        if total_size > 0:
            percent = min(count * block_size / total_size, 1.0)
            self.progress_bar.set(percent)
            self.dl_status_label.configure(text=f"Скачивание {tag}: {int(percent * 100)}%")

    def start_download(self, url, tag, component_type):
        def worker():
            self.after(0, lambda: self.progress_bar.pack(fill="x", padx=20, pady=(0, 10)))
            d = self.runners_dir if component_type in ["runners", "dwproton"] else (self.dxvk_dir if component_type == "dxvk" else self.vkd3d_dir)
            
            ext = ""
            for e in [".tar.xz", ".tar.zst", ".tar.gz"]:
                if url.lower().endswith(e):
                    ext = e; break
                    
            path = os.path.join(d, f"{tag}{ext}")
            self.after(0, lambda: self.dl_status_label.configure(text=f"Подготовка к скачиванию {tag}..."))
            
            try:
                urllib.request.urlretrieve(url, path, reporthook=lambda c, b, t: self.after(0, lambda: self.update_progress(c, b, t, tag)))
                self.after(0, lambda: self.dl_status_label.configure(text=f"Распаковка {tag}..."))
                
                if ext in [".tar.xz", ".tar.zst"]: 
                    subprocess.run(["tar", "-xf", path, "-C", d])
                else: 
                    with tarfile.open(path, "r:gz") as tar: tar.extractall(path=d)
                    
                os.remove(path)
                self.after(0, lambda: self.dl_status_label.configure(text=f"✨ {tag} успешно установлен!", text_color="green"))
                
                if component_type in ["dxvk", "vkd3d"]:
                    self.after(0, self.refresh_dxvk_vkd3d_dropdowns)
                else:
                    self.after(0, self.refresh_runner_dropdown)
                    
            except Exception as e:
                self.after(0, lambda: self.dl_status_label.configure(text=f"❌ Ошибка: {e}", text_color="red"))
                if os.path.exists(path): os.remove(path)
            
            self.after(3000, lambda: self.progress_bar.pack_forget())
            
        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    app = WineLauncher()
    app.mainloop()
