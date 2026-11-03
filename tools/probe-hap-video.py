#!/usr/bin/env python3
"""Real pyatv AP2 URL session test. Usage: probe-hap-video.py RECEIVER MEDIA_URL.

Use an unprotected local H.264 video at least 20 seconds long. Starts visible playback.
"""
import asyncio
import plistlib
import sys

from pyatv.auth.hap_pairing import TRANSIENT_CREDENTIALS
from pyatv.protocols.raop.protocols import StreamContext, TimingServer
from pyatv.protocols.raop.protocols.airplayv2 import AirPlayV2, HEADERS
from pyatv.support.http import http_connect
from pyatv.support.rtsp import RtspSession


async def run(host, url):
    connection = await http_connect(host, 7000)
    rtsp = RtspSession(connection)
    context = StreamContext()
    context.credentials = TRANSIENT_CREDENTIALS
    protocol = AirPlayV2(context, rtsp)
    timing, _ = await asyncio.get_running_loop().create_datagram_endpoint(TimingServer, local_addr=("0.0.0.0", 0))

    async def info():
        response = await connection.get("/playback-info")
        assert response.code == 200
        return plistlib.loads(response.body)

    async def ready(minimum=0):
        for _ in range(30):
            state = await info()
            if state.get("readyToPlay") and state.get("position", 0) >= minimum:
                return state
            await asyncio.sleep(0.5)
        raise AssertionError(f"Playback never became ready: {state}")

    try:
        response = await protocol.play_url(timing.get_extra_info("sockname")[1], url)
        assert response.code == 200
        first = await ready(1)
        print("PASS AP2 pairing, base SETUP, event connection, RECORD, URL playback:", first["position"], flush=True)
        await rtsp.exchange("POST", uri="/rate?value=0")
        await asyncio.sleep(0.8)
        paused = await info()
        await asyncio.sleep(1)
        still_paused = await info()
        assert still_paused["rate"] == 0 and abs(still_paused["position"] - paused["position"]) < 0.3
        print("PASS pause", flush=True)
        await rtsp.exchange("POST", uri="/scrub?position=8")
        await asyncio.sleep(0.8)
        assert abs((await info())["position"] - 8) < 1
        await rtsp.exchange("POST", uri="/rate?value=1")
        await ready(9)
        print("PASS seek and resume", flush=True)
        # Replace content on the same paired socket/event session. No reconnect or re-pairing.
        response = await connection.post("/play", headers=HEADERS, body=plistlib.dumps({
            "Content-Location": url + "?episode=2", "Start-Position-Seconds": 2.0,
        }, fmt=plistlib.FMT_BINARY))
        assert response.code == 200
        await asyncio.sleep(0.5)
        replacement = await ready(3)
        assert replacement["position"] < 8
        print("PASS content replacement in existing session:", replacement["position"], flush=True)
        await rtsp.exchange("POST", uri="/stop")
        await asyncio.sleep(0.6)
        assert (await info()).get("rate", 0) == 0
        await connection.post("/play", headers=HEADERS, body=plistlib.dumps({"Content-Location": url}, fmt=plistlib.FMT_BINARY))
        await ready(1)
        print("PASS stop and new playback without reconnect", flush=True)
        await rtsp.exchange("TEARDOWN")
        await asyncio.sleep(0.6)
        assert (await info()).get("rate", 0) == 0
        print("PASS teardown", flush=True)
    finally:
        protocol.teardown()
        timing.close()
        connection.close()


if __name__ == "__main__":
    asyncio.run(run(sys.argv[1], sys.argv[2]))
