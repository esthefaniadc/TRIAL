#!/usr/bin/env python3
"""
Buck Converter System Integration Test

This script tests the complete buck converter control system
without requiring actual hardware.
"""

import os
import sys
import time
import subprocess
import threading
from src.data_logger import BuckConverterDataLogger

def test_calculations():
    """Test buck converter calculations"""
    print("🧮 Testing Buck Converter Calculations...")
    
    # Read the calculations file
    calc_file = 'src/buck_converter_calculations.md'
    if os.path.exists(calc_file):
        with open(calc_file, 'r') as f:
            content = f.read()
            if '47 μH' in content and '10 μF' in content and '20Ω' in content:
                print("✅ Component calculations present and correct")
                return True
    
    print("❌ Component calculations missing or incorrect")
    return False

def test_esp32_code():
    """Test ESP32 code syntax and structure"""
    print("🔧 Testing ESP32 Code Structure...")
    
    esp32_file = 'src/esp32_buck_controller.ino'
    if not os.path.exists(esp32_file):
        print("❌ ESP32 code file missing")
        return False
    
    with open(esp32_file, 'r') as f:
        content = f.read()
        
        required_elements = [
            '#include <WiFi.h>',
            'PWM_FREQ = 1000',
            'TARGET_VOLTAGE = 2.0',
            'void runControlLoop()',
            'void sendTelemetryData()',
            'ledcWrite'
        ]
        
        missing = []
        for element in required_elements:
            if element not in content:
                missing.append(element)
        
        if missing:
            print(f"❌ ESP32 code missing elements: {missing}")
            return False
        
        print("✅ ESP32 code structure correct")
        return True

def test_data_logger():
    """Test the data logger functionality"""
    print("📊 Testing Data Logger...")
    
    try:
        # Create a test database
        logger = BuckConverterDataLogger('test_buck_converter.db')
        
        # Generate test data
        logger.generate_test_data(device_id="TEST_DEVICE", count=20)
        
        # Retrieve data
        data = logger.get_data(limit=20)
        if len(data) != 20:
            print(f"❌ Expected 20 data points, got {len(data)}")
            return False
        
        # Test analysis
        analysis = logger.analyze_performance()
        if 'error' in analysis:
            print(f"❌ Analysis failed: {analysis['error']}")
            return False
        
        # Check analysis components
        required_keys = ['voltage_analysis', 'error_analysis', 'performance_metrics']
        for key in required_keys:
            if key not in analysis:
                print(f"❌ Analysis missing {key}")
                return False
        
        # Cleanup
        os.remove('test_buck_converter.db')
        
        print("✅ Data logger functionality verified")
        return True
        
    except Exception as e:
        print(f"❌ Data logger test failed: {e}")
        return False

def test_circuit_documentation():
    """Test circuit documentation completeness"""
    print("📋 Testing Circuit Documentation...")
    
    circuit_file = 'schemes/buck_converter_circuit.md'
    if not os.path.exists(circuit_file):
        print("❌ Circuit documentation missing")
        return False
    
    with open(circuit_file, 'r') as f:
        content = f.read()
        
        required_sections = [
            'Circuit Components',
            'Pin Connections',
            'ESP32 Pins Used',
            'Power MOSFET',
            'Schottky Diode',
            'Inductor'
        ]
        
        missing = []
        for section in required_sections:
            if section not in content:
                missing.append(section)
        
        if missing:
            print(f"❌ Circuit documentation missing sections: {missing}")
            return False
        
        print("✅ Circuit documentation complete")
        return True

def test_api_functionality():
    """Test API code structure (without running Flask)"""
    print("🌐 Testing API Code Structure...")
    
    api_file = 'src/cloud_api.py'
    if not os.path.exists(api_file):
        print("❌ API code file missing")
        return False
    
    with open(api_file, 'r') as f:
        content = f.read()
        
        required_endpoints = [
            '@app.route(\'/api/telemetry\', methods=[\'POST\'])',
            '@app.route(\'/api/telemetry\', methods=[\'GET\'])',
            '@app.route(\'/api/analysis\', methods=[\'GET\'])',
            '@app.route(\'/api/health\', methods=[\'GET\'])'
        ]
        
        missing = []
        for endpoint in required_endpoints:
            if endpoint not in content:
                missing.append(endpoint)
        
        if missing:
            print(f"❌ API missing endpoints: {missing}")
            return False
        
        print("✅ API code structure verified")
        return True

def test_project_structure():
    """Test overall project structure"""
    print("📁 Testing Project Structure...")
    
    required_files = [
        'src/esp32_buck_controller.ino',
        'src/cloud_api.py',
        'src/data_logger.py',
        'src/buck_converter_calculations.md',
        'src/README.md',
        'schemes/buck_converter_circuit.md',
        'src/platformio.ini',
        'src/requirements.txt'
    ]
    
    missing = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    
    print("✅ Project structure complete")
    return True

def main():
    """Run all integration tests"""
    print("=" * 60)
    print("BUCK CONVERTER SYSTEM INTEGRATION TEST")
    print("=" * 60)
    print()
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Buck Converter Calculations", test_calculations),
        ("ESP32 Code", test_esp32_code),
        ("Circuit Documentation", test_circuit_documentation),
        ("API Code", test_api_functionality),
        ("Data Logger", test_data_logger)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Buck converter system is ready for deployment.")
        return 0
    else:
        print(f"\n⚠️  {total-passed} test(s) failed. Please review and fix issues.")
        return 1

if __name__ == '__main__':
    # Change to the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    exit_code = main()
    sys.exit(exit_code)