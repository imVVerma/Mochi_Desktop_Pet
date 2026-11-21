package com.example.mochi_companion

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.graphics.PixelFormat
import android.os.Build
import android.os.IBinder
import android.view.Gravity
import android.view.WindowManager
import androidx.core.app.NotificationCompat

/**
 * Foreground Service that maintains Mochi as an omnipresent floating companion
 * over all applications on Android (Wispr Flow architecture).
 */
class FloatingPetService : Service() {

    private lateinit var windowManager: WindowManager
    private lateinit var petView: PetOverlayView
    private lateinit var layoutParams: WindowManager.LayoutParams
    private lateinit var statsManager: PetStatsManager

    companion object {
        const val CHANNEL_ID = "MochiFloatingPetChannel"
        const val NOTIFICATION_ID = 1001
    }

    override fun onCreate() {
        super.onCreate()
        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        statsManager = PetStatsManager(this)

        startForegroundServiceWithNotification()

        val layoutType = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }

        layoutParams = WindowManager.LayoutParams(
            220, // Clean bounded frame for touch hit-testing
            220,
            layoutType,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                    WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 60
            y = 350
        }

        val touchListener = OverlayTouchListener(
            context = this@FloatingPetService,
            windowManager = windowManager,
            layoutParams = this@FloatingPetService.layoutParams,
            onPetClicked = {
                val reaction = statsManager.petMochi()
                petView.showSpeech(reaction)
            }
        )

        petView = PetOverlayView(this).apply {
            setOnTouchListener(touchListener)
        }

        windowManager.addView(petView, layoutParams)
    }

    private fun startForegroundServiceWithNotification() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Mochi Floating Companion",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Keeps Mochi active as your floating desk buddy"
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }

        val notification: Notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Mochi is with you 🐾")
            .setContentText("Tap to pet or drag to reposition")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (::petView.isInitialized) {
            windowManager.removeView(petView)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
