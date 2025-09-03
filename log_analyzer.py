import re
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import argparse
from colorama import Fore, Style, init
from tabulate import tabulate
import os
os.system('clear')

init(autoreset=True)

COLOR_MAP = {
    "RED": Fore.RED,
    "MAGENTA": Fore.MAGENTA,
    "YELLOW": Fore.YELLOW,
    "WHITE": Fore.WHITE,
    "GREEN": Fore.GREEN,
    "BLUE": Fore.BLUE,
    "CYAN": Fore.CYAN,
    "RESET": Style.RESET_ALL
}

def load_patterns(patterns_file):
    with open(patterns_file, 'r') as f:
        data = json.load(f)
    compiled_patterns = {}
    for label, info in data.items():
        compiled_patterns[label] = {
            "pattern": re.compile(info['pattern']),
            "color": COLOR_MAP.get(info.get('color', 'WHITE').upper(), Fore.WHITE),
            "severity": info.get('severity', 'normal').lower()
        }
    return compiled_patterns

def parse_log_file(file_path, patterns):
    log_entries = []
    with open(file_path, 'r') as file:
        for line in file:
            matched_event = None
            extracted_groups = {}
            for label, info in patterns.items():
                match = info['pattern'].search(line)
                if match:
                    matched_event = label
                    extracted_groups = match.groupdict()
                    break
            
            timestamp_str = " ".join(line.split()[:3])
            try:
                timestamp = datetime.strptime(timestamp_str + f" {datetime.now().year}", "%b %d %H:%M:%S %Y")
            except Exception:
                timestamp = None
            
            if matched_event is None:
                log_entries.append({
                    'timestamp': timestamp,
                    'event': 'Normal log',
                    'log': line.strip(),
                    'color': Fore.WHITE,
                    'severity': 'normal',
                    'ip': 'N/A',
                    'user': 'N/A',
                    'port': 'N/A'
                })
            else:
                ip = extracted_groups.get('ip', 'N/A')
                user = extracted_groups.get('user', 'N/A')
                port = extracted_groups.get('port', 'N/A')

                log_entries.append({
                    'timestamp': timestamp,
                    'event': matched_event,
                    'log': line.strip(),
                    'color': patterns[matched_event]['color'],
                    'severity': patterns[matched_event]['severity'],
                    'ip': ip,
                    'user': user,
                    'port': port
                })
    return pd.DataFrame(log_entries)

def save_report(df, output_path):
    df_sorted = df.sort_values(by='timestamp', na_position='last')
    df_sorted.to_csv(output_path, index=False)
    print(f"[+] Report saved to: {output_path}")

def print_logs(df, show_all=False):
    df_sorted = df.sort_values(by='timestamp', na_position='last')
    if not show_all:
        df_sorted = df_sorted[df_sorted['severity'] != 'normal']

    headers = ["Timestamp", "Event", "User", "IP", "Port", "Log"]
    table_data = []
    for _, row in df_sorted.iterrows():
        ts = ""
        if pd.notna(row['timestamp']):
            try:
                ts = row['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                ts = str(row['timestamp'])
        color = row['color']
        severity = row['severity']

        if severity in ('normal', 'info') and show_all:
            table_data.append([
                ts, row['event'], row['user'], row['ip'], row['port'], row['log']
            ])
        elif severity not in ('normal', 'info'):
            table_data.append([
                color + ts + Style.RESET_ALL,
                color + row['event'] + Style.RESET_ALL,
                color + row['user'] + Style.RESET_ALL,
                color + row['ip'] + Style.RESET_ALL,
                color + row['port'] + Style.RESET_ALL,
                color + row['log'] + Style.RESET_ALL,
            ])

    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def main():
    parser = argparse.ArgumentParser(
        #description="🔍 Log analyzer with event highlighting and optional report generation.",
        usage="python log_analyzer.py <file.log> [-option]",
        epilog="Example: python log_analyzer.py /var/log/auth.log -a"
    )
    parser.add_argument("logfile", help="Path to the log file to be analyzed")
    parser.add_argument("-r", "--report", action="store_true", help="Save a CSV report with detected events")
    parser.add_argument("-a", "--all", action="store_true", help="Include all log lines, even normal ones")

    args = parser.parse_args()

    log_path = Path(args.logfile)
    if not log_path.exists():
        print("[!] Log file not found.")
        return

    patterns_path = Path(__file__).parent / "patterns" / "default.json"
    if not patterns_path.exists():
        print("[!] Default pattern file not found in ./patterns/default.json")
        return

    print(f"[*] Loading patterns from: {patterns_path}")
    patterns = load_patterns(patterns_path)

    print(f"[*] Analyzing: {log_path}")
    df = parse_log_file(log_path, patterns)

    if df.empty:
        print("[!] No events found.")
    else:
        print_logs(df, show_all=args.all)

        if args.report:
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            output_path = reports_dir / (log_path.stem + "_report.csv")
            save_report(df, output_path)

if __name__ == "__main__":
    main()
