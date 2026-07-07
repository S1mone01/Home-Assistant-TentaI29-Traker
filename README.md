# Tenda i29 Device Tracker for Home Assistant

Modern Home Assistant custom integration for tracking devices connected to the Tenda i29 access point. Compatible with **HACS** (Home Assistant Community Store) and configurable entirely via the Home Assistant user interface (Config Flow).

## Features
- **Config Flow Support**: Configure IP address and password directly from the Home Assistant UI (Settings -> Devices & Services) without touching `configuration.yaml`.
- **Automatic Authentication**: Manages session cookies and logs back in automatically if the session expires.
- **Local Polling**: Polls the Access Point locally using requests, extracting connected client IP and MAC addresses.

## Installation

### Method 1: Via HACS (Recommended)
1. Ensure [HACS](https://hacs.xyz/) is installed and configured in your Home Assistant.
2. In the HACS interface, click on the three dots in the top right corner and select **Custom repositories**.
3. Paste the URL of this repository: `https://github.com/S1mone01/Home-Assistant-TentaI29-Traker`
4. Select **Integration** as the category and click **Add**.
5. Find the **Tenda i29 Device Tracker** integration in HACS and click **Download**.
6. Restart Home Assistant.

### Method 2: Manual Installation
1. Download the source code of this integration.
2. Copy the `custom_components/tenda_i29` directory into your Home Assistant's `config/custom_components/` directory.
3. Restart Home Assistant.

## Configuration

1. In Home Assistant, navigate to **Settings** -> **Devices & Services**.
2. Click **Add Integration** in the bottom right.
3. Search for **Tenda i29 Device Tracker** and select it.
4. Enter the IP address and admin password of your Tenda i29 Access Point.
5. Click **Submit** to complete the setup.
