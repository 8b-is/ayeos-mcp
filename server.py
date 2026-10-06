"""ayeos-mcp — ternary matrix inference over Model Context Protocol.

Exposes ayeOS MEMNET tools as MCP tools:
  - genesis: get the genesis matrix (256x256, LINOSV seed)
  - quantize: reserved tool; explicitly unsupported by the current daemon
  - capsule: get a MEMNET capsule (ternary matrix encoded)
  - stats: get node address metadata

Requires ayeosd running on localhost:9876.
"""
import asyncio
import time
import json
import socket
from mcp.server.mcpserver import MCPServer

server = MCPServer("ayeos-mcp")

MAX_RESPONSE_BYTES = 4 * 1024 * 1024
TIMEOUT_SECONDS = 5


def _memnet(cmd: str) -> str:
    """Read one EOF-terminated daemon response with a size and time bound."""
    if "\r" in cmd or "\n" in cmd:
        raise ValueError("Command must be a single line")
    if len((cmd + "\n").encode()) > 1024:
        raise ValueError("Command exceeds daemon's 1024-byte request limit")
    deadline = time.monotonic() + TIMEOUT_SECONDS
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT_SECONDS)
            sock.connect(("127.0.0.1", 9876))
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Daemon connection timed out")
            sock.settimeout(remaining)
            sock.sendall((cmd + "\n").encode())
            response = bytearray()
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("Daemon response timed out")
                sock.settimeout(remaining)
                chunk = sock.recv(4096)
                if not chunk:
                    break
                if len(response) + len(chunk) > MAX_RESPONSE_BYTES:
                    raise RuntimeError("Daemon response exceeds size limit")
                response.extend(chunk)
        data = json.loads(response.decode())
        if isinstance(data, dict) and "error" in data:
            raise RuntimeError(str(data["error"]))
        return json.dumps(data, indent=2)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Invalid or incomplete daemon response: {exc}") from exc

@server.tool()
async def genesis() -> str:
    """Get the genesis ternary matrix (256x256, LINOSV seed, 12.80x compression)."""
    return await asyncio.to_thread(_memnet, "capsule genesis")

@server.tool()
async def capsule(name: str = "genesis") -> str:
    """Get a named MEMNET capsule containing a ternary matrix."""
    return await asyncio.to_thread(_memnet, f"capsule {name}")

@server.tool()
async def stats() -> str:
    """Get the ayeOS node address metadata returned by the daemon."""
    return await asyncio.to_thread(_memnet, "stats")

@server.tool()
async def quantize(weights: str) -> str:
    """Unsupported by the current ayeOS daemon; returns an explicit error."""
    raise NotImplementedError("The current ayeOS daemon does not support quantize")

def main():
    server.run(transport="stdio")

if __name__ == "__main__":
    main()
