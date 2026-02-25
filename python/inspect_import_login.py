import sys, traceback
try:
    import launcher.ui.login_window as m
    print('IMPORT_OK')
except Exception:
    traceback.print_exc()
    sys.exit(1)
