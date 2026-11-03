# BeamPlay

Copyright (C) 2026 zegioni — https://github.com/zegioni/beamplay

This program is free software: you can redistribute it and/or modify it under the terms of the
GNU Affero General Public License version 3 as published by the Free Software Foundation (see `LICENSE`),
with the additional terms below.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
License for more details.

## Additional terms (section 7 of the GNU AGPL v3)

These terms supplement the license for all files in this repository that are not listed under
"Third-party code" below:

1. **Attribution (section 7 b).** Every copy and every modified version, in source or object form, and any
   user interface that shows legal notices, must keep this notice and the copyright line
   "Copyright (C) 2026 zegioni", together with a link to https://github.com/zegioni/beamplay.
   Modified versions must say that they were changed and must not suggest they are the original.
2. **Name and icon (section 7 e).** No rights are granted under trademark law, or otherwise, to use the name
   "BeamPlay" or the icon and banner (`docs/icon.png`, `app/src/main/res/mipmap-*/ic_launcher.png`,
   `app/src/main/res/drawable-nodpi/app_banner.png`). Modified or redistributed versions must use a
   different name and a different icon.
3. **No misrepresentation (section 7 c).** Modified versions must be marked as different from the original and
   must not be presented as made or endorsed by the author.

## Based on PhairPlay

BeamPlay started from **PhairPlay** (https://github.com/mazer666/PhairPlay),
Copyright 2026 PhairPlay Contributors (mazer666, kuba/kubacast, Die Klaue, aliozancil, Martijn Hoogenbosch
and others), licensed under the Apache License 2.0 — full text in `LICENSES/Apache-2.0-PhairPlay.txt`.
The PhairPlay parts remain available under that license; BeamPlay as a whole, including all changes made
since (renamed packages, the tvOS-style interface, fixed volume, URL video and HAP pairing work, ALAC crash
fixes, bug fixes, removed experimental features), is distributed under the GNU AGPL v3 as stated above.
BeamPlay is not affiliated with or endorsed by the PhairPlay authors.

## Third-party code

| Component | Location | License |
|---|---|---|
| Apple ALAC decoder | `app/src/main/cpp/alac/` | Apache License 2.0 |
| playfair (FairPlay key decryption) | `app/src/main/cpp/playfair/` | GNU GPL v3 (as published with UxPlay/shairplay) |
| Inter typeface | `app/src/main/res/font/`, `third_party/inter/` | SIL Open Font License 1.1 |
| AndroidX, Media3/ExoPlayer, Kotlin coroutines, Timber, Bouncy Castle, dd-plist | Gradle dependencies | Apache 2.0 / MIT-style, see each project |
| Google Cast TV SDK (`play-services-cast-tv`, googletv flavor only; the Cast receiver is off by default) | Gradle dependency | Android Software Development Kit License |

## Trademarks

AirPlay, Apple TV, HomePod, iPhone, iPad and Mac are trademarks of Apple Inc. BeamPlay is an independent
project and is not affiliated with, authorized or endorsed by Apple Inc. BenQ, Android TV and Fire TV are
trademarks of their respective owners.

## Use at your own risk

BeamPlay is provided "as is", without warranty of any kind. You are responsible for how you install and use it.
