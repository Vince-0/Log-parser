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
- Supports multiple timestamp formats commonly found in system logs:
   - Detailed formats with milliseconds: 2025-01-15 23:39:16,366 GMT+0000
   - ISO 8601: 2025-01-15T23:39:16.366Z
   - Syslog format: Jan 15 23:39:16
   - Apache/NGINX: 15/Jan/2025:23:39:16 +0000
   - Unix date: Wed Jan 15 23:39:16 2025
   - Alternative formats: 2025/01/15 23:39:16, 15-Jan-2025 23:39:16
   - Short formats (assumes current year): Jan 15 23:39:16
   - Unix timestamps: 1579127956

- Output Formatting:
   - List of loaded keywords and their descriptions
   - File name displayed when first match is found in each file
   - For each matched keyword:
     - Description of the keyword
     - Complete log line containing the keyword
     - Separator line for clarity
   - Optional chronological sorting across all input files
   - Optional matched lines output only without readability formatting
   - Optional keyword matches into individual csv output files

Usage:
------
python3 logparser.py --log <logfile1> [--log <logfile2> ...] --keywords <keywords_file> [--chrono]

Arguments:

  --log        
  
  Path to log file(s). Can be specified multiple times and supports wildcards
               Example: --log /var/log/*.log --log /var/log/syslog\*
               
  --keywords   
  
  Path to keywords definition file
  
  --chrono     
  
  Optional: Sort all matching lines chronologically across all log files
  
  --matchonly    
  
  Optional: Output only the matched log lines without formatting
    
  --keywordfiles 
  
  Optional: Output matches for each keyword to separate CSV files

Keywords File Format:
-------------------
The keywords file should contain lines in the format:

#description:keyword1 keyword2

Example:

#Description1:keywords to match go here

#Description2:more things to match

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

To Do:
------------
- Add local timezone stamps
- Add comment/disable tags to ignore keywords 
