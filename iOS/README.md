To get an offline mobile app without having to re-implement all the
functions of the django webapp, this application takes the novel approach
of running the django server itself on iOS.

**Note: this code is almost entirely still demo-quality.**

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

        cd cree-intelligent-dictionary/iOS
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

# Hacks to get the demo working that are broken / wrong / embarrassing

These are things that would typically be addressed in due course, if
dedicating time to making the project maintainable:

  - Instead of being configurable settings to enable/disable features,
    a bunch of code is just *commented out* to disable it for mobile.

    Some of these things get a little bit tricky: we can’t even `import`
    libraries that we haven’t gotten working on mobile, so we can’t use the
    normal django settings mechanism to skip calling something, as settings
    only get configured after most packages have already been imported, and
    it’s the import attempt that fails.

  - kivy is supposed to be a package manager that lets you write recipes to
    automatically build Python packages that have C extensions. I couldn’t
    figure out how to get this working with hfst-optimized-lookup, so I
    just dragged-and-dropped copies of the files into the Xcode project
    instead of using released versions from PyPI.

  - I also couldn’t figure out how to get that working with kivy’s pyobjus
    library, which is supposed to let Python code call Objective-C/Swift
    code; instead there’s a very basic mechanism to register callbacks.

  - Related to that same problem with fitting Python libraries that have C
    extensions into kivy, affix search was only disabled because I couldn’t
    get the library it uses to install.

  - The `sync-python` script that copies python code and assets from the
    morphodict `src` directory is very rough; it has comments with
    suggestions for improvement.

  - The `mobile-requirements.txt` file used by pip has pretty random
    versions of dependencies, instead of using versions that match what’s
    in the main Pipenv.

    (This is actually really easy, I should just fix it.)

  - File names and directory structure have not been refined

## Things that don’t work

  - affix search: uses library with C code, would need to figure out how to
    build

  - cosine vector distance: in addition to memory concerns, requires
    libraries with C extensions

  - phrase translation: uses foma FSTs, which would require figuring out
    how to build foma for iOS
