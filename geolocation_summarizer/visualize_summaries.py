#!/usr/bin/env python3
"""
Single Interactive Hierarchical Summaries Visualization

Creates a single HTML file with interactive grid visualization where you can zoom into each level to see text clearly.
"""

import json
import argparse
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def load_results(json_file):
    """Load the hierarchical results"""
    with open(json_file, 'r') as f:
        return json.load(f)

def create_single_interactive_visualization(data, output_file="hierarchical_summaries.html"):
    """Create a single interactive HTML visualization with zoom capabilities"""
    
    # Create subplots for each level
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            f'Level 0 (1x1 kernels) - {len(data["levels"].get("0", {}))} cells',
            f'Level 1 (2x2 kernels) - {len(data["levels"].get("1", {}))} cells',
            f'Level 2 (4x4 kernels) - {len(data["levels"].get("2", {}))} cells',
            f'Level 3 (8x8 kernels) - {len(data["levels"].get("3", {}))} cells'
        ],
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "scatter"}, {"type": "scatter"}]],
        vertical_spacing=0.08,
        horizontal_spacing=0.08
    )
    
    colors = ['#87CEEB', '#98FB98', '#F0E68C', '#DDA0DD']  # Light blue, light green, khaki, plum
    
    for level_num in range(4):
        level_key = str(level_num)
        row = level_num // 2 + 1
        col = level_num % 2 + 1
        
        if level_key not in data['levels']:
            # Add empty trace for missing level
            fig.add_trace(
                go.Scatter(
                    x=[], y=[],
                    mode='markers',
                    name=f'Level {level_num}',
                    showlegend=False
                ),
                row=row, col=col
            )
            continue
            
        level_data = data['levels'][level_key]
        
        # Extract coordinates and summaries
        coords = []
        summaries = []
        cell_keys = []
        
        for cell_key, cell_info in level_data.items():
            x, y = map(int, cell_key.split('_'))
            coords.append((x, y))
            summaries.append(cell_info['combined_tag'])
            cell_keys.append(cell_key)
        
        if not coords:
            continue
            
        # Create scatter plot for this level
        x_coords = [coord[0] for coord in coords]
        y_coords = [coord[1] for coord in coords]
        
        # Create hover text with full summaries
        hover_text = []
        for i, (cell_key, summary) in enumerate(zip(cell_keys, summaries)):
            hover_text.append(f"<b>Cell: {cell_key}</b><br>Summary: {summary}")
        
        # Determine marker size based on level (smaller for higher levels)
        marker_size = max(15, 25 - level_num * 3)
        
        # Determine text size based on level
        text_size = max(8, 12 - level_num)
        
        fig.add_trace(
            go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='markers+text',
                marker=dict(
                    size=marker_size,
                    color=colors[level_num],
                    line=dict(width=2, color='black'),
                    opacity=0.8
                ),
                text=[summary[:25] + "..." if len(summary) > 25 else summary for summary in summaries],
                textposition="middle center",
                textfont=dict(size=text_size, color="black", family="Arial"),
                hovertemplate="%{hovertext}<extra></extra>",
                hovertext=hover_text,
                name=f'Level {level_num}',
                showlegend=True
            ),
            row=row, col=col
        )
        
        # Set axis properties for this subplot
        fig.update_xaxes(
            title_text="Grid X", 
            row=row, col=col,
            showgrid=True, 
            gridwidth=1, 
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black'
        )
        fig.update_yaxes(
            title_text="Grid Y", 
            row=row, col=col,
            showgrid=True, 
            gridwidth=1, 
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black'
        )
    
    # Update layout for better visibility
    fig.update_layout(
        title={
            'text': 'Interactive Hierarchical Grid Summaries - Zoom to See Details Clearly',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': 'darkblue'}
        },
        height=900,
        width=1200,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12)
        ),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Add instructions as annotation
    fig.add_annotation(
        text="<b>Instructions:</b><br>• Use mouse wheel to zoom in/out<br>• Click and drag to pan<br>• Double-click to reset zoom<br>• Hover over markers for full summaries",
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        font=dict(size=10, color="darkgreen"),
        bgcolor="lightyellow",
        bordercolor="darkgreen",
        borderwidth=1
    )
    
    # Save as HTML
    fig.write_html(output_file, config={
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'hierarchical_summaries',
            'height': 900,
            'width': 1200,
            'scale': 2
        }
    })
    
    return fig

def main():
    """Main visualization function"""
    parser = argparse.ArgumentParser(description='Single Interactive Hierarchical Summaries Visualization')
    parser.add_argument('json_file', help='Path to JSON results file')
    
    args = parser.parse_args()
    
    # Load the results
    try:
        data = load_results(args.json_file)
        print(f"✅ Loaded data from: {args.json_file}")
    except FileNotFoundError:
        print(f"❌ File not found: {args.json_file}")
        return
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON file: {args.json_file}")
        return
    
    # Generate output filename based on input
    import os
    base_name = os.path.splitext(os.path.basename(args.json_file))[0]
    if not os.path.exists('visuals'):
        os.makedirs('visuals')
    output_file = f"visuals/{base_name}_interactive.html"
    
    print("📊 Creating single interactive hierarchical visualization...")
    
    # Create visualization
    fig = create_single_interactive_visualization(data, output_file)
    
    print(f"✅ Saved: {output_file}")
    print("\n🎉 Visualization complete!")
    print(f"📁 Generated file: {output_file}")
    print("\n💡 Instructions:")
    print("   • Open the HTML file in your browser")
    print("   • Use mouse wheel to zoom in/out")
    print("   • Click and drag to pan around")
    print("   • Double-click to reset zoom")
    print("   • Hover over markers for full summaries")
    print("   • Each level shows different granularity of summaries")

if __name__ == "__main__":
    main()