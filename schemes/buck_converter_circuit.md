# Buck Converter Circuit with ESP32 Control

## Circuit Description

This document describes the buck converter circuit controlled by an ESP32 microcontroller for closed-loop voltage regulation.

### Circuit Components

1. **ESP32 Development Board** - Main controller
2. **Power MOSFET** (e.g., IRF520) - Switching element
3. **Schottky Diode** (e.g., 1N5819) - Freewheeling diode
4. **Inductor** - 47μH (calculated value)
5. **Output Capacitor** - 10μF electrolytic + 100nF ceramic
6. **Load Resistor** - 20Ω (for testing)
7. **Voltage Divider** - For feedback (if Vo > 3.3V)
8. **Gate Driver** (optional) - For better MOSFET switching

### Pin Connections

#### ESP32 Pins Used:
- **GPIO 25** - PWM output to MOSFET gate (via gate driver)
- **GPIO 34** - ADC input for voltage feedback
- **GPIO 2** - Status LED
- **VCC/GND** - Power supply connections

#### Circuit Connections:

```
Input (3.3V) ----+----[MOSFET Drain]
                 |
                 +----[Inductor 47μH]----+----[Output Capacitor 10μF]----+---- Vo (2V)
                                         |                                |
                      [Schottky Diode]---+                                |---- [Load 20Ω]
                      (Cathode to Node)  |                                |
                                         |                                |
                                       GND -------------------------------+

ESP32 GPIO25 ----[Gate Driver]---- MOSFET Gate
ESP32 GPIO34 ----[Voltage Divider]---- Output Node (for feedback)
```

### Detailed Component Specifications

#### Power MOSFET (Q1)
- **Type**: N-Channel Power MOSFET
- **Recommended**: IRF520, IRLZ44N, or similar
- **Ratings**: Vds > 10V, Id > 500mA, Rds(on) < 100mΩ
- **Package**: TO-220 or D2PAK

#### Schottky Diode (D1)
- **Type**: Schottky rectifier diode
- **Recommended**: 1N5819, 1N5817, or similar
- **Ratings**: Vr > 10V, If > 500mA, Vf < 0.5V

#### Inductor (L1)
- **Value**: 47μH ±20%
- **Current Rating**: > 200mA
- **Type**: Ferrite core or powdered iron
- **Recommended**: Murata LQH32CN470K23L or similar

#### Output Capacitor (C1)
- **Primary**: 10μF electrolytic, 16V rating
- **Secondary**: 100nF ceramic (X7R), 16V rating
- **Purpose**: Reduce output voltage ripple

#### Gate Driver (Optional but Recommended)
- **Type**: MOSFET gate driver IC
- **Recommended**: TC4427, MCP1407, or similar
- **Purpose**: Improve switching speed and reduce losses

### Voltage Feedback Circuit

Since the ESP32 ADC can handle 0-3.3V and our output is 2V, no voltage divider is needed for this application.

#### Direct Connection:
```
Output Node (2V) ----[100Ω series resistor]---- ESP32 GPIO34
                |
                +----[1nF capacitor]---- GND
```

The series resistor and capacitor form a simple anti-aliasing filter.

### Safety Considerations

1. **Input Protection**: Add a fuse or current limiting resistor on the input
2. **ESD Protection**: Use ESD protection diodes on GPIO pins
3. **Thermal Management**: Ensure adequate heat sinking for the MOSFET
4. **Short Circuit Protection**: Implement current sensing for overcurrent protection

### PCB Layout Guidelines

1. **Keep switching loops small** - Minimize the area between MOSFET, diode, and input capacitor
2. **Ground plane** - Use a solid ground plane for low noise
3. **Separate analog and digital grounds** - Connect at a single point
4. **Component placement** - Keep inductor away from sensitive analog circuits
5. **Thermal vias** - Use thermal vias under the MOSFET for heat dissipation

### Testing and Calibration

1. **Initial Setup**: Start with 50% duty cycle
2. **Open Loop Test**: Verify PWM generation and basic circuit operation
3. **Closed Loop Test**: Enable feedback and monitor regulation
4. **Load Step Test**: Apply load changes and observe transient response
5. **Efficiency Measurement**: Measure input and output power

### Troubleshooting

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| No output voltage | MOSFET not switching | Check PWM signal, gate driver |
| Output too low | High duty cycle needed | Check component values, connections |
| Oscillation | Poor compensation | Adjust PID parameters |
| High ripple | Inadequate filtering | Increase output capacitance |
| Overheating | High losses | Check MOSFET selection, heat sink |

### Performance Specifications

- **Input Voltage**: 3.3V ±5%
- **Output Voltage**: 2.0V ±1%
- **Output Current**: Up to 100mA
- **Switching Frequency**: 1kHz
- **Efficiency**: Expected >85%
- **Ripple**: <1% of output voltage
- **Settling Time**: <100ms for 10% load step