# Prerequisites

Last Updated: 7th Aug. '25

## Required Software

1. [Docker Desktop](https://docs.docker.com/get-started/introduction/get-docker-desktop/)
2. [Node / NPM](https://nodejs.org/en/download)
3. [pd4castr cli](https://npmjs.com/packages/<cli-tool-package-name>)

## Quick Guide - Windows

Start by downloading [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install) and installing it.

Once installed, download the latest [NVM installer (`nvm-setup.exe`)](https://github.com/coreybutler/nvm-windows/releases) from Github and install it.

Once complete, run **Windows Powershell** as an administrator and run the following commands:

```bash
# 1. Install Node 20.x
nvm install 20
nvm use 20

# 2. Install the pdr4casstr CLI
npm install -g @pd4castr/cli

# 3. Verify the installation worked
pd4castr help
```

## Quick Guide - MacOS

TODO - use brew

## Quick Guide - Ubuntu

TODO - use apt-get
