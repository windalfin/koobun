#!/bin/bash
# Kill any existing odoo processes to prevent deadlocks
ps aux | grep "[o]doo" | awk '{print $2}' | xargs -r kill -9 2>/dev/null
sleep 2

# Source the venv and run
source /root/workspace/kebun/odoo-venv/bin/activate
odoo server -c /root/workspace/kebun/odoo.conf -d odoo --init=plt_estate --stop-after-init 2>&1
exit_code=$?
echo "EXIT_CODE: $exit_code"
exit $exit_code
