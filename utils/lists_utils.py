# This is a sample Python script.


def list_range(_start, _stop, _step_value):
    list_of_values = []
    if _start >= _stop:
        list_of_values.append(round(_start, 2))
        return list_of_values
    while True:
        if len(list_of_values) == 0:
            list_of_values.append(round(_start, 2))
        list_of_values.append(round(list_of_values[-1] + _step_value, 2))
        if list_of_values[-1] >= _stop:
            break
    return list_of_values