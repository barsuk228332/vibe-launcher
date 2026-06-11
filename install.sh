#!/bin/bash

# Цвета для вывода в терминал
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0;30m' # Без цвета

echo -e "${BLUE}[*] Начало установки WINE Vibe Launcher...${NC}"

# 1. Создаем нужные папки в локальной директории пользователя
BIN_DIR="$HOME/.local/bin"
DATA_DIR="$HOME/.local/share/vibe-launcher"

mkdir -p "$BIN_DIR"
mkdir -p "$DATA_DIR/covers"
mkdir -p "$DATA_DIR/runners"
mkdir -p "$DATA_DIR/dxvk"
mkdir -p "$DATA_DIR/vkd3d"

# 2. Копируем сам исполняемый файл в ~/.local/bin/ и переименовываем для удобства
echo -e "${BLUE}[*] Копирование исполняемых файлов...${NC}"
if [ -f "wine-gui.py" ]; then
    cp "wine-gui.py" "$BIN_DIR/vibe-launcher"
    chmod +x "$BIN_DIR/vibe-launcher"
else
    echo -e "${RED}[X] Ошибка: Файл wine-gui.py не найден в текущей папке!${NC}"
    exit 1
fi

# 3. Установка зависимостей через pip, если их нет
echo -e "${BLUE}[*] Проверка и установка зависимостей Python...${NC}"
pip install customtkinter Pillow requests --user --quiet 2>/dev/null

# 4. Запускаем лаунчер один раз в фоне, чтобы он сам создал .desktop ярлык
echo -e "${BLUE}[*] Создание системного ярлыка...${NC}"
python3 "$BIN_DIR/vibe-launcher" --headless-init &
# Даем ему секунду создаться и мягко закрываем
sleep 1.5
pkill -f "vibe-launcher"

echo -e "${GREEN}[+] Установка успешно завершена!${NC}"
echo -e "${GREEN}[+] Теперь вы можете запустить лаунчер из меню приложений или командой 'vibe-launcher' в терминале.${NC}"
