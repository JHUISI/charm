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
; added all the bloat to this installer as it includes openssl, gmp, pbc.  You
; will have to install pyparsing on your own.
;
; Future Improvements:
; Support a branch on the interpreter installs such that libmiracl is supported.
;
; Author: Michael Rushanan (micharu1@cs.jhu.edu)
; Date: 09/2011
;
; --------------------------------

!define PRODUCT_NAME "charm-crypto"
!define PRODUCT_VERSION "0.2"
!define PRODUCT_PUBLISHER "Johns Hopkins University, HMS Lab"
!define PRODUCT_WEB_SITE "http://charm-crypto.com/Main.html"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

;bzip2 is an option
SetCompressor lzma



; MUI 1.67 compatible ------
!include "MUI.nsh"
!include "Sections.nsh"
!include "EnvVarUpdate.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "Charm-Package.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "gpl_v3.txt"
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
Var Python32Dir
Var Python27Dir
!define Python32Exe "$Python32Dir\python.exe"
!define Python27Exe "$Python27Dir\python.exe"
; Globals end ------



Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "charm-crypto.exe"
; We won't be using $PROGRAMFILES because that seems to break things.
; Also, will be using python dirs instead of $INSTDIR
InstallDir "C:\charm-crypto"
ShowInstDetails show
ShowUnInstDetails show


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
  ;SetOutPath "$INSTDIR\tests"
  ;File /r /x "C:\MinGW\msys\1.0\home\dev\charm-crypto\tests\.svn\" "C:\MinGW\msys\1.0\home\dev\charm-crypto\tests\"
  SetOutPath "$INSTDIR"
  File "C:\charm-crypto\openssl.cnf"  
  ; Using EnvVarUpdate here:
  ; http://nsis.sourceforge.net/Environmental_Variables:_append,_prepend,_and_remove_entries
  ; Warning about setting path, if you already have a crowded PATH it could mess it up.
  ; So I am going to write the original path to charm-crypto  
  nsExec::Exec 'echo %PATH% > $INSTDIR\old-path.txt'
  ${EnvVarUpdate} $0 "PATH" "A" "HKLM" "$INSTDIR\bin"
  
  CreateDirectory "$SMPROGRAMS\charm-crypto"
  CreateShortCut "$SMPROGRAMS\charm-crypto\uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section /o "Python32" python32_detected
  SetOutPath "$Python32Dir\charm"
  SetOverwrite try
  File /r "C:\Python32\Lib\site-packages\charm\"
  SetOutPath "$Python32Dir\compiler"
  File /r "C:\Python32\Lib\site-packages\compiler\"
  SetOutPath "$Python32Dir\schemes"
  File /r "C:\Python32\Lib\site-packages\schemes\"
  SetOutPath "$Python32Dir\toolbox"
  File /r "C:\Python32\Lib\site-packages\toolbox\"
  SetOutPath "$Python32Dir"
  SetOverwrite ifnewer
  ; CHANGEME on every new release.
  File "C:\Python32\Lib\site-packages\Charm_Crypto-0.2-py3.2.egg-info"
SectionEnd

Section /o "Python27" python27_detected
  SetOutPath "$Python27Dir\charm"
  SetOverwrite try
  File /r "C:\Python27\Lib\site-packages\charm\"
  SetOutPath "$Python27Dir\compiler"
  File /r "C:\Python27\Lib\site-packages\compiler\"
  SetOutPath "$Python27Dir\schemes"
  File /r "C:\Python27\Lib\site-packages\schemes\"
  SetOutPath "$Python27Dir\toolbox"
  File /r "C:\Python27\Lib\site-packages\toolbox\"
  SetOutPath "$Python27Dir"
  SetOverwrite ifnewer
  ; CHANGEME on every new release.
  File "C:\Python27\Lib\site-packages\Charm_Crypto-0.2-py2.7.egg-info"
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
    StrCpy $9 "Lib\site-packages\"
    ReadRegStr $8 HKLM "SOFTWARE\Python\PythonCore\3.2\InstallPath" ""
    StrCmp $8 "" tryPython27 hasPython32
tryPython27:
    ReadRegStr $8 HKLM "SOFTWARE\Python\PythonCore\2.7\InstallPath" ""
    StrCmp $8 "" noPython hasPython27
noPython:
    MessageBox MB_OK "Python version(s) 3.2 / 2.7 not found, the installation will now abort."
    Abort ; We obviously don't want to install if python isn't installed.
hasPython32:
    StrCpy $Python32Dir $8$9
    !insertmacro SelectSection ${python32_detected}
    ReadRegStr $8 HKLM "SOFTWARE\Python\PythonCore\2.7\InstallPath" ""
    StrCmp $8 "" done hasPython27
hasPython27:
    StrCpy $Python27Dir $8$9
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
;Function .onInstSuccess
;     MessageBox MB_YESNO "You have successfully installed Charm-Crypto!  Would you like to visit the home page?" IDNO NoReadme
;          Exec 'C:\Program Files\Internet Explorer\iexplore.exe '
;     NoReadme:
;FunctionEnd
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
  
  ; Depending on what version of python you installed, uninstall.
  StrCmp $Python32Dir "" tryPython27 hasPython32
  tryPython27:
      StrCmp $Python27Dir "" done hasPython27
  hasPython32:
      RMDir /r "$Python32Dir\charm\"
	  RMDir /r "$Python32Dir\compiler\"
	  RMDir /r "$Python32Dir\schemes\"
	  RMDir /r "$Python32Dir\toolbox\"
      Delete "$Python32Dir\Charm_Crypto-0.2-py3.2.egg-info"
	  StrCmp $Python27Dir "" done hasPython27
  hasPython27:
      RMDir /r "$Python27Dir\charm\"
	  RMDir /r "$Python27Dir\compiler\"
	  RMDir /r "$Python27Dir\schemes\"
	  RMDir /r "$Python27Dir\toolbox\"  
      Delete "$Python27Dir\Charm_Crypto-0.2-py2.7.egg-info"
  done:
      ;Don't do anything when done.
  
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  SetAutoClose true
SectionEnd