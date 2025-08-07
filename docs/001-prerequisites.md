# Prerequisites

_Last Updated: 7th Aug. '25_

**Table of Contents**

- [Required Software](#required-software)
- [Quick Guide - Ubuntu via Windows WSL 2](#quick-guide---ubuntu-via-windows-wsl-2)
- [Quick Guide - Windows](#quick-guide---windows)
- [Quick Guide - MacOS](#quick-guide---macos)
- [Quick Guide - Ubuntu](#quick-guide---ubuntu)

## Required Software

1. [Docker Desktop](https://docs.docker.com/get-started/introduction/get-docker-desktop/)
2. [Git](https://git-scm.com/downloads)
3. [Node / NPM](https://nodejs.org/en/download)
4. [pd4castr cli](https://npmjs.com/packages/<cli-tool-package-name>)

## Quick Guide - Ubuntu via Windows WSL 2

First, download
[Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install)
and install it in your Windows environment.

Once Docker Desktop is installed, open your WSL 2 terminal and run the following
commands:

```bash
# 1. Update your local package index
sudo apt update

# 2. Install Git
sudo apt install git

# 3. Install NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# 3. Install Node 20.x
nvm install 20
nvm use 20

# 4. Install the pd4castr CLI
npm install -g @pd4castr/cli

# 5. Verify the installation worked
pd4castr help
```

## Quick Guide - Windows

First, download
[Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install)
and install it. If you are unsure, you most likely want the **WSL 2 based
engine**.

Second, download [Git](https://gitforwindows.org/) and install it. Be sure to
select the standard Git Windows Command Prompt (**not** Git Bash).

Once Docker & Git are installed, download the latest
[NVM installer (`nvm-setup.exe`)](https://github.com/coreybutler/nvm-windows/releases)
from Github and install it.

Once complete, run **Windows Powershell** as an administrator and run the
following commands:

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

First, download
[Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/)
and install it.

The remainder of the setup process can be completed via the terminal. Run the
following commands:

```bash
# 1. Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install Git & NVM
brew install git nvm

# 3. Install Node 20.x
nvm install 20
nvm use 20

# 4. Install the pdr4casstr CLI
npm install -g @pd4castr/cli

# 5. Verify the installation worked
pd4castr help
```

## Quick Guide - Ubuntu

On Ubuntu, installing Docker Engine is a well documented process. Follow the
instructions on the official
[Docker documentation](https://docs.docker.com/engine/install/ubuntu/).

Once Docker is installed, open your terminal and run the following commands:

```bash
# 1. Update your local package index
sudo apt update

# 2. Install Git
sudo apt install git

# 3. Install NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# 3. Install Node 20.x
nvm install 20
nvm use 20

# 4. Install the pd4castr CLI
npm install -g @pd4castr/cli

# 5. Verify the installation worked
pd4castr help
```
