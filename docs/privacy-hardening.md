# Privacy hardening test branch

This branch is for testing before merge or an upstream contribution. It preserves the watch protocol and keeps health history in Android's private database directory. Android's device encryption and app sandbox protect that directory; this is not a separate encrypted-vault implementation.

## Changes

- Remove the all-files permission and the storage permission gate.
- Store `watch.db`, its WAL, and its shared-memory sidecar in the app's private database directory.
- Disable automatic backup and explicitly exclude all storage domains from both cloud backup and device-to-device transfer. Pairing keys remain in private preferences and are excluded too.
- Make the workout command receiver private. An unrelated app must not start a workout or activate route recording through this app's location permission.
- Keep GPS routes and online maps off by default. Custom map providers must use HTTPS. Redirects are rejected, response bodies are capped at 1 MiB, and downloaded image dimensions are bounded. Map URLs containing credentials are rejected and provider URLs are not written to logs.
- Update rusqlite/SQLite, UniFFI, and JNA. Use the checked-in Cargo lockfile for Android builds and keep binding-generator dependencies out of the native app library.
- Restrict the preview/test activities added by debug dependencies. Check the merged manifest as well as the source manifest; AndroidX's platform-permission-protected profile receiver remains available to Android tools.

Online maps deliberately disclose the requested map areas and the phone's network address to the chosen provider. Keeping maps off avoids those requests. No Withings account or cloud sync is added.

## Existing installations and data

This is a clean-install test build. It does not automatically import the previous shared `Documents/withoutings/watch.db`. Existing shared files are left untouched; they remain outside the protection added here until their owner handles them. Preserve the database **and its WAL** before changing installations. Do not copy a database while the old app is recording or syncing.

Clearing app storage or uninstalling deletes private history and pairing keys. Installing a build signed with another key also requires uninstalling first. Automatic backup and external workout automation are intentionally unavailable in this branch. A user-controlled history export/import and a tested migration are follow-up work before recommending this change to existing upstream users.

## Build and checks

Use JDK 17 or newer supported by Gradle, Android SDK platform 35, build tools 35.0.0, and an Android NDK. Install stable Rust, the `aarch64-linux-android` target, and `cargo-ndk` 4.1.2. Set `ANDROID_HOME` and `ANDROID_NDK_HOME` for your installation.

On Linux, `python3 tools/setup_android_sdk.py` installs checksum-pinned Google command-line tools and the required SDK/NDK packages into `ANDROID_HOME`. This also works on runners where `sdkmanager` is no longer preinstalled.

```sh
rustup target add aarch64-linux-android
cargo install cargo-ndk --version 4.1.2 --locked
cargo test --workspace --locked
python3 tools/check_privacy.py
./gradlew :app:testDebugUnitTest :app:lintDebug :app:assembleDebug
```

The test APK is `app/build/outputs/apk/debug/app-debug.apk`. Keep its signing key for subsequent test builds so an update does not require deleting local history. A debug APK is for testing and is not a production release.

## Device test

1. Install the test APK and verify that there is no all-files access request.
2. Pair a ScanWatch 2 and check time, battery, steps, heart-rate history, and sync after restarting the app. Avoid resetting a watch with unsynced data.
3. Leave routes/maps off. On GrapheneOS, deny Network permission and check that Bluetooth sync still works.
4. Enable routes explicitly, grant location access, start a real outdoor workout, and confirm recording stops with the workout. Revoke location and confirm sync still works without routes.
5. Enable maps only if desired and verify that the privacy explanation is visible and tiles load. An HTTP provider URL must not be accepted.
6. While the watch is connected, an external workout broadcast must be denied:

   ```sh
   adb shell am broadcast -n dev.davidv.withoutings/.ipc.WorkoutRequestReceiver -a dev.davidv.withoutings.action.START_WORKOUT --ei dev.davidv.withoutings.extra.ACTIVITY 6
   ```

7. Install a second test build with the same signing key and check that pairing and history survive the update. Uninstalling is expected to erase both.

There has been no physical-watch test in the development environment. Do not merge or submit upstream until the device tests and the existing-user migration decision have been reviewed.
