package com.usace.segrains

import android.app.Activity
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Color
import android.graphics.Paint
import android.graphics.PointF
import android.os.Bundle
import android.view.MotionEvent
import android.view.View
import android.widget.Button
import android.widget.ImageView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

class ResultActivity : AppCompatActivity() {
    
    private lateinit var photoView: ImageView
    private lateinit var calibrateBtn: Button
    private lateinit var saveDownloadsBtn: Button
    private lateinit var backBtn: Button
    private lateinit var shareBtn: Button
    
    private var originalBitmap: Bitmap? = null
    private var overlayBitmap: Bitmap? = null
    private var grainStats: List<GrainStats> = emptyList()
    private var pxPerMm: Double? = null
    
    private var calibrationPoints = mutableListOf<PointF>()
    private var calibrationDistanceMm: Double = 10.0 // Default 10mm reference
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_result)
        
        // Initialize views
        photoView = findViewById(R.id.photoView)
        calibrateBtn = findViewById(R.id.calibrateBtn)
        saveDownloadsBtn = findViewById(R.id.saveDownloadsBtn)
        backBtn = findViewById(R.id.backBtn)
        shareBtn = findViewById(R.id.shareBtn)
        
        // Load and process the latest captured image
        loadAndProcessImage()
        
        // Also try to load the specific rock image file
        loadSpecificRockImage()
        
        // Set up click listeners
        backBtn.setOnClickListener { finish() }
        calibrateBtn.setOnClickListener { startCalibration() }
        saveDownloadsBtn.setOnClickListener { saveResults() }
        shareBtn.setOnClickListener { shareResults() }
        
        // Load existing calibration if available
        pxPerMm = Prefs.getPxPerMm(this)
        
        // Set up image touch handling for calibration
        photoView.setOnTouchListener { _, event ->
            if (calibrationPoints.size < 2 && event.action == MotionEvent.ACTION_UP) {
                handleCalibrationTouch(event.x, event.y)
                true
            } else false
        }
    }
    
    private fun loadAndProcessImage() {
        lifecycleScope.launch {
            try {
                // Find the most recent captured image
                val capturesDir = File(getExternalFilesDir(null), "captures")
                val allFiles = capturesDir.listFiles()
                
                // Debug: Show what files are found
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@ResultActivity, "Found ${allFiles?.size ?: 0} files in captures", Toast.LENGTH_SHORT).show()
                }
                
                val latestFile = allFiles
                    ?.filter { it.name.startsWith("img_") && it.name.endsWith(".jpg") }
                    ?.maxByOrNull { it.lastModified() }
                
                if (latestFile == null) {
                    Toast.makeText(this@ResultActivity, "No captured image found", Toast.LENGTH_LONG).show()
                    return@launch
                }
                
                // Debug: Show which file is being loaded
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@ResultActivity, "Loading: ${latestFile.name}", Toast.LENGTH_LONG).show()
                }
                
                // Load and process the image
                val bitmap = withContext(Dispatchers.IO) {
                    BitmapFactory.decodeFile(latestFile.absolutePath)
                }
                
                if (bitmap != null) {
                    originalBitmap = bitmap
                    processImage(bitmap)
                } else {
                    Toast.makeText(this@ResultActivity, "Failed to load image", Toast.LENGTH_LONG).show()
                }
                
            } catch (e: Exception) {
                Toast.makeText(this@ResultActivity, "Error loading image: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }
    }
    
    private fun loadSpecificRockImage() {
        lifecycleScope.launch {
            try {
                val capturesDir = File(getExternalFilesDir(null), "captures")
                val rockImageFile = capturesDir.listFiles()
                    ?.find { it.name.startsWith("img_1760997517000") } // Your specific rock image file
                
                if (rockImageFile != null) {
                    val bitmap = withContext(Dispatchers.IO) {
                        BitmapFactory.decodeFile(rockImageFile.absolutePath)
                    }
                    
                    if (bitmap != null) {
                        withContext(Dispatchers.Main) {
                            Toast.makeText(this@ResultActivity, "Loaded rock image: ${rockImageFile.name}", Toast.LENGTH_LONG).show()
                            originalBitmap = bitmap
                            // Immediately process and display the rock image
                            lifecycleScope.launch {
                                processImage(bitmap)
                            }
                        }
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@ResultActivity, "Error loading rock image: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    private suspend fun processImage(bitmap: Bitmap) {
        try {
            val result = withContext(Dispatchers.Default) {
                InferenceEngine.run(bitmap, this@ResultActivity)
            }
            
            grainStats = withContext(Dispatchers.Default) {
                MaskAnalysis.analyze(result.mask)
            }
            
            // Create overlay showing detected grains
            val overlay = createOverlayBitmap(bitmap, result.mask, grainStats)
            overlayBitmap = overlay
            
            withContext(Dispatchers.Main) {
                photoView.setImageBitmap(overlay)
                updateUI()
            }
            
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                Toast.makeText(this@ResultActivity, "Processing failed: ${e.message}", Toast.LENGTH_LONG).show()
                photoView.setImageBitmap(originalBitmap)
            }
        }
    }
    
    private fun createOverlayBitmap(original: Bitmap, mask: Bitmap, stats: List<GrainStats>): Bitmap {
        val overlay = original.copy(Bitmap.Config.ARGB_8888, true)
        val canvas = android.graphics.Canvas(overlay)
        
        // Draw mask overlay with transparency
        val paint = Paint().apply {
            alpha = 100
            color = Color.RED
        }
        
        canvas.drawBitmap(mask, 0f, 0f, paint)
        
        // Draw bounding boxes and numbers for each grain
        val textPaint = Paint().apply {
            color = Color.YELLOW
            textSize = 48f
            isAntiAlias = true
        }
        
        stats.forEach { grain ->
            // Draw bounding box
            val boxPaint = Paint().apply {
                color = Color.YELLOW
                style = Paint.Style.STROKE
                strokeWidth = 4f
            }
            canvas.drawRect(
                grain.bboxX.toFloat(),
                grain.bboxY.toFloat(),
                (grain.bboxX + grain.bboxW).toFloat(),
                (grain.bboxY + grain.bboxH).toFloat(),
                boxPaint
            )
            
            // Draw grain number
            canvas.drawText(
                grain.id.toString(),
                grain.bboxX.toFloat() + 10,
                grain.bboxY.toFloat() + 50,
                textPaint
            )
        }
        
        return overlay
    }
    
    private fun updateUI() {
        val count = grainStats.size
        val pxPerMmText = pxPerMm?.let { "%.2f".format(it) } ?: "Not calibrated"
        
        Toast.makeText(
            this,
            "Detected $count rocks. Calibration: $pxPerMmText px/mm",
            Toast.LENGTH_LONG
        ).show()
    }
    
    private fun startCalibration() {
        calibrationPoints.clear()
        Toast.makeText(this, "Tap two points on a known distance (e.g., 10mm)", Toast.LENGTH_LONG).show()
    }
    
    private fun handleCalibrationTouch(x: Float, y: Float) {
        calibrationPoints.add(PointF(x, y))
        
        if (calibrationPoints.size == 2) {
            val distance = kotlin.math.sqrt(
                (calibrationPoints[1].x - calibrationPoints[0].x).let { it * it } +
                (calibrationPoints[1].y - calibrationPoints[0].y).let { it * it }
            )
            
            pxPerMm = distance / calibrationDistanceMm
            Prefs.setPxPerMm(this, pxPerMm!!)
            
            Toast.makeText(
                this,
                "Calibration complete: ${"%.2f".format(pxPerMm)} px/mm",
                Toast.LENGTH_LONG
            ).show()
            
            updateUI()
        }
    }
    
    private fun saveResults() {
        lifecycleScope.launch {
            try {
                val downloadsDir = File(getExternalFilesDir(null), "downloads").apply { mkdirs() }
                val timestamp = System.currentTimeMillis()
                
                // Save grains CSV
                val grainsFile = File(downloadsDir, "grains_$timestamp.csv")
                CsvWriter.writeGrainsCsv(grainsFile, grainStats, pxPerMm)
                
                // Save gradation CSV if calibrated
                if (pxPerMm != null) {
                    val gradationFile = File(downloadsDir, "gradation_$timestamp.csv")
                    CsvWriter.writeGradationCsvExact(
                        gradationFile, 
                        grainStats, 
                        pxPerMm!!, 
                        location = "Field Analysis", 
                        rockType = "Mixed"
                    )
                }
                
                // Save to Downloads folder
                FileSaver.saveToDownloads(this@ResultActivity, grainsFile, "grains_$timestamp.csv")
                if (pxPerMm != null) {
                    val gradationFile = File(downloadsDir, "gradation_$timestamp.csv")
                    FileSaver.saveToDownloads(this@ResultActivity, gradationFile, "gradation_$timestamp.csv")
                }
                
                Toast.makeText(this@ResultActivity, "Results saved to Downloads", Toast.LENGTH_LONG).show()
                
            } catch (e: Exception) {
                Toast.makeText(this@ResultActivity, "Save failed: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }
    }
    
    private fun shareResults() {
        // TODO: Implement sharing functionality
        Toast.makeText(this, "Share functionality not implemented", Toast.LENGTH_SHORT).show()
    }
}