import UIKit
import WebKit

class ViewController: UIViewController {
    @IBOutlet var titleLabel: UINavigationItem!
    @IBOutlet var webView: WKWebView!

    @IBAction func homeButtonAction(_: UIButton) {
        goHome()
    }

    init() {
        super.init(nibName: "main", bundle: Bundle.main)
    }

    @available(*, unavailable)
    required init?(coder _: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    func goHome() {
        titleLabel.title = "itwêwina offline"
        let request = URLRequest(url: URL(string: "http://127.0.0.1:4828/")!)
        webView.load(request)
    }

    override func viewDidLoad() {
        titleLabel.title = "Loading…"
        makeWebViewOfflineOnly()
    }
    
    func makeWebViewOfflineOnly() {
        let blockRules = """
        [
            {
                "trigger": {
                    "url-filter": ".*"
                },
                "action": {
                    "type": "block"
                }
            },
            {
                "trigger": {
                    "url-filter": "http://127\\\\.0\\\\.0\\\\.1:4828/.*"
                },
                "action": {
                    "type": "ignore-previous-rules"
                }
            }
        ]
        """
        let configuration = webView.configuration
        
        // there's a race condition here, but we're choosing to ignore it for now
        WKContentRuleListStore.default().compileContentRuleList(
            forIdentifier: "ContentBlockingRules",
            encodedContentRuleList: blockRules
        ) { contentRuleList, error in
            if let error = error {
                // Handle error
                print(error)
            } else if let contentRuleList = contentRuleList {
                configuration.userContentController.add(contentRuleList)
                print("Added contentRuleList")
            } else {
                print("No contentRuleList")
                return
            }
        }
    }
}
