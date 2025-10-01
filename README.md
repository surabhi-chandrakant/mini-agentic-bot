# Mini Agentic Bot

A LangGraph + LangChain inspired agentic bot with a beautiful web UI that interacts with multiple mock databases and supports natural language CRUD operations with human-in-the-loop verification.

## 🚀 Features

- **🤖 Intelligent Agent**: Natural language processing for database operations
- **🗄️ 2 Mock Databases**: UsersDB & ProjectsDB with multiple tables/modules
- **💬 Beautiful Web UI**: Interactive chat interface with real-time updates
- **🔄 CRUD Operations**: Create, Read, Update, Delete via natural language
- **👥 Human-in-the-loop**: CUD operations require approval via web interface
- **⚡ FastAPI Backend**: High-performance REST API with automatic docs
- **🐳 Docker Support**: Easy deployment with Docker and Docker Compose
- **📱 Responsive Design**: Works perfectly on desktop and mobile devices

## 📋 Project Requirements Met

✅ **Interact with ≥2 mock databases** (UsersDB & ProjectsDB)  
✅ **Support CRUD via natural-language** (All operations working)  
✅ **Read (R): bot returns results directly** (No approval needed)  
✅ **Create/Update/Delete (C/U/D): require human verification** (Approval workflow working)  
✅ **Expose functionality via FastAPI** (REST endpoints + Web UI)  
✅ **Dockerize the project** (Docker files included)  
✅ **Provide detailed documentation** (This README)  

## 🏗️ System Architecture

### Project Structure
```
mini-agentic-bot/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── agents/
│   │   ├── graph.py           # LangGraph workflow
│   │   └── tools.py           # Database tools
│   ├── database/
│   │   ├── mock_db1.py        # Users database
│   │   └── mock_db2.py        # Projects database
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   └── templates/             # HTML templates
├── static/
│   ├── css/style.css          # Custom styles
│   └── js/script.js           # Frontend JavaScript
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### Technology Stack
- **Backend**: FastAPI, Python 3.11
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Architecture**: LangGraph-inspired agentic workflow
- **Containerization**: Docker & Docker Compose
- **API Documentation**: Automatic Swagger UI

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+ or Docker
- Git (for cloning repository)

### Method 1: Local Development (Recommended for Development)

#### 1. Clone and Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd mini-agentic-bot

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 2. Run the Application
```bash
# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Access the Application
- **Web UI**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative UI**: http://localhost:8000/chat

### Method 2: Docker (Recommended for Production)

#### 1. Using Docker Compose (Easiest)
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

#### 2. Using Docker Directly
```bash
# Build the image
docker build -t mini-agentic-bot .

# Run the container
docker run -p 8000:8000 mini-agentic-bot
```

#### 3. Access the Application
Same URLs as local development:
- http://localhost:8000
- http://localhost:8000/docs

## 🎯 Usage Guide

### Web Interface Usage

1. **Open** http://localhost:8000 in your browser
2. **Chat with the bot** using natural language:
   - "Show me all users"
   - "Create a new user named Alice in Marketing" 
   - "Update project budget to 90000"
   - "Delete user with ID 3"

3. **Manage approvals** by clicking the "Approvals" link in the navigation

### API Usage

#### Read Operations (No Approval Required)
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me all users", "user_id": "test"}'
```

#### Create Operations (Require Approval)
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Create a new user named Alice", "user_id": "test"}'
```

#### Approve Operations
```bash
curl -X POST "http://localhost:8000/approve" \
  -H "Content-Type: application/json" \
  -d '{"request_id": "UUID_FROM_RESPONSE", "user_id": "test", "approved": true}'
```

### Example Queries

#### Read Operations (Instant Results)
- "Show all users"
- "List active projects"
- "Find users in Engineering department"
- "Show me completed projects"
- "Get user with email john@example.com"

#### Create Operations (Require Approval)
- "Create a new user named Alice in Marketing"
- "Add a project called AI Research with budget 50000"
- "Create user Bob in Engineering department"

#### Update Operations (Require Approval)
- "Update user John's email to john.doe@company.com"
- "Change project status to completed"
- "Modify project budget to 85000"

#### Delete Operations (Require Approval)
- "Delete user with ID 3"
- "Remove the Mobile App project"
- "Delete all completed projects"

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main web interface |
| `GET` | `/chat` | Alternative chat interface |
| `GET` | `/approvals` | Pending approvals management |
| `GET` | `/data` | Data viewing interface |
| `POST` | `/query` | Process natural language queries |
| `POST` | `/approve` | Approve/reject pending operations |
| `GET` | `/pending-approvals` | List pending approval requests |
| `GET` | `/health` | Service health check |
| `GET` | `/data/users` | Get all users (direct access) |
| `GET` | `/data/projects` | Get all projects (direct access) |
| `GET` | `/docs` | Automatic API documentation |

## 🔧 Development

### Running Tests
```bash
# Create a test file (test.py) and run:
python test.py
```

### Project Structure Details

- **app/main.py**: FastAPI application with all routes
- **app/agents/**: LangGraph workflow and tools
- **app/database/**: Mock database implementations
- **app/models/**: Pydantic schemas and data models
- **app/templates/**: HTML templates for web UI
- **static/**: CSS and JavaScript files

### Adding New Features

1. **New Database Table**: Add to `app/database/`
2. **New API Endpoint**: Add to `app/main.py`
3. **UI Changes**: Modify templates in `app/templates/`
4. **Styling**: Update `static/css/style.css`
5. **Frontend Logic**: Modify `static/js/script.js`

## 🐳 Docker Configuration

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
COPY static/ ./static/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  agentic-bot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
    restart: unless-stopped
```

## 🚀 Deployment

### Production Deployment with Docker
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables
- `PORT`: Application port (default: 8000)

## 📝 LangGraph Workflow

The bot uses a LangGraph-inspired architecture:

1. **Query Analysis**: Natural language processing
2. **Operation Routing**: Determines CRUD operation type
3. **Tool Execution**: Database operations via specialized tools
4. **Approval Check**: Human verification for CUD operations  
5. **Response Generation**: Structured API response with web UI updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



## 🆘 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Use different port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Docker build fails:**
```bash
# Clean build
docker system prune -a
docker build --no-cache -t mini-agentic-bot .
```

**Import errors:**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Getting Help

- Check the API documentation at http://localhost:8000/docs
- Review the browser console for JavaScript errors
- Check server logs for backend issues

## 🎉 Success Message

When everything is working, you should see:
- ✅ Server running on http://localhost:8000
- ✅ Beautiful web interface with chat functionality
- ✅ API documentation at http://localhost:8000/docs
- ✅ All CRUD operations working with proper approval workflow

---

