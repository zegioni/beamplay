package com.beamplay.airplay.handshake

import android.content.Context

/**
 * PairingStore — persists the long-term public keys (Ed25519 LTPK) of controllers that completed PIN
 * pair-setup, keyed by their pairing identifier. pair-verify looks the LTPK up here to authenticate a
 * returning controller, so a paired Mac doesn't need the PIN again. Stored in app-private prefs.
 */
class PairingStore(context: Context) {

    private val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    fun add(controllerId: String, ltpk: ByteArray) {
        prefs.edit().putString(KEY_PREFIX + controllerId, hex(ltpk)).apply()
    }

    fun get(controllerId: String): ByteArray? =
        prefs.getString(KEY_PREFIX + controllerId, null)?.let(::unhex)

    fun remove(controllerId: String) {
        prefs.edit().remove(KEY_PREFIX + controllerId).apply()
    }

    /** True if any controller is paired (used to decide whether to require pairing at all). */
    fun hasAnyPairing(): Boolean = prefs.all.keys.any { it.startsWith(KEY_PREFIX) }

    // ─── Brute-force protection (HAP max-tries) ──────────────────────────────
    // A 4–8 digit PIN is low-entropy, so the real defence against guessing is bounding the number of
    // failed pair-setup attempts. The count is persistent (survives reconnect/restart); a successful
    // pairing resets it, and so does a quiet period of [LOCKOUT_MS] after the last failure — otherwise
    // anyone on the LAN could disable PIN pairing for good with a few bad proofs.
    fun failedAttempts(now: Long = System.currentTimeMillis()): Int {
        val n = prefs.getInt(KEY_FAILS, 0)
        if (n > 0 && now - prefs.getLong(KEY_LAST_FAIL, 0L) >= LOCKOUT_MS) {
            resetFailedAttempts()
            return 0
        }
        return n
    }

    fun recordFailedAttempt(now: Long = System.currentTimeMillis()): Int {
        val n = failedAttempts(now) + 1
        prefs.edit().putInt(KEY_FAILS, n).putLong(KEY_LAST_FAIL, now).apply()
        return n
    }

    fun resetFailedAttempts() {
        prefs.edit().remove(KEY_FAILS).remove(KEY_LAST_FAIL).apply()
    }

    private fun hex(b: ByteArray) = b.joinToString("") { "%02x".format(it) }
    private fun unhex(s: String) = ByteArray(s.length / 2) { s.substring(it * 2, it * 2 + 2).toInt(16).toByte() }

    companion object {
        private const val PREFS = "beamplay_pairings"
        private const val KEY_PREFIX = "ltpk_"
        private const val KEY_FAILS = "pair_failed_attempts"
        private const val KEY_LAST_FAIL = "pair_last_failed_at"
        /** How long PIN pairing stays locked after the last failed attempt. */
        const val LOCKOUT_MS = 15 * 60 * 1000L
    }
}
