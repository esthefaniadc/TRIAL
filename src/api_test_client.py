#!/usr/bin/env python3
"""
API Test Client for Buck Converter Telemetry System

This script demonstrates how to interact with the cloud API and provides
functionality to test the system without the ESP32 hardware.
"""

import requests
import json
import time
import random
import argparse
from datetime import datetime

class BuckConverterAPIClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
    
    def send_test_data(self, device_id="TEST_ESP32", count=10, interval=1):
        """Send simulated telemetry data to test the API"""
        print(f"Sending {count} test data points...")
        
        for i in range(count):
            # Simulate realistic buck converter data
            target_voltage = 2.0
            noise = random.uniform(-0.02, 0.02)  # ±20mV noise
            actual_voltage = target_voltage + noise
            error = target_voltage - actual_voltage
            duty_cycle = 60.6 + random.uniform(-2, 2)  # Around theoretical duty cycle
            pwm_output = (duty_cycle / 100.0) * 4095
            
            data = {
                "timestamp": int(time.time() * 1000),
                "device_id": device_id,
                "target_voltage": target_voltage,
                "actual_voltage": actual_voltage,
                "error": error,
                "duty_cycle": duty_cycle,
                "pwm_output": pwm_output
            }
            
            try:
                response = requests.post(f"{self.base_url}/api/telemetry", 
                                       json=data, 
                                       timeout=5)
                if response.status_code == 200:
                    print(f"✓ Data point {i+1} sent successfully")
                else:
                    print(f"✗ Failed to send data point {i+1}: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"✗ Error sending data point {i+1}: {e}")
            
            if i < count - 1:  # Don't sleep after the last iteration
                time.sleep(interval)
    
    def get_telemetry_data(self, limit=10, device_id=None):
        """Retrieve telemetry data from the API"""
        params = {'limit': limit}
        if device_id:
            params['device_id'] = device_id
            
        try:
            response = requests.get(f"{self.base_url}/api/telemetry", 
                                  params=params, 
                                  timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"Retrieved {data['count']} data points")
                return data['data']
            else:
                print(f"Failed to retrieve data: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving data: {e}")
            return None
    
    def get_analysis(self, device_id=None):
        """Get data analysis from the API"""
        params = {}
        if device_id:
            params['device_id'] = device_id
            
        try:
            response = requests.get(f"{self.base_url}/api/analysis", 
                                  params=params, 
                                  timeout=5)
            if response.status_code == 200:
                analysis = response.json()['analysis']
                self.print_analysis(analysis)
                return analysis
            else:
                print(f"Failed to get analysis: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error getting analysis: {e}")
            return None
    
    def print_analysis(self, analysis):
        """Print formatted analysis results"""
        print("\n" + "="*50)
        print("BUCK CONVERTER PERFORMANCE ANALYSIS")
        print("="*50)
        
        # Voltage Analysis
        va = analysis['voltage_analysis']
        print(f"\nVoltage Performance:")
        print(f"  Mean Output: {va['mean']:.4f}V")
        print(f"  Standard Deviation: {va['std_dev']:.4f}V")
        print(f"  Voltage Range: {va['min']:.4f}V - {va['max']:.4f}V")
        print(f"  Total Range: {va['range']:.4f}V")
        
        # Error Analysis
        ea = analysis['error_analysis']
        print(f"\nError Analysis:")
        print(f"  Mean Absolute Error: {ea['mean_absolute_error']:.4f}V")
        print(f"  RMS Error: {ea['rms_error']:.4f}V")
        print(f"  Maximum Error: {ea['max_error']:.4f}V")
        print(f"  Steady State Error: {ea['steady_state_error']:.4f}V")
        
        # Performance Metrics
        pm = analysis['performance_metrics']
        print(f"\nPerformance Metrics:")
        print(f"  Target Voltage: {pm['target_voltage']:.2f}V")
        print(f"  Tolerance: ±{pm['tolerance']:.3f}V ({pm['tolerance']/pm['target_voltage']*100:.1f}%)")
        print(f"  Samples Within Tolerance: {pm['samples_within_tolerance']}")
        print(f"  Percentage Within Tolerance: {pm['percentage_within_tolerance']:.1f}%")
        
        # Stability Metrics
        sm = analysis['stability_metrics']
        print(f"\nStability Analysis:")
        print(f"  Recent Samples Analyzed: {sm['recent_samples']}")
        print(f"  Recent Mean Error: {sm['recent_mean_error']:.4f}V")
        print(f"  Recent Std Deviation: {sm['recent_std_dev']:.4f}V")
        print(f"  System Stable: {'Yes' if sm['is_stable'] else 'No'}")
        
        # Duty Cycle Analysis
        da = analysis['duty_cycle_analysis']
        print(f"\nDuty Cycle Analysis:")
        print(f"  Mean Duty Cycle: {da['mean']:.2f}%")
        print(f"  Standard Deviation: {da['std_dev']:.2f}%")
        print(f"  Range: {da['min']:.2f}% - {da['max']:.2f}%")
        
        print(f"\nTotal Samples: {analysis['sample_count']}")
    
    def get_devices(self):
        """Get list of connected devices"""
        try:
            response = requests.get(f"{self.base_url}/api/devices", timeout=5)
            if response.status_code == 200:
                devices = response.json()['devices']
                print(f"\nConnected Devices ({len(devices)}):")
                print("-" * 70)
                print(f"{'Device ID':<20} {'Samples':<10} {'First Seen':<20} {'Last Seen'}")
                print("-" * 70)
                for device in devices:
                    print(f"{device['device_id']:<20} {device['sample_count']:<10} "
                          f"{device['first_seen']:<20} {device['last_seen']}")
                return devices
            else:
                print(f"Failed to get devices: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error getting devices: {e}")
            return None
    
    def health_check(self):
        """Check API health"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(f"✓ API is healthy - {health['service']}")
                print(f"  Timestamp: {health['timestamp']}")
                return True
            else:
                print(f"✗ API health check failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ API health check error: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Buck Converter API Test Client')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='API base URL (default: http://localhost:5000)')
    parser.add_argument('--command', choices=['test', 'data', 'analysis', 'devices', 'health'], 
                       default='health', help='Command to execute')
    parser.add_argument('--count', type=int, default=10, 
                       help='Number of test data points to send')
    parser.add_argument('--device-id', help='Filter by device ID')
    parser.add_argument('--limit', type=int, default=10, 
                       help='Limit number of data points to retrieve')
    
    args = parser.parse_args()
    
    client = BuckConverterAPIClient(args.url)
    
    if args.command == 'health':
        client.health_check()
    elif args.command == 'test':
        client.send_test_data(count=args.count)
    elif args.command == 'data':
        data = client.get_telemetry_data(limit=args.limit, device_id=args.device_id)
        if data:
            print(f"\nLatest {len(data)} data points:")
            for i, point in enumerate(data[:5]):  # Show first 5
                print(f"  {i+1}. Target: {point['target_voltage']:.3f}V, "
                      f"Actual: {point['actual_voltage']:.3f}V, "
                      f"Error: {point['error']:.3f}V")
    elif args.command == 'analysis':
        client.get_analysis(device_id=args.device_id)
    elif args.command == 'devices':
        client.get_devices()

if __name__ == '__main__':
    main()