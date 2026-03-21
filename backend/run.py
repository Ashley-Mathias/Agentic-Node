# backend/ — service entrypoint (uvicorn); Railway uses PORT.
"""
Start the FastAPI app on the port Railway provides (PORT env var).
Ensures we always listen on 0.0.0.0 and the correct port.
"""
import os

import uvicorn

if __name__ == "__main__":
    # Railway Networking may be set to 8000 in Settings; listen on PORT so proxy can reach us
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
