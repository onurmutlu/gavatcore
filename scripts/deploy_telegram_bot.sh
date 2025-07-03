#!/bin/bash

# 🤖 GavatCore Telegram Bot Deployment Script

set -e

echo "🚀 Deploying GavatCore Telegram Bot..."

# Check if bot token is provided
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ Error: TELEGRAM_BOT_TOKEN environment variable is required"
    echo "Usage: TELEGRAM_BOT_TOKEN=your_token ./deploy_telegram_bot.sh"
    exit 1
fi

# Create network if it doesn't exist
docker network create gavatcore-network 2>/dev/null || echo "Network already exists"

# Build and deploy
echo "📦 Building Telegram bot image..."
docker-compose -f docker-compose.telegram.yml build

echo "🔄 Stopping existing bot..."
docker-compose -f docker-compose.telegram.yml down

echo "🚀 Starting Telegram bot..."
docker-compose -f docker-compose.telegram.yml up -d

# Wait for bot to start
echo "⏳ Waiting for bot to start..."
sleep 10

# Check bot status
if docker-compose -f docker-compose.telegram.yml ps | grep -q "Up"; then
    echo "✅ Telegram bot deployed successfully!"
    echo "📊 Bot logs:"
    docker-compose -f docker-compose.telegram.yml logs --tail=20
    
    echo ""
    echo "🔗 Bot Commands:"
    echo "   /start - Welcome message"
    echo "   /trial - Start free trial"
    echo "   /status - Check subscription"
    echo "   /plans - View pricing"
    echo ""
    echo "🎯 Users can now interact with @GavatCoreBot"
else
    echo "❌ Telegram bot deployment failed!"
    docker-compose -f docker-compose.telegram.yml logs
    exit 1
fi 