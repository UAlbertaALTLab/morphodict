import time

from CreeDictionary.utils.profiling import timed


def test_timed_decorator(capsys):
    @timed(msg="{func_name} finished in {second:.1f} seconds")
    def quick_nap():
        time.sleep(0.1)

    quick_nap()

    out, err = capsys.readouterr()
    assert "quick_nap finished in 0.1 seconds\n" == out
