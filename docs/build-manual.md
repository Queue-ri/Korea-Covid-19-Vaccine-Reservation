# How to Build Executable
## Windows
### Pyinstaller
- 빌드 속도는 `nuitka` 보다 빠르지만, 프로그램 실행 속도는 더 느립니다.
```cmd
> python -m pip install -r requirements.txt -r requirements-dev.txt
> pyinstaller --onefile cb.py
```

### Nuitka
- 빌드 속도는 `pyinstaller` 보다 느리지만, 프로그램 실행 속도는 더 빠릅니다.
```cmd
> python -m pip install nuitka zstandard -r requirements.txt
> nuitka --show-scons --no-progress --onefile -o cb.exe cb.py
```

## macOS
```sh
$ python -m pip install -r requirements.txt -r requirements-mac.txt -r requirements-dev.txt
$ pyinstaller --onefile cb.py
$ chmod +x dist/cb
```
