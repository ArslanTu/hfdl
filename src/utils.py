# -*- encoding: utf-8 -*-
"""
@File: script_generater.py
@Auther: ArslanTu
@Email: arslantu@arslantu.xyz
@Data: 2024-04-17 12:55:01
@Description: A class to generate a script for downloading files from HF mirror
"""
import asyncio
import tempfile
from typing import List

import aiohttp
from bs4 import BeautifulSoup
from retrying import RetryError, retry


@retry(wait_fixed=2000, stop_max_attempt_number=5)
async def fetch_url(url: str) -> str:
    """
    get the content of the url

    Args:
        url (str): url to fetch

    Returns:
        str: content of the url
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()



async def extract_links(domain: str, hf_path: str) -> List[str]:
    """
    extract links to be downloaded from the given path

    Args:
        domain (str): domain name of hf mirror
        hf_path (str): path to extract links from

    Raises:
        e: RetryError

    Returns:
        List[str]: list of extracted links
    """
    url_prefix = "https://" + domain
    if url_prefix[-1] != "/":
        url_prefix += "/"
    url_suffix = "/tree/main"
    url = url_prefix + hf_path + url_suffix

    try:
        response_content = await fetch_url(url)
    except RetryError as e:
        raise e

    soup = BeautifulSoup(response_content, "html.parser")

    links = soup.find_all("a", href=True)

    extracted_links = []

    for link in links:
        href = link["href"]
        tail = "?download=true"
        if href.endswith(tail):
            extracted_links.append(
                url_prefix[:-1] + href[: len(href) - len(tail)])

    return extracted_links


def generate_script(hf_path:str, links: List[str]) -> str:
    """
    generate a script to download the files

    Args:
        path (str): hf repo path
        links (List[str]): links to be downloaded

    Returns:
        str: script content
    """
    path = hf_path.split('/')[1]
    script_content: str = (
        "#!/bin/bash\n\n"
        f"if [ ! -d '{path}' ]; then\n"
        f"    mkdir -p '{path}'\n"
        f"elif [ -n \"$(ls -A '{path}')\" ]; then\n"
        f"    echo '{path} is not empty, pls delete it and try again.'\n"
        "    exit 1\n"
        "fi\n\n"
    )
    for link in links:
        script_content += f"wget --no-check-certificate -c -P '{path}' '{link}'\n"

    return script_content


def create_file(script_content: str) -> str:
    """
    get the file containing the script

    Args:
        script_content (str): script content

    Returns:
        str: file path
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as file:
        file.write(script_content)
        file_path = file.name
    return file_path


async def get_file(hf_path: str, domain: str) -> str:
    """
    get the file containing the script

    Returns:
        str: file path
    """
    links = await extract_links(domain, hf_path)
    script_content = await asyncio.to_thread(generate_script, hf_path, links)
    file_path = await asyncio.to_thread(create_file, script_content)
    return file_path
