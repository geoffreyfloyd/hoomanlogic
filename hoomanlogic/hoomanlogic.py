# Backward compatibility fix.
from . import *

# todo: improve doc output (requires overriding do_help) by extracting param docs from ugly syntax
#       and utilizing argument definitions to give the user helpful info on how to use the system
#     doc=getattr(self, 'do_' + arg).__doc__
#     if doc:
#         self.stdout.write("%s\n"%str(doc))
#         return
# todo: write HoomanArg.get_min_sequential_args logic
# todo: start matching sub args, if an arg isn't matched by any sub arg, we decide that
#       none of the following ones will either, because the chain has been broken
# todo: Create a HoomanArgs class deriving from list and refactor 'handle_managed_args' to here.
#       Use a better recursion technique to match the args one by one in the given structure, always testing the most
#       likely arg def first down to the least likely
# todo: bugfix: >> progress 30 101 2h30m
#       results in index=101, progress=30, and minutes=120
#       should be index 30, progress 101, and minutes 150
# todo: add ability to parse docstring 'rules' to build rules