#!/bin/bash
# Dvojnoj klik po etomu fajlu zapuskaet programmu poiska mestnosti.
cd "$(dirname "$0")"
.venv/bin/python poisk.py
