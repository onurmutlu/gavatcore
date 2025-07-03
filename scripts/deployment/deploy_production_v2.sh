#!/bin/bash

# ====================================
# GAVATCORE V1.0 PRODUCTION DEPLOYMENT
# ====================================

set -e  # Exit on error

echo "🚀 GavatCore v1.0 Production Deployment Başlıyor..."
echo "=============================================="

# Variables
DEPLOY_TIME=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="logs/deploy"
BACKUP_DIR="backups/$DEPLOY_TIME"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log() {
    echo -e "${GREEN}[$(date +"%Y-%m-%d %H:%M:%S")]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Create directories
mkdir -p $LOG_DIR
mkdir -p $BACKUP_DIR

# ====================================
# 1. ENVIRONMENT CHECK
# ====================================
log "🔍 Ortam kontrolü yapılıyor..."

# Python version check
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.9"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    error "Python 3.9+ gerekli! Mevcut: $PYTHON_VERSION"
fi
log "✅ Python versiyonu: $PYTHON_VERSION"

# Check required files
REQUIRED_FILES=(
    "config.py"
    "requirements.txt"
    "character_engine/__init__.py"
    "utils/humanizer.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        error "Gerekli dosya bulunamadı: $file"
    fi
done
log "✅ Tüm gerekli dosyalar mevcut"

# ====================================
# 2. BACKUP CURRENT STATE
# ====================================
log "💾 Mevcut sistem yedekleniyor..."

# Backup critical files
cp -r character_engine/ $BACKUP_DIR/
cp -r handlers/ $BACKUP_DIR/
cp config.py $BACKUP_DIR/
cp -r data/ $BACKUP_DIR/

log "✅ Yedekleme tamamlandı: $BACKUP_DIR"

# ====================================
# 3. INSTALL/UPDATE DEPENDENCIES
# ====================================
log "📦 Bağımlılıklar güncelleniyor..."

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    log "Virtual environment oluşturuluyor..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

log "✅ Bağımlılıklar güncellendi"

# ====================================
# 4. RUN TESTS
# ====================================
log "🧪 Testler çalıştırılıyor..."

# Run character engine tests
python -m pytest tests/test_character_engine_complete.py -v --tb=short > $LOG_DIR/test_results_$DEPLOY_TIME.log 2>&1

if [ $? -ne 0 ]; then
    error "Testler başarısız! Log: $LOG_DIR/test_results_$DEPLOY_TIME.log"
fi

log "✅ Tüm testler başarılı"

# ====================================
# 5. DATABASE SETUP
# ====================================
log "🗄️ Veritabanı kontrol ediliyor..."

# Check if database exists
if [ ! -f "data/gavatcore.db" ]; then
    log "Veritabanı bulunamadı, oluşturuluyor..."
    python create_basic_tables.py
fi

log "✅ Veritabanı hazır"

# ====================================
# 6. CONFIGURE SERVICES
# ====================================
log "⚙️ Servisler yapılandırılıyor..."

# Create systemd service files
sudo tee /etc/systemd/system/gavatcore-api.service > /dev/null <<EOF
[Unit]
Description=GavatCore API Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/python production_bot_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/gavatcore-bots.service > /dev/null <<EOF
[Unit]
Description=GavatCore Bots Service
After=network.target gavatcore-api.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/python start_all_bots.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

log "✅ Systemd servisleri yapılandırıldı"

# ====================================
# 7. NGINX CONFIGURATION
# ====================================
log "🌐 Nginx yapılandırılıyor..."

sudo tee /etc/nginx/sites-available/gavatcore > /dev/null <<'EOF'
server {
    listen 80;
    server_name api.gavatcore.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/gavatcore /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

log "✅ Nginx yapılandırıldı"

# ====================================
# 8. MONITORING SETUP
# ====================================
log "📊 Monitoring kurulumu..."

# Create monitoring script
cat > monitor_services.sh <<'EOF'
#!/bin/bash
# Service monitoring script

check_service() {
    if systemctl is-active --quiet $1; then
        echo "✅ $1 is running"
    else
        echo "❌ $1 is not running"
        systemctl start $1
    fi
}

# Check services
check_service gavatcore-api
check_service gavatcore-bots

# Check API health
API_HEALTH=$(curl -s http://localhost:8000/health || echo "FAIL")
if [[ "$API_HEALTH" == *"ok"* ]]; then
    echo "✅ API health check passed"
else
    echo "❌ API health check failed"
fi

# Check bot connections
BOTS_STATUS=$(curl -s http://localhost:8000/api/bots/status || echo "{}")
echo "📊 Bot Status: $BOTS_STATUS"
EOF

chmod +x monitor_services.sh

# Add to cron
(crontab -l 2>/dev/null; echo "*/5 * * * * $(pwd)/monitor_services.sh >> $(pwd)/logs/monitoring.log 2>&1") | crontab -

log "✅ Monitoring kuruldu"

# ====================================
# 9. SSL SETUP (Let's Encrypt)
# ====================================
log "🔒 SSL sertifikası ayarlanıyor..."

if command -v certbot &> /dev/null; then
    sudo certbot --nginx -d api.gavatcore.com --non-interactive --agree-tos -m admin@gavatcore.com || warning "SSL kurulumu başarısız"
else
    warning "Certbot bulunamadı, SSL manuel kurulmalı"
fi

# ====================================
# 10. START SERVICES
# ====================================
log "🚀 Servisler başlatılıyor..."

# Stop existing services
sudo systemctl stop gavatcore-api gavatcore-bots 2>/dev/null || true

# Start services
sudo systemctl start gavatcore-api
sleep 5
sudo systemctl start gavatcore-bots

# Enable auto-start
sudo systemctl enable gavatcore-api
sudo systemctl enable gavatcore-bots

log "✅ Servisler başlatıldı"

# ====================================
# 11. HEALTH CHECK
# ====================================
log "🏥 Sistem sağlık kontrolü..."

sleep 10

# Check API
if curl -s http://localhost:8000/health | grep -q "ok"; then
    log "✅ API sağlıklı"
else
    error "API yanıt vermiyor!"
fi

# Check bots
BOTS_STATUS=$(curl -s http://localhost:8000/api/bots/status)
if [[ "$BOTS_STATUS" == *"lara"* ]]; then
    log "✅ Botlar aktif"
else
    warning "Botlar henüz tam aktif değil"
fi

# ====================================
# 12. DEPLOYMENT SUMMARY
# ====================================
echo ""
echo "=============================================="
echo "🎉 GAVATCORE V1.0 DEPLOYMENT TAMAMLANDI! 🎉"
echo "=============================================="
echo ""
echo "📊 ÖZET:"
echo "  - API URL: http://localhost:8000"
echo "  - Public URL: https://api.gavatcore.com"
echo "  - Backup: $BACKUP_DIR"
echo "  - Logs: $LOG_DIR"
echo ""
echo "🔧 KOMUTLAR:"
echo "  - Servisleri kontrol et: sudo systemctl status gavatcore-api gavatcore-bots"
echo "  - Logları görüntüle: journalctl -u gavatcore-api -f"
echo "  - Monitoring: ./monitor_services.sh"
echo ""
echo "📱 FLUTTER PANEL:"
echo "  - cd gavatcore_mobile"
echo "  - flutter build web"
echo "  - Deploy to: https://panel.gavatcore.com"
echo ""
echo "=============================================="

# Create deployment report
cat > $LOG_DIR/deployment_report_$DEPLOY_TIME.json <<EOF
{
    "deployment_time": "$DEPLOY_TIME",
    "python_version": "$PYTHON_VERSION",
    "services": ["gavatcore-api", "gavatcore-bots"],
    "backup_location": "$BACKUP_DIR",
    "test_results": "$LOG_DIR/test_results_$DEPLOY_TIME.log",
    "status": "SUCCESS"
}
EOF

log "✅ Deployment raporu oluşturuldu"

# Final notification
if command -v notify-send &> /dev/null; then
    notify-send "GavatCore Deployment" "v1.0 deployment completed successfully!" -i terminal
fi

exit 0 