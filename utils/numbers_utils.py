# This is a sample Python script.


def truncate_float(number, n):
    md = 10 ** n
    return int(number * md) / md
