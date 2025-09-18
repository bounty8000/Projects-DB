# EmptyReforgerCache (Windows)

**One-click batch file to clear NVIDIA's DXCache** to reduce **intermittent 5–10s stutters** during long ARMA: Reforger sessions.  
This is a **workaround**, not a permanent fix.

> TL;DR: Reforger can leak/balloon VRAM/cache usage over time. When the shader cache fills or churns, some systems hitch hard. Clearing `DXCache` delays the stutters from building up again.

---

## Why this exists

- **Observed behavior**: In longer Arma Reforger sessions, even on high-end GPUs, some users see periodic freezes/stutters (5–10s) that resolve and then return.  
- **Likely cause**: Shader cache growth / memory pressure (effectively a leak-like profile).  
- **Workaround**: Clear the NVIDIA **DirectX shader cache** to buy time before the stutters return.  
- **Real fix**: Bohemia patches the underlying issue as development continues, or use a GPU with **more VRAM**.

> This script **only** removes the shader cache. The next game launch may briefly recompile shaders; initial minutes may show minor shader-compilation hitches (normal).

---

## What it does

Deletes **contents** of:
%LOCALAPPDATA%\NVIDIA\DXCache

It does **not** remove the DXCache directory itself.


## Usage
1. **Download** `EmptyReforgerCache.bat` from this repo.
2. Edit with Notepad and change <User
3. **Close ARMA: Reforger** (and any NVIDIA-heavy apps).
4. **Double-click** the `.bat` file.  
   - A console window will confirm the folder and deletion.
5. **Launch the game** again.

> Optional: Make a Desktop shortcut to the `.bat` for quick use.
> Clear cache prior to game start for best performance.
> Note: Not all shaders files will be deleted, only the non-essentials

## Safety notes
- This permanently deletes cached files (no Recycle Bin).
- Don’t run it while the game is running—files may be locked or immediately refilled.
- Clearing cache may cause short shader recompiles on next launch (normal).

## Troubleshooting
- “Folder not found”: You might be on AMD, or NVIDIA changed the path. Check:
%LOCALAPPDATA%\NVIDIA\DXCache
- “Access denied / files locked”: Ensure the game and overlay apps are closed (GeForce Experience, NV Broadcast, etc.).

## Script contents
```bat
@echo off
setlocal
title Empty NVIDIA DXCache (ARMA: Reforger workaround)
set "FOLDER=%LOCALAPPDATA%\NVIDIA\DXCache"
if not exist "%FOLDER%" (
  echo DXCache folder not found: "%FOLDER%"
  echo Nothing to do.
  goto :EOF
)
echo Emptying: "%FOLDER%"
del /f /q "%FOLDER%\*.*" 2>nul
for /d %%p in ("%FOLDER%\*") do rmdir /s /q "%%p" 2>nul
echo Done. Cache cleared.
timeout /t 2 >nul
endlocal
