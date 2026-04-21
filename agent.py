import os
from dotenv import load_dotenv
from google import genai
from sql_tool import run_sql_tool
from exposure_calculator import run_exposure_tool
from database import setup_database


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

Valid portfolio names:
- Growth Equity Fund
- Conservative Income Fund
- Tech Innovation Fund
- Balanced Portfolio
- ESG Sustainable Fund
- Small Cap Value Fund
- International Equity Fund
- Fixed Income Plus
- Dividend Aristocrats Fund
- Emerging Markets Fund
- Total Stock Market Index Fund
- Total Bond Market Index Fund
- Total International Index Fund

If the tool is exposure_calculator, match the portfolio name from the question to the closest valid portfolio name above.

Question: "{question}"

Respond in this exact format and nothing else:
TOOL: <sql_tool or exposure_calculator>
PORTFOLIO: <matched portfolio name or None>"""

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


def answer_question(question, conn, client):
    print(f"\nQuestion: {question}")
    tool, portfolio = route_question(question, client)
    print(f"Tool selected: {tool}")

    if tool == "exposure_calculator" and portfolio:
        result = run_exposure_tool(portfolio, conn)
    else:
        result = run_sql_tool(question, conn, client)

    return result


def main():
    conn = setup_database()
    client = create_client()

    print("Portfolio Analytics Agent ready. Type 'exit' to quit.")
    while True:
        question = input("\nAsk a question: ").strip()
        if question.lower() == "exit":
            break
        if not question:
            continue
        try:
            result = answer_question(question, conn, client)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()