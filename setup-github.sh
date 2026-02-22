#!/usr/bin/env bash
# Script para configurar GitHub e fazer deploy

USERNAME="jarvis-openclaw"
EMAIL="2traderline@gmail.com"
PASSWORD='2s@K9snrgnB5yGh'

# Configurar git
git config user.email "$EMAIL"
git config user.name "$USERNAME"

# Inicializar repo
git init

# Adicionar ficheiros
git add .

# Commit
git commit -m "Polymarket Trading Dashboard v1.0"

# Criar branch main
git branch -M main

# Configurar remote (usando credential helper)
git remote add origin https://github.com/$USERNAME/polymarket-trading.git

# Tentar push - vai pedir credenciais interativamente
echo "A fazer push para GitHub..."
git push -u origin main

echo ""
echo "Se o push falhar, use manualmente:"
echo "Username: $USERNAME"
echo "Password: $PASSWORD"