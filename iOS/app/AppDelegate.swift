import HTMLString
import os
import UIKit

let log = OSLog(subsystem: "morphodict", category: "default")

var appDelegate: AppDelegate?
var serverHasBeenPreviouslyStarted = false

func serveCallback() {
    if !serverHasBeenPreviouslyStarted {
        DispatchQueue.main.async {
            appDelegate?.viewController?.goHome()
        }
    }
    serverHasBeenPreviouslyStarted = true
}

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    var window: UIWindow?
    var viewController: ViewController?
    private let fm = FileManager.default
    private let applicationSupportDirectory: URL

    override init() {
        applicationSupportDirectory = try! fm.url(
            for: .applicationSupportDirectory, in: .userDomainMask,
            appropriateFor: nil, create: true)

        super.init()
    }

    func application(_: UIApplication, didFinishLaunchingWithOptions _:
        [UIApplication.LaunchOptionsKey: Any]?) -> Bool
    {
        window = window ?? UIWindow()
        appDelegate = self
        viewController = ViewController()
        window!.rootViewController = viewController
        window!.makeKeyAndVisible()

        morphodict_register_callback("serve", serveCallback)

        let pyq = DispatchQueue(
            label: "python server", qos: .userInitiated, attributes: [],
            autoreleaseFrequency: .inherit, target: .none)
        pyq.async { [self] in
            morphodict_register_callback("hello") { print("Hello from swift") }

            do {
                try prePythonSetup()
            } catch {
                handleError(error)
                return
            }

            runPython()
            os_log("runPython finished", log: log)
        }

        return true
    }

    func prePythonSetup() throws {
        setenv("DJANGO_SETTINGS_MODULE",
               "\(String(cString: morphodict_sssttt())).site.settings_mobile", 1)
        setenv("MORPHODICT_ENV_FILE_PATH",
               applicationSupportDirectory.appendingPathComponent(".env").path,
               1)

        let dbDirectory = try createDbDirectory()

        setenv("MORPHODICT_DB_DIRECTORY", dbDirectory.path, 1)

        // Older versions of the app used this file; remove it if it is
        // still around.
        let dbVersionFile = dbDirectory.appendingPathComponent("db_version")
        if fm.fileExists(atPath: dbVersionFile.path) {
            try fm.removeItem(at: dbVersionFile)
        }

        let bundle = Bundle(for: Self.self)
        let includedDb = bundle.url(
            forResource: "db-mobile", withExtension: "sqlite3")!

        setenv("MORPHODICT_BUNDLED_DB", includedDb.path, 1)
    }

    /**
            Create `$APPLICATION_SUPPORT_DIR/db`
     */
    func createDbDirectory() throws -> URL {
        var dbDirectory = applicationSupportDirectory.appendingPathComponent("db", isDirectory: true)
        if !fm.fileExists(atPath: dbDirectory.path) {
            os_log("Creating db directory %@", log: log, dbDirectory.description)
            try fm.createDirectory(
                at: dbDirectory, withIntermediateDirectories: false,
                attributes: nil)
        }

        // don’t add the app’s database to user backups
        var resourceValues = URLResourceValues()
        resourceValues.isExcludedFromBackup = true
        try dbDirectory.setResourceValues(resourceValues)

        return dbDirectory
    }

    func handleError(_ error: Error) {
        let escapedDescription = String(describing: error).addingUnicodeEntities()

        DispatchQueue.main.async {
            self.viewController!.webView.loadHTMLString("""
            <!DOCTYPE html>
            <html>
              <head>
                <meta charset="UTF-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <meta name="referrer" content="no-referrer">
                <title> </title>
              </head>
              <body>
                <h1>Error</h1>

                <p>
                Unfortunately, an error occurred trying to set up the database.
                </p>

                <h3>Technical details</h3>
                <pre
                    style="border: 1px solid gray; float: left"
                >\(escapedDescription)</pre>
              </body>
            </html>
            """, baseURL: nil)
        }
    }

    func applicationDidEnterBackground(_: UIApplication) {
        morphodict_stop_server()
    }

    func applicationWillEnterForeground(_: UIApplication) {
        if serverHasBeenPreviouslyStarted {
            morphodict_resume_server()
        }
    }
}

struct MorphodictError: Error, CustomStringConvertible {
    let message: String
    let callStack: [String]

    init(_ message: String) {
        self.message = message
        // Capture call stack at error creation time
        callStack = Thread.callStackSymbols
    }

    var description: String {
        "\(message)\n\(callStack.joined(separator: "\n"))"
    }
}
