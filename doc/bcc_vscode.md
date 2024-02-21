

#### python debug 
* need super-user privileges to run
```
Exception has occurred: Exception
Need super-user privileges to run
  File "/home/jhyunlee/code/eBPF/bcc/examples/tracing/hello_fields.py", line 18, in <module>
    b.attach_kprobe(event=b.get_syscall_fnname("clone"), fn_name="hello")
Exception: Need super-user privileges to run
```
* setup vscode launch.json : sudo 가능하게 디버깅 하는 방법
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: sudo Run",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "python": "python3",
            "sudo": true,
            "justMyCode": false,
            //"console": "internalConsole",               
            "console": "integratedTerminal",            
            "args": [
                "-v",
                "-s",
                "--debuglevel==DEBUG"
            ]
        }
    ]
}
```

##### error 

```
E+00000.142: /handling #1 request "launch" from Adapter/
             Handler 'launch_request' (file '/home/jhyunlee/.vscode/extensions/ms-python.debugpy-2024.0.0-linux-x64/bundled/libs/debugpy/adapter/../../debugpy/launcher/../../debugpy/launcher/handlers.py', line 14)
             couldn't handle #1 request "launch" from Adapter:
             Couldn't spawn debuggee: [Errno 2] 그런 파일이나 디렉터리가 없습니다: '/usr/bin/sudo python3'
             
             Command line:['/usr/bin/sudo python3', '/home/jhyunlee/.vscode/extensions/ms-python.debugpy-2024.0.0-linux-x64/bundled/libs/debugpy/adapter/../../debugpy/launcher/../../debugpy', '--connect', '127.0.0.1:40107', '--configure-qt', 'none', '--adapter-access-token', '0f9896237c58c5812d135e37850c9c0f802e69b3bb5c148d25abc0b3e50fe95b', '/home/jhyunlee/code/eBPF/hello_fields.py']
```

#### python setting in vscode
```json
{
    "files.autoSave": "afterDelay",
    "cmake.configureOnOpen": true,
    "http.proxyStrictSSL": false,
    "http.proxyAuthorization": null,
    "workbench.settings.applyToAllProfiles": [],
    "editor.formatOnSave": true,
    "editor.formatOnPaste": true,
    "editor.formatOnType": true,
    "typescript.format.placeOpenBraceOnNewLineForFunctions": true,
    "python.experiments.optInto": [],
    "python.analysis.diagnosticSeverityOverrides": {},
    "python.experiments.optOutFrom": [],
    "[python]": {"editor.defaultFormatter": "ms-python.black-formatter"},
    "editor.defaultFoldingRangeProvider": "ms-python.black-formatter",
    "json.schemas": [],
    "editor.largeFileOptimizations": false,
    "[sql]": {
        "editor.defaultFormatter": "inferrinizzard.prettier-sql-vscode"
    },
    "window.zoomLevel": 1
}
```