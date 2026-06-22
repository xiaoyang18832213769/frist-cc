CreateObject("WScript.Shell").Run "pythonw """ & CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\pomodoro.pyw""", 0, False
