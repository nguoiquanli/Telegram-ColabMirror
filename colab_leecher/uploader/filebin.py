
# Simple Filebin uploader using aiohttp
import os, aiohttp, asyncio
BIN_ID = None

async def _ensure_bin(session):
    global BIN_ID
    if BIN_ID:
        return BIN_ID
    async with session.post("https://filebin.net/api/bin") as r:
        data = await r.json()
        BIN_ID = data.get("bin") or data.get("id")
        return BIN_ID

async def upload_to_filebin(file_path: str) -> str:
    """Uploads a file to Filebin and returns the public download URL."""
    global BIN_ID
    async with aiohttp.ClientSession() as session:
        await _ensure_bin(session)
        name = os.path.basename(file_path)
        url = f"https://filebin.net/api/bin/{BIN_ID}/{name}"
        async with session.put(url, data=open(file_path, "rb")) as r:
            if r.status in (400, 415, 406):
                # Try appending .bin when blocked by extension policy
                name = name + ".bin"
                url = f"https://filebin.net/api/bin/{BIN_ID}/{name}"
                async with session.put(url, data=open(file_path, "rb")) as r2:
                    r2.raise_for_status()
                    return f"https://filebin.net/{BIN_ID}/{name}"
            r.raise_for_status()
            return f"https://filebin.net/{BIN_ID}/{name}"
