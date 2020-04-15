# For removing Start Menu shortcut in Windows 7
RequestExecutionLevel user

Unicode True
; The name of the installer
Name "AutoStamp"

; The file to write
OutFile "install.exe"

; The default installation directory
InstallDir $PROGRAMFILES\AutoStamp

; The text to prompt the user to enter a directory
DirText "This will install My Cool Program on your computer. Choose a directory"

;--------------------------------

# start default section
Section
 
    # set the installation directory as the destination for the following actions
 
    # specify file to go in output path
    SetOutPath $INSTDIR\poppler
    File /nonfatal /a /r "poppler\"

    SetOutPath $INSTDIR
    File /nonfatal /a /r "AutoStamp\"
    # create the uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
 
    # create a shortcut named "new shortcut" in the start menu programs directory
    # point the new shortcut at the program uninstaller
    #CreateShortCut "$SMPROGRAMS\AutoStamp.lnk" "$INSTDIR\uninstall.exe"
    CreateShortCut "$DESKTOP\AutoStamp.lnk" "$INSTDIR\AutoStamp.exe" "" "$INSTDIR\icon.ico" 0

    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\AutoStamp" \
                    "AutoStamp" "AutoStamp -- stamp you documents faster"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\AutoStamp" \
                 "UninstallString" "$\"$INSTDIR\uninstall.exe$\""

    ; Add a value
    EnVar::AddValue "path" "$INSTDIR\poppler\bin"
    Pop $0
    DetailPrint "EnVar::AddValue returned=|$0|"
SectionEnd
 
# uninstaller section start
Section "uninstall"

    Delete "$SMPROGRAMS\AutoStamp.lnk"
    RMDir "$INSTDIR\poppler"
    Delete $INSTDIR\AutoStamp.exe
    Delete "$INSTDIR\uninstall.exe"
    Delete "$DESKTOP\AutoStamp.lnk"
    RMDir /R /REBOOTOK "$INSTDIR"
    ; Delete a value from a variable
    EnVar::DeleteValue "PATH" "$INSTDIR\poppler\bin"
    Pop $0
    DetailPrint "EnVar::DeleteValue returned=|$0|"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\AutoStamp"
# uninstaller section end
SectionEnd