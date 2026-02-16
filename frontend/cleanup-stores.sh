#!/bin/bash
set -e

echo "🧹 FRONTEND STORES CLEANUP"
echo "=========================="
echo ""

cd ~/Lernsystem/frontend

# Check which stores are duplicates
echo "📋 Checking for duplicate stores..."
echo ""

STORES_DIR="src/application/stores"

# List all loose .store.ts files
echo "Loose stores found:"
find $STORES_DIR -maxdepth 1 -name "*.store.ts" -type f

echo ""
echo "⚠️  These should be in modules/ subdirectories!"
echo ""

# Create backup
echo "📦 Creating backup..."
mkdir -p .backups/stores
cp -r $STORES_DIR/*.store.ts .backups/stores/ 2>/dev/null || echo "No loose stores to backup"

echo ""
echo "🔍 Checking which stores are already in modules/..."
echo ""

# Check each loose store
for file in $STORES_DIR/*.store.ts; do
    if [ -f "$file" ]; then
        basename=$(basename "$file")
        echo "Checking: $basename"
        
        # Search in modules
        found=$(find $STORES_DIR/modules -name "$basename" 2>/dev/null)
        
        if [ -n "$found" ]; then
            echo "  ✅ Found in: $found"
            echo "  ❌ Can be deleted: $file"
        else
            echo "  ⚠️  NOT in modules - needs migration!"
        fi
        echo ""
    fi
done

echo ""
echo "=========================="
echo "✅ Analysis complete!"
echo ""
echo "Next steps:"
echo "1. Review the output above"
echo "2. Decide which to delete/migrate"
echo "3. Update imports in components"
