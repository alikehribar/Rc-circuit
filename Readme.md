# Measuring the Time Constant of an RC Circuit

Lab sheet — soldered two-channel Pico board

---

## Objective

Measure the exponential step response of an RC circuit and find its time constant `τ = RC` two independent ways:

1. **Simulation** — your reference curve, and the place to debug the analysis method on noise-free data
2. **Oscilloscope** — analogue confirmation

If both agree, the job is done. If they don't, the learning is in finding out where the difference comes from.

The skill at the centre of this: instead of eyeballing an exponential and saying "τ is about there", take the logarithm, straighten it out, and get τ from the slope.

---

## The board

```
                     10 kΩ            X node
   GP2  (pin 4)  ---[========]-----------+------------  scope CH1
                                         |
                                         +
                                         |
                                        === 4.7 nF
                                         |
                                        GND

```

Both channels are nominally identical: 10 kΩ and 4.7 nF. GP2 and GP3 generate the square wave themselves, so no function generator is needed; amplitude 3.3 V.

### Expected values

| Quantity | Value |
|----------|-------|
| τ = RC | 47.00 µs |
| Cutoff frequency f_c = 1/(2πτ) | 3.39 kHz |
| 5τ (full settling) | 235 µs |
| 63.2 % level | 2.09 V |

With 10 kΩ the working frequency of 2 kHz sits just under the 2.13 kHz settling
limit: the half period is 5.3τ, so the capacitor reaches 99.5 % of the target
before the next edge. The margin is thin: raise the frequency
at all and the curve stops settling.

---

## Theory

The capacitor current is `i = C·dv/dt`, so the circuit equation is

```
V_in = R·C·(dv_C/dt) + v_C
```

Charging (input steps to V):

```
v_C(t) = V·(1 − e^(−t/τ))        τ = RC
```

Discharging (input drops to 0):

```
v_C(t) = V·e^(−t/τ)
```

General form for any half period, carrying the initial condition `v₀` across:

```
v(t) = V_target + (v₀ − V_target)·e^(−t_local/τ)
```

### What τ means

| Elapsed time | Fraction reached |
|--------------|------------------|
| 1τ | 63.2 % |
| 2τ | 86.5 % |
| 3τ | 95.0 % |
| 5τ | 99.3 % |

63.2 % is `1 − 1/e`. It doesn't depend on R or C — that is the definition of τ.

### Logarithmic linearisation — the main method

Take the logarithm of the discharge equation:

```
ln(v/V₀) = −t/τ
```

Plot `ln(v/V₀)` against `t` and you get a straight line of slope `−1/τ`, so `τ = −1/slope`. This beats reading a single point because it uses all the data, and it is insensitive to getting `V₀` wrong (a constant error shifts every point equally and leaves the slope alone). It also tells you whether the data really is exponential: if the points don't fall on the line, something is wrong with the model or the circuit.

**Two-point method (quick check):**

```
τ = (t₂ − t₁) / ln(v₁/v₂)
```

**Rise time (free check):** the 10 % → 90 % transition takes `t_r = 2.20·τ`, and the scope measures it automatically.

---

## Stage 1 — Simulation

### Setting it up

1. **Time axis:** step 0.05 µs (about τ/940), covering at least two full periods. A coarser step kinks the curve and spoils the 63.2 % reading.

2. **Input:** a 2 kHz square wave between 0 and 3.3 V. Period 500 µs, so `v_in` is high when `t mod 500 µs` is above 250 µs. *Check your duty cycle before trusting anything downstream* — an off-by-a-factor-of-two here silently gives you 75 % instead of 50 %.

3. **Output:** step through the array carrying the initial condition. With `a = exp(−ts/τ)`:

   ```
   vout[i] = target + (vout[i−1] − target)·a
   ```

   This form inherits `v₀` from the previous sample automatically, so half-period boundaries need no special handling.

4. **Plot:** input and output on the same axes, plus a dashed line at 2.09 V.

### Checks

- At `t = τ` the output is 2.09 V
- At `t = 5τ` it is around 3.28 V
- The 10 % → 90 % transition takes 103.4 µs

If these fail, look first at the time step and at whether the initial condition is being carried across correctly.

### A dry run of the analysis

Take the discharge region of the simulated data, plot `ln(v/V₀)`, and recover τ from the slope. You started from a known τ, so you know the answer — this validates your analysis code on clean data before you point it at real measurements. You should get 47.00 µs to within rounding, and a fit intercept of essentially zero.

Also plot the **residuals** `res = y − (m·t + b)` and note their spread. On simulated data they are numerical noise. On real data they are your fit-quality metric, and any systematic curve in them means something physical is wrong.

**Do not let the window depend on τ.** Choosing the fit window as `3τ/ts` works only because you already know τ; with real data you won't. Select the window from the data instead — start at the falling edge and keep the points above 5 % of `V₀`.

### Change τ and watch

Repeat for τ = 22, 47 and 100 µs on one plot. The shape is identical; only the time axis stretches.

### What to record

- Input and output on the same axes
- τ from the 63.2 % crossing
- The `ln(v/V₀)` plot and τ from its slope, plus the residual spread
- The three-τ comparison plot

---

## Stage 2 — Oscilloscope

### Connections and settings

CH1 to the X node, CH2 to the Y node, ground clips on pin 38 or AGND (pin 33). The Pico still generates the square wave, GP2 and GP3 together at 2 kHz.

- Probe: 10×
- Timebase: 100 µs/div for the whole period, 20 µs/div to zoom one edge
- Vertical: 500 mV/div, DC coupling
- Trigger: CH1, rising edge

**Compensate the probe before you measure anything.** Clip the tip to the scope's calibration output and turn the trimmer until the square corners are flat. A badly compensated 10× probe distorts the first few µs of the edge. At τ = 47 µs that is a small fraction of the whole curve, but it still biases the 63.2 % crossing, which is the earliest and therefore most affected part of the trace.

### Measurements

For each channel:

1. Capture the rising edge.
2. Read the **actual settled top** off the screen first, then put a cursor at 63.2 % of that measured value and read the time to reach it. That is τ directly. Do not assume 2.09 V — taking 63.2 % of a top that is 2 % too high hands you a systematically wrong τ.
3. Read `Rise Time` from the automatic measurements and compute `τ = t_r / 2.20`.
4. Take 5–6 points off the discharge, plot `ln(v/V₀)`, get τ from the slope.
5. Cross-check with the two-point method.


---

## Results

| Measurement | X channel τ | Y channel τ | Deviation % |
|-------------|-------------|-------------|-------------|
| Theory (nominal 10 kΩ × 4.7 nF) | 47.00 µs | 47.00 µs | — |
| Theory (measured 9.78 kΩ × 4.9 nF) | 47.92 µs | not measured | +2.0 % |
| Simulation (log slope) | 47.00 µs | — | ~0 % |
| Scope — 63.2 % (cursor) | 41.80 µs | not measured | −11.1 % |
| Scope — rise time | not measured | not measured | |
| Scope — log slope (captured data) | 49.96 µs | not measured | +6.3 % |
| Scope — two-point | not measured | not measured | |

Deviation = `|τ_measured − τ_theory| / τ_theory × 100`

**What to expect:** resistor tolerance 1–5 %, capacitor tolerance 5–10 %, so around 10 % deviation is normal. If you see more, check in this order: probe compensation, stray capacitance on the board.

Watch the **sign** of your deviations, not just the size. Component tolerance scatters both ways; a systematic error pushes every measurement the same way.

Measure the resistors with the multimeter and recompute the theoretical τ from the real numbers. If you have no LCR meter, invert the problem: `C = τ_measured / R_measured` gives you the capacitor's actual value — and if that comes out far from 4.7 nF, the part is not what the silkscreen says.

The difference between the two channels is not measurement error but component tolerance itself. Comment on it separately.

---

## What the report needs

Objective, the equations used, the board schematic, simulation plots, oscilloscope captures, the completed results table, the `ln(v/V₀)` plots with residuals, and the raw data file. Axis labels and units on every plot.

In the discussion, compare the two stages: which came closest to theory, which deviated most, and why.

---

## Quick reference

```
τ = RC = 10 kΩ × 4.7 nF = 47.00 µs
Charging:    v(t) = V(1 − e^(−t/τ))
Discharging: v(t) = V₀·e^(−t/τ)
At 1τ:       63.2 %  →  2.09 V on a 3.3 V step
Linearised:  ln(v/V₀) = −t/τ,   τ = −1/slope
Two-point:   τ = (t₂ − t₁)/ln(v₁/v₂)
Rise time:   t_r = 2.20·τ = 103.4 µs
Cutoff:      f_c = 1/(2πτ) = 3.39 kHz
Design rule: 5τ ≤ P/2  →  f ≤ 2.13 kHz
```