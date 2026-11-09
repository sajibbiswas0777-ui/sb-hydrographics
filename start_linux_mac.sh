#!/bin/bash
echo "============================================================"
echo "  🌊 SB HYDRO-GRAPHICS - Water Transfer Printing Software"
echo "============================================================"
echo "Starting local server on http://localhost:5000 ..."

if command -v python3 &>/dev/null; then
    echo "[OK] Python3 detected."
    python3 server.py
elif command -v node &>/dev/null; then
    echo "[OK] Node.js detected."
    node server.py
else
    echo "[ERROR] Python 3 or Node.js is required to run the server."
fi
