# Financial Assistance Agent System

A multi-agent system for providing financial assistance and insights through natural language interaction.

## System Architecture

The system consists of five specialized agents:

1. **Intention Agent**: Processes and classifies user queries
2. **Retriever Agent**: Gathers relevant financial data and context
3. **Reasoner Agent**: Analyzes information and generates insights
4. **Writer Agent**: Crafts user-friendly responses
5. **Designer Agent**: Creates visual representations of financial data

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. Start the services:
```bash
docker-compose up -d  # Starts Redis and PostgreSQL
uvicorn main:app --reload  # Starts the FastAPI server
```

## Testing

To run the agent flow test:

1. Make sure your virtual environment is activated and dependencies are installed
2. Set up your OpenAI API key in the `.env` file:
```bash
OPENAI_API_KEY=your-api-key-here
```
3. Run the test:
```bash
python -m tests.test_agent_flow
```

The test will:
- Process a sample query through all agents
- Show the output from each agent
- Demonstrate the complete flow from user input to final response

## Project Structure

```
Hack-5/
├── agents/
│   ├── intention_agent.py
│   ├── retriever_agent.py
│   ├── reasoner_agent.py
│   ├── writer_agent.py
│   └── designer_agent.py
├── core/
│   ├── config.py
│   ├── database.py
│   └── memory.py
├── api/
│   ├── routes/
│   └── models/
├── utils/
│   ├── prompts.py
│   └── tools.py
├── tests/
├── docker-compose.yml
├── requirements.txt
└── main.py
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Monitoring

The system includes OpenTelemetry integration for observability and Prometheus metrics for monitoring.
