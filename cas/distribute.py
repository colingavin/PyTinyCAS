from cas.rules import Rule, simplify_rules_only
from cas.nodes import *
from cas.utils import *
from copy import copy

def distribute_op(matched):
    new_args = copy(matched.args)
    def distribute_modifying_args(term, addition):
        new_args.remove(addition)
        new_args.remove(term)
        new_args.append(Add(*[Multiply(term, add_arg) for add_arg in addition.args]))
    if len(matched.args) > 1 and Rule.is_a(matched.args[0], Add):
        distribute_modifying_args(matched.args[1], matched.args[0])
    else:
        for idx in range(1, len(matched.args)):
            current_arg = matched.args[idx]
            if Rule.is_a(current_arg, Add):
                distribute_modifying_args(matched.args[0], current_arg)
                break
    print "distributing: " + str(matched)
    print "new args: " + str(new_args)
    if len(new_args) == 1:
        return new_args[0]
    else:
        return Multiply(*new_args)
    
distribute = Rule(Multiply, distribute_op)

def distribute_and_test_op(matched):
    new_node = matched.expand()
    if new_node.complexity_count() < matched.complexity_count():
        return new_node
    else:
        return False

simp_by_expand_mult = Rule(Multiply, distribute_and_test_op)
simp_by_expand_add = Rule(Add, distribute_and_test_op)
simp_by_expand_pow = Rule(Power, distribute_and_test_op)