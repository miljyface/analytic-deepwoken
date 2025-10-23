# 🔬 Lightweight Library Alternatives for the Bot

## 📊 Benchmark Results (from local measurements)

### Current Libraries (Load time | Memory)
| Library | Time | Memory | Status |
|--------|------|--------|--------|
| discord.py | 1.077s | 19.7MB | ✅ Essential |
| requests | 0.239s | 2.1MB | ✅ Lightweight |
| rapidfuzz | 0.095s | 0.6MB | ✅ Fast |
| python-dotenv | 0.015s | 0.1MB | ✅ Minimal |
| matplotlib | ~2.0s (lazy) | ~70–80MB | ⚠️ Heavy but needed for charts |

Note: The Supabase SDK was removed and replaced with direct REST calls using requests (lighter, faster). 

---

## 🎯 Alternatives Considered

### 1) Matplotlib → Lighter options

#### ❌ matplotlib (~70–80MB)
- Pros: Powerful, publication-quality charts
- Cons: Heavy dependency footprint
- Current use: 2 files (statevograph.py, ehpbreakdown.py)

#### ✅ Pillow (PIL) + ImageDraw (~10MB)
```python
from PIL import Image, ImageDraw, ImageFont
```
- Pros: Already in use, lightweight, enough for simple charts
- Cons: More manual work for complex visuals
- Load: <0.1s, RAM ~3–5MB
- Recommendation: ⭐⭐⭐⭐⭐ Best lightweight alternative if we refactor charts

#### 🟡 plotly (~30MB)
- Pros: Interactive charts, HTML output
- Cons: Heavier than PIL, HTML not ideal for Discord attachments

#### 🟡 pygal (~5MB)
- Pros: SVG output, lightweight
- Cons: SVG not natively supported by Discord

---

### 2) Supabase → Lighter access layer

#### ❌ supabase SDK (12.6MB, ~1.1s to import)
- Pros: Official SDK, easy API
- Cons: Heavy wrapper over HTTP

#### ✅ requests (kept) or httpx
```python
import requests
headers = {
  'apikey': SUPABASE_KEY,
  'Authorization': f'Bearer {SUPABASE_KEY}'
}
resp = requests.get(f"{SUPABASE_URL}/rest/v1/weapons?select=*", headers=headers)
data = resp.json()
```
- Pros: Lightweight, simple, no SDK overhead
- Cons: Manual error handling
- Recommendation: ⭐⭐⭐⭐⭐ Use requests (already integrated)

---

### 3) discord.py → Alternatives

#### ✅ discord.py (1.077s, 19.7MB)
- Pros: Most popular, stable, best docs
- Cons: Slightly heavy
- Recommendation: ⭐⭐⭐⭐⭐ Keep

#### 🟡 py-cord (similar)
- Fork of discord.py with native slash commands
- Similar size/footprint

#### 🟡 nextcord (similar)
- Another discord.py fork
- Similar size

**Conclusion:** Not worth switching—discord.py is the standard

---

## ⚡ Recommended Optimizations

### 🥇 Priority 1: Replace Supabase SDK with requests (DONE)

Estimated savings: ~10MB RAM, ~0.85s startup

Implementation:
```python
# backbone.py (final)
import requests

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

def fetch_table(table_name):
    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/{table_name}?select=*',
        headers=HEADERS
    )
    return response.json()
```

Benefits:
- ✅ Removes supabase SDK (~10–12MB)
- ✅ Uses existing requests
- ✅ Simpler, more direct code
- ✅ ~0.85s faster startup

---

### 🥈 Priority 2: Consider Pillow instead of matplotlib

Estimated savings: ~75MB install, ~70MB RAM, ~2s startup

Current charts are complex (multi-series, legends, grids, annotations, styles).

Options:

#### Option A: Rewrite with Pillow (if time allows)
```python
from PIL import Image, ImageDraw, ImageFont

def create_chart_pillow(data):
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    # ... draw bars, lines, labels here
    return img
```
- ✅ Saves ~75MB
- ❌ Requires ~300 lines of refactor
- ❌ Harder to maintain
- ⏱️ Est: 4–6 hours

#### Option B: Keep matplotlib with lazy load (current approach)
```python
# Import only when needed
def plot_breakdown(build, talentBase, params):
    import matplotlib
    matplotlib.use('Agg')  # headless
    import matplotlib.pyplot as plt  # lazy import
    # ... rest of code
```
- ✅ No refactor needed
- ✅ Loads only when actually used
- ✅ 5-minute change
- ⚠️ Still heavy on disk

#### Option C: External chart service (innovative)
```python
# QuickChart.io - free chart API
import requests
chart_url = f"https://quickchart.io/chart?c={chart_config}"
response = requests.get(chart_url)
```
- ✅ Zero local deps
- ✅ Professional visuals
- ⚠️ Requires stable internet
- ⚠️ Rate-limited (free tier)

---

### 🥉 Priority 3: Use matplotlib headless

If keeping matplotlib:
```python
import matplotlib
matplotlib.use('Agg')  # Headless backend = lighter
import matplotlib.pyplot as plt
```

Benefits:
- ✅ ~5–10MB less RAM
- ✅ Faster (no GUI)

---

## 📋 Step-by-step Implementation

### Fase 1: Quick Wins (15 minutos) ⚡
1. ✅ Reemplazar supabase con requests
2. ✅ Lazy import de matplotlib
3. ✅ Configurar matplotlib Agg backend

Savings: ~20MB RAM, ~1s startup

### Fase 2: Optimización Media (1-2 horas) 🔧
1. Implementar cache en memoria para tablas de Supabase
2. Comprimir imágenes antes de enviar a Discord
3. Async para comandos largos

**Ahorro:** ~30MB RAM, mejor UX

### Fase 3: Refactor Completo (4-8 horas) 🏗️
1. Reescribir gráficos con Pillow
2. Implementar connection pooling
3. Background tasks para análisis pesados

Savings: ~75MB install, ~50MB RAM

---

## 🎯 Final Recommendation

### Implement now:
1. ✅ **Reemplazar supabase con requests** - 10MB ahorrados
2. ✅ **Lazy import matplotlib** - Mejora startup
3. ✅ **matplotlib.use('Agg')** - 5-10MB ahorrados

### Consider later:
- Reescribir gráficos con Pillow (si crece el bot)
- Usar QuickChart.io (si quieres zero dependencias)

### Avoid:
- ❌ Cambiar discord.py (no hay mejora real)
- ❌ Usar plotly (más pesada que matplotlib)

---

## 📊 Final Comparison Table

| Optimización | Ahorro RAM | Ahorro Startup | Complejidad |
|--------------|------------|----------------|-------------|
| Supabase → requests | ~10MB | ~0.85s | ⭐ Fácil |
| Lazy matplotlib | ~70MB* | ~2s* | ⭐ Muy fácil |
| matplotlib Agg | ~5-10MB | ~0.2s | ⭐ Trivial |
| Pillow rewrite | ~70MB | ~2s | ⭐⭐⭐⭐⭐ Difícil |
| QuickChart API | ~80MB | ~2.5s | ⭐⭐⭐ Media |

*Only when charts are not used

---

## 🚀 Next Steps

If you want to go further:
1. Supabase → requests (done) — save ~10MB
2. Lazy matplotlib (done) — faster startup
3. matplotlib Agg backend (done) — save 5–10MB

Potential future: Pillow rewrite for zero matplotlib dependency.
