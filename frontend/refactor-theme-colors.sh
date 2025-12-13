#!/bin/bash

# Theme Color Refactoring Script
# Replaces all hard-coded Tailwind colors with CSS variables

# Define the source directory
SRC_DIR="./src"

# Function to replace colors in a file
refactor_file() {
    local file="$1"
    echo "Processing: $file"

    # Backup file
    cp "$file" "$file.bak"

    # Replace text colors
    sed -i 's/text-gray-900\b/text-[var(--color-text-primary)]/g' "$file"
    sed -i 's/text-gray-800\b/text-[var(--color-text-primary)]/g' "$file"
    sed -i 's/text-gray-700\b/text-[var(--color-text-secondary)]/g' "$file"
    sed -i 's/text-gray-600\b/text-[var(--color-text-secondary)]/g' "$file"
    sed -i 's/text-gray-500\b/text-[var(--color-text-secondary)]/g' "$file"
    sed -i 's/text-gray-400\b/text-[var(--color-text-tertiary)]/g' "$file"

    # Replace background colors
    sed -i 's/bg-white\b/bg-[var(--color-surface)]/g' "$file"
    sed -i 's/bg-gray-50\b/bg-[var(--color-bg)]/g' "$file"
    sed -i 's/bg-gray-100\b/bg-[var(--color-surface-secondary)]/g' "$file"
    sed -i 's/bg-gray-200\b/bg-[var(--color-surface-secondary)]/g' "$file"
    sed -i 's/bg-gray-800\b/bg-[var(--color-surface)]/g' "$file"
    sed -i 's/bg-gray-900\b/bg-[var(--color-surface)]/g' "$file"
    sed -i 's/bg-gray-950\b/bg-[var(--color-bg)]/g' "$file"

    # Replace border colors
    sed -i 's/border-gray-200\b/border-[var(--color-border)]/g' "$file"
    sed -i 's/border-gray-300\b/border-[var(--color-border)]/g' "$file"
    sed -i 's/border-gray-400\b/border-[var(--color-border-strong)]/g' "$file"
    sed -i 's/border-gray-600\b/border-[var(--color-border)]/g' "$file"
    sed -i 's/border-gray-700\b/border-[var(--color-border)]/g' "$file"

    # Remove dark: modifiers for replaced colors (aggressive cleanup)
    sed -i 's/ dark:text-gray-[0-9]\+//g' "$file"
    sed -i 's/ dark:bg-gray-[0-9]\+//g' "$file"
    sed -i 's/ dark:border-gray-[0-9]\+//g' "$file"
    sed -i 's/ dark:hover:bg-gray-[0-9]\+//g' "$file"
    sed -i 's/ dark:hover:text-gray-[0-9]\+//g' "$file"

    # Remove shadow dark: modifiers
    sed -i 's/ dark:shadow-[a-z]\+//g' "$file"

    echo "✓ Completed: $file"
}

# Find all .vue files and process them
find "$SRC_DIR" -name "*.vue" -type f | while read -r file; do
    refactor_file "$file"
done

echo ""
echo "==================================="
echo "Refactoring completed!"
echo "Backup files created with .bak extension"
echo "==================================="
