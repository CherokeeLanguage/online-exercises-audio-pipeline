#!/bin/bash

# --- CONFIGURATION ---
# Add your IDs here, separated by spaces
ids=(14 24 30 37 42 44 45 49 50 51 62 71 78 92 104 153 157 195 261)

# Define your source and destination directories
SOURCE_DIR="./data/cnd/card_audio"
DEST_DIR="./aiden_files/"
# ---------------------

# Create destination if it doesn't exist
mkdir -p "$DEST_DIR"

echo "Starting copy process..."

for id in "${ids[@]}"; do
    # Pad the ID to 4 digits (e.g., 23 -> 0023)
    padded_id=$(printf "%04d" "$id")
    
    # Construct the pattern: Sentence_for_entry_0023*.m4a
    # The * handles both the versioned (_01) and non-versioned files
    pattern="${SOURCE_DIR}/Sentence_for_entry_${padded_id}*.m4a"
    
    # Check if any files match the pattern before trying to copy
    if ls $pattern >/dev/null 2>&1; then
        cp $pattern "$DEST_DIR/"
        echo "✅ Copied files for ID: $padded_id"
    else
        echo "❌ No files found for ID: $padded_id"
    fi
done

echo "Done!"