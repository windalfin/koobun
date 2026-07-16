#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive

echo "Step 1: Fix dpkg and install packages..."
rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock /var/cache/apt/archives/lock
dpkg --configure -a 2>/dev/null || true
apt-get update -qq 2>&1 | tail -1
apt-get install -y -qq nginx git postgresql-client-16 postgresql-16 python3-venv python3-dev libpq-dev libxml2-dev libxslt1-dev libjpeg-dev zlib1g-dev libsasl2-dev libldap2-dev build-essential curl 2>&1 | tail -3
echo "Step 1 DONE"

echo "Step 2: Start PostgreSQL..."
systemctl enable postgresql
systemctl start postgresql
echo "Step 2 DONE"

echo "Step 3: Create Odoo user and DB..."
su - postgres -c "createuser -s odoo" 2>/dev/null || true
su - postgres -c "createdb -O odoo odoo" 2>/dev/null || true
echo "Step 3 DONE"

echo "Step 4: Setup Odoo venv..."
useradd -m -d /opt/odoo -U -r -s /bin/bash odoo 2>/dev/null || true
su - odoo -c "python3 -m venv /opt/odoo/odoo-venv"
su - odoo -c "/opt/odoo/odoo-venv/bin/pip install --upgrade pip setuptools wheel"
echo "Step 4 DONE"

echo "Step 5: Install Odoo..."
su - odoo -c "/opt/odoo/odoo-venv/bin/pip install odoo -f https://nightly.odoo.com/19.0/nightly/deb/"
echo "Step 5 DONE"

echo "Step 6: Clone Koobun..."
mkdir -p /opt/odoo/addons/19.0
cd /opt/odoo/addons/19.0
git clone https://github.com/windalfin/koobun.git . 2>&1 || echo "Already cloned"
echo "Step 6 DONE"

echo "Step 7: Create Odoo config..."
cat > /opt/odoo/odoo.conf << 'CONF'
[options]
addons_path = /opt/odoo/odoo-venv/lib/python3.12/site-packages/odoo/addons,/opt/odoo/addons/19.0
db_host = localhost
db_port = 5432
db_user = odoo
db_password = False
admin_passwd = koobun-admin-2026
http_port = 8069
workers = 2
max_cron_threads = 1
CONF
echo "Step 7 DONE"

echo "Step 8: Install Koobun modules..."
su - odoo -c "/opt/odoo/odoo-venv/bin/odoo -c /opt/odoo/odoo.conf -d odoo --init=plt_estate,plt_gcg,plt_harvest,plt_transport,plt_sales,plt_payroll,plt_upkeep,plt_planning,plt_plasma,plt_compliance,plt_nursery,plt_reporting --stop-after-init" 2>&1 | tail -5
echo "Step 8 DONE"

echo "Step 9: Configure Nginx..."
cat > /etc/nginx/sites-available/koobun << 'NGINX'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    client_max_body_size 200m;
}
NGINX
ln -sf /etc/nginx/sites-available/koobun /etc/nginx/sites-enabled/koobun
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
echo "Step 9 DONE"

echo "Step 10: Create systemd service..."
cat > /etc/systemd/system/koobun.service << 'SERVICE'
[Unit]
Description=Koobun Plantation Management (Odoo 19)
After=network.target postgresql.service

[Service]
Type=simple
User=odoo
ExecStart=/opt/odoo/odoo-venv/bin/odoo -c /opt/odoo/odoo.conf -d odoo
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE
systemctl daemon-reload
systemctl enable koobun
systemctl start koobun
echo "Step 10 DONE"

echo ""
echo "=== DEPLOY COMPLETE ==="
sleep 3
curl -s -o /dev/null -w "HTTP Status: %{http_code}" http://localhost:80/web/login
echo ""
