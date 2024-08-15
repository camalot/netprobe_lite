#!/usr/bin/env bash

if [[ "${NP_MODULE^^}" == "NETPROBE" ]]; then
    python3 netprobe.py
elif [[ "${NP_MODULE^^}" == "PRESENTATION" ]]; then 
    python3 presentation.py
elif [[ "${NP_MODULE^^}" == "SPEEDTEST" ]]; then 
    python3 netprobe_speedtest.py; 
elif [[ "${NP_MODULE^^}" == "FULL" ]]; then
    python3 /app/main.py
else 
    /bin/bash
fi