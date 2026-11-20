import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_ROOT = ROOT / 'sample_data'
DB = Path(os.getenv('WORKBENCH_DB', str(ROOT/'state/ledger.sqlite3')))
TITLE = '纸上版税'
SLUG = 'press-royalty'
KEY = '作者结算单'
FIELDS = ('期初净销', '出库册数', '实退册数', '定价元', '版税阶梯', '留存百分比', '释放准备金元')
ROLE = '出版社发行核算员'
UNIT = '元'
RULE_VERSION = 'press-royalty-1.0'
SIGNATURE = '版税分项'
TABS = {'intake': '渠道回执', 'contract': '合同字段', 'quality': '争议结算单', 'domain': '版税核算', 'reconcile': '财务勾稽', 'runs': '月结批次', 'review': '会签底稿'}
