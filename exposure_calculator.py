import sqlite3

def calculate_sector_exposure(portfolio_name, conn):
    query = """
        SELECT sec.sector_name, SUM(h.current_weight) as total_weight
        FROM holdings h
        JOIN securities s ON h.security_id = s.security_id
        JOIN sectors sec ON s.sector_id = sec.sector_id
        JOIN portfolios p ON h.portfolio_id = p.portfolio_id
        WHERE p.portfolio_name = ?
        AND s.asset_type = 'Stock'
        GROUP BY sec.sector_name
        ORDER BY total_weight DESC
    """
    try:
        cursor = conn.execute(query, (portfolio_name,))
        rows = cursor.fetchall()

        if not rows:
            return {"error": f"No equity holdings found for portfolio: {portfolio_name}"}

        total = sum(row[1] for row in rows)
        exposures = {row[0]: round((row[1] / total) * 100, 2) for row in rows}

        return {
            "portfolio": portfolio_name,
            "sector_exposures": exposures
        }
    except sqlite3.Error as e:
        return {"error": f"Database error: {e}"}