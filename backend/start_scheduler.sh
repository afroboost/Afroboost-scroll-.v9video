#!/bin/bash
# =========================================
# Script de démarrage du Scheduler Afroboost
# MODE DAEMON PAR DÉFAUT
# =========================================
# Usage:
#   ./start_scheduler.sh           # Mode DAEMON (boucle toutes les 30s)
#   ./start_scheduler.sh --once    # Exécution unique
#   ./start_scheduler.sh --dry-run # Mode test sans envoi réel
#   ./start_scheduler.sh &         # Lancer en arrière-plan

cd /app/backend

if [ "$1" == "--once" ]; then
    echo "📧 Exécution unique du scheduler..."
    python3 scheduler.py --once
elif [ "$1" == "--dry-run" ]; then
    echo "🧪 Mode test (dry-run)..."
    python3 scheduler.py --dry-run --once
else
    echo "🔄 Démarrage du scheduler en MODE DAEMON (CTRL+C pour arrêter)..."
    echo "📱 Les campagnes programmées seront vérifiées toutes les 30 secondes."
    python3 scheduler.py
fi
