# Ucademy

A Python app that delivers short-form educational videos tailored to your learning interests.

![version](https://img.shields.io/badge/version-1.0.0-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![python](https://img.shields.io/badge/python-3.10+-yellow)

## Table of contents
- [Features](#features)
- [Installation](#installation)
- [Running](#running)
- [License](#license)

## Features

- Browse short-form educational videos by topic
- Community-uploaded content from creators
- Lightweight client-server architecture

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/Barak112/Ucademy.git
cd Ucademy
pip install -r requirements.txt
```

## Running

**1. Configure the server IP**

In `common_packages/settings.py`, set `server_ip` to your server's IP address.

**2. Mark source directories**

In PyCharm, right-click each folder below and select **Mark Directory as → Sources Root**:

- `classes`
- `client`
- `client/graphics`
- `client/graphics/components`
- `common_packages`
- `server`

**3. Start the server**

```bash
python server/serverlogic.py
```

**4. Start the client**

```bash
python client/clientlogic.py
```

## License

[MIT](./LICENSE) © Barak Ben Meir, 2026