class Dumper:

    def __init__(self, data):
        self.data = data

    def simpledump(self, obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if hasattr(v, '__iter__'):
                    print(k)
                    self.simpledump(v)
                else:
                    print('%s : %s' % (k, v))
        elif isinstance(obj, list):
            for v in obj:
                if hasattr(v, '__iter__'):
                    self.simpledump(v)
                else:
                    print(v)
        else:
            print(obj)
