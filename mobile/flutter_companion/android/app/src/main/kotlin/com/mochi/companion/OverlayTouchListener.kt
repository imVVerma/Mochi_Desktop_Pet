package com.mochi.companion

import android.animation.ValueAnimator
import android.annotation.SuppressLint
import android.content.Context
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.view.MotionEvent
import android.view.VelocityTracker
import android.view.View
import android.view.WindowManager
import android.view.animation.OvershootInterpolator
import kotlin.math.abs

/**
 * OverlayTouchListener:
 * Handles high-precision touch interaction for Mochi's floating companion:
 * - Single Tap: Pet Mochi (+happiness, squashes softly with haptic).
 * - Double Tap: Feed Strawberry Treat 🍓 (+energy, chew bounce).
 * - Long Press: Cozy cuddle / sleep toggle.
 * - Drag & Fling: Inertial slide with tactile pick-up haptic.
 * - Magnetic Edge Docking: Smooth spring docking to screen margin with position persistence.
 */
class OverlayTouchListener(
    private val context: Context,
    private val windowManager: WindowManager,
    private val layoutParams: WindowManager.LayoutParams,
    private val petView: PetOverlayView,
    private val statsManager: PetStatsManager
) : View.OnTouchListener {

    private var initialX = 0
    private var initialY = 0
    private var initialTouchX = 0f
    private var initialTouchY = 0f
    private var isDragging = false
    private var velocityTracker: VelocityTracker? = null

    // Multi-tap & Long-press detection
    private var lastTapTime = 0L
    private val handler = Handler(Looper.getMainLooper())
    private var longPressRunnable: Runnable? = null
    private var isLongPress = false

    private val vibrator: Vibrator? by lazy {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val vibratorManager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as? VibratorManager
            vibratorManager?.defaultVibrator
        } else {
            @Suppress("DEPRECATION")
            context.getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
        }
    }

    private fun triggerHaptic(durationMs: Long = 15, amplitude: Int = 100) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator?.vibrate(VibrationEffect.createOneShot(durationMs, amplitude))
        } else {
            @Suppress("DEPRECATION")
            vibrator?.vibrate(durationMs)
        }
    }

    @SuppressLint("ClickableViewAccessibility")
    override fun onTouch(v: View, event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                initialX = layoutParams.x
                initialY = layoutParams.y
                initialTouchX = event.rawX
                initialTouchY = event.rawY
                isDragging = false
                isLongPress = false

                velocityTracker?.recycle()
                velocityTracker = VelocityTracker.obtain()
                velocityTracker?.addMovement(event)

                // Schedule long press
                longPressRunnable = Runnable {
                    if (!isDragging) {
                        isLongPress = true
                        triggerHaptic(40, 160)
                        petView.triggerSquash()
                        petView.showSpeech("Cozy cuddle time... 💤")
                    }
                }
                longPressRunnable?.let { handler.postDelayed(it, 650) }
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                velocityTracker?.addMovement(event)
                val dx = (event.rawX - initialTouchX).toInt()
                val dy = (event.rawY - initialTouchY).toInt()

                if (!isDragging && (abs(dx) > 15 || abs(dy) > 15)) {
                    isDragging = true
                    longPressRunnable?.let { handler.removeCallbacks(it) }
                    triggerHaptic(18, 120) // Pick-up haptic tick
                    petView.triggerStretch()
                }

                if (isDragging) {
                    layoutParams.x = initialX + dx
                    layoutParams.y = initialY + dy
                    try {
                        windowManager.updateViewLayout(v, layoutParams)
                    } catch (_: Exception) {}
                }
                return true
            }

            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                longPressRunnable?.let { handler.removeCallbacks(it) }

                velocityTracker?.addMovement(event)
                velocityTracker?.computeCurrentVelocity(1000)

                val vx = velocityTracker?.xVelocity ?: 0f
                val vy = velocityTracker?.yVelocity ?: 0f
                velocityTracker?.recycle()
                velocityTracker = null

                if (!isDragging && !isLongPress) {
                    val now = System.currentTimeMillis()
                    if (now - lastTapTime < 340) {
                        // Double Tap: Feed Strawberry Treat! 🍓
                        triggerHaptic(25, 140)
                        petView.triggerChewBounce()
                        val msg = statsManager.feedTreat()
                        petView.showSpeech(msg)
                        lastTapTime = 0
                    } else {
                        // Single Tap: Pet Mochi! ✨
                        lastTapTime = now
                        triggerHaptic(14, 90)
                        petView.triggerSquash()
                        val msg = statsManager.petMochi()
                        petView.showSpeech(msg)
                    }
                } else if (isDragging) {
                    // Drag ended: apply fling momentum + magnetic edge docking & persist position
                    performMagneticDock(v, vx, vy)
                }
                return true
            }
        }
        return false
    }

    private fun performMagneticDock(view: View, vx: Float, vy: Float) {
        val displayMetrics = context.resources.displayMetrics
        val screenWidth = displayMetrics.widthPixels
        val screenHeight = displayMetrics.heightPixels

        // Estimate target X with fling inertia
        val projectedX = layoutParams.x + (vx * 0.15f).toInt()
        val viewWidth = view.width.coerceAtLeast(180)

        // Snap to nearest edge (Left or Right)
        val targetX = if (projectedX + viewWidth / 2 < screenWidth / 2) {
            16 // Snap to Left Margin
        } else {
            screenWidth - viewWidth - 16 // Snap to Right Margin
        }

        // Clamp target Y within safe screen bounds
        val currentY = layoutParams.y
        val targetY = currentY.coerceIn(100, screenHeight - 320)

        // Persist resting coordinates in PetStatsManager
        statsManager.setPosition(targetX, targetY)

        // Animate smooth spring-docking
        val startX = layoutParams.x
        val animator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 340
            interpolator = OvershootInterpolator(1.3f)
            addUpdateListener { anim ->
                val progress = anim.animatedFraction
                layoutParams.x = (startX + (targetX - startX) * progress).toInt()
                layoutParams.y = targetY
                try {
                    windowManager.updateViewLayout(view, layoutParams)
                } catch (_: Exception) {}
            }
        }
        animator.start()
        triggerHaptic(12, 70) // Dock click
    }
}
