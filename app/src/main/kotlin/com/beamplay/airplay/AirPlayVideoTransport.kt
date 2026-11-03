package com.beamplay.airplay

/** Receiver identity used for URL-video negotiation. Legacy remains the safe default. */
enum class AirPlayVideoTransport(
    val model: String,
    val sourceVersion: String,
    val protocolVersion: String,
    val featuresLow: Long,
    val featuresHigh: Long,
) {
    LEGACY("AppleTV3,2", "220.68", "1.0", AirPlayFeatures.LOW, AirPlayFeatures.HIGH),
    // Keep the experimental identity separate; do not claim Roku's unsupported feature mask.
    AIRPLAY_2("AppleTV14,1", "377.40.00", "1.1", AirPlayFeatures.LOW, AirPlayFeatures.HIGH);

    val isModern: Boolean get() = this == AIRPLAY_2
    val features: Long get() = (featuresHigh shl 32) or featuresLow
    val featuresTxt: String get() = "0x%X,0x%X".format(featuresLow, featuresHigh)
}
