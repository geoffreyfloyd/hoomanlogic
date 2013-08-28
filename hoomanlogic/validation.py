def identify_duplicate_command_words(command_dict):
    """Feed it the command dictionary and print out all the command words that are duplicated."""
    all_commands = []
    for cmd_words in command_dict.itervalues():
        all_commands.extend(cmd_words)

    cmdcount = {}
    for cmd in all_commands:
        cmdcount[cmd] = cmdcount.get(cmd, 0) + 1

    duplicate_commands = []
    for key, value in cmdcount.iteritems():
        if value > 1:
            duplicate_commands.append(key)

    for dup in duplicate_commands:
        print(dup)