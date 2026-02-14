import sys

from drivers import BaseDownloadingProgressHandler


class StdoutDPH(BaseDownloadingProgressHandler):
    """
    Download processor.
    Visualizes the process of downloading a book in the console.
    """

    def show_progress(self):
        sys.stdout.write(
            f"\r{self.status.value}: {self._done_count}/{self._total_count}\t"
            f"{round(self._done_count / (self._total_count / 100), 2)} %"
        )
        sys.stdout.flush()
        if self._done_count == self._total_count:
            print()
