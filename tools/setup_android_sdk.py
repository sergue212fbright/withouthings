#!/usr/bin/env python3
"""Install pinned Google Android command-line tools on Linux build runners."""

import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import urllib.request
import zipfile

URL = "https://dl.google.com/android/repository/commandlinetools-linux-13114758_latest.zip"
SHA256 = "7ec965280a073311c339e571cd5de778b9975026cfcbe79f2b1cdcb1e15317ee"


def main():
    sdk = Path(os.environ["ANDROID_HOME"]).resolve()
    tools = sdk / "cmdline-tools" / "19.0"
    manager = tools / "bin" / "sdkmanager"
    if not manager.exists():
        sdk.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as work:
            archive = Path(work) / "tools.zip"
            with urllib.request.urlopen(URL, timeout=120) as source, archive.open("wb") as target:
                while chunk := source.read(1024 * 1024):
                    target.write(chunk)
            if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
                raise RuntimeError("Android command-line tools checksum mismatch")
            with zipfile.ZipFile(archive) as bundle:
                bundle.extractall(work)
            tools.parent.mkdir(parents=True, exist_ok=True)
            (Path(work) / "cmdline-tools").rename(tools)
        for executable in (tools / "bin").iterdir():
            executable.chmod(0o755)
    command = [str(manager), "--sdk_root=" + str(sdk)]
    subprocess.run(command + ["--licenses"], input="y\n" * 100, text=True, check=True)
    for package in ("platforms;android-35", "build-tools;35.0.0", "ndk;28.2.13676358"):
        subprocess.run(command + [package], check=True)


if __name__ == "__main__":
    main()
