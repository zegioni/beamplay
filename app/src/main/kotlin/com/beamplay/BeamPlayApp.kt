package com.beamplay

import android.app.Application
import timber.log.Timber

/**
 * BeamPlayApp — The Application class for BeamPlay.
 *
 * WHY: Android requires an Application subclass to run initialization code before
 * any Activity or Service starts. We use this to set up logging (Timber) once
 * at startup.
 *
 * HOW: This class is referenced in AndroidManifest.xml via android:name=".BeamPlayApp".
 * It is instantiated automatically by the Android framework when the app process starts.
 *
 * Example (automatic — no user code needed):
 *   The app starts → Android creates BeamPlayApp → onCreate() runs → Timber is ready.
 */
class BeamPlayApp : Application() {

    override fun onCreate() {
        super.onCreate()
        initLogging()
        com.beamplay.util.NetworkUtils.init(this)
    }

    /**
     * Sets up Timber logging.
     *
     * In debug builds: logs to Android logcat with full file/line info.
     * In release builds: only logs warnings and errors (no verbose/debug output).
     *
     * WHY: Timber is a tiny wrapper around android.util.Log that adds:
     * - Automatic class name as a log tag (no more TAG constants everywhere)
     * - Easy filtering by log level in release builds
     * - The ability to swap the log backend (useful for crash reporting in future)
     */
    private fun initLogging() {
        if (BuildConfig.DEBUG) {
            // Debug tree: logs everything, shows file names and line numbers
            Timber.plant(Timber.DebugTree())
        }
        // In release builds, we deliberately plant no tree to avoid
        // exposing debug information. Critical errors use android.util.Log directly.
    }
}
