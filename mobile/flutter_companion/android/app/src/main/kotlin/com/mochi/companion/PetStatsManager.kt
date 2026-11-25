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

    var characterType: String
        get() = prefs.getString(KEY_CHARACTER_TYPE, "bunny") ?: "bunny"
        set(value) = prefs.edit().putString(KEY_CHARACTER_TYPE, value.lowercase()).apply()

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

        return when (characterType) {
            "cat" -> when {
                happiness >= 85 -> "Purr... I love you! ✨"
                happiness >= 50 -> "Meow! *happy tail swish* 🐱"
                else -> "Meow... *rubs against hand* 💕"
            }
            "dog" -> when {
                happiness >= 85 -> "Aroo! Best friend forever! ✨"
                happiness >= 50 -> "Woof! *tail wags excitedly* 🐶"
                else -> "*happy happy panting* 🐾"
            }
            "panda" -> when {
                happiness >= 85 -> "Chirp! Bao gives big warm hug! ✨"
                happiness >= 50 -> "*happy roll and tumble* 🐼"
                else -> "*snuggles closer to you* 💕"
            }
            else -> when {
                happiness >= 85 -> "Purr... I love you! ✨"
                happiness >= 50 -> "*happy ear wiggle* 💕"
                else -> "Thank you for petting me... 🥺"
            }
        }
    }

    fun feedTreat(): String {
        energy = (energy + 20).coerceAtMost(100)
        happiness = (happiness + 10).coerceAtMost(100)
        updateLastInteractionTime()
        return when (characterType) {
            "cat" -> "Nom nom! Tasty salmon treat! 🐟"
            "dog" -> "Crunch crunch! Yummy puppy biscuit! 🦴"
            "panda" -> "Crunchy bamboo shoot snack! 🎋"
            else -> "Yum! Crunchy strawberry treat! 🍓"
        }
    }

    fun recordFocusSession(minutes: Int): String {
        focusMinutes += minutes
        happiness = (happiness + (minutes / 5)).coerceAtMost(100)
        energy = (energy - (minutes / 10)).coerceAtLeast(15)
        updateLastInteractionTime()
        return "Great job focusing for $minutes min! 🎓⭐"
    }

    fun setAppearance(colorHex: String, newAccessory: String, species: String? = null) {
        baseColorHex = colorHex
        accessory = newAccessory
        if (species != null) {
            characterType = species
        }
    }

    fun setCharacter(species: String, newName: String? = null, colorHex: String? = null) {
        characterType = species
        if (newName != null) {
            petName = newName
        }
        if (colorHex != null) {
            baseColorHex = colorHex
        }
    }

    fun setPosition(x: Int, y: Int) {
        positionX = x
        positionY = y
    }

    fun toMap(): Map<String, Any> {
        return mapOf(
            "name" to petName,
            "species" to characterType,
            "characterType" to characterType,
            "happiness" to happiness,
            "energy" to energy,
            "focusMinutes" to focusMinutes,
            "baseColor" to baseColorHex,
            "accessory" to accessory,
            "posX" to positionX,
            "posY" to positionY
        )
    }

    fun applyCircadianDecay() {
        val lastTime = prefs.getLong(KEY_LAST_TIMESTAMP, System.currentTimeMillis())
        val now = System.currentTimeMillis()
        val elapsedMs = (now - lastTime).coerceAtLeast(0)
        val elapsedHours = elapsedMs.toDouble() / (1000.0 * 60.0 * 60.0)

        // Decay 3 points per hour (1 point every 20 minutes)
        val decayPoints = (elapsedHours * 3.0).toInt()
        if (decayPoints > 0) {
            happiness = (happiness - decayPoints).coerceAtLeast(20)
            energy = (energy - decayPoints).coerceAtLeast(20)
            // Advance timestamp ONLY by the exact time consumed, preserving fractional remainder
            val msConsumed = (decayPoints.toDouble() / 3.0 * 3600000.0).toLong()
            prefs.edit().putLong(KEY_LAST_TIMESTAMP, lastTime + msConsumed).apply()
        }
    }

    private fun updateLastInteractionTime() {
        prefs.edit().putLong(KEY_LAST_TIMESTAMP, System.currentTimeMillis()).apply()
    }

    companion object {
        private const val KEY_CHARACTER_TYPE = "character_type"
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
