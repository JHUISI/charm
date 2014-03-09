; --------------------------------
;
; Description:
; Using the NSIS compiler, one can compile this script into a Windows charm-crypto
; installation executable.  It is recommended that you first use mingw32 to build
; charm-crypto (see the INSTALL file), and than run this script to capture the
; latest source.
;
; Specifics:
; The script checks for python32 and/or python27, else it aborts.  Depending on
; the version of Python found, it will check those in for site-package installation.
; Charm dependencies will be installed unknowingly to the user, and for the
; easier installation path the INSTDIR is unmodifiable (C:\charm-crypto).  Dependencies
; added all the bloat to this installer as it includes openssl, gmp, pbc.  
;
; Future Improvements:
; Support optional libs with user defined control.
;
; Author: Michael Rushanan (micharu1@cs.jhu.edu)
; Date: 08/2012
;
; --------------------------------

; MUI 1.67 compatible ------
!include "MUI.nsh"
!include "Sections.nsh"
!include "EnvVarUpdate.nsh"

; For conditionals and 64-bit check.
!include "LogicLib.nsh"
!include "x64.nsh"
!include "nsDialogs.nsh"

; Constants.
!define PRODUCT_NAME "charm-crypto"
!define PRODUCT_VERSION "0.43"
!define PRODUCT_PUBLISHER "Johns Hopkins University, HMS Lab"
!define PRODUCT_WEB_SITE "http://charm-crypto.com/Main.html"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

;bzip2 is an option
SetCompressor lzma

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "Charm-Package.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME

; Custom Changelog page
Page custom changeLogPage

; License page
!insertmacro MUI_PAGE_LICENSE "lgpl.txt"

; Components page
!insertmacro MUI_PAGE_COMPONENTS

; Directory page -- I think this will stop users from being able to modify
; the installation directory.
;!insertmacro MUI_PAGE_DIRECTORY

; Instfiles page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS
; MUI end ------

; Globals ------
Var changeLog
Var Python32Dir
Var Python27Dir

!define Python32Exe "$Python32Dir\python.exe"
!define Python27Exe "$Python27Dir\python.exe"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "charm-crypto.exe"
; We won't be using $PROGRAMFILES because that seems to break things.
; Also, will be using python dirs instead of $INSTDIR
InstallDir "C:\charm-crypto"
ShowInstDetails show
ShowUnInstDetails show

; Changelog Page
Function changeLogPage
    !insertmacro MUI_HEADER_TEXT "Change Log" "Please review the below for recent changes to this version of charm-crypto."
	
	nsDialogs::Create 1018

	;${NSD_CreateLabel} 0 0 100% 12u "2/14/2012"
	;Pop $changeLog
	
	nsDialogs::CreateControl EDIT \
	"${__NSD_Text_STYLE}|${WS_VSCROLL}|${WS_HSCROLL}|${ES_MULTILINE}|${ES_WANTRETURN}" \
	"${__NSD_Text_EXSTYLE}" \
	0 0 100% 100% \
	"- Several bug fixes to base modules (mem leaks, interface issues): pairing (PBC & Miracl), ecc, and integer.$\r$\n- Added new base module for RELIC and fixed bugs for MIRACL (Note: unified abstract interface for base modules coming in v0.43).$\r$\n- Refactored charm package structure. This affects schemes, toolbox, adapters, etc.$\r$\n- setup.py now creates Python egg.$\r$\n- Integrated pytest to replace unit testing framework.$\r$\n- Added doctests to all Charm schemes.$\r$\n- Updated documentation.$\r$\n"
	Pop $changeLog
	
	nsDialogs::Show
FunctionEnd

; This section, dependencies, must be installed.  So no user option control!
Section # Install Charm Dependencies
  SetOutPath "$INSTDIR\bin"
  SetOverwrite try
  File /r "C:\charm-crypto\bin\"
  ;SetOutPath "$INSTDIR\certs"
  ;File "C:\charm-crypto\certs"
  SetOutPath "$INSTDIR\include"
  File /r "C:\charm-crypto\include\"  
  SetOutPath "$INSTDIR\lib"
  File /r "C:\charm-crypto\lib\"
  SetOutPath "$INSTDIR\man"
  File /r "C:\charm-crypto\man\"
  SetOutPath "$INSTDIR\misc"
  File /r "C:\charm-crypto\misc\"
  ;SetOutPath "$INSTDIR\private"
  ;File "C:\charm-crypto\private"
  SetOutPath "$INSTDIR\share"
  File /r "C:\charm-crypto\share\"
  SetOutPath "$INSTDIR"
  File "C:\charm-crypto\openssl.cnf"  
  ; Using EnvVarUpdate here:
  ; http://nsis.sourceforge.net/Environmental_Variables:_append,_prepend,_and_remove_entries
  ; Warning about setting path, if you already have a crowded PATH it could mess it up.
  ; So I am going to write the original path to charm-crypto  
  Exec "echo %PATH% > $INSTDIR\old-path.txt"
  ${EnvVarUpdate} $0 "PATH" "A" "HKLM" "$INSTDIR\bin"
  
  CreateDirectory "$SMPROGRAMS\charm-crypto"
  CreateShortCut "$SMPROGRAMS\charm-crypto\uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section /o "" python32_detected
  SetOutPath "$Python32Dir\Charm_Crypto-${PRODUCT_VERSION}-py3.2-win32.egg"
  SetOverwrite try
  ; Install on dev machine, then run the NSI script.
  File /r "C:\Python32\Lib\site-packages\Charm_Crypto-${PRODUCT_VERSION}-py3.2-win32.egg\"
  ;
  ; Notice how we split the schemes up, we should fix this.
  ; Also need to split out Adapters. 
  ;
  SetOutPath "$INSTDIR\charm-usr-3.2\test"
  File /r "C:\Python32\Lib\site-packages\Charm_Crypto-${PRODUCT_VERSION}-py3.2-win32.egg\charm\test\"
  SetOutPath "$INSTDIR\charm-usr-3.2\schemes"
  File /r "C:\Python32\Lib\site-packages\Charm_Crypto-${PRODUCT_VERSION}-py3.2-win32.egg\charm\schemes\"  
  SetOutPath "$INSTDIR\charm-usr-3.2\adapters"
  File /r "C:\Python32\Lib\site-packages\Charm_Crypto-${PRODUCT_VERSION}-py3.2-win32.egg\charm\adapters\"
  SetOutPath "$Python32Dir"
  SetOverwrite ifnewer
  ; Need to have charm.pth to specify charm egg to PYTHONPATH.
  File "C:\Python32\Lib\site-packages\charm.pth"
  ; Now bundling pyparsing, current version 1.5.6
  File "C:\Python32\Lib\site-packages\pyparsing-1.5.6-py3.2.egg-info"   
  File "C:\Python32\Lib\site-packages\pyparsing.py"
  
  CreateShortCut "$SMPROGRAMS\charm-crypto\charm-usr-3.2.lnk" "$INSTDIR\charm-usr-3.2"
SectionEnd

Section /o "" python27_detected
  SetOutPath "$Python27Dir\Charm_Crypto-${PRODUCT_VERSION}-py2.7-win32.egg"
  SetOverwrite try
  File /r "C:\Python27\Lib\site-packages\Charm_Crypto-${PRODUCT_VERSION}-py2.7-win32.egg\"
  ;
  ; Notice how we split the schemes up, we should fix this.
  ; Also need to split out Adapters. 
  ;
  SetOutPath "$INSTDIR\charm-usr-2.7\test"
  File /r "C:\Python27\Lib\site-packages\Charm_Crypto-${PRODUCT_VERSION}-py2.7-win32.egg\charm\test\"
  SetOutPath "$INSTDIR\charm-usr-2.7\schemes"
  File /r "C:\Python27\Lib\site-packages\Charm_Crypto-${PRODUCT_VERSION}-py2.7-win32.egg\charm\schemes\"
  SetOutPath "$INSTDIR\charm-usr-2.7\adapters"
  File /r "C:\Python27\Lib\site-packages\Charm_Crypto-${PRODUCT_VERSION}-py2.7-win32.egg\charm\adapters\"
  SetOutPath "$Python27Dir"
  SetOverwrite ifnewer
  ; Need to have charm.pth to specify charm egg to PYTHONPATH.
  File "C:\Python27\Lib\site-packages\charm.pth"  
  ; Now bundling pyparsing, current version 1.5.6
  File "C:\Python27\Lib\site-packages\pyparsing-1.5.6-py2.7.egg-info"  
  File "C:\Python27\Lib\site-packages\pyparsing.py"  
  
  CreateShortCut "$SMPROGRAMS\charm-crypto\charm-usr-2.7.lnk" "$INSTDIR\charm-usr-2.7"  
SectionEnd

Section -AdditionalIcons
  CreateDirectory "$SMPROGRAMS\charm-crypto"
  CreateShortCut "$SMPROGRAMS\charm-crypto\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${python32_detected} "$(^Name) will be installed as a site-package of Python3.2"
  !insertmacro MUI_DESCRIPTION_TEXT ${python27_detected} "$(^Name) will be installed as a site-package of Python2.7"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Installation Callback Functions ------
; Callback function to ensure we have python installed, and that
; we can identify a python directory for installation.  This should
; allow Windows users to install for both 3.2 and 2.7.
Function .onInit
  ; Always uninstall before installing the latest version.
  ReadRegStr $R0 HKLM \
  "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
  "UninstallString"
  StrCmp $R0 "" checkPython
 
  MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
  "${PRODUCT_NAME} is already installed. $\n$\nClick `OK` to remove the \
  previous version or `Cancel` to cancel this upgrade." \
  IDOK uninst
  Abort
 
; Run the uninstaller.
uninst:
  ClearErrors
  Exec $INSTDIR\uninst.exe ; instead of the ExecWait line

; Check for python installation and version.
checkPython:
    StrCpy $9 "Lib\site-packages"

    ; This should allow installation on Windows 8.
	${If} ${RunningX64}
		ReadRegStr $8 HKLM "SOFTWARE\Wow6432Node\Python\PythonCore\3.2\InstallPath" ""
	${Else}
		ReadRegStr $8 HKLM "SOFTWARE\Python\PythonCore\3.2\InstallPath" ""
	${EndIf}
    StrCmp $8 "" tryPython27 hasPython32
tryPython27:
	${If} ${RunningX64}
		ReadRegStr $8 HKLM "SOFTWARE\Wow6432Node\Python\PythonCore\2.7\InstallPath" ""
	${Else}
		ReadRegStr $8 HKLM "SOFTWARE\Python\PythonCore\2.7\InstallPath" ""
	${EndIf}
    StrCmp $8 "" noPython hasPython27
noPython:
    MessageBox MB_OK "Python version(s) 3.2 / 2.7 not found, the installation will now abort."
    Abort ; We obviously don't want to install if python isn't installed.
hasPython32:
    StrCpy $Python32Dir $8$9
	SectionSetText ${python32_detected} "Python32"
    !insertmacro SelectSection ${python32_detected}
    ReadRegStr $8 HKLM "SOFTWARE\Python\PythonCore\2.7\InstallPath" ""
    StrCmp $8 "" done hasPython27
hasPython27:
    StrCpy $Python27Dir $8$9
	SectionSetText ${python27_detected} "Python27"	
    !insertmacro SelectSection ${python27_detected}
done:
    ;Debug =)
    ;MessageBox MB_OK $Python27Dir
    ;MessageBox MB_OK $Python32Dir
FunctionEnd
; End .onInit

; Callback function to inform the user which Python versions are
; acceptable for CHARM.
Function .onInstFailed
    MessageBox MB_OK "Python version(s) 3.2 / 2.7 not found, the installation will now abort."
FunctionEnd

; Callback function to query the user to check out the website.
; TODO
Function .onInstSuccess
     MessageBox MB_YESNO "You have successfully installed Charm-Crypto!  Would you like to visit the home page?" IDNO NoReadme
          Exec 'C:\Program Files\Internet Explorer\iexplore.exe ${PRODUCT_WEB_SITE}'
     NoReadme:
FunctionEnd
; Installation Callback Functions end ------

; unInstallation Callback Functions ------
Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd
; unInstallation Callback Functions end ------

; My first attempt to make this less painful than the installation bulk above...
; simple remove the top most dir, and be done with it.
Section Uninstall

  ; Uninstall charm directory.
  Delete "$INSTDIR\uninst.exe"
  Delete "$SMPROGRAMS\charm-crypto\Uninstall.lnk" 
  RMDir /r "$SMPROGRAMS\charm-crypto"
  RMDir /r "$INSTDIR"
  ${un.EnvVarUpdate} $0 "PATH" "R" "HKLM" "$INSTDIR\bin" 
  
  StrCpy $9 "Lib\site-packages"
	${If} ${RunningX64}
		ReadRegStr $8 HKLM "SOFTWARE\Wow6432Node\Python\PythonCore\3.2\InstallPath" ""
	${Else}
		ReadRegStr $8 HKLM "SOFTWARE\Python\PythonCore\3.2\InstallPath" ""
	${EndIf}  
  ; Depending on what version of python you installed, uninstall.
  StrCmp $8 "" tryPython27 hasPython32
  tryPython27:
	${If} ${RunningX64}
		ReadRegStr $8 HKLM "SOFTWARE\Wow6432Node\Python\PythonCore\2.7\InstallPath" ""
	${Else}
		ReadRegStr $8 HKLM "SOFTWARE\Python\PythonCore\2.7\InstallPath" ""
	${EndIf}  
	  StrCmp $8 "" done hasPython27
  hasPython32:
      StrCpy $Python32Dir $8$9  
      RMDir /r "$Python32Dir\Charm_Crypto-${PRODUCT_VERSION}-py3.2-win32.egg\"
	  Delete "$Python32Dir\charm.pth"
      ; Delete "$SMPROGRAMS\charm-crypto\schemes-py32.lnk" 	  	  
	  ReadRegStr $8 HKLM "SOFTWARE\Python\PythonCore\2.7\InstallPath" ""
	  StrCmp $8 "" done hasPython27
  hasPython27:
      StrCpy $Python27Dir $8$9
      RMDir /r "$Python27Dir\Charm_Crypto-${PRODUCT_VERSION}-py2.7-win32.egg\"
	  Delete "$Python27Dir\charm.pth"
	  ; Delete "$SMPROGRAMS\charm-crypto\schemes-py27.lnk"
  done:
      ;Don't do anything when done.
  
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  SetAutoClose true
SectionEnd