; 脚本由 Inno Setup 脚本向导 生成！
; 有关创建 Inno Setup 脚本文件的详细资料请查阅帮助文档！

#define MyAppName "签名加解密工具"
;#define MyAppName "CCS Service Data Analyzer"
#define MyAppVersion "1.0"
#define MyAppPublisher "华为技术有限公司"
#define MyAppURL "http://www.huawei.com/"
#define MyAppExeName "mainWnd.exe"

[Setup]
; 注: AppId的值为单独标识该应用程序。
; 不要为其他安装程序使用相同的AppId值。
; (生成新的GUID，点击 工具|在IDE中生成GUID。)
AppId={{A81F8361-2F65-4A59-926D-D60BEDA00CBB}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\cryptTool
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputBaseFilename={#MyAppName}
Compression=lzma/ultra64
SolidCompression=yes
SetupIconFile=res.dll
UninstallDisplayIcon=res.dll

[Languages]
;Name: english; MessagesFile: "compiler:Languages\English.isl"
Name: chinesesimp; MessagesFile: "compiler:Default.isl"

[Tasks]
;; OnlyBelowVersion: 0,6.1
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
;Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "D:\code\encrypt\dist\mainWnd.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\code\encrypt\dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; 注意: 不要在任何共享系统文件上使用“Flags: ignoreversion”

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
;Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
;Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon
Name: "{userdesktop}\{#MyAppName}";Filename: "{app}\{#MyAppExeName}";WorkingDir: "{app}";IconFilename:{app}\{#MyAppExeName};Comment:{#MyAppName};Tasks: desktopicon
 

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

