#!/bin/bash
# Run Odoo module tests for the PLT suite
# Usage: ./run-tests.sh [module_name]

MODULE=${1:-plt_estate,plt_gcg}
cd /root/workspace/kebun
source odoo-venv/bin/activate

echo "=== Testing modules: $MODULE ==="
echo "Starting Odoo test run..."
odoo server \
    -c odoo.conf \
    -d odoo \
    --init="$MODULE" \
    --test-enable \
    --test-tags="/$MODULE" \
    --stop-after-init \
    --log-level=test \
    2>&1 | tee /tmp/odoo-test-output.log

echo ""
echo "=== Test Summary ==="
grep -E "^(OK|FAIL|ERROR)" /tmp/odoo-test-output.log || echo "Check /tmp/odoo-test-output.log for details"
