# clean_florida_test.py
import tabula
import camelot
import pandas as pd
import argparse
from datetime import datetime
from pathlib import Path

path = "/Users/thawks/Downloads/Ohio/American Indian.pdf"
# df = tabula.read_pdf(path, pages = 1, area = [],
#                      columns = [40, 73], guess = False)
tables = camelot.read_pdf(path)
tables