from __future__ import annotations

import hashlib
import math
import typing as ty

from loguru import logger

if ty.TYPE_CHECKING:
    from pathlib import Path


def convert_from_bytes(bytes_value: int) -> str:
    """
    :param bytes_value: The number of bytes
    :returns: line of view <number> <unit of measurement>
    """
    if bytes_value == 0:
        return "0B"
    size_name = ("б", "КБ", "МБ", "ГБ", "ТБ", "ПБ", "EB", "ZB", "YB")
    i = int(math.floor(math.log(bytes_value, 1024)))
    p = math.pow(1024, i)
    s = round(bytes_value / p, 2)
    return f"{s} {size_name[i]}"


def get_file_hash(file_path: str | Path, hash_func=hashlib.sha256) -> str:
    """
    :param file_path: The Way to the File
    :param hash_func: hash function
    :returns: hash file
    """
    hash_func = hash_func()  # Initialize the hash function
    with open(file_path, "rb") as file:
        # We read the file by blocks in 64kb,
        # to avoid loading large files into RAM
        for block in iter(lambda: file.read(65536), b""):
            hash_func.update(block)
    file_hash = hash_func.hexdigest()
    logger.opt(colors=True).trace(
        f"{hash_func.name} of {str(file_path)}: <y>{file_hash}</y>"
    )
    return file_hash


def get_audio_file_duration(file_path: Path) -> float:
    """
    :param file_path: Path to the audio file.
    :returns: Duration of the audio file in seconds.
    """
