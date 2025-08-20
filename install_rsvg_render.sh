#!/bin/bash
# Установка rsvg-convert на Render без sudo

echo "🔧 Устанавливаю rsvg-convert для Render..."

# Проверяем есть ли уже rsvg-convert
if command -v rsvg-convert &> /dev/null; then
    echo "✅ rsvg-convert уже установлен"
    rsvg-convert --version
    exit 0
fi

# Пробуем установить через apt (если есть права)
if apt-get update && apt-get install -y librsvg2-bin 2>/dev/null; then
    echo "✅ rsvg-convert установлен через apt"
    rsvg-convert --version
    exit 0
fi

# Если нет прав, скачиваем статическую версию
echo "📦 Скачиваю статическую версию rsvg-convert..."

# Создаем директорию для бинарников
mkdir -p $HOME/bin

# Скачиваем предкомпилированный rsvg-convert (если доступен)
# Для Ubuntu/Debian x64
wget -O $HOME/bin/rsvg-convert https://github.com/RazrFalcon/resvg/releases/download/v0.35.0/resvg-linux-x86_64.tar.gz

# Делаем исполняемым
chmod +x $HOME/bin/rsvg-convert

# Добавляем в PATH
export PATH=$HOME/bin:$PATH
echo 'export PATH=$HOME/bin:$PATH' >> $HOME/.bashrc

echo "✅ rsvg-convert установлен в $HOME/bin/"
echo "🔍 Проверяю установку..."
$HOME/bin/rsvg-convert --version || echo "⚠️ Не удалось установить rsvg-convert"