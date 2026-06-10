import tkinter as tk
from tkinter import filedialog
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
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class WineLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("WINE Vibe Launcher")
        self.geometry("680x850")
        self.resizable(False, False)

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

        self.create_desktop_shortcut()

        self.games = self.load_games()
        self.search_query = ""
        self.selected_game = None
        self.game_cards = []
        self.is_editing = False

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.main_screen = ctk.CTkFrame(self.container, fg_color="transparent")
        self.add_screen = ctk.CTkFrame(self.container, fg_color="transparent")
        self.settings_screen = ctk.CTkFrame(self.container, fg_color="transparent")

        self.init_main_screen()
        self.init_add_screen()
        self.init_settings_screen()

        self.show_screen(self.main_screen)

    def create_desktop_shortcut(self):
        apps_dir = os.path.expanduser("~/.local/share/applications")
        os.makedirs(apps_dir, exist_ok=True)
        shortcut_path = os.path.join(apps_dir, "vibe-launcher.desktop")

        if not os.path.exists(shortcut_path):
            script_path = os.path.abspath(sys.argv[0])
            working_dir = os.path.dirname(script_path)
            python_exec = sys.executable

            desktop_entry = f"""[Desktop Entry]
Type=Application
Name=WINE Vibe Launcher
Comment=Управление WINE играми, Proton, DXVK и VKD3D
Exec={python_exec} {script_path}
Path={working_dir}
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

        self.search_entry = ctk.CTkEntry(self.main_screen, placeholder_text="Поиск в библиотеке...")
        self.search_entry.pack(pady=(0, 10), fill="x")
        self.search_entry.bind("<KeyRelease>", self.filter_games)

        self.scroll_frame = ctk.CTkScrollableFrame(self.main_screen, label_text="ВАША ИГРОВАЯ БИБЛИОТЕКА", label_font=("Arial", 11, "bold"))
        self.scroll_frame.pack(fill="both", expand=True, pady=5)

        # Нижняя информационная панель (сделали высоту 165, чтобы точно всё влезло)
        self.info_panel = ctk.CTkFrame(self.main_screen, fg_color="#1e1e1e", border_width=1, border_color="#333", height=165)
        self.info_panel.pack(fill="x", pady=10)
        self.info_panel.pack_propagate(False)
        
        self.info_label = ctk.CTkLabel(self.info_panel, text="Выберите игру из библиотеки выше", justify="left", font=("Arial", 13), text_color="gray", anchor="nw")
        self.info_label.pack(side="left", fill="both", expand=True, padx=15, pady=12)

        # Правая панель кнопок в info_panel
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

        self.run_btn = ctk.CTkButton(self.main_btn_box, text="ИГРАТЬ", command=self.run_game, fg_color="#28a745", hover_color="#218838", font=("Arial", 15, "bold"), height=45)
        self.run_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))

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
        
        self.exe_entry = ctk.CTkEntry(self.add_screen, placeholder_text="Путь к исполняемому файлу (.exe)...")
        self.exe_entry.pack(fill="x", pady=2)
        ctk.CTkButton(self.add_screen, text="Обзор файла", height=25, fg_color="#444", command=self.choose_exe).pack(anchor="e", pady=(0, 5))
        
        self.name_entry = ctk.CTkEntry(self.add_screen, placeholder_text="Название игры в библиотеке...")
        self.name_entry.pack(fill="x", pady=(2, 5))

        self.icon_entry = ctk.CTkEntry(self.add_screen, placeholder_text="Путь к обложке игры (Оставьте пустым для автопоиска)...")
        self.icon_entry.pack(fill="x", pady=2)
        ctk.CTkButton(self.add_screen, text="Выбрать обложку вручную", height=25, fg_color="#444", command=self.choose_icon).pack(anchor="e", pady=(0, 5))
        
        self.args_entry = ctk.CTkEntry(self.add_screen, placeholder_text="Аргументы запуска (например: -skipintro -windowed)")
        self.args_entry.pack(fill="x", pady=2)
        
        self.env_entry = ctk.CTkEntry(self.add_screen, placeholder_text="Переменные окружения (например: DXVK_HUD=1 WINEESYNC=1)")
        self.env_entry.pack(fill="x", pady=(2, 5))

        self.runner_dropdown = ctk.CTkOptionMenu(self.add_screen, values=["Системный WINE"], command=self.on_runner_changed)
        self.runner_dropdown.pack(fill="x", pady=2)
        
        self.proton_frame = ctk.CTkFrame(self.add_screen, fg_color="transparent")
        self.proton_frame.pack(fill="x", pady=2)
        self.proton_entry = ctk.CTkEntry(self.proton_frame, placeholder_text="Путь к Proton слою...")
        self.proton_entry.pack(fill="x", side="left", expand=True, padx=(0, 5))
        
        self.prefix_entry = ctk.CTkEntry(self.add_screen, placeholder_text="Кастомный путь к префиксу (WINEPREFIX)...")
        self.prefix_entry.pack(fill="x", pady=2)
        
        lib_box = ctk.CTkFrame(self.add_screen, fg_color="transparent")
        lib_box.pack(fill="x", pady=5)
        self.dxvk_dropdown = ctk.CTkOptionMenu(lib_box, values=["[ Отключено ]"])
        self.dxvk_dropdown.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.vkd3d_dropdown = ctk.CTkOptionMenu(lib_box, values=["[ Отключено ]"])
        self.vkd3d_dropdown.pack(side="right", expand=True, fill="x", padx=(5, 0))

        opt_box = ctk.CTkFrame(self.add_screen, fg_color="transparent")
        opt_box.pack(fill="x", pady=10)
        
        self.mangohud_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opt_box, text="MangoHud Overlay", variable=self.mangohud_var).pack(side="left", padx=15)
        
        self.gamescope_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opt_box, text="Gamescope", variable=self.gamescope_var).pack(side="left", padx=15)

        self.gamemode_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opt_box, text="Feral GameMode", variable=self.gamemode_var).pack(side="left", padx=15)

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
            "launch_count": self.selected_game["launch_count"] if self.is_editing else 0
        }

        if self.is_editing:
            for i, g in enumerate(self.games):
                if g == self.selected_game: self.games[i] = new_data; break
        else:
            self.games.append(new_data)
            
        self.save_games(); self.update_list(); self.cancel_add()

    def delete_game(self):
        if self.selected_game: 
            self.games.remove(self.selected_game)
            self.selected_game = None
            self.info_label.configure(text="Выберите игру из библиотеки выше", text_color="gray")
            self.save_games(); self.update_list()

    def load_games(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f: return json.load(f).get("games", [])
            except: pass
        return []

    def save_games(self):
        with open(self.config_file, "w") as f: json.dump({"games": self.games}, f, indent=4)

    def update_list(self):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        self.game_cards = []
        
        row, col = 0, 0
        for g in self.games:
            if self.search_query.lower() in g["name"].lower():
                card = ctk.CTkFrame(self.scroll_frame, width=140, height=190, fg_color="#1a1a1a", border_width=1, border_color="#333", corner_radius=8)
                card.grid(row=row, column=col, padx=10, pady=10)
                card.grid_propagate(False)

                img_path = g.get("icon_path", "")
                has_img = False
                
                if img_path and os.path.exists(img_path):
                    try:
                        pil_img = Image.open(img_path).resize((138, 145), Image.Resampling.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(138, 145))
                        lbl_img = ctk.CTkLabel(card, image=ctk_img, text="")
                        lbl_img.pack(side="top", fill="both", expand=True)
                        has_img = True
                    except: pass

                if not has_img:
                    lbl_img = ctk.CTkLabel(card, text=g['name'][:12] + '...' if len(g['name']) > 12 else g['name'], font=("Arial", 12, "bold"), text_color="#1f538d", anchor="center")
                    lbl_img.pack(side="top", fill="both", expand=True, pady=20)

                lbl_name = ctk.CTkLabel(card, text=g['name'], font=("Arial", 11, "bold"), anchor="w", padx=5)
                lbl_name.pack(side="bottom", fill="x", pady=(2, 5))

                for widget in [card, lbl_img, lbl_name]:
                    widget.bind("<Button-1>", lambda e, game=g: self.select_game(game))
                
                self.game_cards.append((g, card))
                
                col += 1
                if col > 3:
                    col = 0
                    row += 1

    def filter_games(self, event):
        self.search_query = self.search_entry.get()
        self.update_list()

    def select_game(self, game):
        self.selected_game = game
        for g, card in self.game_cards:
            if g == game:
                card.configure(border_color="#1f538d", fg_color="#222")
            else:
                card.configure(border_color="#333", fg_color="#1a1a1a")
                
        info = f"Игра: {game.get('name')}\n"
        info += f"Раннер: {game.get('runner_type','wine').upper()} | Префикс: {game.get('wineprefix') or 'Default'}\n"
        info += f"Трансляторы: DXVK: {game.get('dxvk_version','None')} | VKD3D: {game.get('vkd3d_version','None')}\n"
        opts = []
        if game.get('use_gamemode'): opts.append("GameMode")
        if game.get('use_gamescope'): opts.append("Gamescope")
        if game.get('use_mangohud'): opts.append("MangoHud")
        info += f"Оптимизации: {', '.join(opts) if opts else 'Нет'} | Запусков: {game.get('launch_count',0)}"
        self.info_label.configure(text=info, text_color="white")

    def download_cover_auto(self):
        if not self.selected_game:
            self.info_label.configure(text="⚠️ Сначала выберите игру для скачивания обложки!", text_color="#ff4444")
            return
            
        game = self.selected_game
        game_name = game["name"]
        
        self.info_label.configure(text=f"🔍 Ищем обложку для '{game_name}' в Steam...", text_color="cyan")
        
        def worker():
            try:
                search_url = f"https://store.steampowered.com/api/storesearch/?term={urllib.parse.quote(game_name)}&l=russian&cc=RU"
                req = urllib.request.Request(search_url, headers={"User-Agent": "VibeLauncher"})
                
                with urllib.request.urlopen(req) as resp:
                    data = json.loads(resp.read().decode())
                    
                if data and data.get("total") > 0:
                    best_match = data["items"][0]
                    steam_id = best_match["id"]
                    
                    cover_url = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{steam_id}/library_600x900.jpg"
                    
                    clean_name = "".join([c for c in game_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                    save_path = os.path.join(self.covers_dir, f"{clean_name}_{steam_id}.jpg")
                    
                    urllib.request.urlretrieve(cover_url, save_path)
                    
                    game["icon_path"] = save_path
                    self.save_games()
                    
                    self.after(0, lambda: self.info_label.configure(text=f"✨ Обложка для '{game_name}' успешно загружена!", text_color="green"))
                    self.after(0, self.update_list)
                    self.after(50, lambda: self.select_game(game))
                else:
                    self.after(0, lambda: self.info_label.configure(text=f"❌ Игра '{game_name}' не найдена в базе Steam.", text_color="red"))
            except Exception as e:
                self.after(0, lambda: self.info_label.configure(text=f"❌ Ошибка скачивания: {e}", text_color="red"))
                
        threading.Thread(target=worker, daemon=True).start()

    def run_wine_tool(self, tool_name):
        if not self.selected_game: return
        game = self.selected_game
        env = os.environ.copy()
        
        if game.get("wineprefix"): 
            env["WINEPREFIX"] = game["wineprefix"]
            
        if game["runner_type"] == "proton":
            env["STEAM_COMPAT_DATA_PATH"] = game.get("wineprefix") or os.path.join(os.path.dirname(game["exe_path"]), "prefix")
            os.makedirs(env["STEAM_COMPAT_DATA_PATH"], exist_ok=True)
            cmd = [os.path.join(game["proton_path"], "proton"), "run", tool_name]
        else:
            cmd = [tool_name]
            
        subprocess.Popen(cmd, env=env)

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
                    k, v = pair.split("=", 1)
                    env[k] = v
        
        cmd = []
        if game.get("use_gamemode"): cmd += ["gamemoderun"]
        if game.get("use_gamescope"): cmd += ["gamescope", "-f", "-F", "fsr", "--"]
        if game.get("use_mangohud"): cmd += ["mangohud"]
        
        if game["runner_type"] == "proton":
            env["STEAM_COMPAT_DATA_PATH"] = game.get("wineprefix") or os.path.join(os.path.dirname(game["exe_path"]), "prefix")
            os.makedirs(env["STEAM_COMPAT_DATA_PATH"], exist_ok=True)
            cmd += [os.path.join(game["proton_path"], "proton"), "run", game["exe_path"]]
        else:
            if game.get("wineprefix"): env["WINEPREFIX"] = game["wineprefix"]
            cmd += ["wine", game["exe_path"]]
            
        args_str = game.get("launch_args", "").strip()
        if args_str:
            cmd += shlex.split(args_str)
            
        subprocess.Popen(cmd, env=env, cwd=os.path.dirname(game["exe_path"]))
        game["launch_count"] = game.get("launch_count", 0) + 1
        self.save_games(); self.select_game(game)

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
            
        ctk.CTkButton(self.settings_screen, text="ВЕРНУТЬСЯ В ГЛАВНОЕ МЕНЮ", fg_color="#444", hover_color="#555", command=lambda: self.show_screen(self.main_screen)).pack(fill="x", side="bottom", pady=10)

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
