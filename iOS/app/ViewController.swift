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
        let product_names = ["crkeng": "itwêwina", "srseng": "Gūnáhà"]
        let name = product_names[String(cString: morphodict_sssttt()), default: "NAME ME"]
        titleLabel.title = "\(name) offline"
        let request = URLRequest(url: URL(string: "http://127.0.0.1:4828/")!)
        webView.load(request)
    }

    override func viewDidLoad() {
        titleLabel.title = "Loading…"
        makeWebViewOfflineOnly()

        webView.navigationDelegate = self
    }

    func webView(_: WKWebView,
                 decidePolicyFor navigationAction: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void)
    {
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

        var cancelButtonStyle: UIAlertAction.Style = .cancel

        // On iPadOS, iPhone-style action sheets aren’t directly supported.
        // The idea is to provide a popover, ideally pointing at the link that
        // was just tapped, and with any Cancel button automatically removed
        // on the assumption that you can tap elsewhere to close the popup.
        // https://developer.apple.com/documentation/uikit/windows_and_screens/getting_the_user_s_attention_with_alerts_and_action_sheets
        //
        // That gets a bit complicated so for now we simply do our best to mimic
        // an iPhone-style action sheet in the center of the view.
        if let popoverController = controller.popoverPresentationController {
            popoverController.sourceView = view
            popoverController.sourceRect = CGRect(
                x: view.bounds.midX, y: view.bounds.midY,
                width: 0, height: 0)
            popoverController.permittedArrowDirections = []
            cancelButtonStyle = .default
        }

        controller.addAction(UIAlertAction(
            title: "Open in Safari", style: .default) { _ in
                UIApplication.shared.open(URL(string: url)!, options: [:])
        })

        controller.addAction(UIAlertAction(
            title: "Cancel", style: cancelButtonStyle) { _ in
                self.dismiss(animated: true)
        })

        present(controller, animated: true)
    }

    /// Install a content blocker that will block access to everything
    /// except our Django server, as our app is supposed to be offline-only.
    ///
    /// See https://stackoverflow.com/questions/32119975/how-to-block-external-resources-to-load-on-a-wkwebview/48084455#48084455
    /// answers https://stackoverflow.com/a/48084455/14558
    /// and https://stackoverflow.com/a/60864550/14558
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
                    "url-filter": "^http://127\\\\.0\\\\.0\\\\.1:4828/.*"
                },
                "action": {
                    "type": "ignore-previous-rules"
                }
            }
        ]
        """
        let configuration = webView.configuration

        // there's a race condition here, where the app might theoretically
        // try to load a page before the offline-only content blocker is
        // installed, but we're choosing to ignore it for now
        WKContentRuleListStore.default().compileContentRuleList(
            forIdentifier: "ContentBlockingRules",
            encodedContentRuleList: blockRules) { contentRuleList, error in
                if let error = error {
                    // Handle error
                    os_log("Error installing content blocker: %@", log: log,
                           error.localizedDescription)
                } else if let contentRuleList = contentRuleList {
                    configuration.userContentController.add(contentRuleList)
                    os_log("Added contentRuleList", log: log)
                } else {
                    os_log("No contentRuleList", log: log)
                    return
                }
        }
    }
}
