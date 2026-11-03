#!/usr/bin/env python3
"""Exercise a real receiver with independent srptools/cryptography implementations.

Usage: python probe-hap-control.py HOST [PORT]
Requires: srptools, cryptography. Does not log pairing secrets or start media.
"""
import hashlib
import plistlib
import socket
import sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from srptools import SRPClientSession, SRPContext, constants


def tlv(fields):
    result = bytearray()
    for tag, value in fields.items():
        for offset in range(0, len(value), 255):
            chunk = value[offset:offset + 255]
            result.extend(bytes([tag, len(chunk)]) + chunk)
    return bytes(result)


def untlv(data):
    result = {}
    while data:
        assert len(data) >= 2
        tag, size = data[:2]
        assert len(data) >= size + 2
        result[tag] = result.get(tag, b"") + data[2:2 + size]
        data = data[2 + size:]
    return result


class Connection:
    def __init__(self, host, port, video=False):
        self.sock = socket.create_connection((host, port), timeout=10)
        self.reader = self.sock.makefile("rb", buffering=0)
        self.output = self.input = None
        self.sent = self.received = 0
        self.pending = b""
        self.video = video

    def exact(self, size):
        data = b""
        while len(data) < size:
            chunk = self.reader.read(size - len(data))
            if not chunk:
                raise EOFError("Receiver closed connection")
            data += chunk
        return data

    def read(self, size):
        if self.input is None:
            return self.exact(size)
        while len(self.pending) < size:
            header = self.exact(2)
            length = int.from_bytes(header, "little")
            assert length <= 1024
            nonce = bytes(4) + self.received.to_bytes(8, "little")
            self.pending += self.input.decrypt(nonce, self.exact(length + 16), header)
            self.received += 1
        result, self.pending = self.pending[:size], self.pending[size:]
        return result

    def request(self, method, path, body=b"", fragmented=False):
        protocol = "HTTP/1.1" if self.video else "RTSP/1.0"
        identity = "X-Apple-Session-ID: hap-integration-probe" if self.video else "CSeq: 1"
        request = (f"{method} {path} {protocol}\r\n{identity}\r\n"
                   f"X-Apple-HKP: 4\r\nContent-Length: {len(body)}\r\n\r\n").encode() + body
        if self.output:
            wire = b""
            # Deliberately cross HTTP header boundaries with small authenticated frames.
            for offset in range(0, len(request), 37):
                block = request[offset:offset + 37]
                header = len(block).to_bytes(2, "little")
                nonce = bytes(4) + self.sent.to_bytes(8, "little")
                wire += header + self.output.encrypt(nonce, block, header)
                self.sent += 1
        else:
            wire = request
        for offset in range(0, len(wire), 7 if fragmented else max(1, len(wire))):
            self.sock.sendall(wire[offset:offset + (7 if fragmented else len(wire))])
        head = b""
        while not head.endswith(b"\r\n\r\n"):
            head += self.read(1)
            assert len(head) < 65536
        lines = head.decode().split("\r\n")
        assert lines[0].split()[1] == "200", lines[0]
        headers = dict(line.lower().split(":", 1) for line in lines[1:] if ":" in line)
        return self.read(int(headers.get("content-length", "0")))

    def close(self):
        self.reader.close()
        self.sock.close()


def probe(host, port, video):
    connection = Connection(host, port, video)
    try:
        connection.request("POST", "/pair-pin-start")
        m2 = untlv(connection.request("POST", "/pair-setup", tlv({0: b"\0", 6: b"\1", 19: b"\x10"})))
        assert m2[6] == b"\2"
        context = SRPContext("Pair-Setup", "3939", prime=constants.PRIME_3072,
                             generator=constants.PRIME_3072_GEN, hash_func=hashlib.sha512)
        session = SRPClientSession(context)
        key, proof, _ = session.process(m2[3].hex(), m2[2].hex())
        m4 = untlv(connection.request("POST", "/pair-setup", tlv({
            6: b"\3", 3: bytes.fromhex(session.public), 4: bytes.fromhex(proof.decode())})))
        assert m4[6] == b"\4" and session.verify_proof(m4[4].hex().encode()), "Invalid server proof"
        def derive(info):
            return HKDF(algorithm=hashes.SHA512(), length=32, salt=b"Control-Salt",
                        info=info).derive(bytes.fromhex(key.decode()))
        connection.output = ChaCha20Poly1305(derive(b"Control-Write-Encryption-Key"))
        connection.input = ChaCha20Poly1305(derive(b"Control-Read-Encryption-Key"))
        for _ in range(3):
            info = plistlib.loads(connection.request("GET", "/info", fragmented=True))
            assert info["model"] and info["features"]
        print(f"PASS {'HTTP' if video else 'RTSP'}: SRP client/server proofs, encrypted fragmented requests, multi-frame replies, counter progression")
    finally:
        connection.close()


if __name__ == "__main__":
    target = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 7000
    probe(target, port, False)
    probe(target, port, True)
