

#=======================================================================================================================
# Translation and Validation Methods
#=======================================================================================================================
def translate_duration_to_minutes(text, context=None):
    """Recognizes multiple human-input formats for durations of time and converts it to minutes,
    returning minutes as int

    :param text: A human-input string to be converted to minutes
    :type text: str
    :param context: Not used but required for signature compatability with the hoomaninterface
    :type context: None
    """

    # define regex formats
    formats = ('^(\d+)$',  # match positive integers
               '^(\d+)\.(\d+)?(h|hr|hrs|hour|hours)?$',  # match positive decimal numbers (optional numbers after
                                                         # decimal and optional hours nouns)
               '^((\d+) *?(d|dy|dys|day|days){1})? *?((\d+) *?(h|hr|hrs|hour|hours){1})? *?((\d+) *?'
               '(m|min|mins|minute|minutes){1})?$',  # match #d#h#m format, each part is optional
               '^(\d+)?:?(\d+):(\d+)$')  # match #:#:# format

    # init vars for days, hours, and minutes
    days = 0
    hours = 0
    minutes = 0

    # set days, hours, and minutes with supported formats
    import re
    matched = False
    for i, format in enumerate(formats):
        m = re.match(format, text, re.I)
        if m != None:
            groups = m.groups('0')
            if i == 0:  # positive integer
                minutes = int(text)
            elif i == 1:  # match positive decimal numbers (optional numbers after decimal and option h for hours)
                hours = int(groups[0])
                minutes = int(60 * float('0.' + groups[1]))
            elif i == 2:  # match #d#h#m format, each part is optional
                days = int(groups[1])
                hours = int(groups[4])
                minutes = int(groups[7])
            elif i == 3:  # match #:#:# format
                days = int(groups[0])
                hours = int(groups[1])
                minutes = int(groups[2])
            matched = True
            break # break after we find a match

    if matched == False:
        return False, None

    # calculate minutes from days, hours, and minutes
    minutes = minutes + (60 * hours) + (1440 * days)

    # return total minutes
    return True, minutes


def translate_datetime(text, context=None):
    output = str_to_datetime(text)
    if output is not None:
        return True, output
    else:
        return False, None


def translate_date(text, context=None):
    output = str_to_date(text)
    if output is not None:
        return True, output
    else:
        return False, None


def translate_list_to_first_type(text, context):

    list = text.split(',')
    output = []

    for item in list:
        wascast = False
        for type in context:
            cast = string_to_type(text, type, on_fail_return=None)
            if cast is not None:
                wascast = True
                output.append(cast)
                break

        if wascast is False:
            return False, None

    return True, output


def translate_to_dict_key(text, context=None):
    """Recognizes multiple human-input formats for durations of time and converts it to minutes,
    returning minutes as int

    :param text: A human-input string.
    :type text: str
    :param context: A dictionary of list<str> objects or a function returning a dictionary of list<str>
    :type context: dict<list<str>>, or func returning dict<list<str>>
    """

    if isinstance(context, dict):
        dict_ = context
    else:
        try:
            dict_ = context()
        except:
            return False, None

    if dict_ is None or isinstance(dict_, dict) is False or len(dict_) == 0:
        return False, None

    output = text

    # test if arg is in list of acceptable values
    matched_acceptable_value = False
    for key, value in dict_.iteritems():
        if text in value:
            matched_acceptable_value = True
            output = key
            break

    if not matched_acceptable_value:
        return False, None
    else:
        return True, output


def translate_to_first_type(text, context=[str]):

    for type in context:
        cast = string_to_type(text, type, on_fail_return=None)
        if cast is not None:
            return True, cast

    return False, None


def validate_is_in_list(text, context=None):
    if isinstance(context, list):
        list_ = context
    else:
        try:
            list_ = context()
        except:
            return False, None

    if list_ is None or isinstance(list_, list) is False or len(list_) == 0:
        return False, None

    # test if arg is in list of acceptable values
    if text in list_:
        return True, text
    else:
        return False, None


def validate_lcase_is_in_list(text, context=None):
    if isinstance(context, list):
        list_ = context
    else:
        try:
            list_ = context()
        except:
            return False, None

    lcase_input = text.lower()

    if list_ is None or isinstance(list_, list) is False or len(list_) == 0:
        return False, None

    # test if arg is in list of acceptable values
    list_ = map(lambda val: val.lower(), list_)

    if lcase_input in list_:
        return True, text
    else:
        return False, None


def validate_int_is_in_range(int_value, context=None):
    min, max = context

    if int_value >= min and int_value <= max:
        return True, int_value
    else:
        return False, None


#=======================================================================================================================
# Helper Methods used by Translation and Validation Methods
#=======================================================================================================================
def string_to_type(string, type, on_fail_return=None, special_cast=None):
    try:
        if isinstance(type, str):
            func = type_cast_dict[type]
        else:
            func = type_cast_dict[type.__name__]
        return func(string, on_fail_return)
    except:
        return on_fail_return


def str_to_int(string, on_fail_return=None):
    # match the type
    try:
        return int(string)
    except:
        return on_fail_return


def str_to_float(string, on_fail_return=None):
    # match the type
    try:
        return float(string)
    except:
        return on_fail_return


def str_to_datetime(string, on_fail_return=None):
    try:
        from dateutil import parser as p
        output = p.parse(string)
        return output
    except:
        from parsedatetime import Calendar
        from datetime import datetime
        c = Calendar()
        output, flags = c.parse(string)
        if flags > 0:
            return datetime(*output[:6])
        else:
            return None

    return None


def str_to_date(string, on_fail_return=None):
    output = str_to_datetime(string, on_fail_return=on_fail_return)
    if output is not None:
        return output.date()
    else:
        return None

type_cast_dict = {
    'int': str_to_int,
    'float': str_to_float,
    'datetime': str_to_datetime,
    'date': str_to_date
}