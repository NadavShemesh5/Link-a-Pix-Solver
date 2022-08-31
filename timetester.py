import time
import settings


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
        if not settings.PRINT_SPECIFIC_TIME_MEASURES:
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
    def update_paths_num(paths, paths_num=0):
        if paths_num == 0 and (not settings.CHECK_NUM_OF_PATHS or not paths):
            return
        if TimeTester.CurrentSample not in TimeTester.PathsNumber:
            TimeTester.PathsNumber[TimeTester.CurrentSample] = len(paths) + paths_num
        else:
            TimeTester.PathsNumber[TimeTester.CurrentSample] += len(paths) + paths_num
