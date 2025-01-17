LogParser - Log Analysis Tool
===================================

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

Usage:
------
python3 logparser.py --log <logfile1> [--log <logfile2> ...] --keywords <keywords_file> [--chrono]

Arguments:
  --log        Path to log file(s). Can be specified multiple times and supports wildcards
               Example: --log /var/log/*.log --log /var/log/syslog*
  --keywords   Path to keywords definition file
  --chrono     Optional: Sort all matching lines chronologically across all log files

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
