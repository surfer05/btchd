#!/usr/bin/env python3
"""
Update Function Demo

Demonstrates how to use the update function to add new tags to existing hierarchical results.
"""

import asyncio
import json
from hierarchical_summarizer import HierarchicalGridSummarizer

async def demo_update_function():
    """Demo the update function"""
    
    print("🔄 HIERARCHICAL UPDATE FUNCTION DEMO")
    print("=" * 50)
    
    # Initialize summarizer
    summarizer = HierarchicalGridSummarizer(
        provider_type="gemini"
    )
    
    # Load existing results
    existing_file = "delhi_gemini_results_w_lesswords_30_level0summary.json"
    
    print(f"📁 Loading existing results from: {existing_file}")
    
    # Demo 1: Update existing cell
    print(f"\n🔹 DEMO 1: Update existing cell")
    print(f"   Adding: 'Amazing street food' at (28.571, 77.237)")
    
    updated_results = await summarizer.update_with_new_tag(
        lat=28.571,
        lon=77.237,
        tag_text="Amazing street food",
        existing_results=existing_file,
        output_file="demo_update_1.json"
    )
    
    # Demo 2: Add new cell
    print(f"\n🔹 DEMO 2: Add new cell")
    print(f"   Adding: 'New tech hub' at (28.6, 77.3)")
    
    updated_results = await summarizer.update_with_new_tag(
        lat=28.6,
        lon=77.3,
        tag_text="New tech hub",
        existing_results="demo_update_1.json",
        output_file="demo_update_2.json"
    )
    
    # Demo 3: Multiple tags in same cell
    print(f"\n🔹 DEMO 3: Multiple tags in same cell")
    print(f"   Adding: 'Best biryani place' at (28.571, 77.237)")
    
    updated_results = await summarizer.update_with_new_tag(
        lat=28.571,
        lon=77.237,
        tag_text="Best biryani place",
        existing_results="demo_update_2.json",
        output_file="demo_final.json"
    )
    
    print(f"\n🎉 Demo complete!")
    print(f"📁 Generated files:")
    print(f"   • demo_update_1.json - After first update")
    print(f"   • demo_update_2.json - After second update")
    print(f"   • demo_final.json - Final result")

def show_update_usage():
    """Show command-line usage examples"""
    
    print("\n📖 COMMAND-LINE USAGE EXAMPLES")
    print("=" * 50)
    
    examples = [
        {
            "description": "Update existing cell with new tag",
            "command": "python hierarchical_summarizer.py --update --lat 28.571 --lon 77.237 --tag 'Best coffee shop' --existing-results delhi_results.json --output updated_results.json --provider gemini"
        },
        {
            "description": "Add new cell outside existing grid",
            "command": "python hierarchical_summarizer.py --update --lat 28.6 --lon 77.3 --tag 'New area' --existing-results delhi_results.json --output updated_results.json --provider gemini"
        },
        {
            "description": "Update with OpenAI provider",
            "command": "python hierarchical_summarizer.py --update --lat 28.571 --lon 77.237 --tag 'Great place' --existing-results delhi_results.json --output updated_results.json --provider openai"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['description']}:")
        print(f"   {example['command']}")

def show_update_features():
    """Show key features of the update function"""
    
    print("\n🔧 UPDATE FUNCTION FEATURES")
    print("=" * 50)
    
    features = [
        "✅ Updates existing cells with new tags",
        "✅ Creates new cells outside existing grid",
        "✅ Automatically summarizes multiple tags within cells",
        "✅ Updates summaries at all hierarchical levels",
        "✅ Maintains grid structure and boundaries",
        "✅ Works with both OpenAI and Gemini providers",
        "✅ Preserves existing data while adding new information",
        "✅ Handles edge cases (cells outside grid boundaries)"
    ]
    
    for feature in features:
        print(f"   {feature}")

if __name__ == "__main__":
    print("🚀 Choose an option:")
    print("1. Run update demo")
    print("2. Show usage examples")
    print("3. Show features")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(demo_update_function())
    elif choice == "2":
        show_update_usage()
    elif choice == "3":
        show_update_features()
    else:
        print("Invalid choice. Showing all options:")
        show_update_features()
        show_update_usage()
        print("\nTo run the demo, execute: python update_demo.py and choose option 1")
