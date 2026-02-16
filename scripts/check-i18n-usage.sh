
#!/bin/bash

echo "======================================================================"
echo "🔍 i18n LOCALES AUDIT - Ungenutzter Keys Finder"
echo "======================================================================"
echo ""

FRONTEND_PATH="$HOME/Lernsystem/frontend/src"
LOCALES_PATH="$FRONTEND_PATH/infrastructure/i18n/locales"

# Farben
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "📂 Pfade:"
echo "  Frontend: $FRONTEND_PATH"
echo "  Locales:  $LOCALES_PATH"
echo ""

# =============================================================================
# 1. LOCALE FILES ANALYSE
# =============================================================================
echo "======================================================================"
echo "1️⃣  LOCALE FILES ÜBERSICHT"
echo "======================================================================"
echo ""

for lang in de en pl; do
    if [ -f "$LOCALES_PATH/$lang.json" ]; then
        keys=$(jq -r 'paths(scalars) | join(".")' "$LOCALES_PATH/$lang.json" 2>/dev/null | wc -l)
        size=$(du -h "$LOCALES_PATH/$lang.json" | cut -f1)
        echo -e "${GREEN}✅${NC} $lang.json - $keys Keys ($size)"
    else
        echo -e "${RED}❌${NC} $lang.json - Nicht gefunden"
    fi
done

echo ""

# =============================================================================
# 2. EXTRAHIERE ALLE KEYS AUS DE.JSON (Referenz)
# =============================================================================
echo "======================================================================"
echo "2️⃣  ALLE KEYS EXTRAHIEREN (de.json als Referenz)"
echo "======================================================================"
echo ""

if [ ! -f "$LOCALES_PATH/de.json" ]; then
    echo -e "${RED}❌ de.json nicht gefunden!${NC}"
    exit 1
fi

echo "Extrahiere Keys aus de.json..."
jq -r 'paths(scalars) | join(".")' "$LOCALES_PATH/de.json" > /tmp/all_i18n_keys.txt
TOTAL_KEYS=$(wc -l < /tmp/all_i18n_keys.txt)
echo -e "${GREEN}✅ $TOTAL_KEYS Keys gefunden${NC}"
echo ""

# =============================================================================
# 3. FINDE VERWENDETE KEYS IM CODE
# =============================================================================
echo "======================================================================"
echo "3️⃣  VERWENDETE KEYS IM CODE FINDEN"
echo "======================================================================"
echo ""

echo "Suche nach \$t('...') und t('...') Patterns..."

# Erstelle temporäre Datei für gefundene Keys
> /tmp/used_i18n_keys.txt

# Suche nach $t('key') Pattern
grep -roh "\$t(['\"][^'\"]*['\"])" "$FRONTEND_PATH" --include="*.vue" --include="*.ts" --include="*.js" 2>/dev/null \
    | sed "s/\$t(['\"]//g" | sed "s/['\"])//g" \
    | sort -u >> /tmp/used_i18n_keys.txt

# Suche nach t('key') Pattern (Composition API)
grep -roh "t(['\"][^'\"]*['\"])" "$FRONTEND_PATH" --include="*.vue" --include="*.ts" --include="*.js" 2>/dev/null \
    | sed "s/t(['\"]//g" | sed "s/['\"])//g" \
    | sort -u >> /tmp/used_i18n_keys.txt

# Suche nach useI18n() + t() Pattern
grep -roh "{{ t(['\"][^'\"]*['\"])" "$FRONTEND_PATH" --include="*.vue" 2>/dev/null \
    | sed "s/{{ t(['\"]//g" | sed "s/['\"])//g" \
    | sort -u >> /tmp/used_i18n_keys.txt

# Dedupliziere
sort -u /tmp/used_i18n_keys.txt > /tmp/used_i18n_keys_unique.txt
mv /tmp/used_i18n_keys_unique.txt /tmp/used_i18n_keys.txt

USED_KEYS=$(wc -l < /tmp/used_i18n_keys.txt)
echo -e "${GREEN}✅ $USED_KEYS verwendete Keys gefunden${NC}"
echo ""

# =============================================================================
# 4. FINDE UNGENUTZTE KEYS
# =============================================================================
echo "======================================================================"
echo "4️⃣  UNGENUTZTE KEYS IDENTIFIZIEREN"
echo "======================================================================"
echo ""

echo "Vergleiche definierte Keys mit verwendeten Keys..."
comm -23 <(sort /tmp/all_i18n_keys.txt) <(sort /tmp/used_i18n_keys.txt) > /tmp/unused_i18n_keys.txt

UNUSED_KEYS=$(wc -l < /tmp/unused_i18n_keys.txt)

if [ $UNUSED_KEYS -eq 0 ]; then
    echo -e "${GREEN}🎉 PERFEKT! Alle Keys werden verwendet!${NC}"
else
    echo -e "${YELLOW}⚠️  $UNUSED_KEYS ungenutzte Keys gefunden${NC}"
    echo ""
    echo "Erste 20 ungenutzte Keys:"
    echo "----------------------------------------------------------------------"
    head -20 /tmp/unused_i18n_keys.txt | nl
    
    if [ $UNUSED_KEYS -gt 20 ]; then
        echo "... und $((UNUSED_KEYS - 20)) weitere"
    fi
fi

echo ""

# =============================================================================
# 5. KATEGORIE-ANALYSE
# =============================================================================
echo "======================================================================"
echo "5️⃣  KATEGORIE-ANALYSE"
echo "======================================================================"
echo ""

echo "Top-Level Keys (Kategorien):"
echo "----------------------------------------------------------------------"
jq -r 'keys[]' "$LOCALES_PATH/de.json" 2>/dev/null | while read category; do
    cat_keys=$(jq -r ".[\"$category\"] | paths(scalars) | length" "$LOCALES_PATH/de.json" 2>/dev/null)
    
    # Zähle verwendete Keys in dieser Kategorie
    used_in_cat=$(grep -c "^$category\." /tmp/used_i18n_keys.txt 2>/dev/null || echo "0")
    
    # Berechne Nutzungsrate
    if [ "$cat_keys" != "null" ] && [ "$cat_keys" -gt 0 ]; then
        usage_percent=$((used_in_cat * 100 / cat_keys))
        
        if [ $usage_percent -ge 80 ]; then
            color=$GREEN
        elif [ $usage_percent -ge 50 ]; then
            color=$YELLOW
        else
            color=$RED
        fi
        
        echo -e "${color}$category${NC}: $used_in_cat / $cat_keys Keys verwendet (${usage_percent}%)"
    fi
done

echo ""

# =============================================================================
# 6. SPRACH-SYNC CHECK
# =============================================================================
echo "======================================================================"
echo "6️⃣  SPRACH-SYNCHRONISATION CHECK"
echo "======================================================================"
echo ""

echo "Prüfe ob alle Sprachen die gleichen Keys haben..."

# DE Keys
jq -r 'paths(scalars) | join(".")' "$LOCALES_PATH/de.json" | sort > /tmp/de_keys.txt

# EN Keys
if [ -f "$LOCALES_PATH/en.json" ]; then
    jq -r 'paths(scalars) | join(".")' "$LOCALES_PATH/en.json" | sort > /tmp/en_keys.txt
    
    # Fehlende in EN
    missing_en=$(comm -23 /tmp/de_keys.txt /tmp/en_keys.txt | wc -l)
    if [ $missing_en -eq 0 ]; then
        echo -e "${GREEN}✅ EN: Alle Keys vorhanden${NC}"
    else
        echo -e "${RED}❌ EN: $missing_en Keys fehlen${NC}"
        echo "   Erste 5 fehlende:"
        comm -23 /tmp/de_keys.txt /tmp/en_keys.txt | head -5 | sed 's/^/     • /'
    fi
fi

# PL Keys
if [ -f "$LOCALES_PATH/pl.json" ]; then
    jq -r 'paths(scalars) | join(".")' "$LOCALES_PATH/pl.json" | sort > /tmp/pl_keys.txt
    
    # Fehlende in PL
    missing_pl=$(comm -23 /tmp/de_keys.txt /tmp/pl_keys.txt | wc -l)
    if [ $missing_pl -eq 0 ]; then
        echo -e "${GREEN}✅ PL: Alle Keys vorhanden${NC}"
    else
        echo -e "${RED}❌ PL: $missing_pl Keys fehlen${NC}"
        echo "   Erste 5 fehlende:"
        comm -23 /tmp/de_keys.txt /tmp/pl_keys.txt | head -5 | sed 's/^/     • /'
    fi
fi

echo ""

# =============================================================================
# 7. STATISTIK & EMPFEHLUNGEN
# =============================================================================
echo "======================================================================"
echo "📊 FINALE STATISTIK"
echo "======================================================================"
echo ""

USAGE_PERCENT=$((USED_KEYS * 100 / TOTAL_KEYS))

echo "Gesamt Keys:         $TOTAL_KEYS"
echo "Verwendete Keys:     $USED_KEYS (${USAGE_PERCENT}%)"
echo "Ungenutzte Keys:     $UNUSED_KEYS ($((100 - USAGE_PERCENT))%)"
echo ""

if [ $USAGE_PERCENT -ge 80 ]; then
    echo -e "${GREEN}✅ SEHR GUT! Hohe Nutzungsrate (≥80%)${NC}"
elif [ $USAGE_PERCENT -ge 60 ]; then
    echo -e "${YELLOW}⚠️  MITTEL: Einiges an ungenutzten Keys (60-80%)${NC}"
    echo "   Empfehlung: Cleanup lohnt sich!"
else
    echo -e "${RED}❌ ACHTUNG: Viele ungenutzte Keys (<60%)${NC}"
    echo "   Empfehlung: Dringend aufräumen!"
fi

echo ""
echo "======================================================================"
echo "💾 EXPORT FILES"
echo "======================================================================"
echo ""

# Speichere Reports
cp /tmp/unused_i18n_keys.txt ~/i18n-unused-keys.txt
cp /tmp/used_i18n_keys.txt ~/i18n-used-keys.txt
cp /tmp/all_i18n_keys.txt ~/i18n-all-keys.txt

echo "✅ Reports gespeichert:"
echo "   • ~/i18n-unused-keys.txt   - Ungenutzte Keys"
echo "   • ~/i18n-used-keys.txt     - Verwendete Keys"
echo "   • ~/i18n-all-keys.txt      - Alle definierten Keys"
echo ""

echo "======================================================================"
echo "🔧 NÄCHSTE SCHRITTE"
echo "======================================================================"
echo ""

if [ $UNUSED_KEYS -gt 0 ]; then
    echo "1. Prüfe ungenutzte Keys in ~/i18n-unused-keys.txt"
    echo "2. Entscheide welche Keys wirklich gelöscht werden können"
    echo "3. Erstelle Backup: cp de.json de.json.backup"
    echo "4. Nutze das Cleanup-Script (wird generiert)"
    echo ""
    
    # Generiere Cleanup-Script
    cat > ~/cleanup-i18n.sh << 'CLEANUP_EOF'
#!/bin/bash
# i18n Cleanup Script - AUTO-GENERATED
# WARNUNG: Erstelle erst ein Backup!

LOCALES_PATH="$HOME/Lernsystem/frontend/src/infrastructure/i18n/locales"

echo "🧹 i18n Cleanup"
echo "Erstelle Backups..."
cp "$LOCALES_PATH/de.json" "$LOCALES_PATH/de.json.backup"
cp "$LOCALES_PATH/en.json" "$LOCALES_PATH/en.json.backup"
cp "$LOCALES_PATH/pl.json" "$LOCALES_PATH/pl.json.backup"

echo "Lösche ungenutzte Keys..."

# Lese ungenutzte Keys
while IFS= read -r key; do
    echo "  Lösche: $key"
    
    # Lösche in DE
    jq "del(.$key)" "$LOCALES_PATH/de.json" > /tmp/de.json.tmp && mv /tmp/de.json.tmp "$LOCALES_PATH/de.json"
    
    # Lösche in EN
    jq "del(.$key)" "$LOCALES_PATH/en.json" > /tmp/en.json.tmp && mv /tmp/en.json.tmp "$LOCALES_PATH/en.json"
    
    # Lösche in PL
    jq "del(.$key)" "$LOCALES_PATH/pl.json" > /tmp/pl.json.tmp && mv /tmp/pl.json.tmp "$LOCALES_PATH/pl.json"
    
done < ~/i18n-unused-keys.txt

echo "✅ Cleanup abgeschlossen!"
echo "Backups: *.json.backup"
CLEANUP_EOF
    
    chmod +x ~/cleanup-i18n.sh
    echo "   ✅ Cleanup-Script generiert: ~/cleanup-i18n.sh"
else
    echo "✅ Keine Aktion nötig - alle Keys werden verwendet!"
fi

echo ""
echo "======================================================================"
echo "✅ ANALYSE ABGESCHLOSSEN"
echo "======================================================================"
