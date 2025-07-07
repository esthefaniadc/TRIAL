#!/usr/bin/env python3
"""
Simplified Buck Converter Data Logger and Analyzer

This script provides basic data logging and analysis functionality
without requiring external dependencies like Flask.
"""

import sqlite3
import json
import statistics
import datetime
import time
from typing import List, Dict, Optional

class BuckConverterDataLogger:
    def __init__(self, database_path='buck_converter_data.db'):
        self.database_path = database_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database"""
        conn = sqlite3.connect(self.database_path)
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
        print("✅ Database initialized successfully")
    
    def log_data(self, data: Dict) -> bool:
        """Log telemetry data to database"""
        try:
            conn = sqlite3.connect(self.database_path)
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
            return True
            
        except Exception as e:
            print(f"Error logging data: {e}")
            return False
    
    def get_data(self, limit: int = 100, device_id: Optional[str] = None) -> List[Dict]:
        """Retrieve telemetry data from database"""
        try:
            conn = sqlite3.connect(self.database_path)
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
            
        except Exception as e:
            print(f"Error retrieving data: {e}")
            return []
    
    def analyze_performance(self, device_id: Optional[str] = None, limit: int = 1000) -> Dict:
        """Analyze system performance"""
        data = self.get_data(limit, device_id)
        
        if not data:
            return {'error': 'No data available for analysis'}
        
        # Extract values for analysis
        errors = [d['error'] for d in data]
        actual_voltages = [d['actual_voltage'] for d in data]
        duty_cycles = [d['duty_cycle'] for d in data]
        
        # Calculate statistics
        analysis = {
            'sample_count': len(data),
            'analysis_timestamp': datetime.datetime.now().isoformat(),
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
                'rms_error': (sum(e**2 for e in errors) / len(errors))**0.5,
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
        
        return analysis
    
    def generate_test_data(self, device_id="TEST_ESP32", count=50):
        """Generate simulated test data for demonstration"""
        import random
        
        print(f"Generating {count} test data points...")
        
        for i in range(count):
            # Simulate realistic buck converter data
            target_voltage = 2.0
            
            # Simulate some system dynamics
            if i < 10:  # Startup transient
                noise = random.uniform(-0.1, 0.05)  # Larger initial error
            else:  # Steady state
                noise = random.uniform(-0.02, 0.02)  # ±20mV noise
            
            actual_voltage = max(0, target_voltage + noise)
            error = target_voltage - actual_voltage
            duty_cycle = 60.6 + random.uniform(-3, 3)  # Around theoretical duty cycle
            duty_cycle = max(0, min(100, duty_cycle))  # Clamp to valid range
            pwm_output = (duty_cycle / 100.0) * 4095
            
            data = {
                "timestamp": int((time.time() + i) * 1000),  # Spread over time
                "device_id": device_id,
                "target_voltage": target_voltage,
                "actual_voltage": actual_voltage,
                "error": error,
                "duty_cycle": duty_cycle,
                "pwm_output": int(pwm_output)
            }
            
            success = self.log_data(data)
            if not success:
                print(f"❌ Failed to log data point {i+1}")
                break
        
        print(f"✅ Generated {count} test data points")
    
    def print_analysis(self, analysis: Dict):
        """Print formatted analysis results"""
        if 'error' in analysis:
            print(f"❌ {analysis['error']}")
            return
        
        print("\n" + "="*60)
        print("BUCK CONVERTER PERFORMANCE ANALYSIS")
        print("="*60)
        
        # Voltage Analysis
        va = analysis['voltage_analysis']
        print(f"\n📊 Voltage Performance:")
        print(f"   Mean Output: {va['mean']:.4f}V")
        print(f"   Standard Deviation: {va['std_dev']:.4f}V")
        print(f"   Voltage Range: {va['min']:.4f}V - {va['max']:.4f}V")
        print(f"   Total Range: {va['range']:.4f}V")
        
        # Error Analysis
        ea = analysis['error_analysis']
        print(f"\n📈 Error Analysis:")
        print(f"   Mean Absolute Error: {ea['mean_absolute_error']:.4f}V")
        print(f"   RMS Error: {ea['rms_error']:.4f}V")
        print(f"   Maximum Error: {ea['max_error']:.4f}V")
        print(f"   Steady State Error: {ea['steady_state_error']:.4f}V")
        
        # Performance Metrics
        pm = analysis['performance_metrics']
        print(f"\n🎯 Performance Metrics:")
        print(f"   Target Voltage: {pm['target_voltage']:.2f}V")
        print(f"   Tolerance: ±{pm['tolerance']:.3f}V ({pm['tolerance']/pm['target_voltage']*100:.1f}%)")
        print(f"   Samples Within Tolerance: {pm['samples_within_tolerance']}")
        print(f"   Percentage Within Tolerance: {pm['percentage_within_tolerance']:.1f}%")
        
        # Duty Cycle Analysis
        da = analysis['duty_cycle_analysis']
        print(f"\n⚡ Duty Cycle Analysis:")
        print(f"   Mean Duty Cycle: {da['mean']:.2f}%")
        print(f"   Standard Deviation: {da['std_dev']:.2f}%")
        print(f"   Range: {da['min']:.2f}% - {da['max']:.2f}%")
        
        print(f"\n📋 Total Samples: {analysis['sample_count']}")
        print(f"🕒 Analysis Time: {analysis['analysis_timestamp']}")

def main():
    print("Buck Converter Data Logger and Analyzer")
    print("======================================")
    
    logger = BuckConverterDataLogger()
    
    while True:
        print("\nSelect an option:")
        print("1. Generate test data")
        print("2. View recent data")
        print("3. Analyze performance")
        print("4. Export data to JSON")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            count = input("Number of test data points to generate (default: 50): ").strip()
            count = int(count) if count.isdigit() else 50
            logger.generate_test_data(count=count)
            
        elif choice == '2':
            limit = input("Number of recent data points to show (default: 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            data = logger.get_data(limit=limit)
            
            if data:
                print(f"\n📊 Recent {len(data)} data points:")
                print("-" * 80)
                print(f"{'Time':<20} {'Target':<8} {'Actual':<8} {'Error':<8} {'Duty%':<6}")
                print("-" * 80)
                for point in data[:10]:  # Show first 10
                    dt = datetime.datetime.fromtimestamp(point['timestamp'] / 1000.0)
                    print(f"{dt.strftime('%H:%M:%S'):<20} "
                          f"{point['target_voltage']:<8.3f} "
                          f"{point['actual_voltage']:<8.3f} "
                          f"{point['error']:<8.3f} "
                          f"{point['duty_cycle']:<6.1f}")
            else:
                print("❌ No data available")
                
        elif choice == '3':
            analysis = logger.analyze_performance()
            logger.print_analysis(analysis)
            
        elif choice == '4':
            filename = input("Export filename (default: export.json): ").strip()
            filename = filename if filename else "export.json"
            
            data = logger.get_data(limit=1000)
            if data:
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"✅ Exported {len(data)} data points to {filename}")
            else:
                print("❌ No data to export")
                
        elif choice == '5':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-5.")

if __name__ == '__main__':
    main()