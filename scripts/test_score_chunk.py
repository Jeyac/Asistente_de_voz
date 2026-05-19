#!/usr/bin/env python
"""Prueba rápida de /activation/score-chunk."""

import random
import struct
import urllib.error
import urllib.request

URL = "http://127.0.0.1:8000/api/v1/activation/score-chunk"
SESSION = "test-session-debug"


def post_chunk(samples: list[int]) -> None:
    data = struct.pack("h" * len(samples), *samples)
    req = urllib.request.Request(
        URL,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/octet-stream",
            "X-Wake-Session": SESSION,
        },
    )
    try:
        with urllib.request.urlopen(req) as response:
            print(response.status, response.read().decode())
    except urllib.error.HTTPError as exc:
        print("HTTP", exc.code, exc.read().decode())


if __name__ == "__main__":
    post_chunk([0] * 1280)
    for _ in range(30):
        samples = [random.randint(-30_000, 30_000) for _ in range(1280)]
        post_chunk(samples)
