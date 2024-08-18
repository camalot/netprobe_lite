#!/usr/bin/env bash

if [[ "${NP_MODULE^^}" == "NETPROBE" ]]; then
	python3 netprobe.py
	return
elif [[ "${NP_MODULE^^}" == "PRESENTATION" ]]; then
	python3 presentation.py
	return
elif [[ "${NP_MODULE^^}" == "SPEEDTEST" ]]; then
	python3 netprobe_speedtest.py
	return
elif [[ "${NP_MODULE^^}" == "FULL" ]]; then
	python3 /app/main.py
	return
else
	/bin/bash
	return
fi

exit 0
