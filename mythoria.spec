# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
root=Path(SPECPATH)
a=Analysis(['launcher.py'],pathex=[str(root)],
    datas=[(str(root/'templates'),'templates'),(str(root/'static'),'static'),(str(root/'database'/'schema.sql'),'database')],
    hiddenimports=[],excludes=['pytest'],noarchive=False)
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='Mythoria',console=True)
coll=COLLECT(exe,a.binaries,a.datas,name='Mythoria')
