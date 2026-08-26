from __future__ import annotations

import ast
import base64
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, cast

import pytest
import rfc8785
from pydantic import ValidationError

from bsl.application.vs01_study_workspace import (
    REGION_ROLES,
    canonical_workspace_projection_bytes,
    compile_vs01_study_workspace,
)
from bsl.contracts.study_workspace import EXPECTED_WORKSPACE_IDENTITY, VS01StudyWorkspaceProjection
from bsl.infrastructure.study_workspace_authority import T06_PATHS, T08_PATHS

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "fixtures/VS01-T09/john-1-5-study-workspace-projection.json"
SCHEMA = ROOT / "contracts/json-schema/study-workspace/vs01-study-workspace-projection.schema.json"
PAIR_B64 = """
eyJhY3F1aXNpdGlvbl9ydW5faWRlbnRpdHkiOiIzYWM4NTFiNDMxZTc1YjE0YjVkNTBmY2IyNGExNmU2MjQzZTE5ZWNhMWY5MTZk
OGVkODFjYjk1OTY5YzkzMzdlIiwiY29udHJhY3QiOiJWUzAxQjA4UnVudGltZVBhaXJSZXN1bHQiLCJkaXNwb3NpdGlvbiI6IlJF
RkVSRU5DRV9DT05GT1JNQU5UIiwiZXZlbnRzX29ic2VydmVkIjoxNywiZml4ZWRfY2FzZV9yZXN1bHRfaWRlbnRpdHkiOiJlYjNh
ZTk1MmE3Y2I2MjkxMWUyNTkzNTBjYTg0NzI5OWI5NWYxNjYxZGFmOThiZTg3OWM4NmY2NDZhZTFjODgwIiwiZml4ZWRfcG9pbnRz
Ijo4LCJoYXJkX2ZhaWx1cmVzIjpbXSwibGVha2FnZV9pbmNpZGVudHMiOjAsImxpbWl0YXRpb25zIjpbInNpbmdsZSBwYXNzYWdl
IGFuZCBDaGF0R1BULWF1dGhvcmVkIHB1YmxpYyBzY3JlZW5pbmcgcGFpciIsImRldGVybWluaXN0aWMgb3JhY2xlIHJ1bnRpbWUg
cmF0aGVyIHRoYW4gbW9kZWwtbWVkaWF0ZWQgdG9vbCBzZWxlY3Rpb24iLCJubyBjcml0aWNhbCBhcHBhcmF0dXMgb3Igd2l0bmVz
cyBldmlkZW5jZSIsIm5vIFJFVi1QMiBzcGVjaWFsaXN0IGdvbGQiLCJub3QgdHJhaW5pbmcgZWxpZ2libGUgb3IgcHJpdmF0ZS1m
aW5hbCBlbGlnaWJsZSJdLCJwYWlyX3BvaW50cyI6MzYsInBhaXJfcmVzdWx0X2lkZW50aXR5IjoiZjczZmZkMjBmNTA5NmYyYjQ2
NWYzYmQ5MWJkYjA5M2Y0ZDQ0YTFjOWZhNWY3MTdmNjU4OWVhNWFlMTFkOTQyNiIsInBhaXJfc3BlY2lmaWNhdGlvbl9pZGVudGl0
eSI6Ijk4YzVkZjRiNDkwNjI2MWNkOTZmYTE5NGVjZjIwMzU0NzQ2MzNiZGM5OTg4Mzg4ODg2YzhiMDgxZTE4MzVmNTEiLCJyZXBs
YXlfcnVuX2lkZW50aXRpZXMiOlsiM2FjODUxYjQzMWU3NWIxNGI1ZDUwZmNiMjRhMTZlNjI0M2UxOWVjYTFmOTE2ZDhlZDgxY2I5
NTk2OWM5MzM3ZSIsIjNhYzg1MWI0MzFlNzViMTRiNWQ1MGZjYjI0YTE2ZTYyNDNlMTllY2ExZjkxNmQ4ZWQ4MWNiOTU5NjljOTMz
N2UiXSwicnVudGltZV9jcml0ZXJpYSI6W3siY3JpdGVyaW9uX2lkIjoiQjA4LVJULVIxIiwicG9pbnRzIjo0LCJzY29yZSI6Miwi
d2VpZ2h0IjoyfSx7ImNyaXRlcmlvbl9pZCI6IkIwOC1SVC1SMiIsInBvaW50cyI6NCwic2NvcmUiOjIsIndlaWdodCI6Mn0seyJj
cml0ZXJpb25faWQiOiJCMDgtUlQtUjMiLCJwb2ludHMiOjIsInNjb3JlIjoyLCJ3ZWlnaHQiOjF9LHsiY3JpdGVyaW9uX2lkIjoi
QjA4LVJULVI0IiwicG9pbnRzIjo0LCJzY29yZSI6Miwid2VpZ2h0IjoyfSx7ImNyaXRlcmlvbl9pZCI6IkIwOC1SVC1SNSIsInBv
aW50cyI6NCwic2NvcmUiOjIsIndlaWdodCI6Mn0seyJjcml0ZXJpb25faWQiOiJCMDgtUlQtUjYiLCJwb2ludHMiOjQsInNjb3Jl
IjoyLCJ3ZWlnaHQiOjJ9LHsiY3JpdGVyaW9uX2lkIjoiQjA4LVJULVI3IiwicG9pbnRzIjo0LCJzY29yZSI6Miwid2VpZ2h0Ijoy
fSx7ImNyaXRlcmlvbl9pZCI6IkIwOC1SVC1SOCIsInBvaW50cyI6Miwic2NvcmUiOjIsIndlaWdodCI6MX1dLCJydW50aW1lX3Bv
aW50cyI6MjgsInNjaGVtYV92ZXJzaW9uIjoiMS4wIiwidG9vbF9jYWxsc19vYnNlcnZlZCI6N30=
"""
T08_RECEIPT_B64 = """
eyJhY3F1aXNpdGlvbl9ydW5faWRlbnRpdHkiOiIzYWM4NTFiNDMxZTc1YjE0YjVkNTBmY2IyNGExNmU2MjQzZTE5ZWNhMWY5MTZk
OGVkODFjYjk1OTY5YzkzMzdlIiwiYXJjaGl2ZV9wYXRocyI6WyJvYmplY3RzL3NoYTI1Ni8wNC8wNGM5YjQ2ODBhMGQ2MTJiZGEw
NTUwOGRhNjU3MjBlYjU4MzU4N2ViYjgzYWI2Zjc2NmFjMTUxZjFjNjU2MjIyIiwic25hcHNob3RzL2JlbmNobWFyay92czAxLWIw
OC1ydW50aW1lLXBhaXIvcmVmZXJlbmNlLXNjcmVlbmluZy5qc29uIiwibWFuaWZlc3RzL2JlbmNobWFyay92czAxLWIwOC1ydW50
aW1lLXBhaXIvcmVmZXJlbmNlLXNjcmVlbmluZy9ydW50aW1lLXNjcmVlbmluZy1yZWNlaXB0Lmpzb24iLCIuaW5jb21pbmcvdnMw
MS1iMDgtcnVudGltZS1wYWlyLTA0YzliNDY4MGEwZDYxMmJkYTA1NTA4ZGE2NTcyMGViNTgzNTg3ZWJiODNhYjZmNzY2YWMxNTFm
MWM2NTYyMjIucnVudGltZS1zY3JlZW5pbmctc3RhZ2UiXSwiYXJjaGl2ZV9yb290IjoiL1ZvbHVtZXMvQlNMLUFyY2hpdmUvQmli
bGljYWxTY2hvbGFyTGFiIiwiYXV0aG9yaXR5X2ZpbmdlcnByaW50c19pbml0aWFsIjpbWyJ0MDQiLCIyNzYwOWNjMWZkNGNjNmUx
ODQ0ZmM0Mjc1ZGQ1ZGQwY2U4YTQ4NWZiNjhmN2Y3NWRkZGQ3NzkwMDVkNzAwMzFkIl0sWyJ0MDUiLCJiNzk4MTBmOWJmOWNmMzI3
YjBkNDAwNDFiNjQwYTQ5MDc5ZDljYmY1YzA0MzY2MGUxNDhlZDJkNWUzOGExNGExIl0sWyJ0MDYiLCJlYzBiNDAxOGQzMGQ3MTYw
MjEzYjIwOTQ1NDYxMzI1YmU3ODIxYzRiN2U2NjY2NzVkZTU1MjllNGE3NmVkODYwIl0sWyJ0MDciLCJiY2FlOWRkYTkyOTdlYmY1
NGY1YmRmNzZjN2ViYmJmYzkwNGRhNmViZWU1OGY4MzFhZmI1YzkyYWQxMzZkMzY3Il0sWyJhcmNoaXZlX3Jvb3QiLCJmNDVjOGZl
NGJlNTA1NzMyMDllNzRkOTQyMTRiOTRiYWY1MWE1ZjNhNWIwODEwOGU4NTU5OTIwNjNmNzljZDcwIl0sWyJpbmNvbWluZ19pbnZl
bnRvcnkiLCI0ZjUzY2RhMThjMmJhYTBjMDM1NGJiNWY5YTNlY2JlNWVkMTJhYjRkOGUxMWJhODczYzJmMTExNjEyMDJiOTQ1Il1d
LCJhdXRob3JpdHlfZmluZ2VycHJpbnRzX3Bvc3Rfc3RvcmUiOltbInQwNCIsIjI3NjA5Y2MxZmQ0Y2M2ZTE4NDRmYzQyNzVkZDVk
ZDBjZThhNDg1ZmI2OGY3Zjc1ZGRkZDc3OTAwNWQ3MDAzMWQiXSxbInQwNSIsImI3OTgxMGY5YmY5Y2YzMjdiMGQ0MDA0MWI2NDBh
NDkwNzlkOWNiZjVjMDQzNjYwZTE0OGVkMmQ1ZTM4YTE0YTEiXSxbInQwNiIsImVjMGI0MDE4ZDMwZDcxNjAyMTNiMjA5NDU0NjEz
MjViZTc4MjFjNGI3ZTY2NjY3NWRlNTUyOWU0YTc2ZWQ4NjAiXSxbInQwNyIsImJjYWU5ZGRhOTI5N2ViZjU0ZjViZGY3NmM3ZWJi
YmZjOTA0ZGE2ZWJlZTU4ZjgzMWFmYjVjOTJhZDEzNmQzNjciXSxbImFyY2hpdmVfcm9vdCIsImY0NWM4ZmU0YmU1MDU3MzIwOWU3
NGQ5NDIxNGI5NGJhZjUxYTVmM2E1YjA4MTA4ZTg1NTk5MjA2M2Y3OWNkNzAiXSxbImluY29taW5nX2ludmVudG9yeSIsIjRmNTNj
ZGExOGMyYmFhMGMwMzU0YmI1ZjlhM2VjYmU1ZWQxMmFiNGQ4ZTExYmE4NzNjMmYxMTE2MTIwMmI5NDUiXV0sImF1dGhvcml0eV9m
aW5nZXJwcmludHNfcHJlX3N0b3JlIjpbWyJ0MDQiLCIyNzYwOWNjMWZkNGNjNmUxODQ0ZmM0Mjc1ZGQ1ZGQwY2U4YTQ4NWZiNjhm
N2Y3NWRkZGQ3NzkwMDVkNzAwMzFkIl0sWyJ0MDUiLCJiNzk4MTBmOWJmOWNmMzI3YjBkNDAwNDFiNjQwYTQ5MDc5ZDljYmY1YzA0
MzY2MGUxNDhlZDJkNWUzOGExNGExIl0sWyJ0MDYiLCJlYzBiNDAxOGQzMGQ3MTYwMjEzYjIwOTQ1NDYxMzI1YmU3ODIxYzRiN2U2
NjY2NzVkZTU1MjllNGE3NmVkODYwIl0sWyJ0MDciLCJiY2FlOWRkYTkyOTdlYmY1NGY1YmRmNzZjN2ViYmJmYzkwNGRhNmViZWU1
OGY4MzFhZmI1YzkyYWQxMzZkMzY3Il0sWyJhcmNoaXZlX3Jvb3QiLCJmNDVjOGZlNGJlNTA1NzMyMDllNzRkOTQyMTRiOTRiYWY1
MWE1ZjNhNWIwODEwOGU4NTU5OTIwNjNmNzljZDcwIl0sWyJpbmNvbWluZ19pbnZlbnRvcnkiLCI0ZjUzY2RhMThjMmJhYTBjMDM1
NGJiNWY5YTNlY2JlNWVkMTJhYjRkOGUxMWJhODczYzJmMTExNjEyMDJiOTQ1Il1dLCJjYW5vbmljYWxfcmVjb3Zlcnlfc3RhdGUi
OiJFTVBUWSIsImNvbnRyYWN0IjoiVlMwMVJ1bnRpbWVTY3JlZW5pbmdSZWNlaXB0IiwiZGlzcG9zaXRpb24iOiJSRUZFUkVOQ0Vf
Q09ORk9STUFOVCIsImdlbmVyYXRlZF9hdCI6IjIwMjYtMDgtMjZUMTc6MzQ6MjcuMzAzNDA2WiIsImltcGxlbWVudGF0aW9uX2Nv
bW1pdCI6IjJjMDc0ZTZkOWJhMDNhM2EzM2E5NWU5YTk0ZjFmYzI4NzgwYTVmNjkiLCJvcGVyYXRpb25fbGVkZ2VyIjp7ImFjcXVp
c2l0aW9uX3J1bnNfY29uc3RydWN0ZWQiOjIsImJyb2tlcl90b29sX2NhbGxzIjoxNCwiY2Fub25pY2FsX2FyY2hpdmVfd3JpdGVz
IjozLCJjbG91ZF9pbnZvY2F0aW9ucyI6MCwiZGF0YWJhc2Vfd3JpdGVzIjowLCJtb2RlbF9pbnZvY2F0aW9ucyI6MCwibmV0d29y
a19pbnZvY2F0aW9ucyI6MCwib2NyX2ludm9jYXRpb25zIjowLCJwYWlyX3Jlc3VsdHNfY29uc3RydWN0ZWQiOjEsInB1YmxpY2F0
aW9uX2F0dGVtcHRzIjoxLCJyYXdfc291cmNlX3JlYWRzIjowLCJyZWNlaXB0c19jb25zdHJ1Y3RlZCI6MSwic2NvcmluZ19pbnZv
Y2F0aW9ucyI6MSwic3RvcmVfdmVyaWZpY2F0aW9uX2F0dGVtcHRzIjoyLCJzdWJqZWN0X2ludm9jYXRpb25zIjoyLCJzdWNjZXNz
ZnVsX3B1YmxpY2F0aW9ucyI6MSwidDAzX3JlYWRzIjowLCJ2bG1faW52b2NhdGlvbnMiOjB9LCJwYWlyX3Jlc3VsdCI6eyJhY3F1
aXNpdGlvbl9ydW5faWRlbnRpdHkiOiIzYWM4NTFiNDMxZTc1YjE0YjVkNTBmY2IyNGExNmU2MjQzZTE5ZWNhMWY5MTZkOGVkODFj
Yjk1OTY5YzkzMzdlIiwiY29udHJhY3QiOiJWUzAxQjA4UnVudGltZVBhaXJSZXN1bHQiLCJkaXNwb3NpdGlvbiI6IlJFRkVSRU5D
RV9DT05GT1JNQU5UIiwiZXZlbnRzX29ic2VydmVkIjoxNywiZml4ZWRfY2FzZV9yZXN1bHRfaWRlbnRpdHkiOiJlYjNhZTk1MmE3
Y2I2MjkxMWUyNTkzNTBjYTg0NzI5OWI5NWYxNjYxZGFmOThiZTg3OWM4NmY2NDZhZTFjODgwIiwiZml4ZWRfcG9pbnRzIjo4LCJo
YXJkX2ZhaWx1cmVzIjpbXSwibGVha2FnZV9pbmNpZGVudHMiOjAsImxpbWl0YXRpb25zIjpbInNpbmdsZSBwYXNzYWdlIGFuZCBD
aGF0R1BULWF1dGhvcmVkIHB1YmxpYyBzY3JlZW5pbmcgcGFpciIsImRldGVybWluaXN0aWMgb3JhY2xlIHJ1bnRpbWUgcmF0aGVy
IHRoYW4gbW9kZWwtbWVkaWF0ZWQgdG9vbCBzZWxlY3Rpb24iLCJubyBjcml0aWNhbCBhcHBhcmF0dXMgb3Igd2l0bmVzcyBldmlk
ZW5jZSIsIm5vIFJFVi1QMiBzcGVjaWFsaXN0IGdvbGQiLCJub3QgdHJhaW5pbmcgZWxpZ2libGUgb3IgcHJpdmF0ZS1maW5hbCBl
bGlnaWJsZSJdLCJwYWlyX3BvaW50cyI6MzYsInBhaXJfcmVzdWx0X2lkZW50aXR5IjoiZjczZmZkMjBmNTA5NmYyYjQ2NWYzYmQ5
MWJkYjA5M2Y0ZDQ0YTFjOWZhNWY3MTdmNjU4OWVhNWFlMTFkOTQyNiIsInBhaXJfc3BlY2lmaWNhdGlvbl9pZGVudGl0eSI6Ijk4
YzVkZjRiNDkwNjI2MWNkOTZmYTE5NGVjZjIwMzU0NzQ2MzNiZGM5OTg4Mzg4ODg2YzhiMDgxZTE4MzVmNTEiLCJyZXBsYXlfcnVu
X2lkZW50aXRpZXMiOlsiM2FjODUxYjQzMWU3NWIxNGI1ZDUwZmNiMjRhMTZlNjI0M2UxOWVjYTFmOTE2ZDhlZDgxY2I5NTk2OWM5
MzM3ZSIsIjNhYzg1MWI0MzFlNzViMTRiNWQ1MGZjYjI0YTE2ZTYyNDNlMTllY2ExZjkxNmQ4ZWQ4MWNiOTU5NjljOTMzN2UiXSwi
cnVudGltZV9jcml0ZXJpYSI6W3siY3JpdGVyaW9uX2lkIjoiQjA4LVJULVIxIiwicG9pbnRzIjo0LCJzY29yZSI6Miwid2VpZ2h0
IjoyfSx7ImNyaXRlcmlvbl9pZCI6IkIwOC1SVC1SMiIsInBvaW50cyI6NCwic2NvcmUiOjIsIndlaWdodCI6Mn0seyJjcml0ZXJp
b25faWQiOiJCMDgtUlQtUjMiLCJwb2ludHMiOjIsInNjb3JlIjoyLCJ3ZWlnaHQiOjF9LHsiY3JpdGVyaW9uX2lkIjoiQjA4LVJU
LVI0IiwicG9pbnRzIjo0LCJzY29yZSI6Miwid2VpZ2h0IjoyfSx7ImNyaXRlcmlvbl9pZCI6IkIwOC1SVC1SNSIsInBvaW50cyI6
NCwic2NvcmUiOjIsIndlaWdodCI6Mn0seyJjcml0ZXJpb25faWQiOiJCMDgtUlQtUjYiLCJwb2ludHMiOjQsInNjb3JlIjoyLCJ3
ZWlnaHQiOjJ9LHsiY3JpdGVyaW9uX2lkIjoiQjA4LVJULVI3IiwicG9pbnRzIjo0LCJzY29yZSI6Miwid2VpZ2h0IjoyfSx7ImNy
aXRlcmlvbl9pZCI6IkIwOC1SVC1SOCIsInBvaW50cyI6Miwic2NvcmUiOjIsIndlaWdodCI6MX1dLCJydW50aW1lX3BvaW50cyI6
MjgsInNjaGVtYV92ZXJzaW9uIjoiMS4wIiwidG9vbF9jYWxsc19vYnNlcnZlZCI6N30sInBhaXJfcmVzdWx0X2ZpbGVfc2hhMjU2
IjoiMDRjOWI0NjgwYTBkNjEyYmRhMDU1MDhkYTY1NzIwZWI1ODM1ODdlYmI4M2FiNmY3NjZhYzE1MWYxYzY1NjIyMiIsInBhaXJf
cmVzdWx0X2lkZW50aXR5IjoiZjczZmZkMjBmNTA5NmYyYjQ2NWYzYmQ5MWJkYjA5M2Y0ZDQ0YTFjOWZhNWY3MTdmNjU4OWVhNWFl
MTFkOTQyNiIsInBhaXJfc3BlY2lmaWNhdGlvbl9pZGVudGl0eSI6Ijk4YzVkZjRiNDkwNjI2MWNkOTZmYTE5NGVjZjIwMzU0NzQ2
MzNiZGM5OTg4Mzg4ODg2YzhiMDgxZTE4MzVmNTEiLCJwdWJsaXNoZWQiOnRydWUsInJlY2VpcHRfY2Fub25pY2FsX3NoYTI1NiI6
IjhhZjU2MWFiYTFjMmQwZGY0MWJhNThmOGJkNjVmNmE5M2RlNTQ3YjUzNTNlOGJlN2VhYzJjMWVjZTUwNWZhYzkiLCJyZWNlaXB0
X2lkIjoiMDFhMDNmMjMtMzVlNy03ZWY0LWI0ODItZDg0ZGFmYTc3MDEwIiwicmV0YWluZWRfcHVibGljYXRpb25fcmVjZWlwdCI6
bnVsbCwicmV0YWluZWRfcHVibGljYXRpb25fcmVjZWlwdF9maWxlX3NoYTI1NiI6bnVsbCwicmV0YWluZWRfcHVibGljYXRpb25f
cmVjZWlwdF9pZCI6bnVsbCwic2NoZW1hX3ZlcnNpb24iOiIxLjAiLCJ2ZXJpZmllZF9leGlzdGluZyI6ZmFsc2V9
"""
T06_RECEIPT_B64 = """
eyJhcmNoaXZlX3Jvb3QiOiIvVm9sdW1lcy9CU0wtQXJjaGl2ZS9CaWJsaWNhbFNjaG9sYXJMYWIiLCJhcmNoaXZlX3dyaXRlcyI6
NSwiYXV0aG9yaXR5X2ZpbmdlcnByaW50X2FmdGVyIjoiZjJlMzU1MDE1NDBmNGFjMWJmYWVjMjYyYmE3YWQxNjI3NTJiMTRlYjBj
MTFiZjUwZjY0NjY2NDBjMzc1NzRhNSIsImF1dGhvcml0eV9maW5nZXJwcmludF9iZWZvcmUiOiJmMmUzNTUwMTU0MGY0YWMxYmZh
ZWMyNjJiYTdhZDE2Mjc1MmIxNGViMGMxMWJmNTBmNjQ2NjY0MGMzNzU3NGE1IiwiYmFzZV9wbmdfc2hhMjU2IjoiMmMwY2ViYzcy
NDVlYjEwMzJiMmIxZTRjMGVlMTZlNmY3NGRlYzQ3ZTZhNTNkOGY0OWM0YjlkMGE4NDdhYmJmYiIsImJlbmNobWFya19leGVjdXRp
b25zIjowLCJjb250cmFjdCI6IkpvaG4xNVN5bnRoZXRpY1BhZ2VQdWJsaWNhdGlvblJlY2VpcHQiLCJkYXRhYmFzZV93cml0ZXMi
OjAsImRlZ3JhZGVkX3BuZ19zaGEyNTYiOiJjYjQ3MDczYzhlNDBkYTAxMjg1ZDkwZDI2ZWJiNzE0NGIzNDA0N2EyY2RlOGY1OGU0
YmEwZDFmMmNmYjY3ZmNlIiwiZGlzcG9zaXRpb24iOiJQVUJMSVNIRUQiLCJkcnlfcnVuIjpmYWxzZSwiZml4dHVyZV9pZGVudGl0
eSI6IjkyOWRkYzFjMWFlYjFlOTc2YTcwY2ZiY2ViMjM4ZjBlZjZhNTVlOGNhMWIzNTRhMDIxMDQ2M2NlYzUwYjRkOWIiLCJmaXh0
dXJlX2pzb25fc2hhMjU2IjoiYzhjZmM0ZWFmZWU2YjBhMTZmYzJlMDQ0MjE5MDc4MmEzNWUyYjAzNDc3YTYxOTg1NDEwNWQ1Mjcy
ZjA4NDE3ZiIsImdlbmVyYXRlZF9hdCI6IjIwMjYtMDgtMjRUMTc6MTI6NTkuMzY0Njk2WiIsImltcGxlbWVudGF0aW9uX2NvbW1p
dCI6ImZmY2MyODkyYjIwOTZmOGM5NTFmYjgyMmM2Y2YwMWE1NjM0YjY3OTMiLCJtb2RlbF9pbnZvY2F0aW9ucyI6MCwib2NyX2lu
dm9jYXRpb25zIjowLCJwdWJsaWNhdGlvbl9wYXRocyI6WyJvYmplY3RzL3NoYTI1Ni8yYy8yYzBjZWJjNzI0NWViMTAzMmIyYjFl
NGMwZWUxNmU2Zjc0ZGVjNDdlNmE1M2Q4ZjQ5YzRiOWQwYTg0N2FiYmZiIiwib2JqZWN0cy9zaGEyNTYvY2IvY2I0NzA3M2M4ZTQw
ZGEwMTI4NWQ5MGQyNmViYjcxNDRiMzQwNDdhMmNkZThmNThlNGJhMGQxZjJjZmI2N2ZjZSIsIm9iamVjdHMvc2hhMjU2L2M4L2M4
Y2ZjNGVhZmVlNmIwYTE2ZmMyZTA0NDIxOTA3ODJhMzVlMmIwMzQ3N2E2MTk4NTQxMDVkNTI3MmYwODQxN2YiLCJzbmFwc2hvdHMv
cGFnZS9qb2huLTEtNS1zeW50aGV0aWMtZml4dHVyZS5qc29uIiwibWFuaWZlc3RzL3BhZ2Uvam9obi0xLTUtc3ludGhldGljLWZp
eHR1cmUvcGFnZS1maXh0dXJlLXJlY2VpcHQuanNvbiJdLCJwdWJsaXNoZWQiOnRydWUsInJhd19ub25fZm9udF9zb3VyY2VfcmVh
ZHMiOjAsInJlY2VpcHRfaWRlbnRpdHkiOiIwMWEwMzRjMi1kNmU0LTczZjQtOTFiMi03NDEwZTc0NTM3ODMiLCJyZW5kZXJlcl9h
dXRob3JpdHlfc2hhMjU2IjoiM2FjN2RmODkxMGJmNGVhNmE2MzBhOGY1ZTIyMjQ4MzU0MTEyMTQ1ODYyMGE4MGVkZjViYWIyMGQw
Njc2MjNkZSIsInNjaGVtYV92ZXJzaW9uIjoiMS4wIiwidmVyaWZpZWRfZXhpc3RpbmciOmZhbHNlLCJ2bG1faW52b2NhdGlvbnMi
OjB9
"""
REVERSE = object()


def _install(root: Path, relative: str, data: bytes) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    path.chmod(0o444)


@pytest.fixture
def synthetic_archive(tmp_path: Path) -> Path:
    root = tmp_path / "archive"
    pair = base64.b64decode("".join(PAIR_B64.split()))
    _install(root, T08_PATHS[0], pair)
    _install(root, T08_PATHS[1], pair)
    _install(root, T08_PATHS[2], base64.b64decode("".join(T08_RECEIPT_B64.split())))
    fixture = (ROOT / "fixtures/VS01-T06/john-1-5-synthetic-fixture.json").read_bytes()
    _install(root, T06_PATHS[0], (ROOT / "fixtures/VS01-T06/john-1-5-base-page.png").read_bytes())
    _install(
        root,
        T06_PATHS[1],
        (ROOT / "fixtures/VS01-T06/john-1-5-degraded-illegibility-v1.png").read_bytes(),
    )
    _install(root, T06_PATHS[2], fixture)
    _install(root, T06_PATHS[3], fixture)
    _install(root, T06_PATHS[4], base64.b64decode("".join(T06_RECEIPT_B64.split())))
    return root


def _fixture() -> dict[str, Any]:
    return json.loads(FIXTURE.read_bytes())


def _identity(data: dict[str, Any]) -> str:
    return hashlib.sha256(
        rfc8785.dumps({key: value for key, value in data.items() if key != "workspace_identity"})
    ).hexdigest()


def _strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in cast(dict[object, object], value).values() for text in _strings(item)]
    if isinstance(value, list):
        return [text for item in cast(list[object], value) for text in _strings(item)]
    return []


def _tuples(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_tuples(item) for item in cast(list[Any], value))
    if isinstance(value, dict):
        mapping = cast(dict[str, Any], value)
        return {key: _tuples(item) for key, item in mapping.items()}
    return value


def test_real_shape_compiles_twice_from_synthetic_immutable_authority(synthetic_archive: Path) -> None:
    first = compile_vs01_study_workspace(synthetic_archive)
    second = compile_vs01_study_workspace(synthetic_archive)
    assert first == second
    assert first.workspace_identity == second.workspace_identity == EXPECTED_WORKSPACE_IDENTITY
    assert canonical_workspace_projection_bytes(first) == canonical_workspace_projection_bytes(second)
    assert canonical_workspace_projection_bytes(first) + b"\n" == FIXTURE.read_bytes()
    regions = cast(list[dict[str, Any]], first.page_study["regions"])
    variants = cast(list[dict[str, Any]], first.page_study["variants"])
    assert tuple(region["role"] for region in regions) == REGION_ROLES
    assert tuple(variant["variant_id"] for variant in variants) == (
        "BASE",
        "DEGRADED_ILLEGIBILITY",
    )


def test_projection_exact_context_counts_links_and_zero_operations() -> None:
    projection = VS01StudyWorkspaceProjection.model_validate_json(FIXTURE.read_bytes())
    assert (projection.route, projection.answer_mode) == ("DETERMINISTIC_LOCAL_ONLY", "STUDY")
    assert projection.active_context["reference"] == "John.1.5"
    assert projection.active_context["model_route"] == "NONE"
    assert tuple(
        map(
            len,
            (
                projection.translations,
                projection.study_blocks,
                projection.evidence_records,
                projection.claim_records,
                projection.citation_records,
            ),
        )
    ) == (2, 7, 12, 15, 10)
    assert projection.material_unknown_claim_ids == ("CLM-T04-042", "CLM-T04-043")
    assert all(value == 0 for value in projection.operation_disclosure.values())
    strings = _strings(projection.model_dump(mode="json"))
    assert not any(text.startswith("/") for text in strings)
    assert not any(".local/evidence" in text or "postgresql://" in text for text in strings)
    assert "TRANSLATIONS_ARE_NOT_MANUSCRIPT_WITNESSES" not in strings
    assert any("Translation wording is not manuscript attestation." in text for text in strings)
    assert any("not a declaration that no variant exists" in text for text in strings)

    evidence = {item.evidence_id: item for item in projection.evidence_records}
    claims = {item.claim_id: item for item in projection.claim_records}
    citations = {item.citation_id: item for item in projection.citation_records}
    assert len(projection.evidence_inspector) == len(citations) == 10
    for inspector in projection.evidence_inspector:
        citation = citations[cast(str, inspector["citation_id"])]
        record = evidence[citation.evidence_id]
        assert inspector["evidence_id"] == citation.evidence_id
        assert inspector["source_role"] == record.source_role
        assert inspector["source_handle"] == record.source_handle
        assert inspector["selector"] == citation.selector
        assert inspector["quoted_span"] == citation.quoted_span
        assert inspector["inspection_level"] == "PUBLIC_SAFE_PROJECTED_AUTHORITY"
        exposed = cast(tuple[dict[str, Any], ...], inspector["claims"])
        expected = tuple(claim for claim in claims.values() if citation.evidence_id in claim.evidence_ids)
        assert tuple(item["claim_id"] for item in exposed) == tuple(claim.claim_id for claim in expected)
        assert tuple(item["epistemic_status"] for item in exposed) == tuple(
            claim.epistemic_status for claim in expected
        )
        assert tuple(item["required_qualifications"] for item in exposed) == tuple(
            claim.required_qualifications for claim in expected
        )


def test_projection_is_deeply_immutable_and_serialization_stays_identity_bound() -> None:
    projection = VS01StudyWorkspaceProjection.model_validate_json(FIXTURE.read_bytes())
    before = canonical_workspace_projection_bytes(projection)
    with pytest.raises(TypeError):
        cast(Any, projection.active_context)["MUTATED"] = "yes"
    with pytest.raises(TypeError):
        cast(Any, projection.translations[0])["text"] = "bad"
    with pytest.raises(TypeError):
        projection.page_study["regions"][0]["text"] = "bad"
    assert canonical_workspace_projection_bytes(projection) == before
    with pytest.raises(ValidationError):
        canonical_workspace_projection_bytes(projection.model_copy(update={"workspace_identity": "0" * 64}))
    mutated_page = copy.deepcopy(_fixture()["page_study"])
    mutated_page["regions"][0]["text"] = "bad"
    with pytest.raises(ValidationError):
        canonical_workspace_projection_bytes(projection.model_copy(update={"page_study": mutated_page}))


def test_python_tuple_input_is_recursively_frozen() -> None:
    data = cast(dict[str, Any], _tuples(_fixture()))
    projection = VS01StudyWorkspaceProjection.model_validate(data)
    with pytest.raises(TypeError):
        projection.page_study["regions"][0]["text"] = "bad"


MUTATIONS: dict[str, tuple[tuple[object, ...], object]] = {
    "workspace-id": (("workspace_id",), "MUTATED"),
    "route": (("route",), "MODEL"),
    "answer-mode": (("answer_mode",), "BRIEF"),
    "reference": (("active_context", "reference"), "John.1.6"),
    "edition": (("active_context", "greek_edition"), "OTHER"),
    "question": (("question",), "Changed?"),
    "translation-text": (("translations", 0, "text"), "changed"),
    "translation-id": (("translations", 0, "translation_id"), "OTHER"),
    "translation-order": (("translations",), REVERSE),
    "translation-focal": (("translations", 1, "focal_span"), "overcome"),
    "greek-clause": (("greek", "clause"), "changed"),
    "greek-target": (("greek", "target"), "changed"),
    "greek-lemma": (("greek", "lemma"), "changed"),
    "morphology": (("greek", "morphology", "mood_form"), "subjunctive"),
    "block-id": (("study_blocks", 0, "block_id"), "OTHER"),
    "block-order": (("study_blocks",), REVERSE),
    "block-heading": (("study_blocks", 0, "heading"), "changed"),
    "block-text": (("study_blocks", 0, "text"), "changed"),
    "block-claim": (("study_blocks", 0, "claim_ids", 0), "CLM-T04-010"),
    "block-citation": (("study_blocks", 0, "citation_ids", 0), "CIT-T05-001"),
    "block-alternative": (("study_blocks", 4, "alternative_ids", 0), "OTHER"),
    "evidence-id": (("evidence_records", 0, "evidence_id"), "OTHER"),
    "evidence-order": (("evidence_records",), REVERSE),
    "evidence-role": (("evidence_records", 0, "source_role"), "OTHER"),
    "evidence-handle": (("evidence_records", 0, "source_handle"), "OTHER"),
    "evidence-selector": (("evidence_records", 0, "selector"), "OTHER"),
    "evidence-excerpt": (("evidence_records", 1, "exact_excerpt"), "changed"),
    "evidence-acquisition": (("evidence_records", 0, "acquired_by"), "OTHER"),
    "claim-id": (("claim_records", 0, "claim_id"), "OTHER"),
    "claim-order": (("claim_records",), REVERSE),
    "claim-proposition": (("claim_records", 0, "proposition"), "changed"),
    "claim-status": (("claim_records", 0, "epistemic_status"), "UNKNOWN"),
    "claim-evidence": (("claim_records", 0, "evidence_ids", 0), "EV-T04-ASV-001"),
    "claim-qualification": (("claim_records", 0, "required_qualifications", 0), "changed"),
    "citation-id": (("citation_records", 0, "citation_id"), "OTHER"),
    "citation-order": (("citation_records",), REVERSE),
    "citation-evidence": (("citation_records", 0, "evidence_id"), "EV-T04-WEB-001"),
    "citation-selector": (("citation_records", 0, "selector"), "changed"),
    "citation-quote": (("citation_records", 0, "quoted_span"), "changed"),
    "inspector-claim": (("evidence_inspector", 0, "claims", 0, "claim_id"), "OTHER"),
    "inspection-level": (("evidence_inspector", 0, "inspection_level"), "PRIVATE"),
    "alternatives": (("accepted_alternative_ids", 0), "OTHER"),
    "unknowns": (("material_unknown_claim_ids", 0), "CLM-T04-010"),
    "horizon": (("evidence_horizon", 0), "changed"),
    "page-variant": (("page_study", "variants", 0, "variant_id"), "OTHER"),
    "page-hash": (("page_study", "variants", 0, "sha256"), "0" * 64),
    "page-size": (("page_study", "variants", 0, "byte_count"), 1),
    "page-dimensions": (("page_study", "variants", 0, "dimensions_px", 0), 1),
    "page-role": (("page_study", "variants", 0, "region_roles", 0), "OTHER"),
    "page-uncertainty": (("page_study", "variants", 1, "visual_state"), "LEGIBLE"),
    "t04-binding": (("audit_bindings", "t04", "packet_identity"), "0" * 64),
    "t05-binding": (("audit_bindings", "t05", "execution_identity"), "0" * 64),
    "t06-binding": (("audit_bindings", "t06", "fixture_identity"), "0" * 64),
    "t08-binding": (("audit_bindings", "t08", "pair_result_identity"), "0" * 64),
    "score": (("audit_bindings", "t08", "scores", "runtime"), 27),
    "count": (("audit_bindings", "t08", "structure_counts", "claims"), 14),
    "operation": (("operation_disclosure", "model_calls"), 1),
    "absolute-path": (("question",), "/Volumes/private"),
    "database-coordinate": (("database_url",), "postgresql://host/database"),
}


def _mutated(case: str) -> dict[str, Any]:
    data = copy.deepcopy(_fixture())
    path, replacement = MUTATIONS[case]
    target: Any = data
    for part in path[:-1]:
        target = target[part]
    final = path[-1]
    target[final] = list(reversed(target[final])) if replacement is REVERSE else replacement
    data["workspace_identity"] = _identity(data)
    return data


@pytest.mark.parametrize("case", MUTATIONS)
def test_pydantic_and_draft_2020_12_reject_recomputed_adversaries(case: str) -> None:
    jsonschema = pytest.importorskip("jsonschema", reason="external Draft 2020-12 validation tool")
    VS01StudyWorkspaceProjection.model_validate_json(FIXTURE.read_bytes())
    data = _mutated(case)
    with pytest.raises(ValidationError):
        VS01StudyWorkspaceProjection.model_validate_json(rfc8785.dumps(data))
    validator = jsonschema.Draft202012Validator(json.loads(SCHEMA.read_bytes()))
    assert not validator.is_valid(data)


@pytest.mark.parametrize("relative", T08_PATHS + T06_PATHS)
@pytest.mark.parametrize("failure", ("mutable", "mismatch", "symlink", "nonregular"))
def test_every_authority_file_fails_closed(
    synthetic_archive: Path, tmp_path: Path, relative: str, failure: str
) -> None:
    root = synthetic_archive
    target = root / relative
    if failure == "mutable":
        target.chmod(0o644)
    elif failure == "mismatch":
        target.chmod(0o600)
        target.write_bytes(b"changed")
        target.chmod(0o444)
    elif failure == "symlink":
        moved = tmp_path / target.name
        target.rename(moved)
        target.symlink_to(moved)
    else:
        target.unlink()
        target.mkdir()
        target.chmod(0o444)
    with pytest.raises(ValueError):
        compile_vs01_study_workspace(root)


def test_authority_loader_rejects_root_and_component_symlinks(synthetic_archive: Path, tmp_path: Path) -> None:
    linked_root = tmp_path / "linked-archive"
    linked_root.symlink_to(synthetic_archive, target_is_directory=True)
    with pytest.raises(ValueError):
        compile_vs01_study_workspace(linked_root)

    objects = synthetic_archive / "objects"
    moved = synthetic_archive / "objects-real"
    objects.rename(moved)
    objects.symlink_to(moved, target_is_directory=True)
    with pytest.raises(ValueError):
        compile_vs01_study_workspace(synthetic_archive)


@pytest.mark.parametrize("relative", (T08_PATHS[0], T08_PATHS[1], T08_PATHS[2], *T06_PATHS[2:]))
def test_json_authority_rejects_noncanonical_bytes(synthetic_archive: Path, relative: str) -> None:
    target = synthetic_archive / relative
    value = json.loads(target.read_bytes())
    target.chmod(0o600)
    target.write_bytes(json.dumps(value, indent=2).encode() + b"\n")
    target.chmod(0o444)
    with pytest.raises(ValueError):
        compile_vs01_study_workspace(synthetic_archive)


def test_committed_run_tampering_fails_closed(
    synthetic_archive: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import bsl.infrastructure.study_workspace_authority as authority_module

    data = json.loads(authority_module.RUN_FIXTURE.read_bytes())
    data["answer_projection_identity"] = "0" * 64
    tampered = rfc8785.dumps(data) + b"\n"
    path = tmp_path / "reference-runtime-run.json"
    path.write_bytes(tampered)
    monkeypatch.setattr(authority_module, "RUN_FIXTURE", path)
    monkeypatch.setattr(authority_module, "RUN_FIXTURE_SHA256", hashlib.sha256(tampered).hexdigest())
    with pytest.raises(ValueError):
        compile_vs01_study_workspace(synthetic_archive)


def test_implementation_has_no_prohibited_import_or_call_path() -> None:
    files = (
        ROOT / "src/bsl/contracts/study_workspace.py",
        ROOT / "src/bsl/application/vs01_study_workspace.py",
        ROOT / "src/bsl/infrastructure/study_workspace_authority.py",
    )
    forbidden = {
        "verify_t05_owner",
        "load_t04_authority",
        "run_runtime_pair",
        "complete_runtime_pair",
        "compile_runtime_authority",
        "reload_runtime_authority_fingerprints",
        "psycopg",
        "psycopg2",
        "asyncpg",
        "sqlalchemy",
        "requests",
        "httpx",
        "urllib",
        "socket",
        "boto3",
        "openai",
        "anthropic",
        "subprocess",
        "urlopen",
        "create_engine",
        "source_acquisition",
        "normalization",
    }
    for path in files:
        tree = ast.parse(path.read_text())
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        names |= {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
        names |= {
            alias.name.split(".")[-1] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names
        }
        names |= {
            node.module.split(".")[-1] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module
        }
        assert names.isdisjoint(forbidden)


def test_committed_schema_is_exact_draft_2020_12_const() -> None:
    schema = json.loads(SCHEMA.read_bytes())
    fixture = _fixture()
    keys = list(fixture)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert schema["properties"] == {key: {} for key in keys}
    assert schema["required"] == keys
    assert schema["additionalProperties"] is False
    assert schema["const"] == fixture
    assert schema == VS01StudyWorkspaceProjection.model_json_schema(by_alias=False)


def test_committed_schema_passes_external_draft_2020_12_validation() -> None:
    jsonschema = pytest.importorskip("jsonschema", reason="external Draft 2020-12 validation tool")
    schema = json.loads(SCHEMA.read_bytes())
    fixture = _fixture()
    keys = list(fixture)
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)
    assert validator.is_valid(fixture)
    assert not validator.is_valid({**fixture, "unexpected": True})
    assert not validator.is_valid({key: value for key, value in fixture.items() if key != keys[0]})
    assert not validator.is_valid(_mutated("question"))
