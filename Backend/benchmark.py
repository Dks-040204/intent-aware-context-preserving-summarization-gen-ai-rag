import requests
import time
import json
from statistics import mean, stdev
from typing import List, Dict

BASE_URL = "http://localhost:8000"

class PerformanceBenchmark:
    
    def __init__(self):
        self.results = {}
    
    def run_benchmark(self, name: str, payload: Dict, iterations: int = 5) -> Dict:
        times = []
        print(f"\n{'='*60}")
        print(f"🔍 Benchmarking: {name}")
        print(f"{'='*60}")
        print(f"Iterations: {iterations}")
        
        for i in range(iterations):
            start = time.time()
            try:
                response = requests.post(f"{BASE_URL}/summarize", json=payload, timeout=30)
                elapsed = (time.time() - start) * 1000
                
                if response.status_code == 200:
                    times.append(elapsed)
                    print(f"  Iteration {i+1}: {elapsed:.2f}ms ✅")
                else:
                    print(f"  Iteration {i+1}: ERROR (Status {response.status_code}) ❌")
            except Exception as e:
                print(f"  Iteration {i+1}: ERROR ({str(e)}) ❌")
        
        if times:
            result = {
                'name': name,
                'iterations': len(times),
                'min_ms': min(times),
                'max_ms': max(times),
                'avg_ms': mean(times),
                'stdev_ms': stdev(times) if len(times) > 1 else 0,
                'success_rate': (len(times) / iterations) * 100
            }
            print(f"\n📊 Results:")
            print(f"  Min: {result['min_ms']:.2f}ms")
            print(f"  Max: {result['max_ms']:.2f}ms")
            print(f"  Avg: {result['avg_ms']:.2f}ms")
            print(f"  Std Dev: {result['stdev_ms']:.2f}ms")
            print(f"  Success Rate: {result['success_rate']:.1f}%")
            
            self.results[name] = result
            return result
        else:
            print(f"❌ All iterations failed")
            return None
    
    def print_summary(self):
        """Print benchmark summary"""
        print(f"\n{'='*60}")
        print("📈 BENCHMARK SUMMARY")
        print(f"{'='*60}")
        
        if not self.results:
            print("No successful benchmarks")
            return
        
        # Sort by average time
        sorted_results = sorted(self.results.items(), key=lambda x: x[1]['avg_ms'])
        
        for name, result in sorted_results:
            print(f"\n{name}:")
            print(f"  Average: {result['avg_ms']:.2f}ms")
            print(f"  Range: {result['min_ms']:.2f}ms - {result['max_ms']:.2f}ms")
            print(f"  Success: {result['success_rate']:.1f}%")


def main():
    print("\n" + "="*60)
    print("🚀 DOCUMENT SUMMARIZER PERFORMANCE BENCHMARK")
    print("="*60)
    
    benchmark = PerformanceBenchmark()
    
    # Test 1: Short document with speed mode
    print("\n[1/6] Speed Mode - Short Document")
    payload_speed_short = {
        "document": "Machine learning is AI. It learns from data.",
        "quality_preference": "speed"
    }
    benchmark.run_benchmark("Speed Mode (Short Doc)", payload_speed_short, iterations=5)
    
    # Test 2: Medium document with balanced mode
    print("\n[2/6] Balanced Mode - Medium Document")
    payload_balanced_med = {
        "document": """Deep learning is a subset of machine learning using neural networks. 
        Each layer learns different features. It's used for image recognition, NLP, and speech. 
        Training requires GPU acceleration. Popular frameworks include PyTorch and TensorFlow.""",
        "quality_preference": "balanced"
    }
    benchmark.run_benchmark("Balanced Mode (Medium Doc)", payload_balanced_med, iterations=5)
    
    # Test 3: Quality mode
    print("\n[3/6] Quality Mode - Medium Document")
    payload_quality = {
        "document": """Transformers have revolutionized NLP. The attention mechanism allows focusing 
        on relevant sequence parts. BERT and GPT are transformer-based. Self-attention enables learning 
        long-range dependencies. Position encoding preserves sequence information. Transformers scale 
        to billions of parameters like GPT-3.""",
        "quality_preference": "quality"
    }
    benchmark.run_benchmark("Quality Mode (Medium Doc)", payload_quality, iterations=3)
    
    # Test 4: Different intent
    print("\n[4/6] Technical Overview Intent")
    payload_intent = {
        "document": "Convolutional neural networks use filters for feature extraction. ReLU activations add non-linearity. Pooling reduces dimensionality. CNNs excel at image tasks.",
        "intent": "technical_overview"
    }
    benchmark.run_benchmark("Technical Overview Intent", payload_intent, iterations=5)
    
    # Test 5: Methodology intent
    print("\n[5/6] Methodology Intent")
    payload_methodology = {
        "document": """We collected 10000 samples. Training used SGD with learning rate 0.01. 
        Batch size was 32. We trained for 100 epochs. Cross-entropy was the loss function. 
        We achieved 95% accuracy on test set.""",
        "intent": "methodology"
    }
    benchmark.run_benchmark("Methodology Intent", payload_methodology, iterations=5)
    
    # Test 6: Spanish language
    print("\n[6/6] Multilingual - Spanish")
    payload_spanish = {
        "document": "El aprendizaje automático es una rama de la inteligencia artificial importante.",
        "language": "spanish",
        "quality_preference": "speed"
    }
    benchmark.run_benchmark("Spanish Language (Speed)", payload_spanish, iterations=5)
    
    # Print summary
    benchmark.print_summary()
    
    # Save results to file
    with open('benchmark_results.json', 'w') as f:
        json.dump(benchmark.results, f, indent=2)
    print(f"\n✅ Results saved to benchmark_results.json")
    
    print("\n" + "="*60)
    print("✅ BENCHMARK COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
