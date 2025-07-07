from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import datetime
import statistics
import numpy as np
from typing import List, Dict
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE = 'buck_converter_data.db'

def init_database():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            device_id TEXT,
            target_voltage REAL,
            actual_voltage REAL,
            error REAL,
            duty_cycle REAL,
            pwm_output REAL,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_telemetry_data(data: Dict):
    """Insert telemetry data into database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO telemetry 
        (timestamp, device_id, target_voltage, actual_voltage, error, duty_cycle, pwm_output)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['timestamp'],
        data['device_id'],
        data['target_voltage'],
        data['actual_voltage'],
        data['error'],
        data['duty_cycle'],
        data['pwm_output']
    ))
    
    conn.commit()
    conn.close()

def get_telemetry_data(limit: int = 100, device_id: str = None) -> List[Dict]:
    """Retrieve telemetry data from database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    if device_id:
        cursor.execute('''
            SELECT * FROM telemetry 
            WHERE device_id = ? 
            ORDER BY received_at DESC 
            LIMIT ?
        ''', (device_id, limit))
    else:
        cursor.execute('''
            SELECT * FROM telemetry 
            ORDER BY received_at DESC 
            LIMIT ?
        ''', (limit,))
    
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    
    conn.close()
    
    return [dict(zip(columns, row)) for row in rows]

@app.route('/api/telemetry', methods=['POST'])
def receive_telemetry():
    """Endpoint to receive telemetry data from ESP32"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['timestamp', 'device_id', 'target_voltage', 
                          'actual_voltage', 'error', 'duty_cycle', 'pwm_output']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Store in database
        insert_telemetry_data(data)
        
        logger.info(f"Received telemetry from {data['device_id']}: "
                   f"Target={data['target_voltage']:.3f}V, "
                   f"Actual={data['actual_voltage']:.3f}V, "
                   f"Error={data['error']:.3f}V")
        
        return jsonify({'status': 'success', 'message': 'Data received'}), 200
        
    except Exception as e:
        logger.error(f"Error processing telemetry: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    """Endpoint to retrieve telemetry data"""
    try:
        limit = request.args.get('limit', 100, type=int)
        device_id = request.args.get('device_id', None)
        
        data = get_telemetry_data(limit, device_id)
        
        return jsonify({
            'status': 'success',
            'count': len(data),
            'data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving telemetry: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/analysis', methods=['GET'])
def analyze_data():
    """Endpoint to provide data analysis"""
    try:
        device_id = request.args.get('device_id', None)
        limit = request.args.get('limit', 1000, type=int)
        
        data = get_telemetry_data(limit, device_id)
        
        if not data:
            return jsonify({'error': 'No data available for analysis'}), 404
        
        # Extract values for analysis
        errors = [d['error'] for d in data]
        actual_voltages = [d['actual_voltage'] for d in data]
        duty_cycles = [d['duty_cycle'] for d in data]
        
        # Calculate statistics
        analysis = {
            'sample_count': len(data),
            'voltage_analysis': {
                'mean': statistics.mean(actual_voltages),
                'median': statistics.median(actual_voltages),
                'std_dev': statistics.stdev(actual_voltages) if len(actual_voltages) > 1 else 0,
                'min': min(actual_voltages),
                'max': max(actual_voltages),
                'range': max(actual_voltages) - min(actual_voltages)
            },
            'error_analysis': {
                'mean_absolute_error': statistics.mean([abs(e) for e in errors]),
                'rms_error': np.sqrt(np.mean(np.square(errors))),
                'max_error': max([abs(e) for e in errors]),
                'steady_state_error': statistics.mean(errors[-10:]) if len(errors) >= 10 else statistics.mean(errors)
            },
            'duty_cycle_analysis': {
                'mean': statistics.mean(duty_cycles),
                'std_dev': statistics.stdev(duty_cycles) if len(duty_cycles) > 1 else 0,
                'min': min(duty_cycles),
                'max': max(duty_cycles)
            }
        }
        
        # Performance metrics
        target_voltage = data[0]['target_voltage'] if data else 2.0
        voltage_tolerance = 0.02  # 1% tolerance
        
        within_tolerance = sum(1 for v in actual_voltages 
                              if abs(v - target_voltage) <= voltage_tolerance)
        
        analysis['performance_metrics'] = {
            'target_voltage': target_voltage,
            'tolerance': voltage_tolerance,
            'samples_within_tolerance': within_tolerance,
            'percentage_within_tolerance': (within_tolerance / len(actual_voltages)) * 100
        }
        
        # Stability analysis
        recent_data = data[:50] if len(data) >= 50 else data
        recent_errors = [d['error'] for d in recent_data]
        
        analysis['stability_metrics'] = {
            'recent_samples': len(recent_data),
            'recent_mean_error': statistics.mean([abs(e) for e in recent_errors]),
            'recent_std_dev': statistics.stdev(recent_errors) if len(recent_errors) > 1 else 0,
            'is_stable': all(abs(e) <= voltage_tolerance for e in recent_errors[-10:]) if len(recent_errors) >= 10 else False
        }
        
        return jsonify({
            'status': 'success',
            'analysis': analysis,
            'generated_at': datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in data analysis: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get list of devices that have sent data"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT device_id, 
                   COUNT(*) as sample_count,
                   MIN(received_at) as first_seen,
                   MAX(received_at) as last_seen
            FROM telemetry 
            GROUP BY device_id
            ORDER BY last_seen DESC
        ''')
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        
        devices = [dict(zip(columns, row)) for row in rows]
        
        return jsonify({
            'status': 'success',
            'devices': devices
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving devices: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'service': 'Buck Converter Telemetry API'
    }), 200

@app.route('/', methods=['GET'])
def home():
    """Simple home page with API documentation"""
    return """
    <h1>Buck Converter Telemetry API</h1>
    <h2>Available Endpoints:</h2>
    <ul>
        <li><strong>POST /api/telemetry</strong> - Receive telemetry data</li>
        <li><strong>GET /api/telemetry</strong> - Retrieve telemetry data</li>
        <li><strong>GET /api/analysis</strong> - Get data analysis</li>
        <li><strong>GET /api/devices</strong> - List connected devices</li>
        <li><strong>GET /api/health</strong> - Health check</li>
    </ul>
    <p>For detailed usage, see the API documentation.</p>
    """

if __name__ == '__main__':
    init_database()
    logger.info("Starting Buck Converter Telemetry API server...")
    app.run(host='0.0.0.0', port=5000, debug=True)