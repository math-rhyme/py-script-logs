import io
import pytest
import sys
import main
from main import (average_display, average_process_file, average_report, validate_date, process_everything, REPORTS)
from types import SimpleNamespace

LOG_LINES = [
    '{"@timestamp": "2025-06-22T12:00:00", "status": 200, "url": "/api/home", "request_method": "GET", "response_time": 0.1, "http_user_agent": "..."}\n',
    '{"@timestamp": "2025-06-22T12:01:00", "status": 200, "url": "/api/home", "request_method": "GET", "response_time": 0.2, "http_user_agent": "..."}\n',
    '{"@timestamp": "2025-06-23T12:01:00", "status": 200, "url": "/api/about", "request_method": "GET", "response_time": 0.3, "http_user_agent": "..."}\n',
]

# *************************************************
# AUXILARY FUNCTIONS

# function: validate_date
# test cases:
#   1. good +
#   2. okay +
#   3. bad +
#   4. edge +

def test_validate_date():
    assert validate_date("2025-06-22") is True
    assert validate_date("2025-6-22") is True
    assert validate_date("random_string") is False
    assert validate_date("") is False

# function: register_report_type
# test cases:
#   1. `average` registerd ? +

def test_register_report_type_decorator_registers_correctly():
    assert "average" in REPORTS
    func = REPORTS["average"]
    assert callable(func)


# *************************************************
# CL ARGUMENTS FUNCTIONS

# function: process_everything
# test cases:
#   1. good +
#   2. file param err +
#   3. report param err +
#   4. report param err +
#   5. date param err +

def test_process_everything_valid(monkeypatch, tmp_path, capsys):
    file_path = tmp_path / "logfile.log"
    file_path.write_text("".join(LOG_LINES))
    args = SimpleNamespace(file=[str(file_path)],report=["average"],date="2025-06-22")
    process_everything(args)
    captured = capsys.readouterr()
    assert "/api/home" in captured.out
    assert "/api/about" not in captured.out

def test_process_everything_missing_file():
    args = SimpleNamespace(file=None, report=["average"], date=None)
    with pytest.raises(ValueError) as e:
        process_everything(args)
    assert "at least one file" in str(e.value)

def test_process_everything_missing_report():
    args = SimpleNamespace(file=["somelog.log"], report=None, date=None)
    with pytest.raises(ValueError) as e:
        process_everything(args)
    assert "at least one report" in str(e.value)

def test_process_everything_unknown_report():
    args = SimpleNamespace(file=["somelog.log"], report=["random_report_we_dont_have"], date=None)
    with pytest.raises(ValueError) as e:
        process_everything(args)
    assert "Unknown report type" in str(e.value)

def test_process_everything_invalid_date():
    args = SimpleNamespace(file=["somelog.log"], report=["average"], date="not_even_a_date")
    with pytest.raises(ValueError) as e:
        process_everything(args)
    assert "Invalid date format" in str(e.value)


# *************************************************
# AVERAGE REPOSRT FUNCTIONS

# function: average_display
# test cases:
#   1. good data +
#   2. no data +
#   3. filtered +
#   4. no filter +

def test_average_display_with_data():
    report_dict = {"/api/home": [2, 0.3], "/api/about": [1, 0.3],}
    output = average_display(report_dict)
    assert "header" in output
    assert output.index("/api/home") < output.index("/api/about")
    assert "0.150" in output

def test_average_display_no_data():
    assert "No data to display" in average_display({})

def test_average_process_file_date_filter():
    fake_file = io.StringIO("".join(LOG_LINES))
    report_dict = {}
    average_process_file(fake_file, report_dict, date="2025-06-22")
    assert "/api/home" in report_dict
    assert "/api/about" not in report_dict
    assert report_dict["/api/home"][0] == 2
    assert abs(report_dict["/api/home"][1] - 0.3) < 1e-6

def test_average_process_file_no_date_filter():
    fake_file = io.StringIO("".join(LOG_LINES))
    report_dict = {}
    average_process_file(fake_file, report_dict, date=None)
    assert "/api/home" in report_dict
    assert "/api/about" in report_dict
    assert report_dict["/api/about"][0] == 1

# function: average_report
# test cases:
#   1. good +
#   2. file error +

def test_average_report(tmp_path, capsys):
    file_path = tmp_path / "logfile.log"
    file_path.write_text("".join(LOG_LINES))
    output = average_report([str(file_path)], date="2025-06-22")
    assert "header" in output
    assert "/api/home" in output
    assert "/api/about" not in output

def test_average_report_file_not_found(capsys):
    output = average_report(["logdoesnotexist.log"], date=None)
    captured = capsys.readouterr()
    assert "not found" in captured.err

