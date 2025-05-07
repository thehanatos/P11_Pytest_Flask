#!/bin/bash

# Check if a bug name is in the command
if [ -z "$1" ]; then
  echo "❌ Merci de donner un nom de bug. Exemple : ./new-fix.sh bug-456"
  exit 1
fi

BUG_NAME=$1
BRANCH_NAME="fix/$BUG_NAME"

echo "🔁 Passage sur la branche QA et mise à jour..."
git checkout QA && git pull origin QA

echo "🌱 Création de la branche $BRANCH_NAME à partir de QA..."
git checkout -b $BRANCH_NAME

echo "✅ Branche $BRANCH_NAME créée. Tu peux maintenant commencer le fix."