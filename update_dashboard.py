# -*- coding: utf-8 -*-
"""EDLBION: refresh index.html from the locally synced OneDrive Excel file."""
from pathlib import Path
from datetime import datetime, timedelta
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

EXCEL = Path(r'C:\Users\LENOVO\OneDrive\Power BI Data\EDLBION-1.xlsx')
HERE = Path(__file__).resolve().parent
HTML = HERE / 'index.html'
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
COLUMNS = ['amount','currency','bank','links','donor','movement','type',
           'description','caseid','detail2','detail3','office','date','notes','rate','final']

def column_number(ref):
    letters = re.match(r'[A-Z]+', ref).group(0)
    result = 0
    for letter in letters:
        result = result * 26 + ord(letter) - 64
    return result - 1

def read_excel(path):
    with zipfile.ZipFile(path) as archive:
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            root = ET.fromstring(archive.read('xl/sharedStrings.xml'))
            for item in root.findall(NS + 'si'):
                strings.append(''.join(t.text or '' for t in item.iter(NS + 't')))
        sheet = ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
        rows = []
        for row in sheet.iter(NS + 'row'):
            values = [''] * 16
            for cell in row.findall(NS + 'c'):
                idx = column_number(cell.attrib['r'])
                if idx >= 16:
                    continue
                value_tag = cell.find(NS + 'v')
                if cell.attrib.get('t') == 'inlineStr':
                    value = ''.join(t.text or '' for t in cell.iter(NS + 't'))
                elif value_tag is None:
                    value = ''
                else:
                    value = value_tag.text or ''
                    if cell.attrib.get('t') == 's':
                        value = strings[int(value)]
                values[idx] = value
            if row.attrib.get('r') == '1':
                continue
            if not any(values):
                continue
            entry = dict(zip(COLUMNS, values))
            for key in ('amount', 'final'):
                try:
                    entry[key] = float(entry[key]) if entry[key] != '' else 0
                except ValueError:
                    entry[key] = 0
            date = entry['date']
            if date:
                try:
                    entry['date'] = (datetime(1899, 12, 30) + timedelta(days=float(date))).strftime('%Y-%m-%d')
                except ValueError:
                    pass
            for key in ('bank','movement','type','description','currency'):
                entry[key] = str(entry[key]).strip()
            rows.append(entry)
        return rows

def main():
    if not EXCEL.is_file():
        raise FileNotFoundError(f'Excel file not found: {EXCEL}')
    if not HTML.is_file():
        raise FileNotFoundError(f'index.html not found next to this script: {HTML}')
    records = read_excel(EXCEL)
    if len(records) < 10:
        raise RuntimeError('Too few records: refusing to overwrite dashboard.')
    source = HTML.read_text(encoding='utf-8')
    payload = json.dumps(records, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    updated, count = re.subn(r'const\s+DATA\s*=\s*\[.*?\];',
                             lambda _: 'const DATA=' + payload + ';',
                             source, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError('Cannot find const DATA=[...]; in index.html; no changes made.')
    backup = HERE / 'index.before_update.html.bak'
    shutil.copy2(HTML, backup)
    HTML.write_text(updated, encoding='utf-8')
    print(f'Updated index.html with {len(records)} records.')
    print(f'Backup: {backup}')
    print('NEXT: publish index.html using GitHub Desktop (Commit then Push origin).')

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR:', exc)
        sys.exit(1)
