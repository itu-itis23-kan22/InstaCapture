#!/bin/bash

# Script'in bulunduğu dizine git
cd "$(dirname "$0")"

# Renk kodları
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}📲 InstaCapture - Instagram İçerik İndirme Aracı başlatılıyor...${NC}"

# Python varlığını kontrol et
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python bulunamadı! Lütfen Python 3 kurulu olduğundan emin olun.${NC}"
    echo "https://www.python.org/downloads/ adresinden Python 3'ü indirebilirsiniz."
    read -p "Devam etmek için Enter tuşuna basın..."
    exit 1
fi

# Gerekli paketleri kur
echo -e "${BLUE}Gerekli paketler kontrol ediliyor...${NC}"
python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet pillow requests lxml 

# GUI'yi başlat
echo -e "${GREEN}GUI başlatılıyor...${NC}"
python3 run_gui.py

# Hata olduğunda çıkmadan önce bekle
if [ $? -ne 0 ]; then
    echo -e "${RED}Uygulama başlatılırken bir hata oluştu.${NC}"
    read -p "Çıkmak için Enter tuşuna basın..."
    exit 1
fi 