# Chat Application with SQL Query Generation

A Django-based chat application that integrates with OpenAI to generate SQL queries and interact with database products.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- ANTHROPIC_API_KEY

### Running with Docker Compose

1. **Clone and navigate to the project directory**

2. **Set up environment variables** (optional):
   ```bash
   # Create .env file
   echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
   ```
   
3. **Start the application**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - **Main Application**: http://localhost:8000
   - **Admin Panel**: http://localhost:8000/admin

### Default Test User

For testing purposes, use these credentials:
- **Username**: `admin`
- **Password**: `admin`

## Main Endpoints

- `/` - Main chat interface
- `/admin/` - Django admin panel for managing chat sessions and messages
- `/api/chat/` - Chat API endpoint (POST)
- '/api/docs/' - swagger documentation

## Database Management

The application includes a seeding script to populate the database with sample products:

### Seed Commands

```bash
# Populate database with sample products
python manage.py seed_products

# Show help and available options
python manage.py seed_products --help

# Clear existing products and reseed
python manage.py seed_products --clear
```

**Note**: The Docker Compose setup automatically runs the seed command during startup.

## Services

The application uses the following services:

### Web Application (Port 8000)
- Django application server
- Automatically runs migrations and seeds data on startup
- Connects to Redis for caching/sessions

### Redis (Port 6379)
- Used for caching and session storage
- Data persisted in `redis_data` volume

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | - | Anthropic API key for AI functionality |
| `REDIS_HOST` | `redis` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `DEBUG` | `True` | Django debug mode |

## Development

### Local Development Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Seed the database**:
   ```bash
   python manage.py seed_products
   ```

4. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

5. **Start development server**:
   ```bash
   python manage.py runserver
   ```

### Database Schema

The application includes models for:
- **ChatSession**: User chat sessions with timestamps
- **ChatMessage**: Individual messages with SQL query support
- **Product**: Sample products for SQL query testing
- 
### LangSmith Tracing

The application supports LangSmith integration for tracing and monitoring AI interactions.

#### What is LangSmith?

LangSmith is a platform for debugging, testing, and monitoring LLM applications. It provides detailed traces of your AI interactions, helping you:

- Debug conversation flows
- Monitor response quality and latency
- Analyze token usage and costs
- Track performance over time

#### Setup LangSmith

1. Sign up at [LangSmith](https://smith.langchain.com/).
2. Get your API key from the LangSmith dashboard.
3. Add the following to your `.env` file:
    ```env
    LANGSMITH_TRACING=true
    LANGSMITH_ENDPOINT=https://api.smith.langchain.com
    LANGSMITH_API_KEY=your_langsmith_api_key_here
    LANGSMITH_PROJECT=django-llm
    ```
4. Restart the application to enable tracing.

#### Using LangSmith

Once enabled, all AI interactions will be automatically traced and visible in your LangSmith dashboard under the specified project name.

## Features

- Interactive chat interface with AI-powered responses
- SQL query generation and execution
- Admin panel for managing chat data
- Docker containerization for easy deployment
- Redis integration for improved performance
- Comprehensive seeding system for test data

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8000 and 6379 are available
2. **Permission errors**: Make sure Docker has proper permissions
3. **API key issues**: Check if `OPENAI_MOCK_MODE=True` for testing without API key

### Logs

View application logs:
```bash
docker-compose logs web
docker-compose logs redis
```

### Reset Data

To completely reset the application:
```bash
docker-compose down -v
docker-compose up --build
```