package com.mochi.desktoppet.overlay

import android.animation.ValueAnimator
import android.annotation.SuppressLint
import android.content.Context
import android.graphics.*
import android.view.View
import android.view.animation.LinearInterpolator
import kotlin.math.sin

/**
 * PetOverlayView:
 * Hardware-accelerated custom view that renders Mochi (Floppy Bunny)
 * with animated procedural breathing, floppy ear physics, blushing,
 * sparkle eye blinks, and dynamic speech bubble dialogs.
 */
@SuppressLint("ViewConstructor")
class PetOverlayView(
    context: Context,
    private val petName: String = "Mochi",
    private var baseColorHex: String = "#FFF8E7",
    private var accessory: String = "🎀 Red Ribbon"
) : View(context) {

    private val bodyPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor(baseColorHex)
        style = Paint.Style.FILL
    }

    private val innerEarPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FFD1DC") // Pastel Pink
        style = Paint.Style.FILL
    }

    private val eyePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#2B2B2B")
        style = Paint.Style.FILL
    }

    private val eyeSparklePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.WHITE
        style = Paint.Style.FILL
    }

    private val blushPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FF9AA2")
        alpha = 140
        style = Paint.Style.FILL
    }

    private val accessoryPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FF6B6B")
        style = Paint.Style.FILL
    }

    private val speechBubblePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#FFFFFF")
        style = Paint.Style.FILL
        setShadowLayer(8f, 0f, 4f, Color.argb(40, 0, 0, 0))
    }

    private val speechTextPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#333333")
        textSize = 28f
        typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        textAlign = Paint.Align.CENTER
    }

    // Procedural animation state
    private var breathOffset = 0f
    private var earWiggle = 0f
    private var isBlinking = false
    private var speechMessage: String? = null
    private var speechDismissTime = 0L

    private val breathAnimator = ValueAnimator.ofFloat(0f, (2 * Math.PI).toFloat()).apply {
        duration = 2400
        repeatCount = ValueAnimator.INFINITE
        interpolator = LinearInterpolator()
        addUpdateListener { anim ->
            val phase = anim.animatedValue as Float
            breathOffset = (sin(phase) * 3f).toFloat()
            earWiggle = (sin(phase * 1.5f) * 4f).toFloat()
            invalidate()
        }
    }

    init {
        setLayerType(LAYER_TYPE_HARDWARE, null)
        breathAnimator.start()

        // Trigger occasional natural blinks
        postDelayed(object : Runnable {
            override fun run() {
                isBlinking = true
                invalidate()
                postDelayed({
                    isBlinking = false
                    invalidate()
                }, 140)
                postDelayed(this, (2500..6000).random().toLong())
            }
        }, 3000)
    }

    fun showSpeech(message: String, durationMs: Long = 3500) {
        speechMessage = message
        speechDismissTime = System.currentTimeMillis() + durationMs
        invalidate()
        postDelayed({
            if (System.currentTimeMillis() >= speechDismissTime) {
                speechMessage = null
                invalidate()
            }
        }, durationMs + 50)
    }

    fun setBaseColor(hex: String) {
        baseColorHex = hex
        bodyPaint.color = Color.parseColor(hex)
        invalidate()
    }

    fun setAccessory(acc: String) {
        accessory = acc
        when {
            acc.contains("Blue") -> accessoryPaint.color = Color.parseColor("#4A90E2")
            acc.contains("Gold") || acc.contains("Crown") -> accessoryPaint.color = Color.parseColor("#FFD700")
            acc.contains("Lavender") -> accessoryPaint.color = Color.parseColor("#B39DDB")
            else -> accessoryPaint.color = Color.parseColor("#FF6B6B")
        }
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val cx = width / 2f
        val cy = height / 2f + 16f

        // Draw Speech Bubble if active
        speechMessage?.let { msg ->
            val bubbleRect = RectF(cx - 100f, 10f, cx + 100f, 65f)
            canvas.drawRoundRect(bubbleRect, 18f, 18f, speechBubblePaint)
            // Small pointer tail
            val tailPath = Path().apply {
                moveTo(cx - 8f, 65f)
                lineTo(cx + 8f, 65f)
                lineTo(cx, 75f)
                close()
            }
            canvas.drawPath(tailPath, speechBubblePaint)
            canvas.drawText(msg, cx, 46f, speechTextPaint)
        }

        // Draw Droopy Ears (behind head)
        drawFloppyEars(canvas, cx, cy)

        // Draw Chubby Body & Head
        val headRadius = 46f + breathOffset * 0.4f
        canvas.drawCircle(cx, cy, headRadius, bodyPaint)

        // Draw Blushing Cheeks
        canvas.drawCircle(cx - 26f, cy + 10f, 9f, blushPaint)
        canvas.drawCircle(cx + 26f, cy + 10f, 9f, blushPaint)

        // Draw Eyes (Sparkle or Blink)
        if (isBlinking) {
            val blinkPaint = Paint(eyePaint).apply { strokeWidth = 3f; style = Paint.Style.STROKE }
            canvas.drawLine(cx - 22f, cy - 2f, cx - 12f, cy - 2f, blinkPaint)
            canvas.drawLine(cx + 12f, cy - 2f, cx + 22f, cy - 2f, blinkPaint)
        } else {
            // Left eye
            canvas.drawCircle(cx - 16f, cy - 4f, 5.5f, eyePaint)
            canvas.drawCircle(cx - 14.5f, cy - 6f, 2f, eyeSparklePaint)
            // Right eye
            canvas.drawCircle(cx + 16f, cy - 4f, 5.5f, eyePaint)
            canvas.drawCircle(cx + 17.5f, cy - 6f, 2f, eyeSparklePaint)
        }

        // Tiny cute nose & mouth
        val nosePaint = Paint(eyePaint).apply { color = Color.parseColor("#E57373") }
        canvas.drawCircle(cx, cy + 4f, 2.5f, nosePaint)

        // Draw Accessory (Ribbon / Bow)
        if (accessory != "None") {
            canvas.drawCircle(cx - 30f, cy - 32f, 7f, accessoryPaint)
            canvas.drawCircle(cx - 18f, cy - 32f, 7f, accessoryPaint)
            canvas.drawCircle(cx - 24f, cy - 32f, 4f, eyeSparklePaint)
        }
    }

    private fun drawFloppyEars(canvas: Canvas, cx: Float, cy: Float) {
        val earLength = 52f
        val earWidth = 24f

        // Left ear (drooping left with subtle wiggle)
        canvas.save()
        canvas.translate(cx - 28f, cy - 26f)
        canvas.rotate(-25f + earWiggle)
        val leftEar = RectF(-earWidth / 2, 0f, earWidth / 2, earLength)
        canvas.drawRoundRect(leftEar, 12f, 12f, bodyPaint)
        val leftInner = RectF(-earWidth / 3, 6f, earWidth / 3, earLength - 8f)
        canvas.drawRoundRect(leftInner, 8f, 8f, innerEarPaint)
        canvas.restore()

        // Right ear (drooping right with subtle wiggle)
        canvas.save()
        canvas.translate(cx + 28f, cy - 26f)
        canvas.rotate(25f - earWiggle)
        val rightEar = RectF(-earWidth / 2, 0f, earWidth / 2, earLength)
        canvas.drawRoundRect(rightEar, 12f, 12f, bodyPaint)
        val rightInner = RectF(-earWidth / 3, 6f, earWidth / 3, earLength - 8f)
        canvas.drawRoundRect(rightInner, 8f, 8f, innerEarPaint)
        canvas.restore()
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        breathAnimator.cancel()
    }
}
