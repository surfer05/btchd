#!/usr/bin/env python3
"""
Simple Delhi Hierarchical Summaries Visualization

Creates a clean visualization of the hierarchical grid summaries from Delhi data.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import numpy as np

def load_results(json_file):
    """Load the hierarchical results"""
    with open(json_file, 'r') as f:
        return json.load(f)

def create_hierarchical_visualization(data):
    """Create a simple hierarchical visualization"""
    
    # Create figure with subplots for each level
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Delhi Hierarchical Grid Summaries', fontsize=16, fontweight='bold')
    
    levels = ['0', '1', '2', '3']
    level_names = ['Level 0 (1x1)', 'Level 1 (2x2)', 'Level 2 (4x4)', 'Level 3 (8x8)']
    
    for i, (level, level_name) in enumerate(zip(levels, level_names)):
        ax = axes[i//2, i%2]
        
        if level not in data['levels']:
            ax.text(0.5, 0.5, f'No data for {level_name}', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(level_name)
            continue
            
        level_data = data['levels'][level]
        
        # Extract coordinates and create grid
        coords = []
        summaries = []
        
        for cell_key, cell_info in level_data.items():
            x, y = map(int, cell_key.split('_'))
            coords.append((x, y))
            summaries.append(cell_info['combined_tag'])
        
        if not coords:
            ax.text(0.5, 0.5, f'No cells in {level_name}', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(level_name)
            continue
        
        # Create grid visualization
        max_x = max(coord[0] for coord in coords)
        max_y = max(coord[1] for coord in coords)
        
        # Create grid
        for j, (x, y) in enumerate(coords):
            # Create rectangle for each cell
            rect = Rectangle((x, y), 1, 1, 
                           facecolor='lightblue', 
                           edgecolor='black', 
                           linewidth=0.5,
                           alpha=0.7)
            ax.add_patch(rect)
            
            # Add summary text (truncated)
            summary = summaries[j]
            if len(summary) > 20:
                summary = summary[:17] + "..."
            
            ax.text(x + 0.5, y + 0.5, summary, 
                   ha='center', va='center', 
                   fontsize=8, fontweight='bold',
                   rotation=0)
        
        ax.set_xlim(-0.5, max_x + 1.5)
        ax.set_ylim(-0.5, max_y + 1.5)
        ax.set_aspect('equal')
        ax.set_title(f'{level_name} ({len(coords)} cells)')
        ax.set_xlabel('Grid X')
        ax.set_ylabel('Grid Y')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def create_summary_text_visualization(data):
    """Create a text-based summary visualization"""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.95, 'Delhi Hierarchical Summaries Overview', 
            ha='center', va='top', fontsize=20, fontweight='bold',
            transform=ax.transAxes)
    
    y_pos = 0.9
    
    for level in ['0', '1', '2', '3']:
        if level not in data['levels']:
            continue
            
        level_data = data['levels'][level]
        level_name = f'Level {level} ({2**int(level)}x{2**int(level)} kernels)'
        
        # Level title
        ax.text(0.05, y_pos, level_name, 
                ha='left', va='top', fontsize=14, fontweight='bold',
                transform=ax.transAxes)
        y_pos -= 0.05
        
        # Show first few summaries
        count = 0
        for cell_key, cell_info in level_data.items():
            if count >= 5:  # Show max 5 per level
                remaining = len(level_data) - 5
                ax.text(0.1, y_pos, f'... and {remaining} more cells', 
                       ha='left', va='top', fontsize=10, style='italic',
                       transform=ax.transAxes)
                y_pos -= 0.03
                break
                
            summary = cell_info['combined_tag']
            ax.text(0.1, y_pos, f'• {summary}', 
                   ha='left', va='top', fontsize=11,
                   transform=ax.transAxes)
            y_pos -= 0.04
            count += 1
        
        y_pos -= 0.02  # Extra space between levels
    
    plt.tight_layout()
    return fig

def create_final_summary_visualization(data):
    """Create a visualization focusing on the final summary"""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    # Get final level summary
    final_level = data['levels']['3']
    final_cell = list(final_level.values())[0]
    final_summary = final_cell['combined_tag']
    
    # Title
    ax.text(0.5, 0.9, 'Delhi - Final Hierarchical Summary', 
            ha='center', va='top', fontsize=18, fontweight='bold',
            transform=ax.transAxes)
    
    # Final summary box
    summary_box = Rectangle((0.1, 0.3), 0.8, 0.4, 
                           facecolor='lightblue', 
                           edgecolor='navy', 
                           linewidth=2)
    ax.add_patch(summary_box)
    
    ax.text(0.5, 0.5, final_summary, 
            ha='center', va='center', fontsize=14, fontweight='bold',
            transform=ax.transAxes, wrap=True)
    
    # Statistics
    stats_text = f"""
    📊 Processing Statistics:
    • Level 0: {len(data['levels']['0'])} cells (1x1 kernels)
    • Level 1: {len(data['levels']['1'])} cells (2x2 kernels)  
    • Level 2: {len(data['levels']['2'])} cells (4x4 kernels)
    • Level 3: {len(data['levels']['3'])} cells (8x8 kernels)
    • Grid Delta: {data['metadata']['grid_delta']}
    """
    
    ax.text(0.5, 0.2, stats_text, 
            ha='center', va='top', fontsize=12,
            transform=ax.transAxes)
    
    plt.tight_layout()
    return fig

def main():
    """Main visualization function"""
    
    # Load the results
    try:
        data = load_results('delhi_final_results.json')
    except FileNotFoundError:
        print("❌ delhi_final_results.json not found. Trying alternative files...")
        try:
            data = load_results('delhi_gemini_results_w_lesswords_30_level0summary.json')
        except FileNotFoundError:
            print("❌ No results file found. Please run the hierarchical summarizer first.")
            return
    
    print("📊 Creating Delhi hierarchical summaries visualizations...")
    
    # Create visualizations
    fig1 = create_hierarchical_visualization(data)
    fig1.savefig('delhi_hierarchical_grids.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: delhi_hierarchical_grids.png")
    
    fig2 = create_summary_text_visualization(data)
    fig2.savefig('delhi_summaries_text.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: delhi_summaries_text.png")
    
    fig3 = create_final_summary_visualization(data)
    fig3.savefig('delhi_final_summary.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: delhi_final_summary.png")
    
    # Show the plots
    plt.show()
    
    print("\n🎉 Visualization complete!")
    print("📁 Generated files:")
    print("   • delhi_hierarchical_grids.png - Grid visualization for all levels")
    print("   • delhi_summaries_text.png - Text summary overview")
    print("   • delhi_final_summary.png - Final summary focus")

if __name__ == "__main__":
    main()
