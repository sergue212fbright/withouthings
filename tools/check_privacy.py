#!/usr/bin/env python3
"""Check the Android privacy boundary, including an AGP-merged manifest when supplied."""

from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ANDROID = "{http://schemas.android.com/apk/res/android}"
manifest = ET.parse(sys.argv[1] if len(sys.argv) > 1 else ROOT / "app/src/main/AndroidManifest.xml").getroot()
permissions = {item.get(ANDROID + "name") for item in manifest.findall("uses-permission")}
for forbidden in ("MANAGE_EXTERNAL_STORAGE", "READ_EXTERNAL_STORAGE", "WRITE_EXTERNAL_STORAGE", "ACCESS_BACKGROUND_LOCATION"):
    assert "android.permission." + forbidden not in permissions, forbidden

application = manifest.find("application")
assert application is not None
assert application.get(ANDROID + "allowBackup") == "false", "Automatic backup must be disabled"
for kind in ("activity", "activity-alias", "service", "receiver", "provider"):
    for item in application.findall(kind):
        if item.get(ANDROID + "exported") == "true":
            launcher = kind == "activity" and item.get(ANDROID + "name") in (
                ".MainActivity", "dev.davidv.withoutings.MainActivity"
            )
            # AndroidX's profile receiver is restricted by a platform signature
            # permission; ordinary applications cannot invoke it.
            profiler = kind == "receiver" and item.get(ANDROID + "name") == (
                "androidx.profileinstaller.ProfileInstallReceiver"
            ) and item.get(ANDROID + "permission") == "android.permission.DUMP"
            assert launcher or profiler, "Unexpected exported component: " + str(item.attrib)

domains = {"root", "file", "database", "sharedpref", "external", "device_root", "device_file", "device_database", "device_sharedpref"}
for name, sections in (("backup_rules.xml", (".",)), ("data_extraction_rules.xml", ("cloud-backup", "device-transfer"))):
    rules = ET.parse(ROOT / "app/src/main/res/xml" / name).getroot()
    for path in sections:
        section = rules if path == "." else rules.find(path)
        assert section is not None, (name, path)
        excluded = {item.get("domain") for item in section.findall("exclude") if item.get("path") == "."}
        assert domains <= excluded, (name, path, domains - excluded)

print("Privacy boundary checks passed")
