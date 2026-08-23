Set WS = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Huidige script pad
strPath = WScript.ScriptFullName
strFolder = FSO.GetParentFolderName(strPath)
strIconPath = strFolder & "\converter.ico"

' Start het programma
WS.Run "pythonw """ & strFolder & "\image_converter.py""", 0, False

' Controleer of de snelkoppeling bestaat
If Not FSO.FileExists(WS.SpecialFolders("Desktop") & "\Quick Image Converter.lnk") Then
    ' Maak de snelkoppeling
    Set shortcut = WS.CreateShortcut(WS.SpecialFolders("Desktop") & "\Quick Image Converter.lnk")
    shortcut.TargetPath = strPath
    shortcut.WorkingDirectory = strFolder
    shortcut.IconLocation = """" & strIconPath & """,0"
    shortcut.Save
End If