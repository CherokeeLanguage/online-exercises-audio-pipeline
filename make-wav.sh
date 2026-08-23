#!/bin/bash

# --- CONFIGURATION ---
SOURCE_DIR="./aiden_files"           # Where your m4a files are
DEST_DIR="./wav_output"  # Where the wav files will go
# ---------------------

# Create the output directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Loop through all m4a files in the source directory
for file in "$SOURCE_DIR"/*.m4a; do
    
    # Check if any m4a files actually exist to avoid errors
    [ -e "$file" ] || continue

    # Get the filename without the path and without the extension
    filename=$(basename "$file" .m4a)

    echo "Converting: $filename.m4a ..."

    # Run ffmpeg
    # -i: input file
    # -n: skip if file already exists (use -y to overwrite)
    ffmpeg -i "$file" -n "$DEST_DIR/${filename}.wav" 2>/dev/null

    if [ $? -eq 0 ]; then
        echo "✅ Successfully converted to $DEST_DIR/${filename}.wav"
    else
        echo "❌ Failed to convert $filename"
    fi
done

echo "--- Process Complete ---"