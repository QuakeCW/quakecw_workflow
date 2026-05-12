#!/bin/bash
# install.sh - Install QuakeCW environment for a single user
# Must be located at $HOME/project/cw/quakecw_workflow/
# Run from that directory after git clone

set -e

RELEASE="kisti_nurion5_2026"
PYTHON_VERSION="3.12.13"
GIT_BASE="git+ssh://git@github.com/QuakeCW"

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKPOINT_FILE="$HOME/.quakecw_install_checkpoints.txt"

# ---- Enforce correct location ----
EXPECTED_DIR="$HOME/project/cw/quakecw_workflow"
if [[ "$REPO_DIR" != "$EXPECTED_DIR" ]]; then
    echo "Error: install.sh must be located at $EXPECTED_DIR"
    echo "Current location: $REPO_DIR"
    echo ""
    echo "Please move quakecw_workflow to \$HOME/project/cw/ first:"
    echo "  mv quakecw_workflow \$HOME/project/cw/"
    exit 1
fi

PROJECT_DIR="$HOME/project"
CW_DIR="$PROJECT_DIR/cw"
SCRATCH_DIR="/scratch/$USER"

# ---- Functions for checkpoint management ----
checkpoint_exists() {
    local step_name="$1"
    grep -q "^$step_name:.*COMPLETED" "$CHECKPOINT_FILE" 2>/dev/null
}

mark_checkpoint() {
    local step_name="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$step_name: COMPLETED at $timestamp" >> "$CHECKPOINT_FILE"
}

ask_rerun() {
    local step_name="$1"
    local step_desc="$2"
    echo ""
    echo "=== Step: $step_desc ==="
    echo "This step was already completed previously."
    read -p "Do you want to run it again? [y/N] " -r
    if [[ "$REPLY" =~ ^[Yy]$ ]]; then
        return 0  # True - user wants to rerun
    else
        echo "  Skipping $step_desc"
        return 1  # False - skip this step
    fi
}

# ---- Initialize checkpoint file ----
mkdir -p "$(dirname "$CHECKPOINT_FILE")"
touch "$CHECKPOINT_FILE"

echo "=== QuakeCW Installation ==="
echo "Home: $HOME"
echo "Project: $PROJECT_DIR"
echo "QuakeCW: $REPO_DIR"
echo "Scratch: $SCRATCH_DIR"
echo "Checkpoints: $CHECKPOINT_FILE"

# ---- Step 1: Download and extract data archives ----
echo ""
echo "Step 1: Downloading and extracting data archives..."

DROPBOX_FILES=(
    "https://www.dropbox.com/scl/fi/nbpi4b2g5fmojlqb1ic63/Velocity-Model_20260507.tar.gz?rlkey=pl9zr5uh4dwvw0c26cpxsr56g&dl=1"
    "https://www.dropbox.com/scl/fi/k8izl7wq9bh889exni5vr/project_local_20260507.tar.gz?rlkey=js1wgvd8e63a9yg167yx2ba1h&dl=1"
    "https://www.dropbox.com/scl/fi/j8bobtoy1inxvh6d1r92o/quakecw_data_20260507.tar.gz?rlkey=95eknfpb7tlxmdbnav83zwoav&dl=1"
)

declare -A EXTRACT_DIRS
EXTRACT_DIRS["project_local_20260507.tar.gz"]="$PROJECT_DIR"
EXTRACT_DIRS["Velocity-Model_20260507.tar.gz"]="$CW_DIR"
EXTRACT_DIRS["quakecw_data_20260507.tar.gz"]="$CW_DIR"

if checkpoint_exists "STEP1_DATA_DOWNLOAD"; then
    if ask_rerun "STEP1_DATA_DOWNLOAD" "Download and extract data archives"; then
        # Rerun the step
        mkdir -p "$PROJECT_DIR" "$CW_DIR" "$SCRATCH_DIR"
        
        for url in "${DROPBOX_FILES[@]}"; do
            filename=$(basename "${url%%\?*}")
            extract_dir="${EXTRACT_DIRS[$filename]}"
            scratch_file="$SCRATCH_DIR/$filename"
            
            if [[ -f "$scratch_file" ]]; then
                echo "  $filename already exists in scratch, skipping download"
            else
                echo "  Downloading $filename to scratch..."
                wget --no-check-certificate -O "$scratch_file" "$url"
            fi
            echo "  Extracting $filename to $extract_dir..."
            tar -xzf "$scratch_file" -C "$extract_dir/"
        done
        
        mark_checkpoint "STEP1_DATA_DOWNLOAD"
    fi
else
    # First time running this step
    mkdir -p "$PROJECT_DIR" "$CW_DIR" "$SCRATCH_DIR"
    
    for url in "${DROPBOX_FILES[@]}"; do
        filename=$(basename "${url%%\?*}")
        extract_dir="${EXTRACT_DIRS[$filename]}"
        scratch_file="$SCRATCH_DIR/$filename"
        
        if [[ -f "$scratch_file" ]]; then
            echo "  $filename already exists in scratch, skipping download"
        else
            echo "  Downloading $filename to scratch..."
            wget --no-check-certificate -O "$scratch_file" "$url"
        fi
        echo "  Extracting $filename to $extract_dir..."
        tar -xzf "$scratch_file" -C "$extract_dir/"
    done
    
    mark_checkpoint "STEP1_DATA_DOWNLOAD"
fi

# ---- Source paths before pip install ----
source "$REPO_DIR/quakecw_config.sh"

# ---- Step 2: Install uv and Python ----
echo ""
echo "Step 2: Installing uv and Python ${PYTHON_VERSION}..."

if checkpoint_exists "STEP2_UV_PYTHON"; then
    if ask_rerun "STEP2_UV_PYTHON" "Install uv and Python"; then
        if ! command -v uv &> /dev/null; then
            echo "  Installing uv binary directly..."
            mkdir -p "$HOME/.local/bin"
            UV_TARBALL="uv-x86_64-unknown-linux-gnu.tar.gz"
            wget --no-check-certificate -O "/tmp/$UV_TARBALL" \
                "https://github.com/astral-sh/uv/releases/latest/download/$UV_TARBALL"
            tar -xzf "/tmp/$UV_TARBALL" -C /tmp/
            cp "/tmp/uv-x86_64-unknown-linux-gnu/uv" "$HOME/.local/bin/"
            cp "/tmp/uv-x86_64-unknown-linux-gnu/uvx" "$HOME/.local/bin/" 2>/dev/null || true
            chmod +x "$HOME/.local/bin/uv" "$HOME/.local/bin/uvx"
            rm -rf "/tmp/$UV_TARBALL" "/tmp/uv-x86_64-unknown-linux-gnu"
        fi
        export PATH="$HOME/.local/bin:$PATH"
        uv python install "$PYTHON_VERSION"
        mark_checkpoint "STEP2_UV_PYTHON"
    fi
else
    if ! command -v uv &> /dev/null; then
        echo "  Installing uv binary directly..."
        mkdir -p "$HOME/.local/bin"
        UV_TARBALL="uv-x86_64-unknown-linux-gnu.tar.gz"
        wget --no-check-certificate -O "/tmp/$UV_TARBALL" \
            "https://github.com/astral-sh/uv/releases/latest/download/$UV_TARBALL"
        tar -xzf "/tmp/$UV_TARBALL" -C /tmp/
        cp "/tmp/uv-x86_64-unknown-linux-gnu/uv" "$HOME/.local/bin/"
        cp "/tmp/uv-x86_64-unknown-linux-gnu/uvx" "$HOME/.local/bin/" 2>/dev/null || true
        chmod +x "$HOME/.local/bin/uv" "$HOME/.local/bin/uvx"
        rm -rf "/tmp/$UV_TARBALL" "/tmp/uv-x86_64-unknown-linux-gnu"
    fi
    export PATH="$HOME/.local/bin:$PATH"
    uv python install "$PYTHON_VERSION"
    mark_checkpoint "STEP2_UV_PYTHON"
fi

# ---- Step 3: Create virtual environment ----
echo ""
echo "Step 3: Creating Python virtual environment..."

VENV_DIR="$HOME/.local/quakecw_venv"

create_venv() {
    # Remove existing directory if it exists
    if [[ -d "$VENV_DIR" ]]; then
        echo "  Removing existing virtual environment at $VENV_DIR..."
        rm -rf "$VENV_DIR"
    fi
    # Create fresh virtual environment
    uv venv "$VENV_DIR" --python "$PYTHON_VERSION"
    echo "  Virtual environment created successfully"
}

if checkpoint_exists "STEP3_VENV"; then
    if ask_rerun "STEP3_VENV" "Create virtual environment"; then
        create_venv
        mark_checkpoint "STEP3_VENV"
    fi
else
    # First time or no checkpoint
    if [[ -d "$VENV_DIR" ]]; then
        echo "  Virtual environment already exists at $VENV_DIR"
        read -p "  Recreate it? (recommended for clean install) [y/N] " -r
        if [[ "$REPLY" =~ ^[Yy]$ ]]; then
            create_venv
        else
            echo "  Using existing virtual environment"
        fi
    else
        create_venv
    fi
    mark_checkpoint "STEP3_VENV"
fi

# Always activate the environment
source "$VENV_DIR/bin/activate"

# ---- Step 4: Install PyPI packages ----
echo ""
echo "Step 4: Installing PyPI packages from requirements.txt..."

if checkpoint_exists "STEP4_PYPI_PACKAGES"; then
    if ask_rerun "STEP4_PYPI_PACKAGES" "Install PyPI packages"; then
        uv pip install -r "$REPO_DIR/requirements.txt"
        mark_checkpoint "STEP4_PYPI_PACKAGES"
    fi
else
    uv pip install -r "$REPO_DIR/requirements.txt"
    mark_checkpoint "STEP4_PYPI_PACKAGES"
fi

# ---- Step 5: Check SSH access to GitHub ----
echo ""
echo "Step 5: Checking GitHub SSH access..."

if checkpoint_exists "STEP5_SSH"; then
    if ask_rerun "STEP5_SSH" "Configure GitHub SSH access"; then
        if ! ssh -o StrictHostKeyChecking=accept-new -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
            echo "  GitHub SSH not configured. Setting up..."
            
            if [[ ! -f "$HOME/.ssh/id_ed25519" ]]; then
                echo "  Generating SSH key..."
                ssh-keygen -t ed25519 -C "nurion5" -f "$HOME/.ssh/id_ed25519" -N ""
                echo ""
                echo "  =========================================="
                echo "  Add this public key to GitHub:"
                echo "  https://github.com/settings/keys"
                echo ""
                cat "$HOME/.ssh/id_ed25519.pub"
                echo ""
                echo "  =========================================="
                read -p "  Press Enter after adding the key to GitHub..."
            fi
            
            mkdir -p "$HOME/.ssh"
            if ! grep -q "Host github.com" "$HOME/.ssh/config" 2>/dev/null; then
                cat >> "$HOME/.ssh/config" << 'SSHEOF'
Host github.com
    HostName ssh.github.com
    Port 443
    User git
SSHEOF
                echo "  SSH config updated for KISTI."
            fi
        fi
        echo "  GitHub SSH access verified."
        mark_checkpoint "STEP5_SSH"
    fi
else
    if ! ssh -o StrictHostKeyChecking=accept-new -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        echo "  GitHub SSH not configured. Setting up..."
        
        if [[ ! -f "$HOME/.ssh/id_ed25519" ]]; then
            echo "  Generating SSH key..."
            ssh-keygen -t ed25519 -C "nurion5" -f "$HOME/.ssh/id_ed25519" -N ""
            echo ""
            echo "  =========================================="
            echo "  Add this public key to GitHub:"
            echo "  https://github.com/settings/keys"
            echo ""
            cat "$HOME/.ssh/id_ed25519.pub"
            echo ""
            echo "  =========================================="
            read -p "  Press Enter after adding the key to GitHub..."
        fi
        
        mkdir -p "$HOME/.ssh"
        if ! grep -q "Host github.com" "$HOME/.ssh/config" 2>/dev/null; then
            cat >> "$HOME/.ssh/config" << 'SSHEOF'
Host github.com
    HostName ssh.github.com
    Port 443
    User git
SSHEOF
            echo "  SSH config updated for KISTI."
        fi
    fi
    echo "  GitHub SSH access verified."
    mark_checkpoint "STEP5_SSH"
fi

# ---- Step 6: Install QuakeCW packages from GitHub releases ----
echo ""
echo "Step 6: Installing QuakeCW packages from GitHub releases..."

if checkpoint_exists "STEP6_QUAKECW_PACKAGES"; then
    if ask_rerun "STEP6_QUAKECW_PACKAGES" "Install QuakeCW packages"; then
        uv pip install "${GIT_BASE}/qcore.git@${RELEASE}.1"
        uv pip install --no-build-isolation "${GIT_BASE}/IM_calculation.git@${RELEASE}"
        uv pip install --no-build-isolation "${GIT_BASE}/Pre-processing.git@${RELEASE}"
        uv pip install --no-build-isolation "${GIT_BASE}/visualisation.git@${RELEASE}"
        uv pip install --no-build-isolation "${GIT_BASE}/slurm_gm_workflow.git@${RELEASE}"
        mark_checkpoint "STEP6_QUAKECW_PACKAGES"
    fi
else
    uv pip install "${GIT_BASE}/qcore.git@${RELEASE}.1"
    uv pip install --no-build-isolation "${GIT_BASE}/IM_calculation.git@${RELEASE}"
    uv pip install --no-build-isolation "${GIT_BASE}/Pre-processing.git@${RELEASE}"
    uv pip install --no-build-isolation "${GIT_BASE}/visualisation.git@${RELEASE}"
    uv pip install --no-build-isolation "${GIT_BASE}/slurm_gm_workflow.git@${RELEASE}"
    mark_checkpoint "STEP6_QUAKECW_PACKAGES"
fi

# ---- Step 7: Add sourcing to .bashrc ----
echo ""
echo "Step 7: Updating .bashrc..."

if checkpoint_exists "STEP7_BASHRC"; then
    if ask_rerun "STEP7_BASHRC" "Update .bashrc configuration"; then
        # Remove existing QuakeCW lines if they exist
        sed -i '/# QuakeCW environment/d' "$HOME/.bashrc" 2>/dev/null
        sed -i '/quakecw_config.sh/d' "$HOME/.bashrc" 2>/dev/null
        sed -i '/VENV_DIR/d' "$HOME/.bashrc" 2>/dev/null
        
        # Add fresh configuration
        echo "" >> "$HOME/.bashrc"
        echo "# QuakeCW environment" >> "$HOME/.bashrc"
        echo "source $REPO_DIR/quakecw_config.sh" >> "$HOME/.bashrc"
        echo "source \"\$VENV_DIR/bin/activate\"" >> "$HOME/.bashrc"
        
        # Add TMOUT unset if not present
        if ! grep -q "TMOUT" "$HOME/.bashrc" 2>/dev/null; then
            cat >> "$HOME/.bashrc" << 'EOF'

# Disable timeout on login nodes only
if [[ -z "$PBS_JOBID" ]]; then
    unset TMOUT
fi
EOF
        fi
        echo "  .bashrc updated"
        mark_checkpoint "STEP7_BASHRC"
    fi
else
    if ! grep -q "quakecw_config.sh" "$HOME/.bashrc" 2>/dev/null; then
        echo "" >> "$HOME/.bashrc"
        echo "# QuakeCW environment" >> "$HOME/.bashrc"
        echo "source $REPO_DIR/quakecw_config.sh" >> "$HOME/.bashrc"
        echo "source \"\$VENV_DIR/bin/activate\"" >> "$HOME/.bashrc"
        echo "  Added sourcing to .bashrc"
    else
        echo "  .bashrc already sources quakecw_config.sh"
    fi
    
    if ! grep -q "TMOUT" "$HOME/.bashrc" 2>/dev/null; then
        cat >> "$HOME/.bashrc" << 'EOF'

# Disable timeout on login nodes only
if [[ -z "$PBS_JOBID" ]]; then
    unset TMOUT
fi
EOF
        echo "  Added TMOUT unset to .bashrc"
    fi
    mark_checkpoint "STEP7_BASHRC"
fi

# ---- Step 8: Optional large data download ----
echo ""
echo "Step 8: Optional SouthKorea100m velocity model (45 GB)..."
echo "  This is a very large download and may take a long time."
echo "  The model will be stored on scratch and symlinked from ~/project."

VM_URL="https://www.dropbox.com/scl/fi/t27ri7nna1l4v2zjwpghy/SouthKoreaVM100m.tar?rlkey=2i70q7kp97zkhs0vj9q58kqtr&st=dmxvflgr&dl=1"
VM_FILE=$(basename "${VM_URL%%\?*}")
VM_SCRATCH="$SCRATCH_DIR/$VM_FILE"

if checkpoint_exists "STEP8_VELOCITY_MODEL"; then
    if ask_rerun "STEP8_VELOCITY_MODEL" "Download SouthKorea100m velocity model (45 GB)"; then
        read -p "  Download SouthKorea100m velocity model? [y/N] " -r
        if [[ "$REPLY" =~ ^[Yy]$ ]]; then
            if [[ -f "$VM_SCRATCH" ]]; then
                echo "  $VM_FILE already exists in scratch, skipping download"
            else
                echo "  Downloading $VM_FILE (45 GB) to scratch..."
                wget --no-check-certificate -O "$VM_SCRATCH" "$VM_URL"
            fi
            
            echo "  Extracting $VM_FILE to $SCRATCH_DIR..."
            tar -xf "$VM_SCRATCH" -C "$SCRATCH_DIR/"
            
            mkdir -p "$VELOCITY_MODEL_DIR/3D"
            ln -sfn "$SCRATCH_DIR/SouthKoreaVM100m" "$VELOCITY_MODEL_DIR/3D/SouthKoreaVM100m"
            echo "  Symlink created: $VELOCITY_MODEL_DIR/3D/SouthKoreaVM100m -> $SCRATCH_DIR/SouthKoreaVM100m"
        else
            echo "  Skipping SouthKorea100m velocity model."
        fi
        mark_checkpoint "STEP8_VELOCITY_MODEL"
    fi
else
    read -p "  Download SouthKorea100m velocity model? [y/N] " -r
    if [[ "$REPLY" =~ ^[Yy]$ ]]; then
        if [[ -f "$VM_SCRATCH" ]]; then
            echo "  $VM_FILE already exists in scratch, skipping download"
        else
            echo "  Downloading $VM_FILE (45 GB) to scratch..."
            wget --no-check-certificate -O "$VM_SCRATCH" "$VM_URL"
        fi
        
        echo "  Extracting $VM_FILE to $SCRATCH_DIR..."
        tar -xf "$VM_SCRATCH" -C "$SCRATCH_DIR/"
        
        mkdir -p "$VELOCITY_MODEL_DIR/3D"
        ln -sfn "$SCRATCH_DIR/SouthKoreaVM100m" "$VELOCITY_MODEL_DIR/3D/SouthKoreaVM100m"
        echo "  Symlink created: $VELOCITY_MODEL_DIR/3D/SouthKoreaVM100m -> $SCRATCH_DIR/SouthKoreaVM100m"
    else
        echo "  Skipping SouthKorea100m velocity model."
    fi
    mark_checkpoint "STEP8_VELOCITY_MODEL"
fi

# ---- Step 9: Clean up tar files (NEW) ----
echo ""
echo "Step 9: Cleaning up archive files..."

# Find all tar and tar.gz files in scratch directory
TAR_FILES=$(find "$SCRATCH_DIR" -maxdepth 1 -type f \( -name "*.tar" -o -name "*.tar.gz" \) 2>/dev/null)

if [[ -n "$TAR_FILES" ]]; then
    echo "  Found archive files in $SCRATCH_DIR:"
    find "$SCRATCH_DIR" -maxdepth 1 -type f \( -name "*.tar" -o -name "*.tar.gz" \) -exec du -h {} \; 2>/dev/null | sed 's/^/    /'
    
    echo ""
    read -p "  Delete these archive files to free up space? [y/N] " -r
    if [[ "$REPLY" =~ ^[Yy]$ ]]; then
        find "$SCRATCH_DIR" -maxdepth 1 -type f \( -name "*.tar" -o -name "*.tar.gz" \) -delete 2>/dev/null
        echo "  ✓ Archive files deleted."
        
        # Record this in checkpoint
        echo "CLEANUP: Archive files deleted at $(date '+%Y-%m-%d %H:%M:%S')" >> "$CHECKPOINT_FILE"
    else
        echo "  Skipping cleanup. Archive files retained in $SCRATCH_DIR"
    fi
else
    echo "  No archive files found in $SCRATCH_DIR"
fi

# ---- Step 10: Optional cleanup of extracted source directories (NEW) ----
echo ""
echo "Step 10: Optional cleanup of extracted source directories..."

read -p "  Delete extracted source directories from scratch? (This will remove extracted files, keeping only final installed data) [y/N] " -r
if [[ "$REPLY" =~ ^[Yy]$ ]]; then
    # List of directories that might have been extracted
    EXTRACTED_DIRS=(
        "$SCRATCH_DIR/Velocity-Model_20260507"
        "$SCRATCH_DIR/project_local_20260507"
        "$SCRATCH_DIR/quakecw_data_20260507"
        "$SCRATCH_DIR/SouthKoreaVM100m"
    )
    
    for dir in "${EXTRACTED_DIRS[@]}"; do
        if [[ -d "$dir" ]]; then
            echo "  Deleting $dir..."
            rm -rf "$dir"
        fi
    done
    echo "  ✓ Extracted directories deleted."
    echo "CLEANUP: Extracted directories deleted at $(date '+%Y-%m-%d %H:%M:%S')" >> "$CHECKPOINT_FILE"
else
    echo "  Skipping cleanup of extracted directories."
fi

# ---- Done ----
echo ""
echo "=============================================="
echo "Installation complete!"
echo ""
echo "Checkpoint file: $CHECKPOINT_FILE"
echo "Please run: source ~/.bashrc"
echo "=============================================="
