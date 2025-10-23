"""
Test script to measure library loading times and memory usage
"""
import time
import sys
import tracemalloc

def measure_import(lib_name):
    """Measure import time and memory usage"""
    tracemalloc.start()
    start_time = time.time()
    
    try:
        __import__(lib_name)
        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            'success': True,
            'time': end_time - start_time,
            'memory_mb': peak / 1024 / 1024
        }
    except ImportError:
        tracemalloc.stop()
        return {'success': False}

# Test current libraries
print("📊 CURRENT LIBRARIES:")
print("-" * 60)

libs = {
    'discord': 'discord.py',
    'supabase': 'supabase',
    'matplotlib': 'matplotlib',
    'requests': 'requests',
    'rapidfuzz': 'rapidfuzz',
    'dotenv': 'python-dotenv'
}

for lib, full_name in libs.items():
    result = measure_import(lib)
    if result['success']:
        print(f"✅ {full_name:20} | Time: {result['time']:.3f}s | Memory: {result['memory_mb']:.1f}MB")
    else:
        print(f"❌ {full_name:20} | Not installed")

print("\n" + "=" * 60)
print("🔬 TESTING ALTERNATIVES:")
print("=" * 60)

# Test matplotlib alternatives
print("\n📈 MATPLOTLIB ALTERNATIVES:")
print("-" * 60)

alternatives = ['plotly', 'pygal', 'PIL']
for alt in alternatives:
    result = measure_import(alt)
    if result['success']:
        print(f"✅ {alt:20} | Time: {result['time']:.3f}s | Memory: {result['memory_mb']:.1f}MB")
    else:
        print(f"⚠️  {alt:20} | Not installed (can be tested)")

# Test requests alternative
print("\n🌐 REQUESTS ALTERNATIVES:")
print("-" * 60)

http_libs = ['httpx', 'aiohttp', 'urllib3']
for lib in http_libs:
    result = measure_import(lib)
    if result['success']:
        print(f"✅ {lib:20} | Time: {result['time']:.3f}s | Memory: {result['memory_mb']:.1f}MB")
    else:
        print(f"⚠️  {lib:20} | Not installed")

print("\n" + "=" * 60)
print("💡 RECOMMENDATIONS:")
print("=" * 60)
print("""
1. discord.py: ✅ Keep - Most stable and feature-complete
2. supabase: ⚠️  Consider httpx + direct API calls (lighter)
3. matplotlib: ⚠️  Heavy but needed for complex charts
4. requests: ✅ Keep - Simple and reliable
5. rapidfuzz: ✅ Keep - Very fast C++ implementation
6. python-dotenv: ✅ Keep - Minimal overhead
""")
