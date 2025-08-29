# TL431 Resistor Calculator

This tool calculates possible resistor divider values R1, R2, and a series resistor Rs for a TL431 adjustable shunt regulator.
It searches across standard resistor values (E-series) and reports practical solutions that meet current constraints.

## 🔧 Command-line usage

```
python tl431_calc.py --vin 5.0 --vout 3.65
```

Options

--vin
Input supply voltage (V).
Example: --vin 5.0

--vout
Desired output/reference voltage (V).
Example: --vout 3.65

--series
Resistor series to use. Supported: E12, E24, E48 (E96/192 are too large to search).
Default: E12
Example: --series E24

--ik-min
Minimum TL431 cathode current (mA). Default = 1.0

--ik-max
Maximum TL431 cathode current (mA). Default = 20.0

--idiv-max
Maximum divider current (mA). Default = 1.0
Example: --idiv-max 0.5

--results
Maximum number of solutions to print. Default = 20

## 📊 Example Output

```
Target Vout: 3.650 V
Vin = 5.000 V, Series = E24
Ik range = 1.0–20.0 mA, Idiv < 1.0 mA
-----------------------------------------------------------
R1 Ω | R2 Ω | Rs Ω | Vout V | VOUT Err V/%       | Idiv mA | Irs mA | Ik mA
-----------------------------------------------------------
2200 | 4700 | 100  | 3.663  | 0.013000 V / 0.356 % | 0.531  | 13.371 | 12.840
2200 | 4700 | 120  | 3.663  | 0.013000 V / 0.356 % | 0.531  | 11.143 | 10.612
```

## 📐 Notes

Ik is the cathode current of the TL431. Valid operation requires it to be within the min/max bounds (default 1–20 mA).

Idiv is the divider current through R1+R2. A typical target is ≤ 1 mA to minimize wasted current.

Irs is the current through the series resistor Rs, which also supplies the TL431.


