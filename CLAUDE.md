# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GavatCore is an enterprise-grade AI-powered Telegram bot management platform with social gaming features. The system manages multiple Telegram bots with different personalities and roles, implements a token economy system, and provides comprehensive APIs for bot management and analytics.

## Core Architecture

### Multi-Bot System
- **3 Main Bots**: Lara (flirty streamer), BabaGavat (street-smart admin), Geisha (sophisticated moderator)
- **Unified Bot Management**: All bots controlled through `services/telegram/bot_manager/bot_system.py`
- **Session Management**: Telegram sessions stored in `sessions/` directory
- **Bot Configurations**: Defined in `services/telegram/bot_manager/bot_config.py`

### API Layer
- **Production Bot API**: Main API server running on port 5050 (`apis/production_bot_api.py`)
- **XP Token API**: Token economy API on port 5051 (`apis/xp_token_api_sync.py`)
- **SaaS API**: FastAPI-based service in `gavatcore-api/` directory
- **Flutter Dashboard**: Admin panel in `gavatcore_panel/` directory

### Core Components
- **Character Engine**: AI personality system in `character_engine/`
- **Core Services**: Essential services in `core/` directory
- **Database Layer**: Multi-database support (SQLite, PostgreSQL, MongoDB, Redis)
- **Monitoring**: Health checks, analytics, and performance tracking

## Development Commands

### Main System Startup
```bash
# Start the entire system (APIs + Bots)
python run.py

# Start main application
python main.py

# Start unified bot system directly
python -m services.telegram.bot_manager.bot_system
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests
pytest -m slow          # Slow tests
pytest -m api           # API tests

# Run tests from specific directory
pytest tests/
```

### Code Quality
```bash
# Type checking
mypy .

# Format code
black .

# Lint code
flake8 .

# Run all quality checks
pytest && mypy . && black . && flake8 .
```

### Flutter Development
```bash
# Navigate to Flutter project
cd gavatcore_panel

# Install dependencies
flutter pub get

# Run code generation
flutter packages pub run build_runner build --delete-conflicting-outputs

# Build for web
flutter build web

# Run development server
flutter run -d chrome
```

### API Development
```bash
# Start SaaS API server
cd gavatcore-api
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run API tests
pytest gavatcore-api/tests/

# Database migrations
cd gavatcore-api
alembic upgrade head
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose -f infrastructure/docker/docker-compose.yml up -d

# Production deployment
docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d

# Telegram bot specific deployment
docker-compose -f docker-compose.telegram.yml up -d
```

## Key File Locations

### Configuration Files
- `config/requirements.txt` - Python dependencies
- `config/pytest.ini` - Test configuration
- `config/mypy.ini` - Type checking configuration
- `gavatcore_panel/pubspec.yaml` - Flutter dependencies
- `gavatcore-api/requirements.txt` - API service dependencies

### Entry Points
- `run.py` - Main system launcher
- `main.py` - Alternative entry point
- `services/telegram/bot_manager/bot_system.py` - Bot management system
- `gavatcore-api/app/main.py` - FastAPI application

### Core Business Logic
- `character_engine/` - AI personality and behavior system
- `core/` - Essential services and utilities
- `apis/` - API implementations
- `services/` - Service layer implementations

### Database and Storage
- `data/` - Static data files and configurations
- `sessions/` - Telegram session files
- Database schemas in respective service directories

## Important Development Notes

### Bot System Architecture
- The system uses a unified bot management approach where all bots are controlled through a single system
- Each bot has a specific role and personality defined in configuration files
- Session files are critical for bot authentication and should be backed up
- The system supports both manual and automated bot responses

### API Architecture
- Multiple APIs serve different purposes (bot management, token economy, SaaS features)
- Health check endpoints are available for monitoring
- APIs use structured logging for debugging and monitoring

### Testing Strategy
- Comprehensive test suite with unit, integration, and performance tests
- Tests are categorized using pytest markers
- Coverage reports are generated in HTML format
- Async tests are supported through pytest-asyncio

### Code Quality Standards
- Strict type checking with MyPy
- Code formatting with Black
- Comprehensive error handling and logging
- Structured logging with contextual information

### Database Strategy
- Multi-database architecture supporting SQLite, PostgreSQL, MongoDB, and Redis
- Each database serves specific purposes (sessions, analytics, caching, etc.)
- Migration scripts available for database updates

## Common Development Workflows

### Adding a New Bot
1. Update `services/telegram/bot_manager/bot_config.py` with new bot configuration
2. Create session file in `sessions/` directory
3. Add persona data in `data/personas/` if needed
4. Update the unified bot system to include the new bot

### Adding New API Endpoints
1. Add endpoint to appropriate API service in `apis/` directory
2. Update API documentation
3. Add corresponding tests in `tests/`
4. Update health check endpoints if needed

### Database Changes
1. Update model definitions in respective service directories
2. Create migration scripts if using structured databases
3. Update test fixtures and data
4. Test with different database backends

### Frontend Development
1. Navigate to `gavatcore_panel/` directory
2. Use Flutter development tools for UI changes
3. Update API integration in `lib/` directory
4. Build for web deployment when ready

## Troubleshooting

### Common Issues
- **Bot Authentication**: Check session files in `sessions/` directory
- **API Connectivity**: Verify health check endpoints are responding
- **Database Issues**: Check database connection strings and credentials
- **Missing Dependencies**: Run `pip install -r config/requirements.txt`

### Debugging
- Use structured logging output for debugging
- Check health check endpoints for service status
- Review test output for specific error scenarios
- Monitor system resources during bot operations

## Security Considerations

- Session files contain sensitive authentication data
- API endpoints should be properly secured
- Database credentials should be stored in environment variables
- Never commit sensitive configuration files

## Performance Optimization

- Use async/await patterns for I/O operations
- Implement proper caching strategies
- Monitor memory usage during bot operations
- Use connection pooling for database operations