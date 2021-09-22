import HTMLString
import os
import UIKit

// When an app update ships with a new database, either because the dictionary
// was updated or migrations were added, we need to copy it into place. But
// we don’t want to do that on every launch because it would be slow.
//
// So the code will check whether the version number saved into a file matches.
//
// This could be automated by comparing query results between the database
// file shipped with the app and the writable copy in the “Application Support”
// directory.
let CURRENT_DB_VERSION = "1"

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

        setenv("MORPHODICT_ENV_FILE_PATH",
               applicationSupportDirectory.appendingPathComponent(".env").path,
               1)
        morphodict_register_callback("serve", serveCallback)

        let pyq = DispatchQueue(
            label: "python server", qos: .userInitiated, attributes: [],
            autoreleaseFrequency: .inherit, target: .none)
        pyq.async {
            morphodict_register_callback("hello") { print("Hello from swift") }

            do {
                try self.setupDatabase()
            } catch {
                self.handleError(error)
                return
            }

            runPython()
            os_log("runPython finished", log: log)
        }

        return true
    }

    func setupDatabase() throws {
        let dbDirectory = try createDbDirectory()

        let dbFile = dbDirectory.appendingPathComponent("db.sqlite3")
        let dbVersionFile = dbDirectory.appendingPathComponent("db_version")

        func dbFileNeedsUpdate() -> Bool {
            if !fm.fileExists(atPath: dbFile.path) {
                os_log("database file copy does not exist", log: log)
                return true
            }

            if !fm.fileExists(atPath: dbVersionFile.path) {
                os_log("database version file does not exist", log: log)
                return true
            }

            if let savedVersion = try? String(contentsOf: dbVersionFile) {
                os_log("previous database version: %s", log: log, savedVersion)
                return savedVersion != CURRENT_DB_VERSION
            }

            // reading dbVersionFile failed, so try to update
            return true
        }

        if dbFileNeedsUpdate() {
            os_log("Copying database to %@", log: log, dbFile.description)

            let bundle = Bundle(for: Self.self)
            let includedDb = bundle.url(
                forResource: "db-mobile", withExtension: "sqlite3")!
//            try fm.removeItem(at: dbFile)
            try fm.copyItem(at: includedDb, to: dbFile)
            try CURRENT_DB_VERSION.write(to: dbVersionFile, atomically: false, encoding: .utf8)
        }
        setenv("DATABASE_URL", "sqlite://\(dbFile.path)", 1)
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
