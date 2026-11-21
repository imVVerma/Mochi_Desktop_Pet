package com.mochi.desktoppet.overlay

import android.content.Context
import android.content.SharedPreferences
import java.util.concurrent.TimeUnit

/**
 * PetStatsManager:
 * Port of Desktop Mochi's PetStats and circadian cycle engine.
 * Handles:
 * - Happiness, Energy, and Focus points.
 * - Time-based decay during background execution.
 * - Interaction rewards (petting, focus sprints, feeding treats).
 * - Persistent storage via Android SharedPreferences.
 */
class PetStatsManager(context: Context) {

    private val prefs: SharedPreferences = context.getSharedPreferences("mochi_pet_stats", Context.MODE_PRIVATE)

    var happiness: Int
        get() = prefs.getInt(KEY_HAPPINESS, 90)
        private set(value) = prefs.edit().putInt(KEY_HAPPINESS, value.coerceIn(0, 100)).apply()

    var energy: Int
        get() = prefs.getInt(KEY_ENERGY, 100)
        private set(value) = prefs.edit().putInt(KEY_ENERGY, value.coerceIn(0, 100)).apply()

    var focusMinutes: Int
        get() = prefs.getInt(KEY_FOCUS_MINUTES, 0)
        private set(value) = prefs.edit().putInt(KEY_FOCUS_MINUTES, value).apply()

    init {
        applyCircadianDecay()
    }

    fun petMochi(): String {
        happiness = (happiness + 12).coerceAtMost(100)
        energy = (energy - 2).coerceAtLeast(10)
        updateLastInteractionTime()

        return when {
            happiness >= 85 -> "Purr... I love you! ✨"
            happiness >= 50 -> "*happy ear wiggle* 💕"
            else -> "Thank you for petting me... 🥺"
        }
    }

    fun feedTreat(): String {
        energy = (energy + 20).coerceAtMost(100)
        happiness = (happiness + 10).coerceAtMost(100)
        updateLastInteractionTime()
        return "Yum! Crunchy strawberry treat! 🍓"
    }

    fun recordFocusSession(minutes: Int): String {
        focusMinutes += minutes
        happiness = (happiness + (minutes / 5)).coerceAtMost(100)
        energy = (energy - (minutes / 10)).coerceAtLeast(10)
        updateLastInteractionTime()
        return "Great job focusing for $minutes min! 🎓⭐"
    }

    private fun applyCircadianDecay() {
        val lastTime = prefs.getLong(KEY_LAST_TIMESTAMP, System.currentTimeMillis())
        val diffHours = TimeUnit.MILLISECONDS.toHours(System.currentTimeMillis() - lastTime)

        if (diffHours > 0) {
            val decay = (diffHours * 4).toInt()
            happiness = (happiness - decay).coerceAtLeast(20)
            energy = (energy - decay).coerceAtLeast(20)
            updateLastInteractionTime()
        }
    }

    private fun updateLastInteractionTime() {
        prefs.edit().putLong(KEY_LAST_TIMESTAMP, System.currentTimeMillis()).apply()
    }

    companion object {
        private const val KEY_HAPPINESS = "happiness"
        private const val KEY_ENERGY = "energy"
        private const val KEY_FOCUS_MINUTES = "focus_minutes"
        private const val KEY_LAST_TIMESTAMP = "last_interaction_time"
    }
}
