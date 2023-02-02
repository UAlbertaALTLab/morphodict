"""
Borderline hacky stop-resume support for Django’s runserver command.

When an iOS app goes into the background, it is supposed to close any open
files, stop any background processing, free up as much memory as possible, and
so on.

We don’t want to fully do that in our iOS app because Django takes a bit too
long to start up, and we wouldn’t want to have to make users wait that long
regularly, e.g., every time they switched between the dictionary and some
content app while trying to look up words in what they’re reading.

What seems to happen is that the app threads get suspended: they’re still there,
just not runnable while the app is in the background. Which is fine, so we’re
not wasting any CPU cycles, and our memory use is not huge.

Except: as far as I can tell, iOS sometimes, but not always, will close the
server’s listening socket. Python and/or Django have no idea that a listening
socket can be closed out from underneath them, so the Django runserver listening
code just sits there waiting for requests even though the socket is closed, and
the app doesn’t work because the iOS web view can’t load anything from Django.

The workaround, which is a bit hacky, is to poke around in the runserver
internals, find that it calls a function called `run` imported from `basehttp`,
which calls `TCPServer.serve_forever()`, and instead of calling that just once,
call it in a loop which waits for a notification before starting the server back
up on subsequent loop iterations.

This reduces the iOS app’s interaction with the Django server code down to
calling stop_server() when backgrounded, and resume_server() when brought to the
foreground again.
"""


import socketserver
from threading import Condition, Lock
from typing import Optional

from django.core.servers.basehttp import WSGIRequestHandler, WSGIServer


class RunHandler:
    def __init__(self, *, server_address, wsgi_handler, httpd_cls, ipv6, threading):
        self.server_address = server_address
        self.wsgi_handler = wsgi_handler
        self.httpd_cls = httpd_cls
        self.ipv6 = ipv6
        self.threading = threading

        self.httpd = None

        self.condition = Condition()
        self.httpd_lock = Lock()

    def start(self):
        while True:
            ## Portions copied from Django’s basehttp.run
            with self.httpd_lock:
                assert self.httpd is None

                self.httpd = self.httpd_cls(
                    self.server_address, WSGIRequestHandler, ipv6=self.ipv6
                )
            if self.threading:
                # ThreadingMixIn.daemon_threads indicates how threads will behave on an
                # abrupt shutdown; like quitting the server by the user or restarting
                # by the auto-reloader. True means the server will not wait for thread
                # termination before it quits. This will make auto-reloader faster
                # and will prevent the need to kill the server manually if a thread
                # isn't terminating correctly.
                self.httpd.daemon_threads = True
            self.httpd.set_app(self.wsgi_handler)

            print("calling serve_forever()")
            # This method is somewhat misleadingly named: it will exit if
            # `httpd.shutdown()` is called from a different thread.
            self.httpd.serve_forever()
            print("serve_forever stopped, waiting for notification to resume")

            with self.condition:
                self.condition.wait()
                print("notified")

    def resume(self):
        print("RunHandler.resume")
        with self.condition:
            self.condition.notify()

    def stop(self):
        print("RunHandler.stop")
        with self.httpd_lock:
            assert self.httpd

            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None


run_handler: Optional[RunHandler] = None


# Derived from Django’s basehttp.run, with portions split into the RunHandler
# class below to encapsulate state.
def custom_run(
    addr,
    port,
    wsgi_handler,
    ipv6=False,
    threading=False,
    server_cls=WSGIServer,
):
    server_address = (addr, port)
    if threading:
        httpd_cls = type("WSGIServer", (socketserver.ThreadingMixIn, server_cls), {})
    else:
        httpd_cls = server_cls

    global run_handler
    assert (
        run_handler is None
    ), "This run implementation can only be called once per process"

    run_handler = RunHandler(
        server_address=server_address,
        wsgi_handler=wsgi_handler,
        httpd_cls=httpd_cls,
        ipv6=ipv6,
        threading=threading,
    )
    run_handler.start()


def resume_server():
    """Resume serving, to be called some time after stop_server

    This is a separate function to make it easier to call from other languages.
    """
    run_handler.resume()


def stop_server():
    """Stop the django server, including closing the listening port.

    This is a separate function to make it easier to call from other languages.
    """

    run_handler.stop()
