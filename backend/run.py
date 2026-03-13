"""
Start the FastAPI app on the port Railway provides (PORT env var).
Ensures we always listen on 0.0.0.0 and the correct port.
"""
import os

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
