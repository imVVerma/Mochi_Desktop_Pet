package com.mochi.desktoppet.overlay

import android.animation.ValueAnimator
import android.annotation.SuppressLint
import android.content.Context
import android.os.Build
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
 * Handles high-precision touch interaction for Mochi's floating bubble.
 * Features:
 * - Micro-tap vs drag detection (< 10px slop).
 * - Fling velocity tracking with inertial slide.
 * - Magnetic edge docking (snaps smoothly to screen edges or bottom corners).
 * - Tactile haptic feedback on pick-up and drop.
 */
class OverlayTouchListener(
    private val context: Context,
    private val windowManager: WindowManager,
    private val layoutParams: WindowManager.LayoutParams,
    private val onPetClicked: () -> Unit
) : View.OnTouchListener {

    private var initialX = 0
    private var initialY = 0
    private var initialTouchX = 0f
    private var initialTouchY = 0f
    private var isDragging = false
    private var velocityTracker: VelocityTracker? = null

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

                velocityTracker?.recycle()
                velocityTracker = VelocityTracker.obtain()
                velocityTracker?.addMovement(event)
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                velocityTracker?.addMovement(event)
                val dx = (event.rawX - initialTouchX).toInt()
                val dy = (event.rawY - initialTouchY).toInt()

                if (!isDragging && (abs(dx) > 15 || abs(dy) > 15)) {
                    isDragging = true
                    triggerHaptic(durationMs = 20, amplitude = 120) // Pick-up haptic tick
                }

                if (isDragging) {
                    layoutParams.x = initialX + dx
                    layoutParams.y = initialY + dy
                    windowManager.updateViewLayout(v, layoutParams)
                }
                return true
            }

            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                velocityTracker?.addMovement(event)
                velocityTracker?.computeCurrentVelocity(1000)

                val vx = velocityTracker?.xVelocity ?: 0f
                val vy = velocityTracker?.yVelocity ?: 0f
                velocityTracker?.recycle()
                velocityTracker = null

                if (!isDragging) {
                    // Tap event
                    triggerHaptic(durationMs = 12, amplitude = 80)
                    onPetClicked()
                } else {
                    // Drag ended: apply fling + magnetic edge docking
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

        // Estimate target X with inertia
        val projectedX = layoutParams.x + (vx * 0.15f).toInt()
        val viewWidth = view.width.coerceAtLeast(180)

        // Snap to nearest edge (Left or Right)
        val targetX = if (projectedX + viewWidth / 2 < screenWidth / 2) {
            16 // Snap to Left Margin
        } else {
            screenWidth - viewWidth - 16 // Snap to Right Margin
        }

        // Clamp target Y within screen bounds
        val currentY = layoutParams.y
        val targetY = currentY.coerceIn(100, screenHeight - 350)

        // Animate smooth spring-docking
        val startX = layoutParams.x
        val animator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = 320
            interpolator = OvershootInterpolator(1.2f)
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
        triggerHaptic(durationMs = 10, amplitude = 60) // Dock click
    }
}
