package com.mochi.companion

import android.content.Context
import android.content.SharedPreferences

/**
 * PetStatsManager:
 * Port of Desktop Mochi's PetStats and circadian cycle engine.
 * Single source of truth for:
 * - Happiness, Energy, and Focus points.
 * - Persistent appearance (fur color, wardrobe accessories).
 * - Floating screen position coordinates.
 * - Interaction rewards (petting, feeding strawberry treats, focus sprints).
 * - Smooth circadian decay during background execution.
 */
class PetStatsManager(context: Context) {

    private val prefs: SharedPreferences = context.getSharedPreferences("mochi_pet_stats", Context.MODE_PRIVATE)

    var happiness: Int
        get() = prefs.getInt(KEY_HAPPINESS, 92)
        private set(value) = prefs.edit().putInt(KEY_HAPPINESS, value.coerceIn(0, 100)).apply()

    var energy: Int
        get() = prefs.getInt(KEY_ENERGY, 95)
        private set(value) = prefs.edit().putInt(KEY_ENERGY, value.coerceIn(0, 100)).apply()

    var focusMinutes: Int
        get() = prefs.getInt(KEY_FOCUS_MINUTES, 0)
        private set(value) = prefs.edit().putInt(KEY_FOCUS_MINUTES, value).apply()

    var petName: String
        get() = prefs.getString(KEY_PET_NAME, "Mochi") ?: "Mochi"
        set(value) = prefs.edit().putString(KEY_PET_NAME, value).apply()

    var baseColorHex: String
        get() = prefs.getString(KEY_BASE_COLOR, "#FFF8E7") ?: "#FFF8E7"
        set(value) = prefs.edit().putString(KEY_BASE_COLOR, value).apply()

    var accessory: String
        get() = prefs.getString(KEY_ACCESSORY, "🐾 Natural") ?: "🐾 Natural"
        set(value) = prefs.edit().putString(KEY_ACCESSORY, value).apply()

    var positionX: Int
        get() = prefs.getInt(KEY_POS_X, 60)
        set(value) = prefs.edit().putInt(KEY_POS_X, value).apply()

    var positionY: Int
        get() = prefs.getInt(KEY_POS_Y, 350)
        set(value) = prefs.edit().putInt(KEY_POS_Y, value).apply()

    init {
        applyCircadianDecay()
    }

    fun petMochi(): String {
        happiness = (happiness + 12).coerceAtMost(100)
        if (energy > 15) {
            energy = (energy - 2).coerceAtLeast(10)
        }
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
        energy = (energy - (minutes / 10)).coerceAtLeast(15)
        updateLastInteractionTime()
        return "Great job focusing for $minutes min! 🎓⭐"
    }

    fun setAppearance(colorHex: String, newAccessory: String) {
        baseColorHex = colorHex
        accessory = newAccessory
    }

    fun setPosition(x: Int, y: Int) {
        positionX = x
        positionY = y
    }

    fun toMap(): Map<String, Any> {
        applyCircadianDecay()
        return mapOf(
            "name" to petName,
            "happiness" to happiness,
            "energy" to energy,
            "focusMinutes" to focusMinutes,
            "baseColor" to baseColorHex,
            "accessory" to accessory,
            "posX" to positionX,
            "posY" to positionY
        )
    }

    private fun applyCircadianDecay() {
        val lastTime = prefs.getLong(KEY_LAST_TIMESTAMP, System.currentTimeMillis())
        val now = System.currentTimeMillis()
        val elapsedMs = (now - lastTime).coerceAtLeast(0)
        // Convert to fractional hours
        val elapsedHours = elapsedMs.toDouble() / (1000.0 * 60.0 * 60.0)

        // Apply smooth decay if at least 15 minutes have passed
        if (elapsedHours >= 0.25) {
            val decay = (elapsedHours * 3.0).toInt()
            if (decay > 0) {
                happiness = (happiness - decay).coerceAtLeast(20)
                energy = (energy - decay).coerceAtLeast(20)
                updateLastInteractionTime()
            }
        }
    }

    private fun updateLastInteractionTime() {
        prefs.edit().putLong(KEY_LAST_TIMESTAMP, System.currentTimeMillis()).apply()
    }

    companion object {
        private const val KEY_HAPPINESS = "happiness"
        private const val KEY_ENERGY = "energy"
        private const val KEY_FOCUS_MINUTES = "focus_minutes"
        private const val KEY_PET_NAME = "pet_name"
        private const val KEY_BASE_COLOR = "base_color"
        private const val KEY_ACCESSORY = "accessory"
        private const val KEY_POS_X = "pos_x"
        private const val KEY_POS_Y = "pos_y"
        private const val KEY_LAST_TIMESTAMP = "last_interaction_time"
    }
}
