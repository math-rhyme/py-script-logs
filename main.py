import argparse
import json
import tabulate
import sys
from datetime import datetime

REPORTS = {}

def register_report_type(name):
    def decorator(func):
        REPORTS[name] = func
        return func
    return decorator


def average_display(report_dict):
    if not report_dict:
        return "No data to display for your request."

    rows = []
    for key, values in report_dict.items():
        total = values[0]
        avg_response_time = values[1] / total if total else 0
        rows.append([key, total, avg_response_time])

    rows_sorted = sorted(rows, key=lambda x: x[1], reverse=True)
    headers = ["header", "total", "avg_response_time"]

    table_output = tabulate.tabulate(rows_sorted, headers=headers, showindex=True,tablefmt="github",floatfmt=".3f")
    return table_output


def average_process_file(f, report_dict, date):
    for line in f:
        data = json.loads(line)
        timestamp = data.get('@timestamp')
        record_date = ''
        if timestamp:
            record_date = timestamp.split('T')[0]
        if (date is None) or (date == record_date):
            url = data["url"]
            if url not in report_dict:
                report_dict[url] = [1, data["response_time"]]
            else:
                report_dict[url][0] +=1
                report_dict[url][1] += data["response_time"]


@register_report_type('average')
def average_report(files, date):
    report_dict = {}
    for file_path in files:
        try:
            with open(file_path, 'r') as f:
                average_process_file(f, report_dict, date)
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        except Exception as e:
            print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
    return average_display(report_dict)



def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def process_everything(args):
    if not args.file:
        raise ValueError("Please, add at least one file with --file.")
    if not args.report:
        raise ValueError("Please, add at least one report type with --report.")
    if args.date and not validate_date(args.date):
        raise ValueError(f"Invalid date format: {args.date}. Please, use YYYY-MM-DD.")
    
    files = args.file
    date = args.date

    for report_name in args.report:
        if report_name in REPORTS:
            output = REPORTS[report_name](files, date)
            print(output)
        else:
            raise ValueError(f"Unknown report type: {report_name}.\nPlease, use one of these: {', '.join(sorted(REPORTS.keys()))}.")



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', nargs='+', type=str, help='Input file names')
    parser.add_argument('-r', '--report', nargs='+', type=str, help='Input type(s) of report(s)')
    parser.add_argument('-d', '--date', type=str, help='Date filter in YYYY-MM-DD')
    args = parser.parse_args()

    try:
        process_everything(args)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)