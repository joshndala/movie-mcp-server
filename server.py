import os
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import argparse

load_dotenv()

API_KEY = os.getenv("OMDB_API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found! Make sure you have a .env file.")


mcp = FastMCP("Movie Battle Server", host="0.0.0.0", port=8000)

def get_movie_data(title: str):
    """Fetches and cleans data from OMDb."""
    url = f"http://www.omdbapi.com/?t={title}&apikey={API_KEY}"
    try:
        resp = httpx.get(url)
        data = resp.json()
    except Exception:
        return None

    if data.get("Response") == "False":
        return None

    # Parse Box Office (e.g., "$1,000,000" -> 1000000)
    box_office_str = data.get("BoxOffice", "N/A")
    box_office_val = 0
    if box_office_str != "N/A":
        box_office_val = int(box_office_str.replace("$", "").replace(",", ""))

    # Find Rotten Tomatoes Score in the Ratings list
    rt_score = "N/A"
    rt_val = 0
    for rating in data.get("Ratings", []):
        if rating["Source"] == "Rotten Tomatoes":
            rt_score = rating["Value"] # e.g., "93%"
            rt_val = int(rt_score.replace("%", ""))
            break
    
    # Determine color based on RT score (Green=Good, Red=Bad)
    color = "#fa320a" # Rotten (Red)
    if rt_val >= 60:
        color = "#e0218a" if "Barbie" in title else "#46d369" # Fresh (Green)

    return {
        "title": data.get("Title"),
        "poster": data.get("Poster"),
        "box_office_fmt": box_office_str,
        "box_office_val": box_office_val,
        "rt_score": rt_score,
        "rt_val": rt_val,
        "color": color,
        "year": data.get("Year")
    }

@mcp.tool()
def compare_movies(movie_a: str, movie_b: str) -> str:
    """
    Fetches data and returns a standalone HTML/CSS comparison card.
    
    IMPORTANT: The output of this tool is valid HTML. 
    You MUST display this output to the user by generating a generic HTML Artifact 
    containing the exact code returned by the tool.
    """
    # 1. Fetch Real Data
    data_a = get_movie_data(movie_a)
    data_b = get_movie_data(movie_b)

    if not data_a: return f"Error: Could not find movie '{movie_a}'"
    if not data_b: return f"Error: Could not find movie '{movie_b}'"

    # 2. Generate HTML
    # Note: We use the poster URLs returned by the API directly
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 20px; background: #f4f4f9; }}
            .battle-card {{ display: flex; gap: 20px; max-width: 700px; margin: 0 auto; background: white; padding: 25px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            .movie {{ flex: 1; display: flex; flex-direction: column; align-items: center; text-align: center; }}
            .poster {{ width: 150px; height: 225px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); object-fit: cover; margin-bottom: 15px; }}
            .vs {{ align-self: center; font-weight: 900; font-size: 32px; color: #ddd; margin: 0 10px; font-style: italic; }}
            .title {{ font-size: 1.2em; font-weight: 800; margin-bottom: 5px; color: #1a1a1a; height: 3em; display: flex; align-items: center; justify-content: center; }}
            .year {{ color: #888; font-size: 0.9em; margin-bottom: 15px; }}
            .stat-row {{ width: 100%; margin-top: 15px; text-align: left; }}
            .label {{ font-size: 0.75em; text-transform: uppercase; color: #888; letter-spacing: 0.5px; font-weight: 600; margin-bottom: 4px; }}
            .value {{ font-size: 1.3em; font-weight: 700; color: #333; }}
            .bar-bg {{ background: #eee; height: 8px; border-radius: 4px; width: 100%; margin-top: 6px; overflow: hidden; }}
            .bar {{ height: 100%; transition: width 0.5s ease-out; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="battle-card">
            <div class="movie">
                <img src="{data_a['poster']}" class="poster" alt="Poster">
                <div class="title">{data_a['title']}</div>
                <div class="year">({data_a['year']})</div>
                
                <div class="stat-row">
                    <div class="label">Rotten Tomatoes</div>
                    <div class="value" style="color: {data_a['color']}">{data_a['rt_score']}</div>
                    <div class="bar-bg"><div class="bar" style="width: {data_a['rt_val']}%; background: {data_a['color']}"></div></div>
                </div>
                
                <div class="stat-row">
                    <div class="label">Box Office</div>
                    <div class="value">{data_a['box_office_fmt']}</div>
                </div>
            </div>

            <div class="vs">VS</div>

            <div class="movie">
                <img src="{data_b['poster']}" class="poster" alt="Poster">
                <div class="title">{data_b['title']}</div>
                <div class="year">({data_b['year']})</div>
                
                <div class="stat-row">
                    <div class="label">Rotten Tomatoes</div>
                    <div class="value" style="color: {data_b['color']}">{data_b['rt_score']}</div>
                    <div class="bar-bg"><div class="bar" style="width: {data_b['rt_val']}%; background: {data_b['color']}"></div></div>
                </div>
                
                <div class="stat-row">
                    <div class="label">Box Office</div>
                    <div class="value">{data_b['box_office_fmt']}</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"],
                        help="Choose 'stdio' for Desktop Apps or 'sse' for Web/ChatGPT")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")), 
                        help="Port for SSE (defaults to 8000 or PORT env var)")
    
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port
        print(f"🚀 Starting Server (SSE) on port {mcp.settings.port}...")
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")