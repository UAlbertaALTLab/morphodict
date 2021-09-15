import os
import UIKit
import WebKit

class ViewController: UIViewController, WKNavigationDelegate {
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

        webView.navigationDelegate = self
    }

    func webView(_: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        let url = navigationAction.request.url!
        if url.absoluteString.hasPrefix("http://127.0.0.1:4828/")
            || url.absoluteString == "about:blank"
        {
            decisionHandler(.allow)
        } else {
            promptToOpenInSafari(url: url.absoluteString)
            decisionHandler(.cancel)
        }
    }

    func promptToOpenInSafari(url: String) {
        let controller = UIAlertController(
            title: "This link goes outside the app",
            message: url,
            preferredStyle: .actionSheet)

        controller.addAction(UIAlertAction(
            title: "Open in Safari", style: .default) { _ in
                UIApplication.shared.open(URL(string: url)!, options: [:])
        })

        controller.addAction(
            UIAlertAction(title: "Cancel",
                          style: .cancel) { _ in
                self.dismiss(animated: true)
            })

        present(controller, animated: true)
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
            encodedContentRuleList: blockRules) { contentRuleList, error in
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
