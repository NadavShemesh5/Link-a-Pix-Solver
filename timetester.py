import time
from contstants import PRINT_SPECIFIC_TIME_MEASURES, CHECK_NUM_OF_PATHS


class TimeTester:
    DeepCopies = 0
    FindPaths = 0
    ReevaluateClues = 0

    TimesLocal = {}
    TimesGlobal = {}

    CurrentSample = None
    PathsNumber = {}

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

    @staticmethod
    def update_paths_num(paths):
        if not CHECK_NUM_OF_PATHS or not paths:
            return
        if TimeTester.CurrentSample not in TimeTester.PathsNumber:
            TimeTester.PathsNumber[TimeTester.CurrentSample] = len(paths)
        else:
            TimeTester.PathsNumber[TimeTester.CurrentSample] += len(paths)
