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
    }
}
