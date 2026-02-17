# Movie Battle MCP Server

A Model Context Protocol (MCP) server that fetches real-world movie data from the OMDb API and generates visual, side-by-side comparison "battle cards" for film buffs and analysts.

## Features

- **`compare_movies`**: A powerful tool that takes two movie titles and returns a beautifully formatted HTML comparison card.
- **Visual Analytics**: Compares Rotten Tomatoes scores and Box Office performance at a glance.
- **Dynamic Styling**: Automatically adjusts card colors based on movie themes (e.g., special "Barbie" styling).

## Prerequisites

- **Python 3.10+**
- **OMDb API Key**: You can get a free key at [omdbapi.com](http://www.omdbapi.com/apikey.aspx).

## Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd movie-mcp-server
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add your OMDb API key:
   ```env
   OMDB_API_KEY=your_actual_api_key_here
   ```

## Usage

### 1. Developer Mode (stdio)
This is the default mode, used for local integration with Claude Desktop or other MCP clients.
```bash
python server.py
```

### 2. Network Mode (SSE)
Use this for web-based clients or the MCP Inspector. It automatically detects the `PORT` environment variable (common for platforms like Render).
```bash
python server.py --transport sse
```

## Testing & Debugging

### Using MCP Inspector
The easiest way to test your tools is with the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

**Option A: Direct (stdio)**
```bash
npx @modelcontextprotocol/inspector python server.py
```

**Option B: Via SSE**
1. Start the server: `python server.py --transport sse`
2. Run inspector: `npx @modelcontextprotocol/inspector http://localhost:8000/sse`

## Integration

### Claude Desktop
To use this server in Claude Desktop, add it to your configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "movie-battle": {
      "command": "/Users/joshua_ndala/repos/movie-mcp-server/.venv/bin/python",
      "args": [
        "/Users/joshua_ndala/repos/movie-mcp-server/server.py"
      ],
      "env": {
        "OMDB_API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```
> **Note**: Always use the absolute path to your virtual environment's python and the `server.py` file.


## License
MIT
