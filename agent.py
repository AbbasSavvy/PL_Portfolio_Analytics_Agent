import os
from dotenv import load_dotenv
from google import genai


load_dotenv()

def create_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    return genai.Client(api_key=api_key)


def route_question(question, client):
    prompt = f"""You are a portfolio analytics assistant. Given a user question, decide which tool to use.

Tools available:
1. sql_tool - for questions about portfolio data, holdings, transactions, performance, risk metrics, securities, counts, sums, averages
2. exposure_calculator - ONLY for questions asking about sector exposure or sector breakdown of a specific portfolio

If the tool is exposure_calculator, also extract the portfolio name from the question.

Question: "{question}"

Respond in this exact format and nothing else:
TOOL: <sql_tool or exposure_calculator>
PORTFOLIO: <portfolio name or None>"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return parse_routing(response.text.strip())


def parse_routing(response_text):
    lines = response_text.strip().split("\n")
    tool = None
    portfolio = None
    for line in lines:
        if line.startswith("TOOL:"):
            tool = line.replace("TOOL:", "").strip()
        elif line.startswith("PORTFOLIO:"):
            portfolio = line.replace("PORTFOLIO:", "").strip()
            if portfolio == "None":
                portfolio = None
    return tool, portfolio

