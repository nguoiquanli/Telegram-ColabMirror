
import os, aiohttp, asyncio, json, uuid

BIN_ID = None

async def _ensure_bin(session):
    global BIN_ID
    if BIN_ID:
        return BIN_ID
    try:
        async with session.post("https://filebin.net/api/bin", headers={"Accept":"application/json"}) as r:
            if r.status == 200:
                try:
                    data = await r.json(content_type=None)
                    BIN_ID = data.get("bin") or data.get("id")
                    if BIN_ID:
                        return BIN_ID
                except Exception:
                    pass
    except Exception:
        pass
    BIN_ID = uuid.uuid4().hex[:12]
    return BIN_ID

async def upload_to_filebin(file_path: str) -> str:
    global BIN_ID
    async with aiohttp.ClientSession() as session:
        await _ensure_bin(session)
        name = os.path.basename(file_path)
        async def do_put(nm):
            url = f"https://filebin.net/api/bin/{BIN_ID}/{nm}"
            async with session.put(url, data=open(file_path, "rb")) as r:
                return r
        r = await do_put(name)
        if r.status in (400, 415, 406, 409, 404):
            name = name + ".bin"
            r = await do_put(name)
            r.raise_for_status()
        else:
            r.raise_for_status()
        return f"https://filebin.net/{BIN_ID}/{name}"
