#!/usr/bin/env python3
"""
Open Interactive Visualizations

Simple script to open the generated HTML visualizations in the default browser.
"""

import webbrowser
import os
import sys
import glob

def open_visualizations():
    """Open all generated HTML visualizations"""
    
    # print("🌐 Opening Interactive Hierarchical Summaries Visualizations")
    # print("=" * 60)
    
    # Find all HTML files
    html_files = glob.glob("*.html")
    
    if not html_files:
        # print("❌ No HTML files found in current directory")
        # print("   Run: python visualize_summaries.py <json_file>")
        return
    
    # print(f"📁 Found {len(html_files)} HTML files:")
    
    # Open files
    for html_file in sorted(html_files):
        # print(f"   📊 Opening: {html_file}")
        webbrowser.open(f"file://{os.path.abspath(html_file)}")
    
    # print(f"\n✅ Opened {len(html_files)} visualization files")
    # print("   💡 Use mouse wheel to zoom in/out for clear text visibility")

def list_visualizations():
    """List available visualizations"""
    
    html_files = glob.glob("*.html")
    
    if not html_files:
        # print("❌ No HTML files found")
        return
    
    # print("📊 Available Visualizations:")
    # print("=" * 40)
    
    for html_file in sorted(html_files):
        file_size = os.path.getsize(html_file) / (1024 * 1024)  # MB
        # print(f"   • {html_file} ({file_size:.1f} MB)")
    
    # print(f"\n📁 Total: {len(html_files)} files")

def main():
    """Main function"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_visualizations()
    else:
        open_visualizations()

if __name__ == "__main__":
    main()