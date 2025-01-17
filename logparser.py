#!/usr/bin/env python3
"""
LogParser - Network Log Analysis Tool
===================================

This script parses network log files to identify and report specific keywords and their associated
contexts.

Features:
---------
- Multiple log file support: Can process multiple log files in a single run
- Wildcard support: Accepts * wildcard patterns for log file paths
- Keyword mapping: Uses a separate keywords file to map keywords to their descriptions
- Flexible input: Handles various log file formats
- Error handling: Validates file existence and permissions before processing
- Chronological sorting: Optional strict chronological sorting across all log files combined

Usage:
------
python3 logparser8.py --log <logfile1> [--log <logfile2> ...] --keywords <keywords_file> [--chrono]

Arguments:
  --log        Path to log file(s). Can be specified multiple times and supports wildcards
               Example: --log /var/log/*.log --log /var/log/syslog*
  --keywords   Path to keywords definition file
  --chrono     Optional: Sort all matching lines chronologically across all log files

Output Format:
-------------
Standard Output:
1. List of loaded keywords and their descriptions
2. File name on first match in each file
3. For each matched keyword:
   - Description of the keyword
   - Complete log line containing the keyword
   - Separator line for clarity

Chronological Output (--chrono):
1. All matches from all input files are merged and sorted by timestamp
2. File source is shown for each match
3. For each match in time order:
   - Description of the keyword
   - Complete log line
   - Separator line
4. Lines without valid timestamps are treated as earliest possible time
5. Strict chronological order is maintained across all input files

Error Handling:
--------------
- Validates existence and readability of all input files
- Reports malformed lines in the keywords file
- Handles missing or malformed timestamps gracefully
- Continues processing remaining files if one file has an error
- Reports invalid wildcard patterns

Dependencies:
------------
- Python 3.x
- Standard library modules: argparse, os, collections.defaultdict, glob, datetime
"""

import argparse
import os
import glob
import datetime
from collections import defaultdict

def parse_arguments():
    parser = argparse.ArgumentParser(description="Parse log files for keywords")
    parser.add_argument("--log", action="append", help="Path to log file (supports wildcards)", required=True)
    parser.add_argument("--keywords", help="Path to keywords file", required=True)
    parser.add_argument("--chrono", action="store_true", help="Sort matches chronologically")
    return parser.parse_args()

def expand_log_paths(log_patterns):
    """
    Expands wildcard patterns in log file paths and returns a list of matching files.
    """
    log_files = []
    for pattern in log_patterns:
        matched_files = glob.glob(pattern)
        if not matched_files:
            print(f"Warning: No files found matching pattern '{pattern}'")
        log_files.extend(matched_files)
    return log_files

def read_keywords(keywords_file):
    keyword_comment_map = defaultdict(str)
    with open(keywords_file, 'r') as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) == 2:
                comment, keyword = map(str.strip, parts)
                keyword_comment_map[keyword] = comment
                print(f"Keyword: {keyword}, Comment: {comment}")
            else:
                print(f"Invalid line in keywords file: {line.strip()}")
    return keyword_comment_map

def parse_timestamp(line):
    """
    Parse timestamp from log line, focusing on the exact format found in the logs:
    2025-01-16 07:01:46,964 GMT+0000
    """
    try:
        # Extract timestamp before GMT
        timestamp_part = line.split(" GMT")[0]
        # Convert comma to period for milliseconds
        timestamp_part = timestamp_part.replace(",", ".")
        # Parse the timestamp
        return datetime.datetime.strptime(timestamp_part, "%Y-%m-%d %H:%M:%S.%f")
    except (ValueError, IndexError):
        return None

def collect_matches(log_files, keyword_comment_map):
    """
    Collect all matches from all files with their timestamps and source files.
    Returns: list of (timestamp, comment, line, source_file) tuples
    """
    matches = []
    min_datetime = datetime.datetime.min
    
    for log_file in log_files:
        if not os.path.isfile(log_file) or not os.access(log_file, os.R_OK):
            print(f"Error: Log file '{log_file}' not found or not readable.")
            continue

        with open(log_file, 'r') as f:
            for line in f:
                line = line.strip()
                for keyword in keyword_comment_map:
                    if keyword in line:
                        timestamp = parse_timestamp(line)
                        if timestamp is None:
                            timestamp = min_datetime
                        matches.append({
                            'timestamp': timestamp,
                            'comment': keyword_comment_map[keyword],
                            'line': line,
                            'file': log_file
                        })
    
    # Sort all matches by timestamp
    matches.sort(key=lambda x: x['timestamp'])
    return matches

def search_log_files(log_files, keyword_comment_map, chronological=False):
    """
    Search log files for keywords and output matches.
    If chronological is True, sort all matches by timestamp before output.
    """
    if chronological:
        # Collect and sort all matches from all files
        matches = collect_matches(log_files, keyword_comment_map)
        
        if matches:
            print("\nMatches in chronological order:")
            current_file = None
            
            for match in matches:
                # Print file header if it's from a new file
                if match['file'] != current_file:
                    print(f"\nFrom file: {match['file']}")
                    current_file = match['file']
                
                print(f"\nDescription: {match['comment']}")
                print(f"Log entry: {match['line']}")
                print("-" * 80)
    else:
        # Original file-by-file output
        print("Occurrences of keywords in log files:")
        for log_file in log_files:
            if not os.path.isfile(log_file):
                print(f"Error: Log file '{log_file}' not found.")
                continue
            if not os.access(log_file, os.R_OK):
                print(f"Error: Log file '{log_file}' is not readable.")
                continue

            file_header_shown = False
            with open(log_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    for keyword in keyword_comment_map:
                        if keyword in line:
                            if not file_header_shown:
                                print(f"\nFrom file: {log_file}")
                                file_header_shown = True
                            print(f"\nDescription: {keyword_comment_map[keyword]}")
                            print(f"Log entry: {line}")
                            print("-" * 80)

def main():
    args = parse_arguments()
    log_files = expand_log_paths(args.log)
    if not log_files:
        print("Error: No log files found matching the provided patterns")
        return
    
    keyword_comment_map = read_keywords(args.keywords)
    search_log_files(log_files, keyword_comment_map, args.chrono)

if __name__ == "__main__":
    main()
