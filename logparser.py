#!/usr/bin/env python3
"""
LogParser - Log Analysis Tool
===================================
Author: https://github.com/Vince-0
This script parses log files to identify and report specific keywords and their associated
contexts.

Features:
---------
- Multiple log file support: Can process multiple log files in a single run
- Wildcard support: Accepts * wildcard patterns for log file paths
- Keyword mapping: Uses a separate keywords file to map keywords to their descriptions
- Flexible input: Handles various log file formats
- Error handling: Validates file existence and permissions before processing
- Chronological sorting: Optional strict chronological sorting across all log files combined

Advanced Features:
----------------
1. Timestamp Parsing:
   Supports multiple timestamp formats commonly found in system logs:
   - Detailed formats with milliseconds: 2025-01-15 23:39:16,366 GMT+0000
   - ISO 8601: 2025-01-15T23:39:16.366Z
   - Syslog format: Jan 15 23:39:16
   - Apache/NGINX: 15/Jan/2025:23:39:16 +0000
   - Unix date: Wed Jan 15 23:39:16 2025
   - Alternative formats: 2025/01/15 23:39:16, 15-Jan-2025 23:39:16
   - Short formats (assumes current year): Jan 15 23:39:16
   - Unix timestamps: 1579127956

2. Output Formatting:
   - File name displayed when first match is found in each file
   - Clear separation between matches using horizontal lines
   - Structured output with description and log entry pairs
   - Optional chronological sorting across all input files
   - Optional matched lines output only without readability formatting
   - Optional keyword matches into csv output files

Usage:
------
python3 logparser.py --log <logfile1> [--log <logfile2> ...] --keywords <keywords_file> [--chrono]

Arguments:
  --log          Path to log file(s). Can be specified multiple times and supports wildcards
                 Example: --log /var/log/*.log --log /var/log/syslog*
  --keywords     Path to keywords definition file
  --chrono       Optional: Sort all matching lines chronologically across all log files
  --matchonly    Optional: Output only the matched log lines without formatting
  --keywordfiles Optional: Output matches for each keyword to separate CSV files

Keywords File Format:
-------------------
The keywords file should contain lines in the format:
<description>:<keyword>

Example:
#Description1:keywords go here
#Description2:more things to match

Output Format:
-------------
Standard Output:
1. List of loaded keywords and their descriptions
2. File name on first match in each file
3. For each matched keyword:
   - Description of the keyword
   - Complete log line containing the keyword
   - Separator line for clarity

Chronological Output - optional (--chrono):
1. All matches from all input files are merged and sorted by timestamp
2. File source is shown for each match
3. For each match in time order:
   - Description of the keyword
   - Complete log line
   - Separator line
4. Lines without valid timestamps are treated as earliest possible time
5. Strict chronological order is maintained across all input files

Keyword Output - optional (--keywordfiles):
Creates separate CSV files for each keyword matched:

#Keyword1_matches.csv
#Keyword2_matches.csv

Each file contains only the lines matching that specific keyword

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
    parser.add_argument("--matchonly", action="store_true", help="Output only matched log lines")
    parser.add_argument("--keywordfiles", action="store_true", help="Output matches for each keyword to separate CSV files")
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
    Parse timestamp from log line.
    Returns datetime object if successful, None if no timestamp found.
    """
    try:
        # CSV style dd/MM/yyyy HH:mm:ss tt format
        if ',' in line:
            parts = line.split(',')
            if len(parts) >= 4:  # Connected field is the 4th column
                timestamp_str = parts[3].strip()
                return datetime.datetime.strptime(timestamp_str, "%d/%m/%Y %I:%M:%S %p")
        
        # Standard log formats
        formats = [
            "%Y-%m-%d %H:%M:%S,%f",          # 2025-01-15 23:39:16,366
            "%Y-%m-%dT%H:%M:%S.%fZ",         # 2025-01-15T23:39:16.366Z
            "%b %d %H:%M:%S %Y",             # Jan 15 23:39:16 2025
            "%d/%b/%Y:%H:%M:%S %z",          # 15/Jan/2025:23:39:16 +0000
            "%a %b %d %H:%M:%S %Y",          # Wed Jan 15 23:39:16 2025
            "%Y/%m/%d %H:%M:%S",             # 2025/01/15 23:39:16
            "%d-%b-%Y %H:%M:%S",             # 15-Jan-2025 23:39:16
            "%b %d %H:%M:%S",                # Jan 15 23:39:16
        ]
        
        # Try each format
        first_part = ' '.join(line.split()[:6])
        for fmt in formats:
            try:
                return datetime.datetime.strptime(first_part, fmt)
            except ValueError:
                continue
                
        return None
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

def search_log_files(log_files, keyword_comment_map, chronological=False, matchonly=False, keywordfiles=False):
    """
    Search log files for keywords and output matches.
    If chronological is True, sort all matches by timestamp before output.
    If matchonly is True, only output the matched log lines.
    If keywordfiles is True, output matches for each keyword to separate CSV files.
    """
    if keywordfiles:
        matches = collect_matches(log_files, keyword_comment_map)
        write_keyword_files(matches, keyword_comment_map)
        return

    if matchonly:
        if chronological:
            matches = collect_matches(log_files, keyword_comment_map)
            for match in matches:
                print(match['line'])
        else:
            for log_file in log_files:
                if not os.path.isfile(log_file) or not os.access(log_file, os.R_OK):
                    continue
                with open(log_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        for keyword in keyword_comment_map:
                            if keyword in line:
                                print(line)
    elif chronological:
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

def write_keyword_files(matches, keyword_comment_map):
    """
    Write matches to separate files for each keyword.
    """
    # Create a dictionary to store matches for each keyword
    keyword_matches = {keyword: [] for keyword in keyword_comment_map.keys()}
    
    # Collect matches for each keyword
    for match in matches:
        for keyword in keyword_comment_map.keys():
            if keyword in match['line']:
                keyword_matches[keyword].append(match['line'])
    
    # Write each keyword's matches to a separate file
    for keyword, lines in keyword_matches.items():
        if lines:  # Only create file if there are matches
            filename = f"{keyword}_matches.csv"
            print(f"Writing {len(lines)} matches for keyword '{keyword}' to {filename}")
            with open(filename, 'w') as f:
                for line in lines:
                    f.write(line + '\n')

def main():
    args = parse_arguments()
    log_files = expand_log_paths(args.log)
    if not log_files:
        print("Error: No log files found matching the provided patterns")
        return
    
    keyword_comment_map = read_keywords(args.keywords)
    search_log_files(log_files, keyword_comment_map, args.chrono, args.matchonly, args.keywordfiles)

if __name__ == "__main__":
    main()
