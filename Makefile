
help:
	@echo "\n\n**********************"
	@echo "Makefile commands:\n"
	@echo "\tinstall    - Install dependencies from requirements.txt"
	@echo "\trun        - Run the program with example log files and average report"
	@echo "\ttest       - Run tests with pytest and coverage"
	@echo "\tclean      - Remove __pycache__ directory"
	@echo "\n**********************\n"

install:
	pip install -r requirements.txt

run:
	python3 main.py -f example1.log example2.log -r average

test:
	pytest --cov=main test_main.py

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm .coverage
	rm -rf htmlcov

html_report:
	pytest --cov=main --cov-report=html
# 	xdg-open htmlcov/index.html

.PHONY: help install run test clean