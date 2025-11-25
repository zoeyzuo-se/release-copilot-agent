#!/bin/bash

# Post-create script to install Azure CLI
set -e

echo "Installing Azure CLI..."

# Update package list
sudo apt-get update

# Install prerequisites
sudo apt-get install -y ca-certificates curl apt-transport-https lsb-release gnupg

# Download and install the Microsoft signing key
curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null

# Add the Azure CLI software repository
AZ_REPO=$(lsb_release -cs)
# Detect architecture and set appropriate value
ARCH=$(dpkg --print-architecture)
echo "deb [arch=$ARCH] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | sudo tee /etc/apt/sources.list.d/azure-cli.list

# Update repository information and install the Azure CLI
sudo apt-get update
sudo apt-get install -y azure-cli

# Verify installation
az --version

echo "Azure CLI installation completed successfully!"
echo "Note: Azure credentials are mounted from host machine."
echo "Please authenticate with 'az login' on your host machine first."