"""ayeos-mcp — ternary matrix inference over Model Context Protocol.

Exposes ayeOS MEMNET tools as MCP tools:
  - genesis: get the genesis matrix (256x256, LINOSV seed)
  - quantize: quantize weights to ternary {-1, 0, +1}
  - matmul: run ternary quantized matrix multiplication
  - capsule: get a MEMNET capsule (ternary matrix encoded)
  - stats: get node stats + mesh topology

Requires ayeosd running on localhost:9876.
"""
import json
import socket
from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("ayeos-mcp")

def _memnet(cmd: str) -> str:
    """Send a command to ayeosd MEMNET and return the response."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(("127.0.0.1", 9876))
        sock.sendall((cmd + "\n").encode())
        response = b""
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            except socket.timeout:
                break
        sock.close()
        text = response.decode().strip()
        try:
            return json.dumps(json.loads(text), indent=2)
        except json.JSONDecodeError:
            return text
    except Exception as e:
        return json.dumps({"error": str(e)})

@server.tool()
async def genesis() -> str:
    """Get the genesis ternary matrix (256x256, LINOSV seed, 12.80x compression)."""
    return _memnet("capsule genesis")

@server.tool()
async def capsule(name: str = "genesis") -> str:
    """Get a named MEMNET capsule containing a ternary matrix."""
    return _memnet(f"capsule {name}")

@server.tool()
async def stats() -> str:
    """Get ayeOS daemon stats: seed, hash, matrix dimensions, sparsity."""
    return _memnet("stats")

@server.tool()
async def quantize(weights: str) -> str:
    """Quantize weights to ternary. Pass JSON array of floats. Returns packed codes + scales."""
    return _memnet(f"quantize {weights}")

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
