# Buck Converter Control System with ESP32 and Cloud Analytics

This project implements a closed-loop buck converter control system using an ESP32 microcontroller with cloud connectivity for data collection and analysis.

## System Overview

The system consists of:
1. **Buck Converter Circuit** - Steps down 3.3V to 2V at 1kHz switching frequency
2. **ESP32 Controller** - Provides PWM control and voltage feedback with PID regulation
3. **Cloud API** - Collects telemetry data and provides analytics
4. **Data Analysis** - Real-time performance monitoring and system optimization

## Component Specifications

### Calculated Component Values
- **Input Voltage (Vs)**: 3.3V
- **Output Voltage (Vo)**: 2.0V  
- **Switching Frequency**: 1 kHz
- **Inductor (L)**: 47 μH
- **Output Capacitor (C)**: 10 μF
- **Load Resistor (R)**: 20 Ω
- **Theoretical Duty Cycle**: 60.6%

## Files and Code Structure

### Hardware Design
- `src/buck_converter_calculations.md` - Component value calculations
- `schemes/buck_converter_circuit.md` - Circuit diagram and connections

### ESP32 Firmware
- `src/esp32_buck_controller.ino` - Main ESP32 Arduino code
- `src/platformio.ini` - PlatformIO configuration for ESP32

### Cloud API and Analytics
- `src/cloud_api.py` - Flask-based REST API server
- `src/requirements.txt` - Python dependencies
- `src/api_test_client.py` - API testing and demo client

## Features

### ESP32 Controller Features
- **PWM Generation**: 1kHz switching frequency with 12-bit resolution
- **Voltage Feedback**: ADC-based output voltage monitoring
- **PID Control**: Closed-loop regulation with tunable parameters
- **WiFi Connectivity**: Connects to cloud API for data transmission
- **Real-time Monitoring**: Serial output for debugging and monitoring
- **Parameter Tuning**: Runtime PID parameter adjustment via serial commands

### Cloud API Features
- **Data Collection**: Receives telemetry from ESP32 devices
- **SQLite Database**: Stores historical data with timestamps
- **REST Endpoints**: Full API for data retrieval and analysis
- **Performance Analytics**: Statistical analysis of system performance
- **Multi-device Support**: Handles multiple ESP32 devices simultaneously
- **Health Monitoring**: API health checks and device status

### Data Analysis Capabilities
- **Voltage Statistics**: Mean, standard deviation, min/max analysis
- **Error Analysis**: MAE, RMS error, steady-state error calculation
- **Performance Metrics**: Tolerance analysis and stability assessment
- **Duty Cycle Analysis**: PWM statistics and regulation efficiency
- **Real-time Monitoring**: Continuous system performance evaluation

## Quick Start Guide

### 1. Hardware Setup
1. Build the buck converter circuit according to `schemes/buck_converter_circuit.md`
2. Connect ESP32 pins as specified in the circuit documentation
3. Power the system with 3.3V input supply

### 2. ESP32 Programming
1. Install PlatformIO or Arduino IDE
2. Update WiFi credentials in `esp32_buck_controller.ino`:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```
3. Update API endpoint URL:
   ```cpp
   const char* apiEndpoint = "http://your-server:5000/api/telemetry";
   ```
4. Upload the code to ESP32

### 3. Cloud API Setup
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the API server:
   ```bash
   python cloud_api.py
   ```
3. The API will be available at `http://localhost:5000`

### 4. Testing and Monitoring
1. Use the test client to verify API functionality:
   ```bash
   python api_test_client.py --command health
   python api_test_client.py --command test --count 20
   ```
2. Monitor ESP32 output via serial terminal (115200 baud)
3. Access analysis endpoints for performance data

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/telemetry` | Receive telemetry data from ESP32 |
| GET | `/api/telemetry` | Retrieve stored telemetry data |
| GET | `/api/analysis` | Get performance analysis |
| GET | `/api/devices` | List connected devices |
| GET | `/api/health` | API health check |

## PID Tuning

The ESP32 controller supports runtime PID parameter tuning via serial commands:

```
KP=100.0    # Set proportional gain
KI=50.0     # Set integral gain  
KD=10.0     # Set derivative gain
STATUS      # Show current parameters and system status
```

## Performance Monitoring

The system provides comprehensive performance metrics:

- **Voltage Regulation**: Target vs actual voltage tracking
- **Error Analysis**: MAE, RMS, and steady-state error
- **Stability Metrics**: System stability and convergence analysis
- **Efficiency Monitoring**: Duty cycle and PWM utilization
- **Historical Tracking**: Long-term performance trends

## Circuit Safety

- **Current Limiting**: Implement input current protection
- **Thermal Management**: Ensure adequate MOSFET heat sinking
- **ESD Protection**: Use protection diodes on GPIO pins
- **Short Circuit Protection**: Monitor load current for safety

## Troubleshooting

### Common Issues
1. **No Output Voltage**: Check MOSFET switching and gate driver
2. **Poor Regulation**: Tune PID parameters or check feedback circuit
3. **WiFi Connection Issues**: Verify credentials and network connectivity
4. **API Connection Errors**: Check server URL and network firewall settings

### Debug Commands
- Serial monitor at 115200 baud for ESP32 debugging
- API health check: `python api_test_client.py --command health`
- System status via serial: Send "STATUS" command to ESP32

## Future Enhancements

- **Current Sensing**: Add input/output current monitoring
- **Efficiency Calculation**: Real-time efficiency computation
- **Advanced Control**: Implement adaptive or fuzzy logic control
- **Web Dashboard**: Browser-based monitoring interface
- **Data Logging**: CSV export and long-term data storage
- **Alerts**: Email/SMS notifications for system anomalies

## License

This project is part of the WRO Future Engineers competition materials and is provided for educational purposes.

## Contributing

This is a competition project template. Modifications should align with competition requirements and safety standards.