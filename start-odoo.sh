#!/bin/bash
# Odoo 19 Development Server Startup Script
# Usage: ./start-odoo.sh

cd /root/workspace/kebun
source odoo-venv/bin/activate
odoo server -c odoo.conf -d odoo
