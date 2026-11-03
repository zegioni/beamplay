# AirPlay 2 transport: evidence and implementation gaps

Legacy deployment remains enabled. Experimental edits are not a complete transport.

## Verified sources

- https://github.com/postlund/pyatv/blob/master/pyatv/protocols/raop/protocols/airplayv2.py
  implements sender URL playback using verified pairing, base SETUP, encrypted event channel,
  RECORD and /play. It does not implement fp-setup2. This demonstrates an alternative sender
  path, not proof that Safari chooses the same path.
- https://github.com/openairplay/airplay2-receiver/blob/master/ap2-receiver.py
  routes fp-setup2 to handle_auth_setup, but handle_X_setup explicitly rejects unsupported
  encrypted setup. The route is not a working implementation.
- https://github.com/metaneutrons/shairplay-rust
  has concrete receiver modules: crypto/pairing_homekit.rs, crypto/chacha_transport.rs,
  raop/handlers_ap2.rs, raop/connection.rs and raop/event_channel.rs. Review and interoperability
  tests are required before adopting their protocol behavior. HLS handlers alone do not prove
  Safari episode replacement compatibility.
- https://github.com/music-assistant/airplay-cli
  provides an additional AP2 audio sender for comparison of HAP, encrypted RTSP and timing;
  audio support must not be equated with Safari URL-video support.

## Local implementation gaps

PairingSession still implements raw binary legacy pairing. A separate HapTransientPairing now
handles explicit X-Apple-HKP: 4 transient requests, rejecting them when PIN access is enabled.
Both control and HTTP connections switch to HapInputStream/HapOutputStream only after sending
the plaintext M4 response. Reverse HTTP output uses the same encrypted stream after upgrade.
Persistent HAP pair-setup/pair-verify are not implemented.

startMirrorKeys still only drains event socket bytes; it does not decrypt or answer encrypted
HTTP events. The speculative keyless SETUP branch which supplied empty media keys was removed.
Encrypted AP2 event transport and keyless base SETUP remain unimplemented. The experimental
profile is hidden and Legacy remains active; no Roku identity or feature mask is advertised.

## Corrections to earlier conclusions

PTP packets and modern mDNS records do not prove the media replacement algorithm on Roku.
Missing TCP packets do not establish encryption: first inspect all IPv6 traffic and capture coverage.
Bit 2 being absent on Roku does not by itself prove that clearing it avoids fp-setup2 in Safari.
Copying the complete Roku feature mask advertises unimplemented capabilities.
The present evidence does not prove that licensed code is the only possible implementation.

## Next independently verifiable milestone

Implement encrypted event request/response handling and keyless base SETUP without pretending
media keys exist. Only after
an actual pyatv URL playback session passes should a minimal supported profile be tested with Safari.
Legacy remains separately selectable when the experimental path is ready for testing.

## Installed milestone and validation (2026-09-20)

- `testGoogletvDebugUnitTest assembleGoogletvDebug`: 272 tests, zero failures/errors/skips.
- APK installed with `adb install -r --user 0` on BenQGP01, then MainActivity launched.
- `tools/probe-hap-control.py` tested the physical projector with independent `srptools`
  SRP-3072/SHA-512 and Python `cryptography` ChaCha20-Poly1305/HKDF implementations.
  Both RTSP and HTTP paths passed client/server proof verification and three sequential
  encrypted `/info` exchanges, with 37-byte HAP frames fragmented into 7-byte TCP writes.
  This also verified multi-frame receiver replies and continued nonce progression.
- Unit tests cover a separate Python AEAD vector, damaged/truncated frames, failed writes,
  invalid SRP public keys/proofs, sequence checks, and rejecting non-transient pairing.

These checks establish control-channel interoperability, **not** Safari media replacement,
full AirPlay 2 support, or resolution of `media failed to decode`.
