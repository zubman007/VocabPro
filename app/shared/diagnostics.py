"""Safe error diagnostics: never log provider exception strings containing secrets."""
import logging


def report_error(error, *, operation, logger=None):
    """Log classification and traceback locations, excluding message and locals."""
    log = logger or logging.getLogger('vocabpro')
    frames = []
    traceback = error.__traceback__
    while traceback is not None:
        code = traceback.tb_frame.f_code
        frames.append(f'{code.co_name}:{traceback.tb_lineno}')
        traceback = traceback.tb_next
    log.error('%s: %s [%s]', operation, type(error).__name__, ' -> '.join(frames))
