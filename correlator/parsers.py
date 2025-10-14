
from __future__ import annotations
import json, re
from datetime import datetime, date, time
from typing import List, Dict, Optional
from .models import Event

class ParseReport:
    def __init__(self):
        self.errors: List[str] = []
        self.counts: Dict[str, int] = {"API":0, "DB":0, "STORAGE":0, "UNKNOWN":0}

    def add_error(self, msg: str):
        self.errors.append(msg)

def parse_api(path: str, report: ParseReport) -> List[Event]:
    events: List[Event] = []
    pat = re.compile(r'^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (?P<user>[^|]+) \| (?P<method>[A-Z]+) (?P<path>\S+) \| request_id=(?P<rid>\S+)$')
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            m = pat.match(line)
            if not m:
                report.add_error(f'API:{i} Unrecognized: {line}')
                continue
            ts = datetime.strptime(m.group('ts'), '%Y-%m-%d %H:%M:%S')
            user = m.group('user').strip()
            action = f"{m.group('method')} {m.group('path')}"
            rid = m.group('rid')
            events.append(Event(ts=ts, source='API', actor=user, action=action, meta={'request_id': rid}))
            report.counts['API'] += 1
    return events

def parse_db(path: str, report: ParseReport, assumed_date: Optional[str]=None) -> List[Event]:
    events: List[Event] = []
    pat = re.compile(r'^\[(?P<hms>\d{2}:\d{2}:\d{2})\]\s+user=(?P<user>\w+)\s+query="(?P<query>.+?)"(?:\s+triggered_by=(?P<rid>\S+))?(?:\s+rows=(?P<rows>-?\d+))?$')
    base_date = None
    if assumed_date:
        base_date = datetime.strptime(assumed_date, '%Y-%m-%d').date()
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            m = pat.match(line)
            if not m:
                report.add_error(f'DB:{i} Unrecognized: {line}')
                continue
            hms = m.group('hms')
            user = m.group('user')
            query = m.group('query')
            rid = m.group('rid')
            rows = m.group('rows')
            d = base_date or datetime.utcnow().date()
            h, mi, s = map(int, hms.split(':'))
            ts = datetime.combine(d, time(h, mi, s))
            action = f"SQL {query}"
            meta = {}
            if rid:
                meta['triggered_by'] = rid
            if rows is not None:
                try:
                    meta['rows'] = int(rows)
                except ValueError:
                    meta['rows'] = rows
            events.append(Event(ts=ts, source='DB', actor=user, action=action, meta=meta))
            report.counts['DB'] += 1
    return events

def parse_storage(path: str, report: ParseReport) -> List[Event]:
    events: List[Event] = []
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                ts = datetime.fromisoformat(obj['timestamp'])
                actor = obj.get('actor', 'unknown')
                action = f"{obj.get('action','?')} {obj.get('file','?')}"
                meta = {}
                if 'parent_request' in obj:
                    meta['parent_request'] = obj['parent_request']
                if 'size_kb' in obj:
                    meta['size_kb'] = obj['size_kb']
                events.append(Event(ts=ts, source='STORAGE', actor=actor, action=action, meta=meta))
                report.counts['STORAGE'] += 1
            except Exception as ex:
                report.add_error(f'STORAGE:{i} {ex} :: {line}')
                continue
    return events
