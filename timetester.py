import time

from contstants import PRINT_SPECIFIC_TIME_MEASURES


class TimeTester:
    DeepCopies = 0
    FindPaths = 0
    ReevaluateClues = 0

    TimesLocal = {}
    TimesGlobal = {}

    @staticmethod
    def time(key):
        if not PRINT_SPECIFIC_TIME_MEASURES:
            return
        if key not in TimeTester.TimesLocal:
            TimeTester.TimesLocal[key] = time.time()
        else:
            diff = time.time() - TimeTester.TimesLocal[key]
            if key not in TimeTester.TimesGlobal:
                TimeTester.TimesGlobal[key] = diff
            else:
                TimeTester.TimesGlobal[key] += diff
            del TimeTester.TimesLocal[key]

