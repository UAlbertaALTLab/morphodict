import HTMLString
import os
import UIKit

let log = OSLog(subsystem: "morphodict", category: "testing")

var appDelegate: AppDelegate?;

func serveCallback() {
    DispatchQueue.main.async {
        appDelegate?.viewController?.goHome()
    }
}

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    var window: UIWindow?
    var viewController: ViewController?
    private let fm = FileManager.default

    func application(_: UIApplication, didFinishLaunchingWithOptions _: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        window = window ?? UIWindow()
        appDelegate = self
        viewController = ViewController()
        window!.rootViewController = viewController
        window!.makeKeyAndVisible()

        swiftpy_register_callback("serve", serveCallback)

        DispatchQueue.global(qos: .userInitiated).async {
            swiftpy_register_callback("hello") { print("Hello from swift") }

            do {
                try self.setupDatabase()
            } catch {
                self.handleError(error)
                return
            }

            runPython()
        }

        return true
    }

    func setupDatabase() throws {
        let dbDirectory = try createDbDirectory()

        let dbFile = dbDirectory.appendingPathComponent("db.sqlite3")

        if !fm.fileExists(atPath: dbFile.path) {
            os_log("Copying database to %@", log: log, dbFile.description)

            let bundle = Bundle(for: Self.self)
            let includedDb = bundle.url(forResource: "db-mobile", withExtension: "sqlite3")!
            try fm.copyItem(at: includedDb, to: dbFile)
        }
        setenv("DATABASE_URL", "sqlite://\(dbFile.path)", 1)
    }

    /**
            Create `$APPLICATION_SUPPORT_DIR/db`
     */
    func createDbDirectory() throws -> URL {
        let applicationSupportDirectory = try fm.url(for: .applicationSupportDirectory, in: .userDomainMask, appropriateFor: nil, create: true)
        var dbDirectory = applicationSupportDirectory.appendingPathComponent("db", isDirectory: true)
        if !fm.fileExists(atPath: dbDirectory.path) {
            os_log("Creating db directory %@", log: log, dbDirectory.description)
            try fm.createDirectory(at: dbDirectory, withIntermediateDirectories: false, attributes: nil)
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
