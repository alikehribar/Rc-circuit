# RC Zaman Sabiti Deneyi — Proje Bağlamı

## Bu proje ne

Üniversite laboratuvarı için RC devresinin zaman sabitini ölçme deneyi. Öğrenci hem deneyi yapacak hem de föyü yazdı, ayrıca konuyu başkasına anlatabilecek düzeyde öğrenmesi gerekiyor.

τ = RC üç bağımsız yoldan bulunacak:
1. Simülasyon (Python, analitik çözüm)
2. Raspberry Pi Pico 2 ile sayısal ölçüm
3. Osiloskop ile analog doğrulama

## Nasıl yardım edilmesini istiyorum

**Kod yazıp geçme, açıklayarak ilerle.** Öğrenci konuyu öğrenmek istiyor, hazır çözüm istemiyor. Kodu parça parça ver, her parçanın ne yaptığını ve neden öyle olduğunu anlat, beklenen çıktıyı söyle ki kendi kontrol edebilsin.

Matematik gerektiğinde LaTeX kullan, kod bloğu içinde formül yazma — okunmuyor.

Öğrenci Türkçe konuşuyor.

## Donanım

Lehimli kart, iki özdeş kanal. Breadboard yok, bileşenler değiştirilemez.

```
                    2.2 kΩ            X düğümü
   GP2  (pin 4)  ---[========]-----------+------------  osiloskop CH1
                                         |
                                         +------------  GP26 (pin 31) ADC0
                                         |
                                        === 4.7 nF
                                         |
                                        GND

                    2.2 kΩ            Y düğümü
   GP3  (pin 5)  ---[========]-----------+------------  osiloskop CH2
                                         |
                                         +------------  GP27 (pin 32) ADC1
                                         |
                                        === 4.7 nF
                                         |
                                        GND

   GND (pin 38) / AGND (pin 33) --------------------  osiloskop toprak klipsleri
```

Kare dalgayı GPIO üretiyor, sinyal jeneratörü yok. Genlik 3,3 V. GPIO çıkış direnci ~50 Ω, 2,2 kΩ yanında ihmal edilebilir.

## Sayılar

| Büyüklük | Değer |
|---|---|
| τ = RC | 10,34 µs |
| Kesim frekansı f_c | 15,4 kHz |
| Yükselme zamanı t_r = 2,20τ | 22,7 µs |
| 5τ (tam oturma) | 51,7 µs |
| Maks. kullanılabilir kare dalga | ≈ 9,7 kHz |
| Çalışma frekansı | 2 kHz (yarım periyot ≈ 24τ) |
| %63,2 seviyesi | 2,086 V |
| %10 / %90 seviyeleri | 0,33 V / 2,97 V |

## Teori

Devre denklemi:

$$\frac{dv}{dt} = \frac{V - v}{\tau}, \qquad \tau = RC$$

Şarj:

$$v(t) = V\left(1 - e^{-t/\tau}\right)$$

Deşarj:

$$v(t) = V_0\, e^{-t/\tau}$$

Genel hâl (her yarım periyot için, başlangıç koşulu devralınarak):

$$v(t) = V_{\text{hedef}} + (v_0 - V_{\text{hedef}})\,e^{-t_{\text{yerel}}/\tau}$$

Logaritmik doğrusallaştırma (asıl ölçüm yöntemi):

$$\ln\!\left(\frac{v}{V_0}\right) = -\frac{t}{\tau}$$

Eğim `m = −1/τ`, dolayısıyla `τ = −1/m`. Bu yöntem tüm veriyi kullandığı için gürültüye dayanıklı ve `V₀` hatasından etkilenmiyor (sabit hata bütün noktaları eşit kaydırır, eğim değişmez).

İki nokta yöntemi (kontrol amaçlı):

$$\tau = \frac{t_2 - t_1}{\ln(v_1/v_2)}$$

Transfer fonksiyonu ve kesim frekansı:

$$H(s) = \frac{1}{1+sRC}, \qquad f_c = \frac{1}{2\pi\tau}$$

## Nerede kalındı

**1. Aşama — Simülasyon, tamamlandı.** Dosya: `sim.py`

Çalışan zincir:
- Sabitler: `R=2200`, `C=4.7e-9`, `tau=R*C`, `V=3.3`, `F=5000`, `P=1/F`, `ts=0.05e-6`, `D=0.5`, `t=np.arange(0, 2*P, ts)` → 8001 nokta
- Giriş: `v_in = V * np.where(((t % P) < (1-D)*P), 0, 1)`. **Dikkat:** başta `(1-D)*P/2` yazılmıştı, bu duty'yi `(1+D)/2` yapıyordu (D=0,5 için %75). `/2` kaldırıldı.
- Çıkış: adım adım özyineleme, `a = np.exp(-ts/tau)` = 0,995176
  ```python
  for i in range(1, len(t)):
      target = v_in[i - 1]
      vout[i] = (target + (vout[i-1] - target) * a)
  ```
  Bu form başlangıç koşulunu kendiliğinden devrediyor, yarım periyot sınırı ayrıca ele alınmıyor.
- Kenar tespiti: `edges = np.where(np.diff(v_in) < -1)[0]`, `k = edges[0]` → **k = 4000** (3999 değil; `np.arange` yuvarlaması yüzünden `t[4000] % P` sıfıra dönmüyor). `V0 = vout[k]` = 3,29979 V
- Pencere: `n = int(round((3*tau)/ts))` = 620, `start = k+1`, `vwin = vout[start:(start+n)]`
- Analiz: `t_local = np.arange(n)*ts`, `y = np.log(vwin/V0)`, `m, b = np.polyfit(t_local, y, 1)`, `tau_measured = -1/m`

Doğrulanan sayılar (hepsi çalıştırılarak ölçüldü):

| Kontrol | Sonuç |
|---|---|
| 1τ sonra vout | 2,081 V (teorik 2,086) |
| 3τ sonra vout | 3,135 V |
| 5τ sonra vout | 3,278 V |
| `tau_measured` | **10,3400 µs — hata %0** |
| `polyfit` kesişimi `b` | 0,00000 (V₀ ve kenar doğru) |

1τ'daki 5 mV fark hata değil: `target = v_in[i-1]` kullanıldığı için yükseliş bir örnek (0,05 µs) geç başlıyor.

Not: `sim.py`'da analiz satırları (31-35) şu an yorumda, grafik bloğu aktif.

Yapılmayanlar (isteğe bağlı, τ sonucunu değiştirmez):
- `ln(v/V₀)` doğrusunun grafiği
- Artık (residual) kontrolü — `res = y - (m*t_local + b)`, `np.std(res)`. Gerçek veride prob kompanzasyonu bozuksa artıklar kavis yapar; bunu yakalamanın yolu bu.
- τ = 5 / 10,34 / 20 µs karşılaştırmalı grafiği

Grafikler için sadece numpy ve matplotlib, başka kütüphane yok.

### Pencere seçiminde bilinen sızıntı

`n = 3*tau/ts` satırı τ'yu **biliyor**. Gerçek veride bilmeyeceksin. Veriden karar veren karşılığı (denendi, aynı 620 noktayı ve aynı 10,34 µs'yi veriyor):

```python
seg = vout[start:(start + 2000)]
mask = (seg > (0.05 * V0))
v_win = seg[mask]
t_local = (np.arange(len(v_win)) * ts)
```

## 2. Aşama — Pico 2 / CircuitPython (kod yazıldı, test edilmedi)

**Kritik kısıt:** τ = 10,34 µs. Düzgün örnekleme için τ başına 5–10 nokta, yani 1–2 µs örnekleme aralığı gerekiyor. CircuitPython'da düz `adc.value` döngüsü örnek başına 50–100 µs harcıyor — tüm geçici olayın 5–10 katı. **Düz döngüyle bu eğri ölçülemez.**

**Seçilen yöntem: A — DMA ile seri yakalama.** Ama C/Pico SDK ile değil, CircuitPython'un `analogbufio` modülüyle. Bu modül ADC'yi DMA ile arka planda bir tampona dolduruyor, Python hiç devrede olmuyor.

Karar gerekçesi: makinede C araç zinciri yok (`cmake`, `arm-none-eabi-gcc`, `picotool`, `PICO_SDK_PATH` — hiçbiri kurulu değil, kontrol edildi). Kartta zaten CircuitPython var. `analogbufio` aynı DMA yolunu kurulum gerektirmeden veriyor.

`code.py` (CIRCUITPY sürücüsüne kaydedilecek):

```python
# RC time constant measurement - Pico 2 / CircuitPython
# GP2 drives the RC network, GP26 (A0) reads the capacitor voltage.

import array
import board
import analogbufio
import pwmio

SAMPLE_RATE = 500000      # samples per second -> 2 us per sample
SAMPLE_COUNT = 1000       # 1000 samples -> 2 ms of data
SQUARE_HZ = 2000          # square wave on GP2
VREF = 3.3                # ADC full scale in volts

square = pwmio.PWMOut(board.GP2, frequency=SQUARE_HZ, duty_cycle=32768)

buf = array.array("H", ([0] * SAMPLE_COUNT))
adc = analogbufio.BufferedIn(board.A0, sample_rate=SAMPLE_RATE)
adc.readinto(buf)
adc.deinit()

dt = (1.0 / SAMPLE_RATE)

print("t_us,volt")
for i in range(SAMPLE_COUNT):
    t_us = ((i * dt) * 1e6)
    volt = ((buf[i] / 65535.0) * VREF)
    print("%.2f,%.4f" % (t_us, volt))
```

Tasarım notları:
- Kare dalgayı `pwmio` donanımı üretiyor, Python değil. `readinto` bloklarken pin oynatılamaz, o yüzden PWM sürekli serbest dönüyor. Titreşim saat kristaline bağlı, ihmal edilebilir.
- `duty_cycle=32768` = 65536'nın yarısı = %50.
- `board.A0` = GP26 = ADC0.
- 500 kSps → 2 µs/örnek → **τ başına 5 nokta, 5τ boyunca 26 nokta**. Simülasyondaki 620 noktaya karşılık. Eğri köşeli görünecek, normal.
- 1000 örnek = 2 ms = 2 kHz'de 4 periyot → **4 deşarj** yakalanıyor, ortalama alınabilir.
- `deinit()` şart, yoksa ikinci kanal (GP27) açılırken kanal meşgul hatası gelir.
- `VREF` τ'yu etkilemiyor — `ln(v/V₀)`'da ölçek çarpanı sadeleşiyor. Sadece CSV'nin volt cinsinden okunması ve osiloskopla karşılaştırma için var.

**İlk çalıştırmadan önce doğrulanacak:** `import analogbufio` çalışıyor mu. Hata verirse CircuitPython sürümü eski, güncellenecek.

### CSV'yi `sim.py` analizine bağlamak

Üç yer değişiyor, gerisi (`V0`, `v_win`, `t_local`, `ln`, `polyfit`, `-1/m`) aynı kalıyor:

```python
data = np.loadtxt("data.csv", delimiter=",", skiprows=1)
t = (data[:, 0] * 1e-6)
vout = data[:, 1]

edges = np.where(np.diff(vout) < -0.3)[0]   # v_in yok, kenari vout'tan bul
k = edges[0]

dt = 2e-6      # ts yerine
n = 15         # 3*tau/dt, 620 yerine
```

Kenar eşiği −0,3 V: deşarj başında iki örnek arası düşüş ~0,58 V (`3,3 → 3,3·e^{-2/10,34}`), düz kısımlarda ~0. **Dikkat:** deşarjın ilk 3–4 örneği de eşiği geçiyor, yani `edges` art arda indeksler içerir. `edges[0]` doğru başlangıcı verir ama ikinci deşarjı bulmak için aradaki boşluklara bakmak gerekir.

**Sonra:** Y kanalı (GP3 / GP27 / A1) için aynısı tekrarlanacak, iki kanalın τ farkı bileşen toleransı olarak raporlanacak.

## 3. Aşama — Osiloskop (henüz başlanmadı)

CH1 → X düğümü, CH2 → Y düğümü. Toprak klipsleri pin 38 veya AGND pin 33. Kare dalgayı Pico üretiyor, GP2 ve GP3 birlikte 2 kHz.

Ayarlar: prob 10×, 10 µs/div (kenar için 2 µs/div), 500 mV/div, DC kuplaj, tetikleme CH1 yükselen kenar.

Ölçümler: %63,2 imleç yöntemi, otomatik `Rise Time` (τ = t_r/2,20), deşarjdan 5–6 nokta alıp log eğim, iki nokta yöntemi.

Ek gözlem: frekansı 2 → 10 → 30 → 100 kHz kademeli artır, yarım periyot 3τ altına inince çıkışın üçgene dönüşmesini gözle (integratör davranışı).

## Bilinen tuzaklar

**Prob kompanzasyonu.** Bu deneyin en büyük hata kaynağı. Ayarsız prob, kare dalganın köşelerini yuvarlar ve bu yuvarlanma devrenin τ'su sanılır. Ölçüme başlamadan kalibrasyon çıkışına takıp trimmer'ı ayarlamak şart.

**ln analizinde gürültü tabanı.** `v` sıfıra yaklaştıkça `ln` aşırı duyarlı hale gelir ve noktalar doğrudan sapar. `V₀`'ın %5'inin altına inen noktalar analizden çıkarılmalı.

**Başlangıç koşulu devri.** Simülasyonda her yarım periyot bir öncekinin bıraktığı gerilimden başlar. Atlanırsa ikinci periyottan itibaren eğri yanlış.

**Nano/mikro karışması.** `4.7e-9` (nano) ile `4.7e-6` (mikro). Bir kez bu hata yapıldı, τ bin kat büyük çıktı.

## Tolerans beklentisi

Direnç %1–5, kondansatör %5–10 tolerans. τ = RC olduğu için bağıl hatalar toplanır, yani %10 civarı sapma normal. Bundan fazlası varsa sırayla bakılacak: prob kompanzasyonu, kartın kaçak kapasitesi, ADC örnekleme yükü.

İki kanal (X ve Y) aynı nominal değerlere sahip. Aralarındaki fark ölçüm hatası değil, doğrudan bileşen toleransıdır ve raporda ayrıca yorumlanacak.

Dirençler multimetreyle ölçülüp teorik değer gerçek sayılarla yeniden hesaplanacak. LCR metre yoksa iş tersine çevrilebilir: `C = τ_ölçüm / R_ölçülen` ile kapasitenin gerçek değeri bulunur.
