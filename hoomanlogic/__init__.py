"""
hoomanlogic

Framework for building interfaces that accept text-based human language input.

In its current state, it is limited in the recognition of human input, and is more akin to an intuitive command-line
format than actual human language input in full sentence structure, but the framework is built the future of this in
mind, and as the framework becomes more 'intelligent', projects that implement this will need only minimal, if any,
changes to their code.
"""

import translation
import string

IDENTCHARS = string.ascii_letters + string.digits + '_'


#=======================================================================================================================
# Operator
#=======================================================================================================================
class Operator(object):

    """The main entry point for managing interfaces and directing human language input.

    This will hold context info, store the last command run, and whether it is perceived that the user
    was successfully understood and we did what the user expected. At any time the user can type 'no' and
    we will log that the last command run was not what the user expected

    :ivar root_scope: The outermost hoomaninterface scope of the human language interface.
    :type root_scope: object
    :ivar interfaces: The list of interfaces.
    :type interfaces: list<object>
    :ivar current_scope: The current hoomaninterface scope that input should be evaluated against.
    :type current_scope: object
    :ivar message_user_func: A function that accepts a string to output a msg to the user.
    :type message_user_func: func
    :ivar last_scope: The last scope that handled user input.
    :type last_scope: object

    :ivar last_suggestion: The last suggestion for a user-input command that
                             wasn't found in the list of command synonyms.
    :type last_suggestion: str
    :ivar last_suggestion_argline: The raw argument lines for the last suggestion for a user-input
                                   command that wasn't found in the list of command synonyms.
    :type last_suggestion_argline: str
    :ivar last_suggestion_was_accepted: The user's decision for the last suggestion for a user-input command
                                        that wasn't found in the list of command synonyms.
    :type last_suggestion_was_accepted: bool
    """

    identchars = IDENTCHARS

    def __init__(self, message_user_func=None):

        self.root_scope = None
        self.interfaces = []
        self.current_scope = None
        self.message_user_func = message_user_func
        self.last_scope = None
        self.last_suggestion = None
        self.last_suggestion_argline = None
        self.last_suggestion_was_accepted = False

    def register_interface(self, interface, child_of=None):
        self.interfaces.append(interface)
        interface.operator = self

        if child_of is None:
            self.root_scope = interface
        else:
            for iter_interface in self.interfaces:
                if iter_interface is child_of:
                    child_of.register_child_interface(interface)

        if self.current_scope is None:
            self.current_scope = self.root_scope

        # call the method to register the hooman
        # interface if one is defined
        if hasattr(interface, 'register_hli'):
            getattr(interface, 'register_hli')()

        # compile a full listing of the command thesaurus
        for attr in dir(interface.__class__):
            if hasattr(getattr(interface, attr), 'translator'):
                for key, value in getattr(interface, attr).translator.synonyms.iteritems():
                    interface.command_dictionary[key] = value

    def listen_and_respond(self, says):

        cmd, arg, says = self.parseline(says)
        get_help = False

        if cmd is not None:
            # search command word
            if cmd == 'help':
                get_help = True
                # do we want a general listing of everything or just
                # help with a specific command?

                # first part of argument is the command, if any, to get help on. Ignore the rest.
                if arg is not None and arg != '':
                    cmd = arg.split()[0]
                    arg = ''
                else:
                    cmd = ''
                    arg = ''

            # if there is a command, lets make sure the interface recognizes it
            if cmd != '':
                found, newcmd, argprefix = self.search_interface_dictionary(self.current_scope, cmd)
                if found:
                    cmd = newcmd

        if get_help and cmd is not None and cmd != '':
            func = getattr(self.current_scope, cmd)
            self.tell_func_usage(func)
            return True

        elif get_help:
            for key, value in self.current_scope.command_dictionary.iteritems():
                print('Command: ' + key + '  ::  Synonyms: ' + str(value))

        elif cmd is not None:
            try:
                func = getattr(self.current_scope, cmd)
            except AttributeError:
                return False
            if hasattr(func, 'translator'):
                if argprefix is None:
                    argprefix = ''

                args_required = False
                if argprefix + arg == '':
                    for arg_mediatior in func.translator.arg_mediators:
                        if arg_mediatior.required == True:
                            args_required = True
                            break

                if args_required == False and argprefix + arg == '':
                    function_return = func()
                else:
                    success, function_return = func(HumanLanguageInput(' '.join([argprefix, arg])))
                    # todo: Handle failed in cases where the user needs to be aware
                    #       but for now the only 'failure' is user cancelling the command.
                    #       Might also need to handle function returns, but interface methods should
                    #       be talking directly to the UI to return whatever need be.
                return True
            else:
                return False

        return False

    def search_interface_dictionary(self, interface, cmd):
        found_command = False
        argprefix = ''
        for key, value in interface.command_dictionary.iteritems():
            if cmd in value:
                found_command = True
                cmd = key

                if len(cmd.split()) > 1:
                    argprefix = ' '.join(cmd.split()[1:])
                    cmd = cmd.split()[0]

                break

        if found_command:
            return True, cmd, argprefix
        else:
            return False, None, None

    def tell(self, message, *args, **kwargs):
        if self.message_user_func is not None:
            self.message_user_func(message, *args, **kwargs)

    def split_args(says):
        import shlex
        args = shlex.split(says)
        return args

    def parseline(self, line):
        """Parse the line into a command name and a string containing the arguments.

        :returns: Returns a tuple containing (command, args, line). 'command' and 'args'
                  may be None if the line couldn't be parsed.
        :rtype: tuple|None
        """
        line = line.strip()
        if not line:
            return None, None, line
        elif line[0] == '?':
            line = 'help ' + line[1:]
        # elif line[0] == '!':
        #     if hasattr(self, 'do_shell'):
        #         line = 'shell ' + line[1:]
        #     else:
        #         return None, None, line
        i, n = 0, len(line)
        while i < n and line[i] in self.identchars: i += 1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line

    def tell_func_usage(self, func):
        message = None

        if hasattr(func, 'translator'):
            message = "{}: {}\n".format(func.translator.fn.func_name, func.translator.description)

            if len(func.translator.arg_mediators) > 0:
                message += "\nCommand Arguments:"
            for arg_mediator in func.translator.arg_mediators:
                required = ' (required)'
                max_count = ''

                if not arg_mediator.required:
                    required = ' (optional)'
                if arg_mediator.max_count is None:
                    max_count = ' There is no limit to the number of times this argument can be used.'
                elif arg_mediator.max_count == 1:
                    max_count = ' It can only be used once.'
                else:
                    max_count = ' It can only be used up to ' + str(arg_mediator.max_count) + ' times.'

                message += "  {}{}: {}{}\n".format(arg_mediator.name, required, arg_mediator.description, max_count)

        if message is not None:
            self.tell(message)


#=======================================================================================================================
# Input
#=======================================================================================================================
class HumanLanguageInput(object):

    """Used to trigger the human-language interface, instead of passing a str to the actual function."""

    def __init__(self, input):
        self.input = input


class InputChain(object):

    """Chained-input structure of the human-language input, storing argument definition match scenarios.

    :ivar input: The portion of human-language input that the chain-link represents.
    :type input: str
    :ivar matched_by: A dictionary of argument names that matched the input containing tuples (output, is_prefix,
                      certainty).
    :type matched_by: dict
    :ivar position: The position of the input part in relation to the rest of the chain
    :type position: int
    :ivar previous_link: Previous input part.
    :type previous_link: Input|None
    :ivar next_link: Next input part.
    :type next_link: Input|None
    """

    @staticmethod
    def convert_to_chain(input_str):
        """Convert human-language input to chain of inputs.

        :param input_str: Human-language input.
        :type input_str: str
        """

        # todo: decide how to best group and recognize special language contexts. perhaps each argument should try to
        #       expand based on the expected type, or perhaps there should be a separate set of groups on top of the
        #       standard set of 'words'.
        
        # identify and group recognized language contexts such as datetime and recurrence patterns
        # import parsedatetime as pdt
        # p = pdt.Calendar()
        # date_matches = p.nlp(input_str)
        #
        # if date_matches is not None and len(date_matches) > 0:
        #     import re
        #
        #     position_pushed = 0
        #     for match in date_matches:
        #         # no grouping required, all one 'word'
        #         if not ' ' in match[4]:
        #             continue
        #
        #         before_and_after = []
        #         if match[2] > 0:
        #             before_and_after.append(input_str[match[2] - 1 + position_pushed])
        #         if match[3] + position_pushed < len(input_str):
        #             before_and_after.append(input_str[match[3] + position_pushed])
        #         is_quoted = False
        #         quote_char = '"'
        #         if len(before_and_after) == 2 and before_and_after[0] in ['"', "'"] and before_and_after[1] in ['"', "'"]:
        #             is_quoted = True
        #
        #         if not is_quoted:
        #             if (len(before_and_after) > 0 and before_and_after[0] == quote_char) or \
        #                     (len(before_and_after) > 1 and before_and_after[1] == quote_char):
        #                 quote_char = "'"
        #
        #             input_str = input_str[0:match[2] + position_pushed] + quote_char + match[4] + quote_char + input_str[match[3] + position_pushed:]
        #             position_pushed += 2

        import shlex
        input_groups = shlex.split(input_str)

        first_link = None
        previous_link = None
        for input in input_groups:
            next_link = InputChain(input, previous_link, hooman_says=True)
            if previous_link is None:
                first_link = next_link
            else:
                previous_link.next_link = next_link
            # prepare for next loop
            previous_link = next_link

        return first_link

    def __init__(self, input, previous_link=None, **kwargs):

        if 'hooman_says' not in kwargs:
            raise Exception("InputChain cannot be instantiated directly. Use static method 'hooman_says'.")

        self.previous_link = previous_link
        self.next_link = None
        if previous_link is not None:
            position = previous_link.position + 1
        else:
            position = 1
        self.position = position
        self.input = input
        self.matched_by = {}

    def read(self):
        """Returns the next link in the chain (or None if at the end of the chain)."""
        return self.next_link

    def read_backwards(self):
        """Returns the previous link in the chain (or None if at the beginning of the chain)."""
        return self.previous_link

    def is_matched(self):
        """Returns whether the current link has been matched."""
        return len(self.matched_by) > 0

    def first(self):
        """Returns the first link in the chain."""
        while self.read_backwards() is not None:
            self = self.read_backwards()
        return self

    def last(self):
        """Returns the last link in the chain."""
        while self.read() is not None:
            self = self.read()
        return self

    def get_links_matched_by(self, arg_mediator_name):
        """Returns all the links matched by the named argument mediator."""
        self = self.first()
        list_ = []
        while self is not None:
            if arg_mediator_name in self.matched_by:
                list_.append(self)
            self = self.read()
        return list_

    def count(self):
        """Returns the number of links in the chain."""
        return self.last().position

    def add_match(self, arg_mediator_name, translation, is_prefix, certainty):
        self.matched_by[arg_mediator_name] = (translation, is_prefix, certainty)

    def get_output(self, arg_mediator_name):
        return self.matched_by.get(arg_mediator_name, (None, None, None))

    def accept_input(self):
        to_return = None

        if self.previous_link is None and self.next_link is None:
            return to_return
        elif self.previous_link is not None and self.next_link is not None:
            self.previous_link.next_link = self.next_link
            self.next_link.previous_link = self.previous_link
            to_return = self.previous_link
        elif self.previous_link is not None and self.next_link is None:
            self.previous_link.next_link = None
            to_return = self.previous_link
        elif self.previous_link is None and self.next_link is not None:
            self.next_link.previous_link =  None
            to_return = self.next_link
        self.previous_link = None
        self.next_link = None
        return to_return

    def get_by_pos(self, pos):
        self = self.first()
        while self is not None:
            if self.position == pos:
                return self
            self = self.read()
        return None

    def get_match_results(self):
        link = self.first()
        match_results = {}
        while link is not None:
            for key, value in link.matched_by.iteritems():
                if key not in match_results:
                    match_results[key] = []
                match_results[key].append(InputMatchResult(link, value[0], value[1], value[2]))
            link = link.read()
        return match_results


class InputMatchResult(object):

    """Input match result object."""

    def __init__(self, link, translation, is_prefix, certainty):
        self.link = link
        self.translation = translation
        self.is_prefix = is_prefix
        self.certainty = certainty


#=======================================================================================================================
# Arguments
#=======================================================================================================================
class ArgumentMediator(object):

    """An argument definition for bridging human-input strings to function parameters.

    :ivar name: Short name of an argument, used in building help, usage, and error messages.
    :type name: str
    :ivar description: Description of the argument, pulled from the docstrings unless explicitly defined.
    :type description: str
    :ivar required: Flags the argument as required.
    :type required: bool
    :ivar max_count: Max number of arguments that can be matched to the argument definition.
    :type max_count: None|int
    :ivar argument_prefixer: non-operative prefix that helps identify the argument (ie. -t, --tags, etc.)
    :type argument_prefixer: str|list<str>|tuple<str>
    :ivar rules: Tuples (rule_function, human-friendly description of rule, context obj passed to function)
                 for validating and translating the input. For multiple rules, use a tuple of tuples.
    :type rules: tuple
    :ivar question: Human-readable question to request input for the argument.
    :type question: str
    """

    #===================================================================================================================
    # Initialization
    #===================================================================================================================
    def __init__(self, name, description='', required=False, max_count=1, argument_prefixer=None, rules=None,
                 question=None, from_func_info=None):

        self.name = name
        self.description = description
        self.required = required
        self.argument_prefixer = argument_prefixer
        self.max_count = max_count
        self.rules = rules
        self.question = question

        # if function info object was supplied, grab the info and apply it
        if from_func_info is not None:
            for parameter in from_func_info.parameters:
                if parameter.name == self.name:
                    self.description = parameter.description
                    type_str = parameter.types.strip()
                    if type_str != '':
                        type_str = type_str.replace(' ', '')
                        types = type_str.split(',')
                        self.types = types

    #===================================================================================================================
    # Public Methods
    #===================================================================================================================
    def try_match(self, input_part, prefix_matched=False):
        """Try to match argument definition to the input and return a bool indicating if it was successful.

        If a match is made, it will call the ``InputChain`` instance's add_match() function, adding itself for later
        consideration of the best match.

        :return: Returns a bool indicating whether it was successfully matched to the input.
        :rtype: bool
        """

        translation = input_part.input
        match_len = 1
        certainty = 1

        # check for prefix
        prefix = 0
        if self.argument_prefixer is not None and not prefix_matched:
            if input_part.previous_link is None:
                return False
            if hasattr(self.argument_prefixer, '__iter__'):
                if input_part.previous_link.input not in self.argument_prefixer:
                    return False
            else:
                if input_part.previous_link.input != self.argument_prefixer:
                    return False
            prefix = 1

        # test rules if defined
        if self.rules is not None and isinstance(self.rules, tuple) and len(self.rules) > 0:
            if isinstance(self.rules[0], tuple):
                for rule_args in self.rules:
                    rule, description, context = rule_args
                    recognized, evaluation_output = rule(translation, context)
                    if not recognized:
                        return False
                    else:
                        translation = evaluation_output
            else:
                rule, description, context = self.rules
                recognized, evaluation_output = rule(translation, context)
                if not recognized:
                    return False
                else:
                    translation = evaluation_output

        # if we made it this far, then match was successful!
        # add to managed_args and return true
        input_part.add_match(self.name, translation, False, certainty)

        # match prefix
        if prefix > 0:
            reader = input_part
            for x in range(0, prefix):
                reader = reader.read_backwards()
                reader.add_match(self.name, translation, True, certainty)

        # try to match everything following this if it depends on the prefix
        # but as soon as one doesn't match, it breaks the argument chain
        if prefix > 0 and (self.max_count is None or self.max_count > 1):
            reader = input_part.read()
            matched = True
            match_count = 1
            while reader is not None and matched is True:
                matched = self.try_match(reader, True)
                match_count += 1
                if match_count == self.max_count:
                    break
                reader = input_part.read()

        # match extended parts
        if match_len > 1:
            reader = input_part
            for i in range(1, match_len):
                reader = reader.read()
                reader.add_match(self.name, translation, False, certainty)

        return True

    def ask(self):
        """Prompt user to give input in the case that required input was not already supplied or identified."""
        if self.question is None:
            self.question = "Please supply a value for required argument '{}':".format(self.name)
        line = raw_input("{} ".format(self.question))
        line = line.strip()
        if line in ('', 'quit', 'cancel', 'q', 'abort', 'nevermind', 'forget it'):
            return False, True, None

        input_chain = InputChain.convert_to_chain(line)

        # match every input to every arg so we can build stats and see what we have to work with
        reader = input_chain
        while reader is not None:
            if not self.try_match(reader):
                print("Sorry, I didn't understand that. Please try again or hit enter to abort.")
                return False, False, None
            else:
                return True, False, reader

    def learn(self):
        """Especially useful for main command translator, but may be useful for other translators as well."""
        pass


#=======================================================================================================================
# Decorators
#=======================================================================================================================
def interface(original_class):
    """The command dictionary for defining the command words for command functions as well as the argument structure.

    Complex configuration of the interface commands:

    A decorated class looks for a function named ``register_hli`` during the initialization and
    calls it if it exists.

    In many cases, the @hoomando decorators on the functions can take care of all the required setup, however,
    there may be times when you either want to put all of the configuration in one area to keep the decorators
    clean, or you need more complex logic for configuration.

    See a basic example below::

        def register_hli(self):
            # todo: add example

    See ``build_command_words`` for help with registering complex lists of command words

    :param original_class:
    :type original_class:
    :return:
    :rtype:
    """
    # make copy of original __init__, so we can call it without recursion
    orig_init = original_class.__init__

    def __init__(self, *args, **kws):
        self.command_dictionary = {}
        self.interfaces = []
        self.parent_interface = None
        self.operator = None

        orig_init(self, *args, **kws)  # call the original __init__

    def register_child_interface(self, child):
        if child not in self.interfaces:
            if child.parent_interface is None:
                child.parent_interface = self
                self.interfaces.append(child)
            else:
                raise Exception("The child already has a parent interface assigned!")
        else:
            raise Exception("The child is already assigned to this interface!")

    def tell_operator(self, message, *args, **kwargs):
        """Checks for operator and ignores message if operator isn't available."""
        if self.operator is None:
            return

        self.operator.tell(message, *args, **kwargs)

    # add functions to original class
    original_class.__init__ = __init__
    original_class.register_child_interface = register_child_interface
    original_class.tell_operator = tell_operator

    # return the original class
    return original_class


def translator(synonyms=None, arg_mediators=None, rules=None, code_alert=0):
    """Wraps a function to accept HumanLanguageInput and translate to expected arguments.

    :param synonyms: A dictionary of 'commandname[ arg]' key entries each with a
                     list of synonyms that equate to the key.
    :type synonyms: dict<str,list<str>>
    :param arg_mediators: List of ArgumentMediator objects in match priority order.
    :type arg_mediators: list<ArgumentMediator>
    :param rules: Tuples of rule functions and context objects to pass to the function.
    :type rules: tuple<func,object>|tuple<tuple<func,object>,...>
    :param code_alert: 0 - non-modifying code, 1 - non-critical modifying code, 2 - critical modifying code
    :type code_alert: int
    """

    class Translator(object):

        """Contains information about the function it wraps and has a method to accept a human-input string and attempt to build the parameters to call the function.

        :ivar fn: The raw function that the hoomaninterface method wraps.
        :type fn: func
        :ivar description: Description of the function being wrapped. If not supplied, it is extracted from docstrings.
        :type description: str
        :ivar arg_mediators: List of ArgumentMediator objects in match priority order.
        :type arg_mediators: list<ArgumentMediator>
        :ivar synonyms: A dictionary of 'commandname[ arg]' key entries each with a
                        list of synonyms that equate to the key.
        :type synonyms: dict<str,list<str>>
        """

        def __init__(self, fn, arg_mediators=None, synonyms=None, description=None, code_alert=0, auto_setup=True):

            self.fn = fn
            self.description = description

            if arg_mediators is not None:
                self.arg_mediators = arg_mediators
            else:
                self.arg_mediators = []

            # add synonyms
            self.synonyms = {}

            if synonyms is not None:
                if isinstance(synonyms, dict):
                    self.synonyms = synonyms
                elif isinstance(synonyms, list):
                    self.synonyms[fn.func_name] = ['q', 'quit', 'goodbye', 'aufwiedersehen', 'ciao', 'fuckoff', 'hastalavista']

            # if flagged for no automatic setup to set synonyms and
            # argument mediators with the necessary constructs, then return
            if not auto_setup:
                return

            # add func_name to synonyms if it isn't already there
            if fn.func_name in self.synonyms:
                if fn.func_name not in self.synonyms[fn.func_name]:
                    self.synonyms[fn.func_name].append(fn.func_name)
            else:
                self.synonyms[fn.func_name] = [fn.func_name]

            # extract function documentation
            self.func_info = FunctionInfo(fn)
            self.description = self.func_info.description

            # auto-add rules from function info
            if arg_mediators is None:
                if len(self.func_info.parameters) > 0:
                    for par in self.func_info.parameters:

                        # build a generic types rule if a known type
                        rule = None
                        type_str = par.types.strip()
                        if type_str != '':
                            type_str = type_str.replace(' ', '')
                            types = type_str.split(',')
                            self.types = types
                            if 'str' not in types and 'None' not in types:
                                context_types = []
                                add_rule = True
                                for key in types:
                                    if key in translation.type_cast_dict:
                                        context_types.append(key)
                                    else:
                                        add_rule = False  # unrecognized object
                                        break

                                if add_rule and len(context_types) > 0:
                                    rule = (translation.translate_to_first_type,
                                            'Value must be translatable to one of the '
                                            'following types: {}.'.format(type_str), context_types)

                        arg_mediator = ArgumentMediator(par.name,
                                                        description=par.description,
                                                        required=par.has_default is False,
                                                        rules=rule)
                        self.arg_mediators.append(arg_mediator)

        def add_to_managed_args(self, input_chain, arg_mediator, managed_args):
            """Add output to managed args and pop link from the chain, returning the chain."""

            # get the matched variables
            output, is_prefix, certainty = input_chain.get_output(arg_mediator.name)

            # accept the input to pop it from the input chain
            input_chain = input_chain.accept_input()

            # if it's just context for argument matching, do not add to managed args
            if is_prefix:
                return input_chain

            # add to managed args
            if arg_mediator.max_count is None or arg_mediator.max_count > 1:
                if not arg_mediator.name in managed_args:
                    managed_args[arg_mediator.name] = []
                managed_args[arg_mediator.name].append(output)
            else:
                managed_args[arg_mediator.name] = output

            # return what is left of the chain
            return input_chain

        def translate_and_run(self, obj, line):
            self.obj = obj
            input_chain = InputChain.convert_to_chain(line)

            # match every input to every arg so we can build stats and see what we have to work with
            link = input_chain
            while link is not None:
                for arg_mediator in self.arg_mediators:
                    arg_mediator.try_match(link)
                link = link.read()

            # now evaluate the input matches and pick the best options
            managed_args = {}  # dict of managed args

            # first, if there are required args that are only matched once, accept those matches
            if input_chain is not None:
                for arg_mediator in self.arg_mediators:
                    match_results = input_chain.get_match_results()
                    if arg_mediator.name in match_results and len(match_results[arg_mediator.name]) == 1 and arg_mediator.required:

                        link = input_chain.get_links_matched_by(arg_mediator.name)[0]
                        input_chain = self.add_to_managed_args(input_chain.get_by_pos(link.position), arg_mediator, managed_args)

                    if input_chain is None:
                        break

            # next, lets go in order of arg defs, which should be in the order of most
            # specific (narrowest match case) to least specific (broadest match case)
            if input_chain is not None:
                for arg_mediator in self.arg_mediators:

                    links = input_chain.get_links_matched_by(arg_mediator.name)

                    for link in links[:]:
                        if arg_mediator.name not in managed_args or arg_mediator.max_count is None or \
                                (arg_mediator.max_count > 1 and len(managed_args[arg_mediator.name]) < arg_mediator.max_count):
                            input_chain = self.add_to_managed_args(input_chain.get_by_pos(link.position), arg_mediator, managed_args)

                    if input_chain is None:
                        break

            # check if any required args haven't been assigned to
            # and prompt user to supply required input
            required_args_were_not_matched = False
            for arg_mediator in self.arg_mediators:
                if arg_mediator.required and arg_mediator.name not in managed_args:
                    matched = False
                    abort = False
                    i_c = None
                    while matched is False and abort is False:
                        matched, abort, input_chain = arg_mediator.ask()

                    if matched:
                        self.add_to_managed_args(input_chain, arg_mediator, managed_args)
                    else:
                        required_args_were_not_matched = True
                        break

            # if user cancels before matching all required args, return None
            if required_args_were_not_matched:
                return False, None

            # check if any input is still unrecognized
            unrecognized_input_exists = input_chain is not None

            # if this is a critical function, or there was ignored input
            # then lets make sure we're doing what the user really wants
            if code_alert > 0 or unrecognized_input_exists:
                args_verify = ''
                for key, value in managed_args.iteritems():
                    args_verify += "\n    {}: {}".format(key, value)
                line = raw_input("{}: {}{}\n\nIs this what you want to do? ".format(self.func_info.name, self.description, args_verify))
                if line == 'y':
                    return True, (self.fn(obj, **managed_args))
                else:
                    return False, None
            else:
                return True, (self.fn(obj, **managed_args))

    def wrapper(fn):
        def wrapped(self, *args, **kwargs):
            if args is not None and len(args) == 1 and isinstance(args[0], HumanLanguageInput):
                # hooman
                return fn.translator.translate_and_run(self, args[0].input)
            else:
                # musheen
                return fn(self, *args, **kwargs)
        hltranslator = Translator(fn, synonyms=synonyms, arg_mediators=arg_mediators, code_alert=code_alert)
        wrapped.translator = hltranslator
        fn.translator = hltranslator
        return wrapped

    return wrapper


#=======================================================================================================================
# Helper Methods and Classes
#=======================================================================================================================
def build_command_words(*args):
    """Builds a list of command words for a single command, especially for joining together common synonyms of parts of a command.

    Ie. Supplying a tuple of lists of strings::

        build_command_words(['find','search'], ['action', 'task'])

    would result in a list of strings ``['findaction', 'searchaction', 'findtask','searchtask']``.

    Note that tuples build the command words in the order they are given, so if you want the reverse of it to be built
    as well, then supply another tuple.

    Ie.::

        build_command_words(['action', 'task'], ['find','search'])

    would result in 'actionfind', 'taskfind', etc.

    A list of str objects outside of a tuple is appended to the list of command words without joining them with
    another list

    Here is another example using all the acceptable types::

        build_command_words((['find','search'], ['action', 'task']), ['unjoined', 'command_words'], 'oneoffcommand')

    would result in ``['findaction', 'findtask', 'searchaction', 'searchtask', 'unjoined', 'command_words',
    'one off command']``

    It is not recommended to use spaces in your command words, as the command prompt would interpret the space as the
    beginning of the arguments list. However, once optional speech recognition is implemented in HoomanCmd these
    command parts will be fully supported and treated as separate words, so keep that in mind in your implementation
    and split the words of the command in tuples whenever possible, as opposed to supplying a string that already
    has two or more words joined together.

    :param args: Handles tuples of lists of str, lists of str objects, and str objects.
    :type args: tuple<list<str>>, list<str>, str
    :return: Returns a list of str objects of all the combined command parts and lists given.
    :rtype: list<str>
    """

    command_words = []

    for arg in args:
        if isinstance(arg, tuple) and len(arg) > 1:
            for cmd_part_1 in arg[0]:
                for cmd_part_2 in arg[1]:
                    if len(arg) > 2:
                        for cmd_part_3 in arg[2]:
                            command_words.append(''.join([cmd_part_1, cmd_part_2, cmd_part_3]))
                    else:
                        command_words.append(''.join([cmd_part_1, cmd_part_2]))
        elif isinstance(arg, list) and len(arg) > 0 and isinstance(arg[0], str):
            command_words.extend(arg)
        elif isinstance(arg, str):
            command_words.append(arg)

    return command_words


class FunctionInfo():

    """Garners information about a given function and its parameters."""

    def __init__(self, func):
        self.name = func.func_name
        self.description = ''
        self.parameters = []

        raw_func_docs = ''
        if func.func_doc is not None:
            raw_func_docs = func.func_doc

        oneline = raw_func_docs.replace('\n', '')
        while '  ' in oneline:
            oneline = oneline.replace('  ', ' ')

        import re
        docmatch = re.match('^(.*?)(:[^ ]+ *?[^ ]+:|$).*', oneline)
        if docmatch is not None:
            groups = docmatch.groups('')
            self.description = groups[0]

        # get default count to calculate which parameters have default values
        if func.func_defaults is None:
            default_count = 0
        else:
            default_count = len(func.func_defaults)
        first_default_pos = func.func_code.co_argcount - default_count

        position_modifier = 0
        for i in range(0, func.func_code.co_argcount):
            if i == 0 and func.func_code.co_varnames[i] == "self":
                position_modifier = 1
                continue

            par = ParameterInfo(func.func_code.co_varnames[i], i + 1)
            par.position_modifier = position_modifier

            # if the parameter has a default, let's learn about it
            if i >= first_default_pos:
                par.has_default = True
                par.default = func.func_defaults[i - first_default_pos]

            # try to get parameter description
            docmatch = re.match('.*:param *?' + func.func_code.co_varnames[i] + ':(.*?)(:[^ ]+ *?[^ ]+:|$).*', oneline)
            if docmatch is not None:
                groups = docmatch.groups('')
                par.description = groups[0]

            # try to get parameter types
            docmatch = re.match('.*:type *?' + func.func_code.co_varnames[i] + ':(.*?)(:[^ ]+ *?[^ ]+:|$).*', oneline)
            if docmatch is not None:
                groups = docmatch.groups('')
                par.types = groups[0]

            # try to get parameter rules
            docmatch = re.match('.*:rules *?' + func.func_code.co_varnames[i] + ':(.*?)(:[^ ]+ *?[^ ]+:|$).*', oneline)
            if docmatch is not None:
                groups = docmatch.groups('')
                par.rules = groups[0]

            self.parameters.append(par)


class ParameterInfo():

    """Contains information about a function parameter.

    :ivar name: Name of the parameter.
    :type name: str
    :ivar position: One-based position of the parameter, without position-modifier off-set.
    :type position: int
    :ivar position_modifier: Number of positions we are ignorning to be used to off-set the position.
    :type position_modifier: int
    :ivar has_default: Whether the parameter has a default value.
    :type has_default: bool
    :ivar default: The parameter's default value, could be None, so check ``has_default``
                   to see if it is actually a default value.
    :type default: object
    :ivar description: Description of the parameter from docstring.
    :type description: str
    :ivar types: Types of the parameter from docstring.
    :type types: str
    :ivar rules: Rules of the parameter from docstring.
    :type rules: str
    """

    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.position_modifier = 0
        self.has_default = False
        self.default = None
        self.description = ''
        self.types = ''
        self.rules = ''