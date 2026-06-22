@echo off
:: 关联 .pyw 文件到 pythonw.exe（仅当前用户，无需管理员权限）
set PYTHONW=C:\Users\su'da\AppData\Local\Programs\Python\Python314\pythonw.exe

reg add HKCU\Software\Classes\.pyw /ve /d Python.NoConFile /f
reg add HKCU\Software\Classes\Python.NoConFile\shell\open\command /ve /d "\"%PYTHONW%\" \"%%1\" %%*" /f

echo .pyw 文件关联设置完成！
pause
