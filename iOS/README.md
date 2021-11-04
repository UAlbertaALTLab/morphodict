To get an offline mobile app without having to re-implement all the
functions of the django webapp, this application takes the novel approach
of running the django server itself on iOS.

# Theory of building open-source C/C++ packages for iOS

Xcode supports, as a very normal matter of course, having C/C++ files in
projects. You just create new files in Xcode, or drag and drop existing
ones into the project. Xcode automatically compiles C/C++ code for both the
simulator and devices, and C/C++ functions compiled that way are accessible
from the Objective C and Swift code more typically used for iOS
applications.

However, Xcode does not directly support building non-trivial open-source
unix-style C/C++ packages for iOS. Packages like python have complicated
configuration processes, custom build setups, and rely on a bunch of other
C/C++ dependencies. Those are all things that Xcode doesn’t directly
support.

For incorporating those packages into iOS applications, the process
for each packages is:

 1. Build the code as a static library multiple times, at least once for
    the simulator and at least once for physical devices.

    If the library supports a GNU Autotools-style build, this involves
    building the same code multiple times into different target
    directories, with different `configure` calls that’ll cause it to use
    different platform-specific headers, cross-compilers, and linker
    options.

    You’ll need to build against at least the simulator SDK and the iOS
    device SDK. The simulator SDK currently comes in both Apple Silicon and
    x86 versions, so you can/should have three builds here.

    Right now there is only one iOS device SDK. But in the past the iOS
    device SDK has come in additional variants, such as 32-bit vs 64-bit
    and armv6 vs armv7, so it is likely that someday in the future it will
    be necessary to support multiple iOS device SDKs again.

 2. Link the resulting static library files together into a single ‘fat’
    multi-architecture aka universal static library file. The lipo(1) tool
    is useful for this.

 3. That single ‘fat’ static library file can then be dragged-and-dropped
    into the Xcode project where it will be linked into the iOS
    application. Platform-specific headers [are doable
    too][platform-specific-headers].

[platform-specific-headers]: https://stackoverflow.com/questions/1474315/iphone-xcode-search-path-for-device-vs-simulator/1474747#1474747

Rather than doing all of that manually, or writing our own tooling to do
it, we use the kivy-ios tooling.

## kivy-ios

The pre-existing [kivy-ios] package already supports building and running
Python on iPhones and other apple devices. It handles the automation of the
steps described above for Python and its prerequisites such as OpenSSL.

[kivy-ios]: https://github.com/kivy/kivy-ios

kivy is a general-purpose multiplatform GUI framework, but the *only* thing
we are using from it is the stuff that compiles Python for iPhone.

# Prerequisites

You’ll need a mac with python 3.9, pipenv, git-lfs, node, and Xcode all
installed.

  - You’ll also need `db-mobile.sqlite3`, created by doing a full import of
    the normal dictionary using the normal process and making a copy of
    db.sqlite3, but with the hacks on this branch that disable wordform
    instantiation and phrase translation.

 - Also run `npx rollup -c` and `./crkeng-manage collectstatic` to build
   all the static assets, just as you would when developing the non-mobile
   version.

# Steps to build

 1. First, you need kivy to build.

         cd morphodict/iOS
         git clone https://github.com/UAlbertaALTLab/kivy-ios

    Normally at this point you’d use the kivy-ios tools to build python
    repeatedly. But our fork uses git-lfs to store pre-compiled files, so
    you shouldn’t need to do anything more here. That said, if you `cd`
    into this directory, open a pipenv shell, then `./kivy-toolchain` will
    let you rebuild python &c.

 2. In the `iOS` directory, run `./do-pip-install` to install the required
    libraries from `mobile-requirements.txt` into the virtualenv that Xcode will
    copy into the iOS application bundle.

 3. Open `iOS/app/itwewina-offline.xcodeproj` in Xcode, build it and run
    it.

## Building the mobile database

This magic lets you access a mobile database:

    USE_TEST_DB=False \
    DATABASE_URL=sqlite:///src/crkeng/db/db-mobile.sqlite3 \
    ./crkeng-manage …

For example, you can update the dictionary database with:

    USE_TEST_DB=False \
    DATABASE_URL=sqlite:///src/crkeng/db/db-mobile.sqlite3 \
    ./crkeng-manage importjsondict \
    --incremental --no-translate-wordforms --atomic --purge

This could definitely be scripted.

## Potential problems

  - Error claims that `"iphonesimulator" cannot be located`

        xcrun: error: SDK "iphonesimulator" cannot be located
        xcrun: error: unable to lookup item 'Path' in SDK 'iphonesimulator'

    The homebrew installation process downloads a new mac-only set of
    developer tools and makes them the default, even if you already have
    Xcode installed.

    Try running

        sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer

    to switch the system default developer tools back to ones that support
    iOS development.

  - Help! The app works fine when deployed from Xcode, but not through
    TestFlight!

    It may not cover *every* possible case, but at least once, [using a
    release build instead of a debug one][TestFlight-troubleshooting] for
    running the application has reproduced the issue, allowing both quick
    iteration on the code and the ability to stop and breakpoints to
    investigate and resolve the issue.

[TestFlight-troubleshooting]: https://stackoverflow.com/questions/55759806/how-can-i-attach-to-released-in-the-testflight-application-to-debug

# How the app works

The `kivy-toolchain` command can create a new Xcode starter project for
you. It’s intended for using with kivy, which runs on top of Python. So it
includes Python, but because it expects you to use the kivy framework for
all the GUI stuff, it leaves out all the typical boilerplate UI code you’d
have in a normal IOS app. This generated code is also written in
Objective-C instead of the newer Swift.

The current demo was created by creating default starter projects with both
`kivy-toolchain` and the standard Xcode process, and using the
kivy-generated project with some of the kivy-specific stuff removed and the
some of standard Xcode stuff added in.

On startup, the iOS app does the following:

  - The boilerplate kivy-ios Objective-C code calls some of our custom
    swift code:

      - That swift code creates a writable user directory to hold the database

      - It then copies the default database file from the app bundle to
        the writable user directory, if it’s already there

  - There’s currently also some custom Objective-C code in there to
    register our custom modules with Python before the Python interpreter
    starts running.

  - The kivy boilerplate code starts running python in a background thread,
    and runs our `mobile.py` python code.

  - `mobile.py` does `django.setup()`, then calls `runserver`

  - On the main thread, normal iOS code written in Swift takes over to
    display a GUI: a web view. When django is ready, it sends a signal to
    the swift code which loads the internal django server’s home page.

# Hacks to get the demo working that are broken / wrong / embarrassing

These are things that would typically be addressed in due course, if
dedicating time to making the project maintainable:

  - kivy is supposed to be a package manager that lets you write recipes to
    automatically build Python packages that have C extensions. I couldn’t
    figure out how to get this working with hfst-optimized-lookup,
    so Xcode builds the C/C++ files from the `site_packages` directory.

  - For python modules where we haven’t done the work to make the C
    extensions compile, there are ‘fake’ packages in `iOS/fakes`,
    so that you can still `import` libraries that aren’t available,
    even though configuration will prevent you from using them.

  - I also couldn’t figure out how to get kivy’s pyobjus library working.
    That’s supposed to let Python code call Objective-C/Swift code; instead
    there’s a custom, very basic mechanism to register callbacks.

  - The `sync-python` script that copies python code and assets from the
    morphodict `src` directory is very rough; it has comments with
    suggestions for improvement.

  - File names and directory structure have not been refined

  - Often `black` will search for python files inside the installed
    packages for the iOS app, making PyCharm extremely slow and breaking
    submit hooks. Hopefully there are some configuration option that can
    address this.

## Things that don’t work

  - affix search: uses library with C code, would need to figure out how to
    build

  - cosine vector distance: in addition to memory concerns, requires
    libraries with C extensions

  - phrase translation: uses foma FSTs, which would require figuring out
    how to build foma for iOS

## Future stuff

  - The core of the app is a web view. There are various things we could
    there. See [the “Web Views” chapter of *Programming iOS
    14*][webviews-chapter] for some of the capabilities of web vies.

    In particular, the web view and the django app can likely talk to each
    other through a custom scheme instead of a TCP socket.

[webviews-chapter]: https://learning.oreilly.com/library/view/programming-ios-14/9781492092162/part02ch07.html#chap_id24

# Submitting the app

To do this, you’ll need an organization-specific ‘Distribution’
certificate, with the private key, in your keychain. Get it from someone
who already has it. They can go into Keychain Access → My Certificates,
right-click it, and export.

You can, technically, also create a new one in App Store connect, or even
have Xcode create one automatically, but the organization account is
limited to only three distribution certificates. If you remove existing
distribution certificates to make room for new ones, it *will* work for
you, but Apple will mark those removed certificates as ‘revoked,’ causing
all sorts of mysterious errors for other people who were using them
successfully.

 1. First, to upload a new build, you’ll need to increment the build
    number. Select the project in the project navigator; click the target,
    and then under General, increment the build number.

    If you update the version number, that triggers a time-consuming
    re-review from Apple, even if the build is only intended for external
    TestFlight users.

    So you should only update the build number, not the version number.
    However, once the app makes it into a public app store, new version
    numbers will be required for every release that goes to the public app
    store.

 2. Make sure the selected device is “Any iOS Device” and not a specific
    device or simulator

 3. Do Build → Archive

 4. Follow the steps, accepting the defaults. Try to have Xcode do the
    signing automatically. But if it fails, choose the “Manually manage
    signing” option, click the Download Profile option, and choose the
    “itwêwina offline” profile.

    For more about certificate types, provisioning profiles, &c., see the
    “Running on a device” section of the “Life Cycle of a Project” chapter
    of
    [Neuberg](https://learning.oreilly.com/library/view/ios-14-programming/9781492092087/part02ch04.html#idm45495341795176).

 5. Wait for the app to finish processing. [`watchbuild`] is a handy tool
    for this.

 6. In App Store Connect, find the app, click on the TestFlight tab, click
    on each group of internal or external testers you want to release the
    build to, and click the + sign under ‘Builds.’

[`watchbuild`]: https://github.com/fastlane/watchbuild
