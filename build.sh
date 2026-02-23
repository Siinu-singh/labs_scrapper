#!/bin/bash

# Install system dependencies for Chromium/Selenium
apt-get update
apt-get install -y chromium-browser

# Install Python dependencies
pip install -r requirements.txt
