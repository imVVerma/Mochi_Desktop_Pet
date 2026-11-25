package com.mochi.companion

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.ServiceInfo
import android.graphics.PixelFormat
import android.os.Build
import android.os.IBinder
import android.provider.Settings
import android.util.TypedValue
import android.view.Gravity
import android.view.WindowManager
import androidx.core.app.NotificationCompat

/**
 * Foreground Service that maintains Mochi as an omnipresent floating companion.
 * Features:
 * - Density-independent DP scaling (130dp bounded frame).
 * - Safe lifecycle permission guard (checks canDrawOverlays).
 * - Position persistence (remembers last dragged coordinates).
 * - Interactive notification with "Open App" and "Tuck Mochi In" stop action.
 * - Screen-off battery saver (pauses 60fps canvas loop when phone screen turns off).
 */
class FloatingPetService : Service() {

    private lateinit var windowManager: WindowManager
    private lateinit var petView: PetOverlayView
    private lateinit var layoutParams: WindowManager.LayoutParams
    private lateinit var statsManager: PetStatsManager

    private var screenStateReceiver: BroadcastReceiver? = null

    companion object {
        const val CHANNEL_ID = "MochiFloatingPetChannel"
        const val NOTIFICATION_ID = 1001
        const val ACTION_STOP_PET = "com.mochi.companion.STOP_PET"

        var isRunning: Boolean = false
            private set
        var instance: FloatingPetService? = null
            private set
    }

    override fun onCreate() {
        super.onCreate()

        // 1. Permission Guard
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !Settings.canDrawOverlays(this)) {
            stopSelf()
            return
        }

        instance = this
        isRunning = true
        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        statsManager = PetStatsManager(this)

        startForegroundServiceWithNotification()

        val layoutType = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }

        // 2. DP-Based Density Scaling (145dp x 160dp with speech bubble headroom)
        val widthPx = TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            145f,
            resources.displayMetrics
        ).toInt()
        val heightPx = TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            160f,
            resources.displayMetrics
        ).toInt()

        // 3. Position Persistence
        val initialX = statsManager.positionX.coerceAtLeast(0)
        val initialY = statsManager.positionY.coerceAtLeast(80)

        layoutParams = WindowManager.LayoutParams(
            widthPx,
            heightPx,
            layoutType,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                    WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = initialX
            y = initialY
        }

        petView = PetOverlayView(
            context = this,
            petName = statsManager.petName,
            baseColorHex = statsManager.baseColorHex,
            accessory = statsManager.accessory,
            species = statsManager.characterType
        )

        val touchListener = OverlayTouchListener(
            context = this,
            windowManager = windowManager,
            layoutParams = layoutParams,
            petView = petView,
            statsManager = statsManager
        )
        petView.setOnTouchListener(touchListener)

        try {
            windowManager.addView(petView, layoutParams)
        } catch (e: Exception) {
            stopSelf()
            return
        }

        // 4. Screen-Off Battery Saver
        screenStateReceiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context?, intent: Intent?) {
                when (intent?.action) {
                    Intent.ACTION_SCREEN_OFF -> petView.pauseAnimation()
                    Intent.ACTION_SCREEN_ON -> petView.resumeAnimation()
                }
            }
        }
        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_SCREEN_OFF)
            addAction(Intent.ACTION_SCREEN_ON)
        }
        registerReceiver(screenStateReceiver, filter)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP_PET) {
            stopSelf()
            return START_NOT_STICKY
        }
        return START_STICKY
    }

    fun updateAppearance(colorHex: String, accessory: String, species: String? = null) {
        if (::petView.isInitialized) {
            petView.setBaseColor(colorHex)
            petView.setAccessory(accessory)
            if (species != null) {
                petView.setCharacter(species)
            }
        }
    }

    fun triggerPetReaction(message: String) {
        if (::petView.isInitialized) {
            petView.triggerSquash()
            petView.showSpeech(message)
        }
    }

    fun triggerTreatReaction(message: String) {
        if (::petView.isInitialized) {
            petView.triggerChewBounce()
            petView.showSpeech(message)
        }
    }

    private fun startForegroundServiceWithNotification() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Mochi Companion",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Keeps Mochi active as your floating pocket companion"
                setShowBadge(false)
            }
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }

        // Tap notification to open Flutter app
        val openAppIntent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP
        }
        val pendingOpenIntent = PendingIntent.getActivity(
            this,
            0,
            openAppIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or (if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) PendingIntent.FLAG_IMMUTABLE else 0)
        )

        // Action button to Tuck Mochi In (Stop service)
        val stopIntent = Intent(this, FloatingPetService::class.java).apply {
            action = ACTION_STOP_PET
        }
        val pendingStopIntent = PendingIntent.getService(
            this,
            1,
            stopIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or (if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) PendingIntent.FLAG_IMMUTABLE else 0)
        )

        val notification: Notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Mochi is with you 🐾")
            .setContentText("Tap to open companion • Drag or double-tap to feed 🍓")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentIntent(pendingOpenIntent)
            .addAction(android.R.drawable.ic_menu_close_clear_cancel, "🔕 Tuck Mochi In", pendingStopIntent)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true)
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        isRunning = false
        instance = null

        screenStateReceiver?.let {
            try {
                unregisterReceiver(it)
            } catch (_: Exception) {}
        }

        if (::petView.isInitialized) {
            try {
                windowManager.removeView(petView)
            } catch (_: Exception) {}
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
