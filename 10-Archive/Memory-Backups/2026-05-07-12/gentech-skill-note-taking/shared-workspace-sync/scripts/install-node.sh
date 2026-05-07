#!/bin/bash
# Install Node.js from official binaries (bypasses apt issues)
# Usage: ./install-node.sh [version]  (default: v22.11.0)

set -e

VERSION="${1:-v22.11.0}"
ARCH="linux-x64"
TARBALL="node-${VERSION}-${ARCH}.tar.xz"
URL="https://nodejs.org/dist/${VERSION}/${TARBALL}"
TMPDIR="/tmp/node-install"
INSTALL_DIR="/usr/local/node"

echo "=== Installing Node.js ${VERSION} from ${URL} ==="

# Clean up any previous attempts
rm -rf "${TMPDIR}"
mkdir -p "${TMPDIR}"

# Download
echo "Downloading..."
curl -fsSL "${URL}" -o "${TMPDIR}/${TARBALL}"

# Extract
echo "Extracting..."
tar -xf "${TMPDIR}/${TARBALL}" -C "${TMPDIR}"

# Remove old installation if exists
if [ -d "${INSTALL_DIR}" ]; then
    echo "Removing previous Node.js installation..."
    rm -rf "${INSTALL_DIR}"
fi

# Move to final location
mv "${TMPDIR}/node-${VERSION}-${ARCH}" "${INSTALL_DIR}"

# Symlink binaries to /usr/local/bin
echo "Linking binaries..."
for bin in node npm npx; do
    ln -sf "${INSTALL_DIR}/bin/${bin}" "/usr/local/bin/${bin}"
done

# Verify
echo ""
echo "=== Verification ==="
node --version
npm --version

# Check WebCrypto availability (obsidian-headless requirement)
if node -e "console.log('webcrypto' in globalThis ? 'YES' : 'NO')" | grep -q YES; then
    echo "✓ WebCrypto available"
else
    echo "⚠ WARNING: WebCrypto NOT available — obsidian-headless may fail"
fi

echo ""
echo "Installation complete. If 'ob' command not found, run:"
echo "  ln -sf /usr/local/node/bin/ob /usr/local/bin/ob"