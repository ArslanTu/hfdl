# -*- encoding: utf-8 -*-
"""
@File: main.py
@Auther: ArslanTu
@Email: arslantu@arslantu.xyz
@Data: 2024-04-17 10:50:13
@Description: API for downloading files from HF mirror as simple as possible
"""
import os
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from retrying import RetryError

from .utils import get_file

app = FastAPI(title="HF download")
tmp_files: List[str] = []  # record the temporary files created


@app.on_event("shutdown")
def remove_tmp_files() -> None:
    """
    remove the temporary files created during the process
    """
    for file_path in tmp_files:
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass



@app.get("/", response_model=None, responses={500: {"model": str}})
async def download(hf_path: str, domain: str = "hf-mirror.com") -> str:
    """
    api for download

    Args:
        path (str): hf repo path
        domain (str, optional): hf mirror domain. Defaults to "hf-mirror.com".

    Raises:
        HTTPException: failed to fetch the URL

    Returns:
        str: script for downloading the files
    """
    try:
        script_file = await get_file(hf_path, domain)
        return FileResponse(script_file, filename="dl.sh")
    except RetryError as e:
        raise HTTPException(
            status_code=500, detail="Failed to fetch the URL, pls try again later") from e


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
