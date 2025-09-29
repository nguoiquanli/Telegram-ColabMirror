
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


async def upload_to_filebin(file_path: str) -> str:
    """
    Upload a file to Filebin and return the public URL.
    Strategy:
      - Ensure (or synthesize) BIN_ID
      - Try PUT to /api/bin/{BIN_ID}/{filename}
      - If 400/404/405/415/409: retry with:
          * sanitized filename (URL-quoted)
          * forced Content-Type
          * ensure a fresh BIN_ID from API
          * append .bin suffix if needed
    """
    global BIN_ID
    import os
    from urllib.parse import quote

    async with aiohttp.ClientSession() as session:
        await _ensure_bin(session)

        base_name = os.path.basename(file_path)
        async def attempt(name, ensure_new_bin=False, use_post=False, add_suffix=False):
            nonlocal BIN_ID
            if ensure_new_bin:
                # try re-creating BIN via API; if fails, keep current BIN_ID (fallback)
                try:
                    async with session.post("https://filebin.net/api/bin", headers={"Accept":"application/json"}) as r:
                        if r.status == 200:
                            data = await r.json(content_type=None)
                            BIN_ID = data.get("bin") or data.get("id") or BIN_ID
                except Exception:
                    pass
            nm = name + (".bin" if add_suffix and not name.endswith(".bin") else "")
            nm_q = quote(nm, safe="._-")
            url = f"https://filebin.net/api/bin/{BIN_ID}/{nm_q}"
            headers = {"Content-Type": "application/octet-stream"}
            data = open(file_path, "rb")
            if use_post:
                return await session.post(url, data=data, headers=headers)
            else:
                return await session.put(url, data=data, headers=headers)

        # Try sequence of attempts
        r = await attempt(base_name)
        if r.status in (400,404,405,409,415):
            r = await attempt(base_name, ensure_new_bin=True)
        if r.status in (400,404,405,409,415):
            r = await attempt(base_name, use_post=True)
        if r.status in (400,404,405,409,415):
            r = await attempt(base_name, use_post=True, add_suffix=True)
        r.raise_for_status()
        # Final name may have .bin
        name_used = base_name if r.status < 300 else base_name
        # If we appended .bin in the last attempt infer name_used accordingly
        if r.request_info.url.human_repr().endswith(".bin"):
            if not name_used.endswith(".bin"):
                name_used = name_used + ".bin"
        return f"https://filebin.net/{BIN_ID}/{quote(name_used, safe='._-')}"
