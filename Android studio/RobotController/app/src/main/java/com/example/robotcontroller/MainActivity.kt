package com.example.robotcontroller

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import okhttp3.FormBody
import okhttp3.OkHttpClient
import okhttp3.Request
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {

    private lateinit var etIpAddress: EditText
    private lateinit var btnConnect: Button
    private lateinit var btnForward: Button
    private lateinit var btnBackward: Button
    private lateinit var btnStartRecording: Button
    private lateinit var btnStopRecording: Button
    private lateinit var btnIgnoreObstacles: Button
    private lateinit var btnEmergencyStop: Button

    private val client = OkHttpClient()
    private var serverUrl: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize UI elements
        etIpAddress = findViewById(R.id.et_ip_address)
        btnConnect = findViewById(R.id.btn_connect)
        btnForward = findViewById(R.id.btn_forward)
        btnBackward = findViewById(R.id.btn_backward)
        btnStartRecording = findViewById(R.id.btn_start_recording)
        btnStopRecording = findViewById(R.id.btn_stop_recording)
        btnIgnoreObstacles = findViewById(R.id.btn_ignore_obstacles)
        btnEmergencyStop = findViewById(R.id.btn_emergency_stop)

        // Disable action buttons until connected
        setButtonsEnabled(false)

        // Connect Button
        btnConnect.setOnClickListener {
            val ipAddress = etIpAddress.text.toString().trim()
            if (ipAddress.isEmpty()) {
                Toast.makeText(this, "Please enter an IP address", Toast.LENGTH_SHORT).show()
            } else {
                serverUrl = "http://$ipAddress:5000"
                Toast.makeText(this, "Connected to $serverUrl", Toast.LENGTH_SHORT).show()
                setButtonsEnabled(true)
            }
        }

        // Command buttons
        btnForward.setOnClickListener { sendCommand("forward") }
        btnBackward.setOnClickListener { sendCommand("backward") }
        btnStartRecording.setOnClickListener { sendCommand("start_recording") }
        btnStopRecording.setOnClickListener { sendCommand("stop_recording") }
        btnIgnoreObstacles.setOnClickListener { sendCommand("ignore_obstacles") }
        btnEmergencyStop.setOnClickListener { sendCommand("emergency_stop") }
    }

    private fun sendCommand(command: String) {
        if (serverUrl == null) {
            Toast.makeText(this, "Please connect to the Raspberry Pi first", Toast.LENGTH_SHORT).show()
            return
        }

        thread {
            val formBody = FormBody.Builder()
                .add("command", command)
                .build()

            val request = Request.Builder()
                .url("$serverUrl/move")
                .post(formBody)
                .build()

            try {
                val response = client.newCall(request).execute()
                if (!response.isSuccessful) {
                    showToast("Command failed: ${response.message}")
                }
            } catch (e: Exception) {
                showToast("Error: ${e.message}")
            }
        }
    }

    private fun showToast(message: String) {
        runOnUiThread {
            Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
        }
    }

    private fun setButtonsEnabled(enabled: Boolean) {
        btnForward.isEnabled = enabled
        btnBackward.isEnabled = enabled
        btnStartRecording.isEnabled = enabled
        btnStopRecording.isEnabled = enabled
        btnIgnoreObstacles.isEnabled = enabled
        btnEmergencyStop.isEnabled = enabled
    }
}
