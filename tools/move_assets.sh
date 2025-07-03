#!/bin/bash

# Ana dizindeki assets'leri projelere taşıma
MAIN_ASSETS="/Users/siyahkare/code/gavatcore/assets"
PROJECTS=("sefer_panel" "sefer_panel_v2" "gavatcore_mobile")
ASSET_TYPES=("animations" "images" "icons" "fonts")

# Her proje için
for project in "${PROJECTS[@]}"; do
    # Asset tiplerini kontrol et ve taşı
    for type in "${ASSET_TYPES[@]}"; do
        if [ -d "$MAIN_ASSETS/$type" ]; then
            echo "Moving $type to $project..."
            mkdir -p "$project/assets/$type"
            cp -r "$MAIN_ASSETS/$type/"* "$project/assets/$type/"
        fi
    done
done

# Ana dizindeki assets klasörünü yedekle ve sil
if [ -d "$MAIN_ASSETS" ]; then
    echo "Backing up main assets..."
    mv "$MAIN_ASSETS" "${MAIN_ASSETS}_backup_$(date +%Y%m%d_%H%M%S)"
fi

echo "Asset migration completed!" 