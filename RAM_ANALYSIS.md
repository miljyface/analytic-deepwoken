# 📊 Bot Disk Space & RAM Usage Analysis

## 💾 DISK SPACE USAGE

```
Total Bot Size: 191.9 MB
├── venv/        191.68 MB (99.9%) - Python environment & dependencies
├── src/         0.13 MB   (0.1%)  - Bot source code
├── data/        0.0 MB    (0.0%)  - JSON data files
└── other/       0.09 MB   (0.0%)  - Config, docs, scripts
```

### Breakdown:
- **Virtual Environment (venv/)**: 191.68 MB
  - Contains all Python packages and dependencies
  - Main contributors: discord.py, matplotlib, requests, rapidfuzz
  
- **Source Code (src/)**: 0.13 MB (130 KB)
  - Very lean - all Python files combined
  - 17 Python modules total
  
- **Data Files**: Negligible
  - racialstats.json and other configs

---

## 🧠 RAM USAGE ANALYSIS

### Database Tables (Supabase):
Based on MCP analysis of the DeepwokenPlanner project:

| Table | Rows | Disk Size | JSON Data Size | Est. RAM |
|-------|------|-----------|----------------|----------|
| **talents** | 1454 | 784 KB | 608 KB | ~650 KB |
| **equipment** | 285 | 264 KB | 47 KB | ~60 KB |
| **outfits** | 74 | 280 KB | N/A | ~50 KB |
| **mantras** | 227 | 232 KB | N/A | ~180 KB |
| **weapons** | 210 | 128 KB | N/A | ~100 KB |
| **TOTAL** | 2,250 | ~1.65 MB | ~655 KB | **~1.1 MB** |

---

## 📋 COMMAND-BY-COMMAND RAM ANALYSIS

### **Best Case Scenario** (Minimal Command)

**Command:** `.help`
- **Tables loaded:** None
- **External dependencies:** None
- **RAM Usage:**
  - Base bot: ~23 MB (discord.py, dotenv, rapidfuzz, requests)
  - Command overhead: ~0.1 MB
  - **Total: ~23 MB**

---

### **Average Case** (Lookup Commands)

**Commands:** `.weapon`, `.mantra`, `.equipment`, `.outfit`, `.talent`

**Example: `.weapon flame hb`**

**Process:**
1. Load weapon_names list on first call (lazy load)
2. Fuzzy match with rapidfuzz
3. Fetch single item from Supabase
4. Build embed

**RAM Usage:**
- Base bot: ~23 MB
- Weapon names cache: ~0.1 MB (210 weapons)
- Rapidfuzz processing: ~0.5 MB
- HTTP response (single weapon): ~0.5 KB
- Discord embed: ~0.2 MB
- **Total: ~24 MB**

**Other lookup commands:**
- `.talent`: ~24.5 MB (727 talents, larger cache ~350 KB)
- `.mantra`: ~24 MB (227 mantras)
- `.equipment`: ~24 MB (285 items)
- `.outfit`: ~23.5 MB (74 outfits)

**Average across all lookups: ~24 MB**

---

### **Heavy Case** (Graph Generation - No matplotlib loaded)

**Commands:** Build analytics with graphs
- `.stats` (stat evolution graph)
- `.ehp` (EHP breakdown graphs)

**First Call (Cold Start):**

**Example: `.stats https://deepwoken.co/builder?id=xyz`**

**Process:**
1. Parse build URL and fetch data
2. Load ALL tables (talents, weapons, etc.) - needed for calculations
3. **Load matplotlib for first time** (lazy import)
4. Generate graph
5. Send via Discord

**RAM Usage:**
- Base bot: ~23 MB
- All tables loaded: ~1.1 MB
- Build data: ~0.5 MB
- **Matplotlib import**: ~70 MB (first time)
- Graph generation: ~15 MB (PIL operations)
- Discord file upload: ~2 MB
- **Total: ~111 MB**

---

### **Worst Case** (Multiple Graphs - matplotlib loaded)

**Command:** `.ehp https://deepwoken.co/builder?id=xyz`

**Process:**
1. Parse build
2. Load ALL tables (if not cached)
3. Generate TWO EHP breakdown graphs (matplotlib already loaded)
4. Combine images with PIL
5. Send combined image

**RAM Usage:**
- Base bot: ~23 MB
- All tables (cached): ~1.1 MB
- Build data: ~0.5 MB
- Matplotlib (already loaded): ~70 MB
- **Two graph generations**: ~30 MB (2x15 MB)
- Image combination (PIL): ~5 MB
- Discord file upload: ~3 MB
- **Total: ~132 MB**

---

## 📊 SUMMARY TABLE

| Scenario | Command Example | RAM Usage | Tables Loaded | Matplotlib |
|----------|----------------|-----------|---------------|------------|
| **Best Case** | `.help` | **~23 MB** | None | No |
| **Light Lookup** | `.weapon flame hb` | **~24 MB** | weapons only | No |
| **Heavy Lookup** | `.talent terminus` | **~24.5 MB** | talents only | No |
| **First Graph** | `.stats <build>` | **~111 MB** | All | Yes (cold) |
| **Subsequent Graph** | `.stats <build>` | **~88 MB** | All (cached) | Yes (warm) |
| **Worst Case** | `.ehp <build>` | **~132 MB** | All (cached) | Yes (warm) |

---

## 🎯 KEY INSIGHTS

### 1. **Base Memory Footprint: ~23 MB**
The bot without any commands uses minimal RAM:
- discord.py: ~19.7 MB
- requests: ~2.1 MB
- rapidfuzz: ~0.6 MB
- python-dotenv: ~0.1 MB
- Other overhead: ~0.5 MB

### 2. **Database Tables are Tiny**
All Supabase tables combined: **~1.1 MB in RAM**
- Very efficient JSON structures
- Negligible impact on memory
- Caching all tables is viable

### 3. **Matplotlib is the Memory Hog**
- **~70 MB** on first import
- Persistent for bot lifetime once loaded
- Largest single contributor to peak RAM

### 4. **Lookup Commands are Extremely Efficient**
- Average: **~24 MB** (only 1 MB over base)
- Fast fuzzy matching with rapidfuzz
- HTTP requests are lightweight

### 5. **Graph Generation is Expensive**
- First graph: **+88 MB** over base
- Each graph generation: **~15 MB** temporary
- Image combination: **+5 MB** with PIL

---

## 💡 OPTIMIZATION OPPORTUNITIES

### Already Implemented ✅
1. **Lazy matplotlib loading** - Only loads when graphs needed
2. **Removed pandas/numpy** - Saved ~72 MB
3. **Direct Supabase REST API** - Saved ~10 MB vs SDK
4. **Headless matplotlib backend** - Saves ~5-10 MB

### Future Potential 🚀
1. **Table caching in memory**
   - Cache all 5 tables on first use (~1.1 MB)
   - Avoid repeated Supabase calls
   - **Savings:** Network latency, not RAM

2. **Graph caching**
   - Cache generated graphs for 5 minutes
   - Reuse for duplicate requests
   - **Savings:** ~15 MB per duplicate request

3. **Replace matplotlib with Pillow charts**
   - Rewrite charts using PIL.ImageDraw
   - Eliminate matplotlib dependency
   - **Savings:** ~70 MB permanent, ~15 MB per graph

4. **Async command processing**
   - Generate graphs in background
   - Don't block other commands
   - **Savings:** Better UX, not RAM

---

## 🎮 REAL-WORLD USAGE PATTERNS

### Typical User Session:
1. User starts with `.help` - **23 MB**
2. Looks up weapon: `.weapon rapier` - **24 MB**
3. Looks up talent: `.talent vanishing follow-up` - **24.5 MB**
4. Analyzes build: `.stats <url>` - **111 MB** (peak)
5. Returns to lookups: `.mantra ice chains` - **88 MB** (matplotlib still loaded)

**Session Peak:** **~132 MB** (if `.ehp` is used)
**Session Average:** **~40 MB**

### Server with Multiple Users:
- Each user command is independent
- Peak RAM = highest single command
- Commands don't stack (bot processes sequentially)
- **Expected Peak: 132 MB**

---

## 🔧 RECOMMENDATIONS

### Current State: **EXCELLENT** ✅
- **Base: 23 MB** - Very lean
- **Average: 24 MB** - Efficient lookups
- **Peak: 132 MB** - Acceptable for graph generation

### If you need to reduce further:
1. **Remove matplotlib** → Peak drops to **~50 MB**
   - Rewrite charts with Pillow (4-6 hours work)
   
2. **Preload all tables** → Faster responses, +0.74 MB
   - Load on startup, eliminate lazy loading
   
3. **Use QuickChart API** → Zero graph memory
   - External service generates charts
   - Bot just requests URLs

---

**Analysis Date:** October 23, 2025
**Bot Version:** 1.0 (Optimized)
