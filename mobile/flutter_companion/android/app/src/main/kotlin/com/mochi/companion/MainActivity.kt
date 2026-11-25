package com.mochi.companion

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.annotation.NonNull
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

/**
 * MainActivity:
 * High-performance native bridge between Flutter companion dashboard
 * and the omnipresent Android FloatingPetService overlay.
 *
 * Exposes:
 * - Single source of truth pet stats (happiness, energy, focus, wardrobe).
 * - Live service lifecycle controls (isServiceRunning, start, stop).
 * - Real-time wardrobe synchronization across app and overlay.
 * - Dynamic care actions (petting, feeding treats, focus sprints).
 */
class MainActivity : FlutterActivity() {
    private val CHANNEL = "com.mochi.companion/overlay"
    private lateinit var statsManager: PetStatsManager

    override fun configureFlutterEngine(@NonNull flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        statsManager = PetStatsManager(this)

        // Request POST_NOTIFICATIONS permission on Android 13+
        requestNotificationPermissionIfNeeded()

        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "checkOverlayPermission" -> {
                    val hasPermission = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                        Settings.canDrawOverlays(this)
                    } else {
                        true
                    }
                    result.success(hasPermission)
                }

                "requestOverlayPermission" -> {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !Settings.canDrawOverlays(this)) {
                        val intent = Intent(
                            Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                            Uri.parse("package:$packageName")
                        )
                        startActivity(intent)
                    }
                    result.success(true)
                }

                "isServiceRunning" -> {
                    result.success(FloatingPetService.isRunning)
                }

                "startFloatingPet" -> {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !Settings.canDrawOverlays(this)) {
                        result.error("PERMISSION_DENIED", "Overlay permission not granted", null)
                    } else {
                        val intent = Intent(this, FloatingPetService::class.java)
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                            startForegroundService(intent)
                        } else {
                            startService(intent)
                        }
                        result.success(true)
                    }
                }

                "stopFloatingPet" -> {
                    val intent = Intent(this, FloatingPetService::class.java)
                    stopService(intent)
                    result.success(true)
                }

                "getPetStats" -> {
                    result.success(statsManager.toMap())
                }

                "petMochi" -> {
                    val reaction = statsManager.petMochi()
                    FloatingPetService.instance?.triggerPetReaction(reaction)
                    result.success(mapOf(
                        "reaction" to reaction,
                        "stats" to statsManager.toMap()
                    ))
                }

                "feedTreat" -> {
                    val reaction = statsManager.feedTreat()
                    FloatingPetService.instance?.triggerTreatReaction(reaction)
                    result.success(mapOf(
                        "reaction" to reaction,
                        "stats" to statsManager.toMap()
                    ))
                }

                "recordFocusSession" -> {
                    val minutes = call.argument<Int>("minutes") ?: 25
                    val reaction = statsManager.recordFocusSession(minutes)
                    result.success(mapOf(
                        "reaction" to reaction,
                        "stats" to statsManager.toMap()
                    ))
                }

                "setAppearance" -> {
                    val colorHex = call.argument<String>("baseColor") ?: statsManager.baseColorHex
                    val accessory = call.argument<String>("accessory") ?: statsManager.accessory
                    val species = call.argument<String>("species") ?: call.argument<String>("characterType")
                    statsManager.setAppearance(colorHex, accessory, species)
                    FloatingPetService.instance?.updateAppearance(colorHex, accessory, species)
                    result.success(statsManager.toMap())
                }

                "setCharacter" -> {
                    val species = call.argument<String>("species") ?: call.argument<String>("character") ?: "bunny"
                    val name = call.argument<String>("name")
                    val colorHex = call.argument<String>("baseColor")
                    val accessory = call.argument<String>("accessory") ?: statsManager.accessory
                    statsManager.setCharacter(species, name, colorHex)
                    FloatingPetService.instance?.updateAppearance(statsManager.baseColorHex, accessory, species)
                    result.success(statsManager.toMap())
                }

                else -> result.notImplemented()
            }
        }
    }

    private fun requestNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(
                    this,
                    arrayOf(Manifest.permission.POST_NOTIFICATIONS),
                    1002
                )
            }
        }
    }
}
