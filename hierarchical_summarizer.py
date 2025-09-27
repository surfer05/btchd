#!/usr/bin/env python3
"""
Minimalistic Hierarchical Grid Summarizer

This script implements a step-by-step hierarchical grid summarization system:
1. Define rectangular area boundaries
2. Create grid cells with 0.01 delta
3. Combine tags within each cell
4. Create hierarchical levels with non-overlapping kernels
5. Batch summarize using GPT API
"""

import json
import argparse
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import asyncio
import aiohttp
import os

from dotenv import load_dotenv
load_dotenv()

from summary_providers import SummaryProviderFactory

@dataclass
class Tag:
    """Represents a location tag"""
    lat: float
    lon: float
    text: str
    votes: int

@dataclass
class GridCell:
    """Represents a grid cell with combined tags"""
    lat: float
    lon: float
    combined_tag: str
    level: int = 0
    kernel_size: int = 1
    # Kernel boundaries
    min_lat: float = 0.0
    max_lat: float = 0.0
    min_lon: float = 0.0
    max_lon: float = 0.0
    # Cell coordinates within level
    x: int = 0
    y: int = 0

class HierarchicalGridSummarizer:
    def __init__(self, api_key: str = None, grid_delta: float = 0.01, provider_type: str = "openai"):
        """Initialize the summarizer"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.grid_delta = grid_delta  # Grid cell size
        self.summary_provider = SummaryProviderFactory.create_provider(provider_type, api_key=api_key)
        
    def load_data(self, json_path: str) -> List[Tag]:
        """Load tags from JSON file"""
        print(f"📁 Loading data from: {json_path}")
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        tags = []
        for tag_data in data.get('tags', []):
            tag = Tag(
                lat=float(tag_data['latitude']),
                lon=float(tag_data['longitude']),
                text=tag_data['tag'],
                votes=tag_data['votes']
            )
            tags.append(tag)
        
        print(f"✅ Loaded {len(tags)} tags successfully")
        return tags
    
    def define_boundaries(self, tags: List[Tag], custom_boundaries: Optional[Tuple[float, float, float, float]] = None) -> Tuple[float, float, float, float]:
        """Define rectangular area boundaries from data or use custom boundaries"""
        if custom_boundaries:
            min_lat, max_lat, min_lon, max_lon = custom_boundaries
            print(f"📍 Using custom boundaries:")
            print(f"   Latitude: {min_lat:.6f} to {max_lat:.6f}")
            print(f"   Longitude: {min_lon:.6f} to {max_lon:.6f}")
            return min_lat, max_lat, min_lon, max_lon
        
        print("📍 Calculating boundaries from data...")
        lats = [tag.lat for tag in tags]
        lons = [tag.lon for tag in tags]
        
        min_lat = min(lats)
        max_lat = max(lats)
        min_lon = min(lons)
        max_lon = max(lons)
        
        # Add small buffer
        buffer = self.grid_delta
        boundaries = (min_lat - buffer, max_lat + buffer, min_lon - buffer, max_lon + buffer)
        
        print(f"✅ Calculated boundaries:")
        print(f"   Latitude: {boundaries[0]:.6f} to {boundaries[1]:.6f}")
        print(f"   Longitude: {boundaries[2]:.6f} to {boundaries[3]:.6f}")
        print(f"   Buffer added: {buffer}")
        
        return boundaries
    
    def create_base_grid(self, tags: List[Tag], boundaries: Tuple[float, float, float, float]) -> Dict[Tuple[int, int], GridCell]:
        """Create base grid cells and combine tags within each cell"""
        print(f"🔲 Creating base grid with cell size: {self.grid_delta}")
        min_lat, max_lat, min_lon, max_lon = boundaries
        
        # Calculate grid dimensions
        lat_range = max_lat - min_lat
        lon_range = max_lon - min_lon
        grid_lat_cells = int(lat_range / self.grid_delta) + 1
        grid_lon_cells = int(lon_range / self.grid_delta) + 1
        
        print(f"   Grid dimensions: {grid_lat_cells} x {grid_lon_cells} cells")
        print(f"   Total possible cells: {grid_lat_cells * grid_lon_cells}")
        
        # Create grid cells
        grid = {}
        cells_with_tags = 0
        
        print(f"📍 Processing {len(tags)} tags...")
        for i, tag in enumerate(tags):
            # Calculate grid coordinates
            grid_lat = int((tag.lat - min_lat) / self.grid_delta)
            grid_lon = int((tag.lon - min_lon) / self.grid_delta)
            
            # Calculate cell center
            cell_lat = min_lat + (grid_lat + 0.5) * self.grid_delta
            cell_lon = min_lon + (grid_lon + 0.5) * self.grid_delta
            
            # Calculate kernel boundaries
            cell_min_lat = min_lat + grid_lat * self.grid_delta
            cell_max_lat = min_lat + (grid_lat + 1) * self.grid_delta
            cell_min_lon = min_lon + grid_lon * self.grid_delta
            cell_max_lon = min_lon + (grid_lon + 1) * self.grid_delta
            
            if (grid_lat, grid_lon) not in grid:
                grid[(grid_lat, grid_lon)] = GridCell(
                    lat=cell_lat,
                    lon=cell_lon,
                    combined_tag="",
                    level=0,
                    kernel_size=1,
                    min_lat=cell_min_lat,
                    max_lat=cell_max_lat,
                    min_lon=cell_min_lon,
                    max_lon=cell_max_lon,
                    x=grid_lat,
                    y=grid_lon
                )
                cells_with_tags += 1
            
            # Add tag to cell (simple concatenation for now)
            if grid[(grid_lat, grid_lon)].combined_tag:
                grid[(grid_lat, grid_lon)].combined_tag += f"; {tag.text}"
            else:
                grid[(grid_lat, grid_lon)].combined_tag = tag.text
        
        # Normalize coordinates so top-left is (0,0)
        if grid:
            min_x = min(cell.x for cell in grid.values())
            min_y = min(cell.y for cell in grid.values())
            
            print(f"   Normalizing coordinates: shifting by (-{min_x}, -{min_y})")
            for cell in grid.values():
                cell.x -= min_x
                cell.y -= min_y
        
        print(f"✅ Created {len(grid)} grid cells with tags")
        print(f"   Cells with tags: {cells_with_tags}")
        print(f"   Empty cells: {grid_lat_cells * grid_lon_cells - cells_with_tags}")
        
        # Count cells with multiple tags
        multi_tag_cells = sum(1 for cell in grid.values() if ';' in cell.combined_tag)
        print(f"   Cells with multiple tags: {multi_tag_cells}")
        
        return grid
    
    async def summarize_cell_tags(self, grid: Dict[Tuple[int, int], GridCell], batch_size: int = 30) -> Dict[Tuple[int, int], GridCell]:
        """Summarize multiple tags within each cell"""
        print(f"\n🔍 Summarizing tags within individual cells...")
        
        # Find cells with multiple tags
        cells_with_multiple_tags = []
        for coord, cell in grid.items():
            if ';' in cell.combined_tag:
                cells_with_multiple_tags.append(cell)
        
        if not cells_with_multiple_tags:
            print("   No cells with multiple tags found")
            return grid
        
        print(f"   Found {len(cells_with_multiple_tags)} cells with multiple tags")
        
        # Process in batches
        total_batches = (len(cells_with_multiple_tags) + batch_size - 1) // batch_size
        
        for batch_idx in range(0, len(cells_with_multiple_tags), batch_size):
            batch = cells_with_multiple_tags[batch_idx:batch_idx + batch_size]
            batch_num = batch_idx // batch_size + 1
            
            print(f"   📦 Processing batch {batch_num}/{total_batches} ({len(batch)} cells)...")
            
            # Create descriptions for cells with multiple tags
            cell_descriptions = []
            for i, cell in enumerate(batch):
                tags = cell.combined_tag.split('; ')
                cell_descriptions.append(f"Cell {i+1} (lat: {cell.lat:.3f}, lon: {cell.lon:.3f}): {', '.join(tags)}")
            
            try:
                print(f"     🔄 Calling {self.summary_provider.__class__.__name__} API...")
                summaries = await self.summary_provider.summarize_batch(cell_descriptions, -1, 1)  # Level -1 for cell-level summarization
                
                # Update cells with summaries
                updated_count = 0
                for i, cell in enumerate(batch):
                    if str(i) in summaries:
                        cell.combined_tag = summaries[str(i)]
                        updated_count += 1
                
                print(f"     ✅ Updated {updated_count}/{len(batch)} cells with summaries")
                
            except Exception as e:
                print(f"     ❌ Error processing batch {batch_num}: {e}")
        
        print(f"✅ Completed cell-level tag summarization")
        return grid
    
    def create_next_level(self, current_level: Dict[Tuple[int, int], GridCell], level_num: int) -> Dict[Tuple[int, int], GridCell]:
        """Create the next hierarchical level from the current level (after summarization)"""
        kernel_size = 2 ** level_num  # 2x2, 4x4, 8x8, etc.
        stride = kernel_size  # Non-overlapping
        
        print(f"   Creating Level {level_num} with {kernel_size}x{kernel_size} kernels (stride: {stride})...")
        
        next_level = {}
        
        # Get grid bounds
        coords = list(current_level.keys())
        min_lat = min(coord[0] for coord in coords)
        max_lat = max(coord[0] for coord in coords)
        min_lon = min(coord[1] for coord in coords)
        max_lon = max(coord[1] for coord in coords)
        
        print(f"     Grid bounds: lat({min_lat}, {max_lat}), lon({min_lon}, {max_lon})")
        
        # Create non-overlapping kernels
        kernels_created = 0
        for start_lat in range(min_lat, max_lat + 1, stride):
            for start_lon in range(min_lon, max_lon + 1, stride):
                # Collect cells in this kernel
                kernel_cells = []
                for i in range(kernel_size):
                    for j in range(kernel_size):
                        coord = (start_lat + i, start_lon + j)
                        if coord in current_level:
                            kernel_cells.append(current_level[coord])
                
                if kernel_cells:
                    # Calculate center
                    center_lat = sum(cell.lat for cell in kernel_cells) / len(kernel_cells)
                    center_lon = sum(cell.lon for cell in kernel_cells) / len(kernel_cells)
                    
                    # Calculate kernel boundaries (min/max from all cells in kernel)
                    kernel_min_lat = min(cell.min_lat for cell in kernel_cells)
                    kernel_max_lat = max(cell.max_lat for cell in kernel_cells)
                    kernel_min_lon = min(cell.min_lon for cell in kernel_cells)
                    kernel_max_lon = max(cell.max_lon for cell in kernel_cells)
                    
                    # Combine SUMMARIZED tags from all cells in kernel
                    combined_tags = []
                    for cell in kernel_cells:
                        if cell.combined_tag:
                            combined_tags.append(cell.combined_tag)
                    
                    combined_tag = "; ".join(combined_tags) if combined_tags else ""
                    
                    # Create new cell with (x,y) coordinates for this level
                    kernel_x = start_lat // stride
                    kernel_y = start_lon // stride
                    kernel_coord = (kernel_x, kernel_y)
                    
                    next_level[kernel_coord] = GridCell(
                        lat=center_lat,
                        lon=center_lon,
                        combined_tag=combined_tag,
                        level=level_num,
                        kernel_size=kernel_size,
                        min_lat=kernel_min_lat,
                        max_lat=kernel_max_lat,
                        min_lon=kernel_min_lon,
                        max_lon=kernel_max_lon,
                        x=kernel_x,
                        y=kernel_y
                    )
                    kernels_created += 1
        
        print(f"     Created {kernels_created} kernels")
        
        # Normalize coordinates so top-left is (0,0) for this level
        if next_level:
            min_x = min(cell.x for cell in next_level.values())
            min_y = min(cell.y for cell in next_level.values())
            
            print(f"     Normalizing Level {level_num} coordinates: shifting by (-{min_x}, -{min_y})")
            for cell in next_level.values():
                cell.x -= min_x
                cell.y -= min_y
        
        return next_level
    
    async def batch_summarize_level(self, level_data: Dict[Tuple[int, int], GridCell], level: int, batch_size: int = 30) -> Dict[Tuple[int, int], GridCell]:
        """Summarize a level using batch GPT API calls"""
        print(f"🤖 Summarizing Level {level}...")
        cells = list(level_data.values())
        kernel_size = 2 ** level if level > 0 else 1
        
        # Filter cells with tags
        cells_with_tags = [cell for cell in cells if cell.combined_tag.strip()]
        
        if not cells_with_tags:
            print(f"   ⚠️  No cells with tags, skipping summarization")
            return level_data
        
        # Batch process (15+ cells per API call)
        total_batches = (len(cells_with_tags) + batch_size - 1) // batch_size
        
        print(f"   📊 Processing {len(cells_with_tags)} cells with tags in {total_batches} batches")
        print(f"   🔧 Kernel size: {kernel_size}x{kernel_size}, Batch size: {batch_size}")
        
        for batch_idx in range(0, len(cells_with_tags), batch_size):
            batch = cells_with_tags[batch_idx:batch_idx + batch_size]
            batch_num = batch_idx // batch_size + 1
            
            print(f"   📦 Processing batch {batch_num}/{total_batches} ({len(batch)} cells)...")
            
            # Create batch descriptions
            cell_descriptions = []
            for i, cell in enumerate(batch):
                cell_descriptions.append(f"Cell {i+1} (lat: {cell.lat:.3f}, lon: {cell.lon:.3f}): {cell.combined_tag}")
            
            try:
                print(f"     🔄 Calling {self.summary_provider.__class__.__name__} API...")
                summaries = await self.summary_provider.summarize_batch(cell_descriptions, level, kernel_size)
                
                # Update cells with summaries
                updated_count = 0
                for i, cell in enumerate(batch):
                    if str(i) in summaries:
                        cell.combined_tag = summaries[str(i)]
                        updated_count += 1
                
                print(f"     ✅ Updated {updated_count}/{len(batch)} cells with summaries")
                
            except Exception as e:
                print(f"     ❌ Error processing batch {batch_num}: {e}")
        
        print(f"✅ Completed summarization for Level {level}")
        return level_data
    
    
    def save_results(self, levels: Dict[int, Dict[Tuple[int, int], GridCell]], output_file: str):
        """Save results to JSON file"""
        results = {
            "metadata": {
                "grid_delta": self.grid_delta,
                "total_levels": len(levels)
            },
            "levels": {}
        }
        
        for level, level_data in levels.items():
            level_info = {}
            for coord, cell in level_data.items():
                # Use (x,y) coordinates as key
                key = f"{cell.x}_{cell.y}"
                level_info[key] = {
                    "kernel_boundaries": {
                        "min_lat": cell.min_lat,
                        "max_lat": cell.max_lat,
                        "min_lon": cell.min_lon,
                        "max_lon": cell.max_lon
                    },
                    "combined_tag": cell.combined_tag
                }
            results["levels"][str(level)] = level_info
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to {output_file}")

async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Hierarchical Grid Summarizer')
    parser.add_argument('json_path', help='Path to JSON data file')
    parser.add_argument('--output', '-o', default='hierarchical_results.json', help='Output file path')
    parser.add_argument('--api-key', help='OpenAI API key (or set OPENAI_API_KEY env var)')
    parser.add_argument('--grid-delta', '-d', type=float, default=0.01, help='Grid cell size (default: 0.01)')
    parser.add_argument('--min-lat', type=float, help='Minimum latitude for custom boundaries')
    parser.add_argument('--max-lat', type=float, help='Maximum latitude for custom boundaries')
    parser.add_argument('--min-lon', type=float, help='Minimum longitude for custom boundaries')
    parser.add_argument('--max-lon', type=float, help='Maximum longitude for custom boundaries')
    parser.add_argument('--provider', choices=['openai', 'gemini'], default='openai', help='LLM provider to use (default: openai)')
    parser.add_argument('--batch-size', type=int, default=30, help='Batch size for API calls (default: 15)')
    
    args = parser.parse_args()
    
    print("🚀 Starting Hierarchical Grid Summarizer")
    print("=" * 50)
    
    # Initialize summarizer
    summarizer = HierarchicalGridSummarizer(
        api_key=args.api_key, 
        grid_delta=args.grid_delta, 
        provider_type=args.provider
    )
    
    # Step a) Load data
    print("\n📋 Step a) Loading data...")
    tags = summarizer.load_data(args.json_path)
    
    # Step b) Define boundaries
    print("\n📍 Step b) Defining boundaries...")
    custom_boundaries = None
    if all([args.min_lat, args.max_lat, args.min_lon, args.max_lon]):
        custom_boundaries = (args.min_lat, args.max_lat, args.min_lon, args.max_lon)
        print("   Using custom boundaries provided via command line")
    else:
        print("   Using automatic boundary calculation from data")
    
    boundaries = summarizer.define_boundaries(tags, custom_boundaries)
    
    # Step c) Create base grid and combine tags
    print("\n🔲 Step c) Creating base grid and combining tags...")
    base_grid = summarizer.create_base_grid(tags, boundaries)
    
    # Step c.1) Summarize tags within individual cells
    print("\n🔍 Step c.1) Summarizing tags within individual cells...")
    base_grid = await summarizer.summarize_cell_tags(base_grid, batch_size=args.batch_size)
    
    # Step d) Create hierarchical levels progressively
    print("\n🏗️  Step d) Creating hierarchical levels progressively...")
    levels = {0: base_grid}
    current_level = base_grid
    level_num = 1
    
    print(f"   Level 0: {len(current_level)} cells (base level)")
    
    # Step e) Summarize and create next level iteratively
    print("\n🤖 Step e) Summarizing and creating levels iteratively...")
    while len(current_level) > 1:
        # First summarize the current level
        print(f"\n🤖 Summarizing Level {level_num - 1}...")
        current_level = await summarizer.batch_summarize_level(current_level, level_num - 1, args.batch_size)
        levels[level_num - 1] = current_level
        
        # Then create the next level using summarized tags
        print(f"\n🏗️  Creating Level {level_num} from summarized Level {level_num - 1}...")
        next_level = summarizer.create_next_level(current_level, level_num)
        
        if next_level:
            levels[level_num] = next_level
            current_level = next_level
            level_num += 1
        else:
            print(f"   No kernels created, stopping hierarchy")
            break
    
    # Summarize the final level
    if len(current_level) > 0:
        print(f"\n🤖 Summarizing final Level {level_num - 1}...")
        current_level = await summarizer.batch_summarize_level(current_level, level_num - 1, args.batch_size)
        levels[level_num - 1] = current_level
    
    print(f"\n✅ Created {len(levels)} hierarchical levels")
    for level, level_data in levels.items():
        kernel_size = 2 ** level if level > 0 else 1
        print(f"   Level {level}: {len(level_data)} cells (kernel: {kernel_size}x{kernel_size})")
    
    # Save results
    print("\n💾 Saving results...")
    summarizer.save_results(levels, args.output)
    
    print("\n🎉 Hierarchical grid summarization complete!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
