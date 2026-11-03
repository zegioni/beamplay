# Changelog

## 1.0.0 — 2026-11-03

First BeamPlay release.

- New name, icon and Android TV banner; package `com.beamplay.googletv` / `com.beamplay.firetv`.
- AirPlay screen mirroring (iPhone, iPad, Mac) with audio, advertised at 1440p.
- AirPlay audio (RAOP and AirPlay 2 buffered audio) with a tvOS-style Now Playing screen.
- Plain-URL AirPlay video (HLS/MP4) played on the device, with pause, seek and playlist switching.
- An incoming session wakes the display from standby and brings the app to the front.
- Fixed volume (sender volume is ignored), optional PIN pairing, start on boot.
- Fixes in the bundled Apple ALAC decoder (buffer bounds, read-ahead padding).
- Bug fixes from a full code review (see the release notes).
- The experimental multi-room mode was removed.

Based on PhairPlay (Apache-2.0); see NOTICE.md.
