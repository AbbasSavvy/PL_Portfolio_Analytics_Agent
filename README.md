# Portfolio Analytics Agent

An AI agent that answers natural language questions about portfolio data using Google Gemini. It either converts questions into SQL queries or calculates sector exposures depending on the question.

## Setup

**1. Clone the repository and navigate into it**

```bash
git clone <repo_url>
cd PL_Portfolio_Analytics_Agent
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install google-genai python-dotenv pandas numpy
```

**4. Get a Gemini API key**

Go to https://aistudio.google.com, sign in, and create an API key.

**5. Create a .env file in the project root**

```
GEMINI_API_KEY=your_api_key_here
```

## Running the Agent

```bash
python agent.py
```

Type any portfolio-related question and the agent will answer it. Type `exit` to quit.


## Sample Questions

```
Ask a question: How many portfolios do we have?
Ask a question: What are the names of all active portfolios?
Ask a question: Which securities are in the Technology sector?
Ask a question: What is the total AUM for portfolios with high target risk level?
Ask a question: Show me the top 5 holdings by cost basis in the Growth Equity Fund
Ask a question: What are the sector exposures for the Tech Innovation Fund?
Ask a question: Calculate the sector exposure breakdown for international equity
```

## Running the Evaluator

```bash
python evaluator.py
```

Runs all 10 questions from `ground_truth_dataset.json` through the agent and scores the results.

## How it works

The agent receives a question and makes a routing call to Gemini to decide which tool to use:

- **SQL tool** - for general data questions. Sends the question along with the database schema to Gemini, which generates a SQL query that gets executed on the database. Only SELECT queries are allowed.
- **Exposure calculator** - for sector exposure questions. Joins holdings and securities tables, filters to equities only, and returns sector weights as percentages. No AI involved, pure SQL and math.

The database is loaded fresh into memory on every run from the CSV files in the data folder.