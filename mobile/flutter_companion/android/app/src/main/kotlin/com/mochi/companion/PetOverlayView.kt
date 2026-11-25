package com.mochi.companion

import android.animation.ValueAnimator
import android.annotation.SuppressLint
import android.content.Context
import android.graphics.*
import android.os.Build
import android.text.Layout
import android.text.StaticLayout
import android.text.TextPaint
import android.view.View
import android.view.animation.LinearInterpolator
import android.view.animation.OvershootInterpolator
import java.util.Calendar
import kotlin.math.cos
import kotlin.math.sin

/**
 * PetOverlayView:
 * Hardware-accelerated custom view that renders Mochi (Floppy Bunny) with:
 * - Animated procedural breathing, ear momentum, blushing, and sparkle eye blinks.
 * - Procedural rendering for all 6 accessories (Crown, Ribbon, Sakura, Glasses, Top Hat, Scarf).
 * - Dynamic squash & stretch physics on touch, fling, and feeding.
 * - Soft contact shadow grounding Mochi on screen.
 * - Circadian sleep mode after 10 PM.
 * - Speech bubble dialogs with auto-dismissal.
 */
@SuppressLint("ViewConstructor")
class PetOverlayView(
    context: Context,
    private val petName: String = "Mochi",
    private var baseColorHex: String = "#FFF8E7",
    private var accessory: String = "🐾 Natural"
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
        alpha = 150
        style = Paint.Style.FILL
    }

    private val shadowPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.argb(45, 0, 0, 0)
        style = Paint.Style.FILL
    }

    private val speechBubblePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.WHITE
        style = Paint.Style.FILL
        setShadowLayer(8f, 0f, 4f, Color.argb(40, 0, 0, 0))
    }

    private val speechTextPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#333333")
        textSize = 28f
        typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
        textAlign = Paint.Align.CENTER
    }

    // Dynamic Squash & Stretch
    private var scaleXFactor = 1.0f
    private var scaleYFactor = 1.0f

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

    private var blinkRunnable: Runnable? = null

    init {
        setLayerType(LAYER_TYPE_HARDWARE, null)
        breathAnimator.start()

        // Natural random eye blinks
        blinkRunnable = object : Runnable {
            override fun run() {
                isBlinking = true
                invalidate()
                postDelayed({
                    isBlinking = false
                    invalidate()
                }, 140)
                postDelayed(this, (2500..6000).random().toLong())
            }
        }
        blinkRunnable?.let { postDelayed(it, 2500) }
    }

    fun pauseAnimation() {
        if (breathAnimator.isRunning) {
            breathAnimator.pause()
        }
    }

    fun resumeAnimation() {
        if (breathAnimator.isPaused) {
            breathAnimator.resume()
        }
    }

    fun triggerSquash() {
        animateSquashStretch(1.22f, 0.82f, 260)
    }

    fun triggerStretch() {
        animateSquashStretch(0.85f, 1.20f, 280)
    }

    fun triggerChewBounce() {
        animateSquashStretch(1.12f, 0.90f, 220)
    }

    private fun animateSquashStretch(targetSx: Float, targetSy: Float, durationMs: Long) {
        val anim = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = durationMs
            interpolator = OvershootInterpolator(1.8f)
            addUpdateListener { a ->
                val frac = a.animatedFraction
                if (frac < 0.5f) {
                    val p = frac * 2
                    scaleXFactor = 1.0f + (targetSx - 1.0f) * p
                    scaleYFactor = 1.0f + (targetSy - 1.0f) * p
                } else {
                    val p = (frac - 0.5f) * 2
                    scaleXFactor = targetSx + (1.0f - targetSx) * p
                    scaleYFactor = targetSy + (1.0f - targetSy) * p
                }
                invalidate()
            }
        }
        anim.start()
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
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val cx = width / 2f
        val cy = height / 2f + 20f

        // Draw Speech Bubble if active (dynamic wrapping so text never overflows)
        speechMessage?.let { msg ->
            val maxBubbleWidth = (width - 16f).coerceAtLeast(120f)
            val maxTextWidth = (maxBubbleWidth - 28f).toInt()

            val textPaint = TextPaint(Paint.ANTI_ALIAS_FLAG).apply {
                color = Color.parseColor("#333333")
                textSize = 21f
                typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
            }

            val staticLayout = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                StaticLayout.Builder.obtain(msg, 0, msg.length, textPaint, maxTextWidth)
                    .setAlignment(Layout.Alignment.ALIGN_CENTER)
                    .setLineSpacing(2f, 1f)
                    .setIncludePad(false)
                    .build()
            } else {
                @Suppress("DEPRECATION")
                StaticLayout(msg, textPaint, maxTextWidth, Layout.Alignment.ALIGN_CENTER, 1f, 2f, false)
            }

            var measuredLineWidth = 0f
            for (i in 0 until staticLayout.lineCount) {
                val lw = staticLayout.getLineWidth(i)
                if (lw > measuredLineWidth) {
                    measuredLineWidth = lw
                }
            }

            val padX = 14f
            val padY = 8f
            val halfBubbleW = (measuredLineWidth / 2f + padX).coerceIn(45f, maxBubbleWidth / 2f)
            val bubbleH = staticLayout.height.toFloat() + padY * 2f

            val bubbleTop = 6f
            val bubbleBottom = bubbleTop + bubbleH
            val bubbleRect = RectF(cx - halfBubbleW, bubbleTop, cx + halfBubbleW, bubbleBottom)
            canvas.drawRoundRect(bubbleRect, 14f, 14f, speechBubblePaint)

            // Pointer tail
            val tailPath = Path().apply {
                moveTo(cx - 6f, bubbleBottom)
                lineTo(cx + 6f, bubbleBottom)
                lineTo(cx, bubbleBottom + 8f)
                close()
            }
            canvas.drawPath(tailPath, speechBubblePaint)

            // Draw wrapped multi-line text inside bubble
            canvas.save()
            canvas.translate(cx - (maxTextWidth / 2f), bubbleTop + padY)
            staticLayout.draw(canvas)
            canvas.restore()
        }

        // Draw Soft Contact Shadow
        val shadowWidth = 44f * scaleXFactor
        val shadowHeight = 9f
        val shadowRect = RectF(cx - shadowWidth, cy + 42f, cx + shadowWidth, cy + 42f + shadowHeight)
        canvas.drawOval(shadowRect, shadowPaint)

        // Apply Squash & Stretch Transform
        canvas.save()
        canvas.scale(scaleXFactor, scaleYFactor, cx, cy + 40f)

        // Draw Droopy Ears (behind head)
        drawFloppyEars(canvas, cx, cy)

        // Draw Chubby Body & Head
        val headRadius = 45f + breathOffset * 0.4f
        canvas.drawCircle(cx, cy, headRadius, bodyPaint)

        // Draw Blushing Cheeks
        canvas.drawCircle(cx - 26f, cy + 10f, 9f, blushPaint)
        canvas.drawCircle(cx + 26f, cy + 10f, 9f, blushPaint)

        // Check Night Time (Sleepy Eyes)
        val currentHour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY)
        val isNightTime = currentHour >= 22 || currentHour < 7

        if (isNightTime) {
            // Sleepy curved resting eyelids
            val sleepEyePaint = Paint(eyePaint).apply {
                strokeWidth = 3.5f
                style = Paint.Style.STROKE
                strokeCap = Paint.Cap.ROUND
            }
            val leftEyeArc = RectF(cx - 22f, cy - 8f, cx - 10f, cy + 2f)
            val rightEyeArc = RectF(cx + 10f, cy - 8f, cx + 22f, cy + 2f)
            canvas.drawArc(leftEyeArc, 20f, 140f, false, sleepEyePaint)
            canvas.drawArc(rightEyeArc, 20f, 140f, false, sleepEyePaint)
        } else if (isBlinking) {
            val blinkPaint = Paint(eyePaint).apply { strokeWidth = 3.5f; style = Paint.Style.STROKE }
            canvas.drawLine(cx - 22f, cy - 2f, cx - 10f, cy - 2f, blinkPaint)
            canvas.drawLine(cx + 10f, cy - 2f, cx + 22f, cy - 2f, blinkPaint)
        } else {
            // Large anime sparkle eyes
            canvas.drawCircle(cx - 16f, cy - 4f, 5.5f, eyePaint)
            canvas.drawCircle(cx - 14.5f, cy - 6f, 2f, eyeSparklePaint)
            canvas.drawCircle(cx - 17.5f, cy - 2f, 1.2f, eyeSparklePaint)

            canvas.drawCircle(cx + 16f, cy - 4f, 5.5f, eyePaint)
            canvas.drawCircle(cx + 17.5f, cy - 6f, 2f, eyeSparklePaint)
            canvas.drawCircle(cx + 14.5f, cy - 2f, 1.2f, eyeSparklePaint)
        }

        // Tiny cute pink nose
        val nosePaint = Paint(eyePaint).apply { color = Color.parseColor("#E57373") }
        canvas.drawCircle(cx, cy + 5f, 2.5f, nosePaint)

        // Classic bunny split-lip smile
        val mouthPaint = Paint(eyePaint).apply {
            strokeWidth = 2f
            style = Paint.Style.STROKE
            color = Color.parseColor("#7A5050")
        }
        canvas.drawLine(cx, cy + 5f, cx, cy + 8.5f, mouthPaint)
        canvas.drawArc(RectF(cx - 7f, cy + 6f, cx, cy + 12f), 20f, 140f, false, mouthPaint)
        canvas.drawArc(RectF(cx, cy + 6f, cx + 7f, cy + 12f), 20f, 140f, false, mouthPaint)

        // Draw Accessory Outfits
        drawAccessory(canvas, cx, cy)

        canvas.restore()
    }

    private fun drawFloppyEars(canvas: Canvas, cx: Float, cy: Float) {
        val earLength = 52f
        val earWidth = 24f

        // Left ear (drooping left with subtle momentum wiggle)
        canvas.save()
        canvas.translate(cx - 28f, cy - 26f)
        canvas.rotate(-25f + earWiggle)
        val leftEar = RectF(-earWidth / 2, 0f, earWidth / 2, earLength)
        canvas.drawRoundRect(leftEar, 12f, 12f, bodyPaint)
        val leftInner = RectF(-earWidth / 3, 6f, earWidth / 3, earLength - 8f)
        canvas.drawRoundRect(leftInner, 8f, 8f, innerEarPaint)
        canvas.restore()

        // Right ear (drooping right with subtle momentum wiggle)
        canvas.save()
        canvas.translate(cx + 28f, cy - 26f)
        canvas.rotate(25f - earWiggle)
        val rightEar = RectF(-earWidth / 2, 0f, earWidth / 2, earLength)
        canvas.drawRoundRect(rightEar, 12f, 12f, bodyPaint)
        val rightInner = RectF(-earWidth / 3, 6f, earWidth / 3, earLength - 8f)
        canvas.drawRoundRect(rightInner, 8f, 8f, innerEarPaint)
        canvas.restore()
    }

    private fun drawAccessory(canvas: Canvas, cx: Float, cy: Float) {
        val accLower = accessory.lowercase()
        if (accLower.contains("natural") || accLower == "none" || accLower.isEmpty()) {
            return
        }

        when {
            // 1. Silk Ribbon Bow
            accLower.contains("ribbon") || accLower.contains("bow") -> {
                val rx = cx - 24f
                val ry = cy - 32f
                val bowPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#FF6B81") }
                val knotPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#FF3366") }
                canvas.drawOval(RectF(rx - 12f, ry - 6f, rx, ry + 6f), bowPaint)
                canvas.drawOval(RectF(rx, ry - 6f, rx + 12f, ry + 6f), bowPaint)
                canvas.drawCircle(rx, ry, 4f, knotPaint)
            }

            // 2. Royal Golden Crown
            accLower.contains("crown") -> {
                val topY = cy - 48f
                val crownPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
                    color = Color.parseColor("#FFD700")
                    style = Paint.Style.FILL
                }
                val rubyPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
                    color = Color.parseColor("#FF1744")
                    style = Paint.Style.FILL
                }
                val path = Path().apply {
                    moveTo(cx - 16f, topY + 8f)
                    lineTo(cx - 20f, topY - 10f)
                    lineTo(cx - 8f, topY - 2f)
                    lineTo(cx, topY - 14f)
                    lineTo(cx + 8f, topY - 2f)
                    lineTo(cx + 20f, topY - 10f)
                    lineTo(cx + 16f, topY + 8f)
                    close()
                }
                canvas.drawPath(path, crownPaint)
                canvas.drawCircle(cx, topY, 3.5f, rubyPaint)
            }

            // 3. Sakura Cherry Blossom
            accLower.contains("sakura") || accLower.contains("flower") -> {
                val fx = cx - 26f
                val fy = cy - 30f
                val petalPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#FFB7C5") }
                val pollenPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#FFE082") }
                val petalR = 5.5f
                for (angle in listOf(0, 72, 144, 216, 288)) {
                    val rad = Math.toRadians(angle.toDouble())
                    val px = fx + (cos(rad) * 6.5).toFloat()
                    val py = fy + (sin(rad) * 6.5).toFloat()
                    canvas.drawCircle(px, py, petalR, petalPaint)
                }
                canvas.drawCircle(fx, fy, 3.5f, pollenPaint)
            }

            // 4. Smart Glasses
            accLower.contains("glasses") -> {
                val glassPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
                    color = Color.parseColor("#2C3E50")
                    strokeWidth = 3f
                    style = Paint.Style.STROKE
                }
                canvas.drawCircle(cx - 16f, cy - 3f, 8.5f, glassPaint)
                canvas.drawCircle(cx + 16f, cy - 3f, 8.5f, glassPaint)
                canvas.drawLine(cx - 7.5f, cy - 3f, cx + 7.5f, cy - 3f, glassPaint)
            }

            // 5. Gentleman Top Hat
            accLower.contains("hat") -> {
                val hx = cx + 2f
                val hy = cy - 44f
                val hatPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#2B2B2B") }
                val bandPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#E74C3C") }
                // Brim
                canvas.drawRoundRect(RectF(hx - 22f, hy + 2f, hx + 22f, hy + 8f), 4f, 4f, hatPaint)
                // Crown cylinder
                canvas.drawRoundRect(RectF(hx - 14f, hy - 18f, hx + 14f, hy + 4f), 4f, 4f, hatPaint)
                // Red silk band
                canvas.drawRect(RectF(hx - 14f, hy - 2f, hx + 14f, hy + 3f), bandPaint)
            }

            // 6. Cozy Scarf
            accLower.contains("scarf") -> {
                val scarfPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#FF7675") }
                val scarfRect = RectF(cx - 28f, cy + 28f, cx + 28f, cy + 40f)
                canvas.drawRoundRect(scarfRect, 8f, 8f, scarfPaint)
                // Hanging tail
                canvas.drawRoundRect(RectF(cx + 8f, cy + 34f, cx + 20f, cy + 54f), 5f, 5f, scarfPaint)
            }
        }
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        breathAnimator.cancel()
        blinkRunnable?.let { removeCallbacks(it) }
    }
}
