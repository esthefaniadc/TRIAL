# Buck Converter Design Calculations

## Specifications
- Input Voltage (Vs): 3.3V
- Output Voltage (Vo): 2V  
- Switching Frequency (fs): 1kHz
- Duty Cycle (D): Vo/Vs = 2V/3.3V ≈ 0.606

## Component Calculations

### Inductor (L) Calculation
For continuous conduction mode (CCM), the inductor value is calculated to limit current ripple.

Assuming 20% current ripple (ΔIL = 0.2 * Io):
- Estimated load current: Io = 100mA (typical for low-power applications)
- Current ripple: ΔIL = 0.02A

L = (Vs - Vo) * D / (ΔIL * fs)
L = (3.3 - 2) * 0.606 / (0.02 * 1000)
L = 1.3 * 0.606 / 20
L ≈ 39.4 μH

**Selected: L = 47 μH** (standard value)

### Output Capacitor (C) Calculation
For 1% output voltage ripple:
- Voltage ripple: ΔVo = 0.01 * 2V = 0.02V

C = ΔIL / (8 * fs * ΔVo)
C = 0.02 / (8 * 1000 * 0.02)
C ≈ 1.25 μF

**Selected: C = 10 μF** (provides good margin)

### Load Resistor (R) Calculation
For 100mA load current:
R = Vo / Io = 2V / 0.1A = 20Ω

**Selected: R = 20Ω**

## Summary of Component Values
- **Inductor (L)**: 47 μH
- **Capacitor (C)**: 10 μF
- **Load Resistor (R)**: 20Ω
- **Switching Frequency**: 1 kHz
- **Duty Cycle**: ~60.6%