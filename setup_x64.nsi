;--------------------------------

Unicode true
ShowInstDetails show

!ifdef VERSION
!else
  !define VERSION 0.0.0.0 git commit 00000000
!endif

; The name of the installer
!define APPNAME "main"
!define BinaryNAME "${APPNAME}.exe"
!define COMPANYNAME "iseetech"
!define DESCRIPTION "This is ${APPNAME}"
!define StartupProgram "$INSTDIR\dist\${APPNAME}.exe"
!define StartMenu_Folder "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}"
!define UserGuide "$INSTDIR\guideline.pdf"

Name "${COMPANYNAME}'s ${APPNAME}64 ${VERSION} ${GIT}"

;Name and file
OutFile "${APPNAME}64Setup ${VERSION}(git_${GIT}_${AUTHOR}_${TIME}).exe"
InstallDir "$PROGRAMFILES64\${COMPANYNAME}\${APPNAME}"
; Request application privileges for Windows Vista
; RequestExecutionLevel admin

VIProductVersion ${VERSION}
VIAddVersionKey ProductName "${APPNAME}"
VIAddVersionKey CompanyName "${COMPANYNAME}"
VIAddVersionKey LegalCopyright "http://www.iseetech.com.cn/"
VIAddVersionKey FileVersion ${Version}
VIAddVersionKey FileDescription ""
VIAddVersionKey ProductVersion ${Version}
VIAddVersionKey InternalName "${COMPANYNAME} Launcher"

DirText "This will install iSeeTech Corp's ${APPNAME} 64Bits software to your computer. Please close ${APPNAME} software and keep default install directory.$\r$\n${VERSION}, Git: ${GIT}, Author: ${AUTHOR}, Time: ${TIME}"

;--------------------------------
; Pages
Page components
Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

;--------------------------------
; The stuff to install

; SilentInstall silent
; SilentUninstall silent

Section "${APPNAME}64 (required)"
    SectionIn RO

    ExecWait "taskkill /f /im ${BinaryNAME}"

    ; Set output path to the installation directory.
    SetOutPath $INSTDIR
    WriteUninstaller "uninstall.exe"

    ; Put file there
    File /r /x *.nsi /x log Changelog.md README.md taskschd.xml
    File /r /x "log" /x "${APPNAME}.log" /x "${APPNAME}.exe.log" /x "dump" "dist"

    ; CreateDirectory $INSTDIR\dist
    SetOutPath $INSTDIR\dist
    File setting.json version run.bat

    ; desktop
    CreateShortcut "$DESKTOP\${APPNAME}.lnk" "${StartupProgram}"

    ; shortcuts
    CreateDirectory "${StartMenu_Folder}"
    CreateShortcut "${StartMenu_Folder}\${APPNAME}_uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
    CreateShortcut "${StartMenu_Folder}\${APPNAME}_startup.lnk" "${StartupProgram}" ""
    SetAutoClose True

    Call InstallService
    Exec "${StartupProgram}"
SectionEnd

;--------------------------------
; Uninstaller
Section "Uninstall"
    ExecWait "taskkill /f /im ${BinaryNAME}"

    ; Desktop
    Delete "$DESKTOP\${APPNAME}.lnk"

    ; Remove files and uninstaller
    Delete $INSTDIR\*.*

    ; Remove shortcuts, if any
    Delete "${StartMenu_Folder}\*.*"

    ; Remove directories used
    Delete "$INSTDIR\dist\log\*.*"
    Delete "$INSTDIR\dist\*.*"
    RMDir /r "$INSTDIR\dist\log"
    RMDir /r "$INSTDIR\dist"
    RMDir /r "$INSTDIR"

    ExecWait '"schtasks.exe" /f /delete /tn ${APPNAME}'
    SetAutoClose True
SectionEnd

Function InstallService
    ExecWait '"schtasks.exe" /f /delete /tn ${APPNAME}'
    ExecWait '"schtasks.exe" /Create /XML "$INSTDIR\taskschd.xml" /tn ${APPNAME}'
FunctionEnd