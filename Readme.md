# Measuring the Time Constant of an RC Circuit

Lab sheet — using the soldered two-channel Pico board

---

## Objective

Measure the exponential step response of an RC circuit and find its time constant `τ = RC` three independent ways:

1. **Simulation** — you learn what to expect, and this becomes your reference curve
2. **The board itself** — digital measurement through the Pico's ADC
3. **Oscilloscope** — analogue, real-time confirmation

If all three values of τ agree, the job is done. If they don't, the real learning is in working out where the difference comes from.

The skill at the centre of this: instead of looking at an exponential curve and saying "τ is about there", take the logarithm, straighten it out, and get τ from the slope.

---

## Your board

```
                    2.2 kΩ            X node
   GP2  (pin 4)  ---[========]-----------+------------  scope CH1
                                         |
                                         +------------  GP26 (pin 31) ADC0
                                         |
                                        === 4.7 nF
                                         |
                                        GND

                    2.2 kΩ            Y node
   GP3  (pin 5)  ---[========]-----------+------------  scope CH2
                                         |
                                         +------------  GP27 (pin 32) ADC1
                                         |
                                        === 4.7 nF
                                         |
                                        GND

   GND (pin 38) / AGND (pin 33) --------------------  scope ground clips
```

Both channels are identical: 2.2 kΩ and 4.7 nF. GP2 and GP3 generate the square wave themselves, so no separate function generator is needed; the nominal amplitude is 3.3 V.

**The GPIO is not an ideal source.** Its output impedance is around 50 Ω, and that 50 Ω sits in series with your 2.2 kΩ, so the capacitor actually sees 2250 Ω. Two consequences, both small but both larger than you can ignore at this precision:

- The real time constant is `(2200 + 50)·4.7 nF = 10.58 µs`, **2.3 % above** the nominal 10.34 µs.
- The step the capacitor settles to is divided down: `3.3 V · 2200/2250 = 3.23 V`, not 3.3 V. So the 63.2 % crossing sits at **2.04 V**, not 2.09 V.

2.3 % is the same order as the resistor tolerance, so this is not a rounding detail — it is a systematic offset that pushes every measured τ slightly high. Use the nominal figures below for the pre-lab, but expect your measurements to cluster above them, and say so in your discussion rather than blaming it on noise.

### Expected values

| Quantity | Value |
|----------|-------|
| τ = RC | 10.34 µs |
| Cutoff frequency f_c | 15.4 kHz |
| Rise time t_r | 22.7 µs |
| 5τ (full settling) | 51.7 µs |
| Max usable square wave | ≈ 9.7 kHz |
| Working frequency (chosen) | 2 kHz → half period ≈ 24τ |
| 63.2 % level (at a 3.3 V step) | 2.09 V |
| **τ including the 50 Ω GPIO impedance** | **10.58 µs** (+2.3 %) |
| **Settled step with 50 Ω included** | **3.23 V** |
| **63.2 % level of that real step** | **2.04 V** |

---

## Theory

The capacitor current is `i = C·dv/dt`, so the circuit equation is

```
V_in = R·C·(dv_C/dt) + v_C
```

When the input steps to 3.3 V (charging):

```
v_C(t) = V·(1 − e^(−t/τ))        τ = RC
```

When it drops to zero (discharging):

```
v_C(t) = V·e^(−t/τ)
```

### What τ means

| Elapsed time | Fraction reached |
|--------------|------------------|
| 1τ | 63.2 % |
| 2τ | 86.5 % |
| 3τ | 95.0 % |
| 5τ | 99.3 % |

The 63.2 % figure is `1 − 1/e`. It doesn't change with R or C; that is the definition of τ.

### Logarithmic linearisation

Take the logarithm of the discharge equation:

```
ln(v/V) = −t/τ
```

Plot `ln(v/V)` against `t` and you get a straight line of slope `−1/τ`. This is far more reliable than looking at a single point, because it uses all the data. It also tells you whether the data really is exponential: if the points don't fall on the line, something is wrong with either the model or the circuit.

**Two-point method (quick check):**

```
τ = (t₂ − t₁) / ln(v₁/v₂)
```

The amplitude doesn't appear in this formula, so misreading `V` won't spoil the result.

### The frequency side

The transfer function is `H(s) = 1/(1 + sRC)`, a low-pass filter. The cutoff frequency is `f_c = 1/(2πτ)`. Being slow in the time domain and cutting high frequencies are the same phenomenon; there is one parameter, τ.

**Rise time:** the 10 % → 90 % transition takes `t_r = 2.20·τ`. The scope measures this automatically, so it's a free check.

---

## Pre-lab calculations

1. Work out the τ, f_c and t_r values in the table above yourself and confirm they hold.
2. Show that `v_C(τ)/V` comes out to 0.632.
3. Derive the maximum square wave frequency from the `5τ ≤ P/2` rule.
4. Derive `t_r = 2.20·τ`.
5. If the components are 5 % parts, what range can τ fall in? What's the largest difference you'd expect between the two channels?
6. Redo the τ calculation with the GPIO's 50 Ω included and confirm the 10.58 µs and 2.04 V figures. Is this shift larger or smaller than the spread you found in question 5?

---

## Stage 1 — Simulation

### Setting it up

1. **Time axis:** from 0 to 1 ms with a step of 0.05 µs. That's about one two-hundredth of τ; a coarser step makes the curve look kinked and you won't read the 63.2 % moment accurately. Cover at least two full periods.

2. **Build the input:** a 2 kHz square wave between 0 and 3.3 V. The period is 500 µs, so the input is 3.3 V when `t mod 500 µs` is below 250 µs, and 0 otherwise.

3. **Solve the output half period by half period.** Each half period has its own initial condition: the voltage `v₀` left on the capacitor as that half period begins.
   - While the input is high: `v(t) = V + (v₀ − V)·e^(−t_local/τ)`
   - While the input is low: `v(t) = v₀·e^(−t_local/τ)`

   Here `t_local` is the time elapsed since the start of that half period. For the first half period `v₀ = 0`; after that it's the final value of the previous half period.

4. **Plot:** input and output on the same axes. Add a horizontal dashed line at 2.09 V so you can see the 63.2 % moment.

### Checks

If your code is right, all three of these should hold:

- At `t = τ` the output is 2.09 V
- At `t = 5τ` the output is around 3.28 V
- The 10 % → 90 % transition takes 22.7 µs

If they don't, look first at the step size and at whether you're carrying the initial condition across correctly.

These checks use the **ideal** 3.3 V source and τ = 10.34 µs, which is what makes the simulation a clean reference. That is why the simulation will read 2.09 V where the scope reads 2.04 V — the difference is the 50 Ω, not a mistake in your code. If you want the simulation to predict the hardware rather than the ideal circuit, rerun it with `V = 3.23 V` and `τ = 10.58 µs` and keep both curves.

### Change τ and watch

Repeat the same calculation for τ = 5 µs, 10.34 µs and 20 µs. Notice that the shape of the curves stays the same and only stretches along the time axis. This foreshadows the behaviour you'll see in Stage 3 when you raise the frequency.

### A dry run of the analysis

Take 5–6 points from the discharge region of the simulated data, plot `ln(v/V)`, and recover τ from the slope. You started from a known τ, so you know what the answer should be — this tests your analysis method on clean, noise-free data. You'll apply the same procedure to real data in Stages 2 and 3.

### What to record

- The plot with input and output on the same axes
- The moment the curve crosses 2.09 V, i.e. `τ_sim`
- The `ln(v/V)` plot and the τ you get from its slope
- A comparison plot for the three different values of τ

---

## Stage 2 — Measurement with the Board

### First, a problem: is the ADC fast enough?

τ = 10.34 µs. To sample the curve properly you need at least 5–10 points per time constant, so the sampling interval has to be 1–2 µs. A simple `adc.read_u16()` loop in MicroPython manages only 20–40 kSps (25–50 µs per sample), which is two to five times τ itself — a single sample interval swallows most of the 51.7 µs transient. In other words, **you cannot measure this curve with a plain loop.** That's not a setback but one of the things the experiment teaches: your instrument's bandwidth has to exceed the event you're measuring.

You have two ways out.

### Method A — DMA burst capture (500 kSps)

The Pico's ADC runs up to 500 kSps in free-running mode, i.e. 2 µs per sample. (This holds for both the RP2040 and the RP2350, so it does not matter which Pico you have.) That gives 5 points per τ and 26 points across 5τ. It's marginal for a log fit, but sufficient.

How it works:
1. Hold GP2 low and wait at least 5τ (≈ 52 µs) so the capacitor discharges completely.
2. Put the ADC in free-running mode and point DMA at a 1000-sample buffer.
3. Raise GP2 and start the capture at the same moment.
4. When the buffer is full, dump the data over the serial port as CSV.
5. Repeat for GP3 / GP27.

The Pico SDK's stock `adc_dma` example does almost exactly this; you only need to set the clock divider for 500 kSps.

### Method B — Equivalent-time sampling

Because the signal is repetitive you can cheat: shift the sampling instant slightly on each repetition and rebuild the curve piece by piece. You get 0.5 µs resolution out of a slow ADC. Sampling oscilloscopes do exactly this.

How it works:
1. Start with delay `d = 0`.
2. GP2 low, wait 5τ (capacitor empty).
3. Raise GP2, wait exactly `d`, take a **single** ADC reading.
4. Drop GP2, wait 5τ.
5. Repeat this loop 100 times at the same `d` and average the readings. Noise drops by roughly a factor of ten.
6. Increase `d` by 0.5 µs and repeat steps 2–5. Continue up to and including `d = 60 µs`.
7. You end up with a 121-point charging curve at 0.5 µs resolution. (60 µs / 0.5 µs = 120 steps, plus the reading at `d = 0` that needed no step. 60 µs is 5.8τ, so the curve has fully settled by the last point.)

The critical part of this method is that the delay must be **stable**. MicroPython's timing jitter is on the order of a few µs, which is comparable to τ itself, so you need to generate the delay with a hardware timer or PIO.

### One more trap: the top of the ADC's range

The ADC measures against a 3.3 V reference, and your signal settles at about 3.23 V — within 2 % of full scale. The Pico's ADC is at its least linear in exactly that top stretch, so the tail of your charging curve is the least trustworthy part of the data.

This matters because the tail is where the log fit is most sensitive: `ln(v/V)` blows up as `v` approaches `V`, so a couple of millivolts of ADC error there moves the fitted slope far more than the same error near the middle of the curve. **Fit the charging data over roughly 0 to 2τ, or fit the discharge instead** — discharge heads toward 0 V, away from the bad region, which is why the discharge is the better dataset for the log method.

Whichever method you pick, the code can be written separately — this sheet contains no code.

### What to record

- The raw data file (CSV)
- Plots of the charging and discharging curves
- The `ln(v/V)` plot and the τ calculated from its slope
- The quality of the fit (how well the points fall on the line)
- Separate values of τ for the two channels (X and Y)

---

## Stage 3 — Oscilloscope

### Connections and settings

Connect CH1 to the X node and CH2 to the Y node. Attach the ground clips to pin 38 (or AGND, pin 33). The Pico still generates the square wave: toggle GP2 and GP3 together at 2 kHz.

- Probe: 10× position
- Timebase: 10 µs/div (drop to 2 µs/div to zoom the edge)
- Vertical: 500 mV/div, DC coupling
- Trigger: CH1, rising edge

**Compensate the probe before you start measuring.** Clip the tip to the scope's calibration output and turn the trimmer on the probe body until the square wave corners look flat. When you're working at τ = 10 µs, skipping this step means the "slow rise" you measure may be the probe's own error. This is the biggest source of error in the whole experiment.

### Measurements

For each channel separately:

1. Bring the rising edge onto the screen and capture it.
2. Read the **actual settled top of the waveform** off the screen first — expect about 3.23 V, not 3.3 V — then put a cursor at 63.2 % of that measured value (around 2.04 V) and measure the time to reach it. That's τ directly. Don't assume the 2.09 V figure: taking 63.2 % of a value that is 2 % too high hands you a τ that is systematically wrong, and the whole point of this method is that it needs the real final value.
3. Read `Rise Time` from the automatic measurement menu and compute `τ = t_r / 2.20`.
4. Read 5–6 points off the discharge curve (t and v pairs). Plot them as `ln(v/V)` and get τ from the slope.
5. Do one more check with the two-point method.

### What happens as you raise the frequency

Step the Pico's square wave up: 2 kHz → 10 kHz → 30 kHz → 100 kHz. At each step, sketch what the output waveform becomes once the half period falls below 3τ. At the highest frequency the output is nearly a triangle wave, meaning the circuit is now acting as an integrator. Explain why in your report.

### Optional: viewing both channels in XY mode

Drive GP2 and GP3 **in phase** (toggle them on the same instruction) and switch the scope to **XY mode**, which plots CH1 on the horizontal axis against CH2 on the vertical instead of against time.

If the two channels were identical, every instant would have `v_X = v_Y` and the trace would collapse onto a straight 45° line. Any mismatch in τ means one channel lags the other during the transient, so the trace opens out into a thin loop. The width of that loop is your mismatch, read straight off the screen with no cursors and no fitting.

Do **not** drive them a quarter period out of phase for this test: that produces a large loop even with perfectly matched channels, so the mismatch you are looking for is buried in a much bigger effect.

---

## Results

| Measurement | X channel τ | Y channel τ | Deviation % |
|-------------|-------------|-------------|-------------|
| Theory (nominal 2.2 kΩ × 4.7 nF) | 10.34 µs | 10.34 µs | — |
| Theory (2250 Ω, GPIO impedance included) | 10.58 µs | 10.58 µs | — |
| Theory (R measured with multimeter, + 50 Ω) | | | |
| Simulation | | | |
| Board — log slope | | | |
| Scope — 63.2 % | | | |
| Scope — rise time | | | |
| Scope — log slope | | | |
| Scope — two-point | | | |

Deviation = `|τ_measured − τ_theory| / τ_theory × 100`

**What to expect:** resistor tolerance is 1–5 %, capacitor tolerance 5–10 %. A deviation of around 10 % is therefore normal. If you see more, check these in order: probe compensation, the 50 Ω GPIO impedance (worth a fixed +2.3 % on its own, and it always pushes the same direction), stray capacitance on the board, the ADC's sampling load. Measure the resistors with the multimeter, add the 50 Ω, and recompute the theoretical value from the real numbers — you'll see the deviation shrink noticeably.

Watch the **sign** of your deviations, not just the size. Component tolerance scatters either way; the GPIO impedance only ever makes τ larger. If every one of your measurements lands above theory, that is the fingerprint of a systematic error, not random spread.

The difference between the two channels, on the other hand, is not measurement error but component tolerance itself. Comment on it separately.

---

## Questions

1. Why is τ independent of the square wave amplitude? Show it from the equations.
2. Why can't a plain sampling loop in MicroPython measure this curve? What minimum ratio should hold between the sampling interval and τ?
3. Why does equivalent-time sampling only work on **repetitive** signals? What would you do for a single-shot event?
4. If the points on the `ln(v/V)` plot curve away from the line toward the end, what could cause it?
5. If you took the output across the resistor instead of the capacitor, what would the transfer function be, and how would that circuit respond to the same square wave?
6. A scope probe typically loads the circuit with 10 MΩ and 15 pF. Is that negligible next to 4.7 nF? Does the situation change with a 1× probe (usually around 100 pF)? Calculate it.
7. At the moment of sampling, the ADC input connects its own hold capacitor (a few pF) to the circuit. Which way does that shift the voltage you measure?
8. When the half period is shorter than 3τ, the capacitor doesn't fully discharge and each cycle starts from a residual voltage instead of zero. Does the 63.2 % method still give the right τ? If not, which method does?
9. Suppose you find an 8 % difference between the two channels' time constants. How would you tell whether it comes from the resistors or the capacitors?
10. The 50 Ω GPIO impedance raises τ by 2.3 % but does **not** change the difference between the two channels. Explain why, and say what that implies about which of your results it can and cannot account for.
11. Both the log-slope method and the two-point method are immune to getting the amplitude `V` wrong, but the 63.2 % method is not. Show why from the equations, and say which method you would trust most on this board given the 3.23 V step.

---

## What the report needs

Objective, the equations you used, the board schematic, simulation plots, plots of the board data, oscilloscope captures, the completed results table, the `ln(v/V)` plots, and your answers to the questions. Attach the raw data file. Don't forget axis labels and units on the plots.

In the discussion, compare the results of the three stages: which came closest to theory, which deviated most, and why?

---

## Quick reference

```
τ = RC = 10.34 µs          nominal
τ = 10.58 µs               with the 50 Ω GPIO impedance (what you will measure)
Charging:    v(t) = V(1 − e^(−t/τ))
Discharging: v(t) = V·e^(−t/τ)
At 1τ:       63.2 %   →  2.09 V on a 3.3 V step, 2.04 V on the real 3.23 V step
Linearised:  ln(v/V) = −t/τ
Two-point:   τ = (t₂ − t₁)/ln(v₁/v₂)
Rise time:   t_r = 2.20·τ = 22.7 µs
Cutoff:      f_c = 1/(2πτ) = 15.4 kHz
Design rule: 5τ ≤ P/2  →  f ≤ 9.7 kHz
```
# Rc-circuit
