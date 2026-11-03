package com.beamplay.airplay.handshake

import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment

@RunWith(RobolectricTestRunner::class)
class PairingStoreLockoutTest {

    private val store = PairingStore(RuntimeEnvironment.getApplication()).also { it.resetFailedAttempts() }

    @Test
    fun failedAttemptsAccumulateWithinTheLockoutWindow() {
        val t0 = 1_000_000L
        repeat(3) { store.recordFailedAttempt(t0 + it * 1_000L) }
        assertEquals(3, store.failedAttempts(t0 + 5_000L))
    }

    @Test
    fun lockoutExpiresAfterQuietPeriod() {
        val t0 = 1_000_000L
        repeat(10) { store.recordFailedAttempt(t0) }
        assertEquals(10, store.failedAttempts(t0 + PairingStore.LOCKOUT_MS - 1))
        assertEquals(0, store.failedAttempts(t0 + PairingStore.LOCKOUT_MS))
        // counting starts over after the reset
        assertEquals(1, store.recordFailedAttempt(t0 + PairingStore.LOCKOUT_MS + 1))
    }

    @Test
    fun successfulPairingClearsTheCounter() {
        store.recordFailedAttempt(1_000L)
        store.resetFailedAttempts()
        assertEquals(0, store.failedAttempts(2_000L))
    }
}
