import os
import json
import csv
from pathlib import Path
from datetime import datetime


# Saves the whole working tree in "logs", so that I can see what data I need to re-download from Stooq to set this up again
# Vibe-coded with Claude Sonnet 4.5

# Actually, you should just use "find ." or "find . -type f" for files specifically. This is a terminal command that will aid you here.
# Way less resource intensive... let's not get carried away here.


def scan_directory_tree(root_path='.', output_format='both', exclude_dirs=None):
    """
    Recursively scan a directory tree and save all files and folders.
    
    Args:
        root_path (str): The root directory to scan (default: current directory)
        output_format (str): 'csv', 'json', or 'both' (default: 'both')
        exclude_dirs (list): List of directory names to skip (default: None)
    
    Returns:
        tuple: (list of file/folder info, json_filename, csv_filename)
    """
    root_path = Path(root_path).resolve()
    
    # Default exclusions if none provided
    if exclude_dirs is None:
        exclude_dirs = []
    
    # Create logs directory if it doesn't exist
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Collect all files and directories
    items = []
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Remove excluded directories from dirnames in-place to prevent os.walk from entering them
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        dirpath = Path(dirpath)
        relative_path = dirpath.relative_to(root_path)
        
        # Add directories
        for dirname in dirnames:
            full_path = dirpath / dirname
            items.append({
                'type': 'directory',
                'name': dirname,
                'relative_path': str(relative_path / dirname),
                'absolute_path': str(full_path),
                'size_bytes': None,
                'modified_time': datetime.fromtimestamp(full_path.stat().st_mtime).isoformat()
            })
        
        # Add files
        for filename in filenames:
            full_path = dirpath / filename
            try:
                stat_info = full_path.stat()
                items.append({
                    'type': 'file',
                    'name': filename,
                    'relative_path': str(relative_path / filename),
                    'absolute_path': str(full_path),
                    'size_bytes': stat_info.st_size,
                    'modified_time': datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                })
            except (OSError, PermissionError) as e:
                print(f"Warning: Could not access {full_path}: {e}")
    
    # Generate output filenames with timestamp in logs directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_filename = logs_dir / f'directory_tree_{timestamp}.json'
    csv_filename = logs_dir / f'directory_tree_{timestamp}.csv'
    
    # Save to JSON
    if output_format in ['json', 'both']:
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'scan_time': datetime.now().isoformat(),
                'root_directory': str(root_path),
                'total_items': len(items),
                'items': items
            }, f, indent=2)
        print(f"JSON file saved: {json_filename}")
    
    # Save to CSV
    if output_format in ['csv', 'both']:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            if items:
                writer = csv.DictWriter(f, fieldnames=items[0].keys())
                writer.writeheader()
                writer.writerows(items)
        print(f"CSV file saved: {csv_filename}")
    
    print(f"\nTotal items scanned: {len(items)}")
    print(f"Files: {sum(1 for item in items if item['type'] == 'file')}")
    print(f"Directories: {sum(1 for item in items if item['type'] == 'directory')}")
    
    return items, str(json_filename) if output_format in ['json', 'both'] else None, \
           str(csv_filename) if output_format in ['csv', 'both'] else None


if __name__ == '__main__':
    # Example usage: scan current directory and save to both formats
    # Exclude common directories like node_modules, .git, __pycache__, etc.
    scan_directory_tree('.', output_format='both', exclude_dirs=['node_modules', '.git', '__pycache__', 'venv', '.venv'])
    
    # Other usage examples:
    # scan_directory_tree('/path/to/directory', output_format='json', exclude_dirs=['build', 'dist'])
    # scan_directory_tree('.', output_format='csv', exclude_dirs=[])  # No exclusions
