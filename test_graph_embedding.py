#!/usr/bin/env python3
"""
Test script to verify graph embedding functionality
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_graph_embedding():
    """Test the graph embedding functionality"""
    
    print("🧪 Testing Graph Embedding Functionality")
    print("=" * 50)
    
    # Check if consolidated analysis folder exists
    if not os.path.exists("consolidated_analysis"):
        print("❌ consolidated_analysis folder not found!")
        print("Please run database analysis first.")
        return False
    
    # Check for markdown files
    md_files = []
    for file in os.listdir("consolidated_analysis"):
        if file.endswith("_consolidated_analysis.md"):
            md_files.append(file)
    
    if not md_files:
        print("❌ No consolidated analysis markdown files found!")
        print("Please run database analysis first.")
        return False
    
    print(f"✅ Found {len(md_files)} consolidated analysis file(s):")
    for file in md_files:
        print(f"   - {file}")
    
    # Check for graph folders
    graph_folders = []
    for item in os.listdir("consolidated_analysis"):
        item_path = os.path.join("consolidated_analysis", item)
        if os.path.isdir(item_path) and item.endswith("_graphs"):
            graph_folders.append(item)
    
    if not graph_folders:
        print("⚠️  No graph folders found in consolidated_analysis!")
        print("This might mean no graphs were generated or embedding failed.")
    else:
        print(f"✅ Found {len(graph_folders)} graph folder(s):")
        for folder in graph_folders:
            folder_path = os.path.join("consolidated_analysis", folder)
            graph_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
            print(f"   - {folder}: {len(graph_files)} graph(s)")
    
    # Check markdown content for image references
    print("\n📄 Checking markdown files for image embedding...")
    for md_file in md_files:
        md_path = os.path.join("consolidated_analysis", md_file)
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for image syntax
        if "![" in content and "](" in content:
            print(f"   ✅ {md_file}: Contains image references")
            
            # Count images
            image_count = content.count("![")
            print(f"      📊 Found {image_count} image reference(s)")
        else:
            print(f"   ❌ {md_file}: No image references found")
    
    print("\n🎯 Summary:")
    print(f"   - Markdown files: {len(md_files)}")
    print(f"   - Graph folders: {len(graph_folders)}")
    
    if graph_folders:
        print("   ✅ Graph embedding appears to be working!")
    else:
        print("   ⚠️  Graph embedding may not be working properly.")
        print("   💡 Try running database analysis again.")
    
    return True

if __name__ == "__main__":
    test_graph_embedding()
