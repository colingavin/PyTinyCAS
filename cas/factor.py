from cas.nodes import *
from cas.rules import Rule
from cas.utils import *
from copy import copy
    
def comm_factors(facts1, facts2):
    common = []
    for fact in facts1:
        if fact in facts2:
            common.append(fact)
    return common

def remove_facts(args, common):
    new_args = []
    for arg in args:
        if not arg in common:
           new_args.append(arg)
    return new_args 

def factor_op(matched):
    pairs = every_pair(matched.args)
    old_args = copy(matched.args)
    new_args = []
    for pair in pairs:
        can_factor = False
        if Rule.all_are(pair, Multiply):
            can_factor = True
            terms1 = pair[0].args
            terms2 = pair[1].args
        elif Rule.is_a(pair[0], Atom) and Rule.is_a(pair[1], Multiply):
            can_factor = True
            terms1 = [pair[0], Const(1)]
            terms2 = pair[1].args
        elif Rule.is_a(pair[0], Multiply) and Rule.is_a(pair[1], Atom):
            can_factor = True
            terms1 = pair[0].args
            terms2 = [pair[1], Const(1)]
        if can_factor:
            common_factors = comm_factors(terms1, terms2)
            if len(common_factors) > 0:
                old_args.remove(pair[0])
                old_args.remove(pair[1])
                if len(common_factors) == 1:
                    pulled = common_factors[0]
                else:
                    pulled = Multiply(*common_factors)
                remains1 = remove_facts(copy(terms1), common_factors)
                remains2 = remove_facts(copy(terms2), common_factors)
                new_args.append(Multiply(pulled, Add(*(remains1 + remains2))))
                break
    new_args = new_args + old_args
    if len(new_args) == 1:
        return new_args[0]
    else:
        return Add(*new_args)

factor = Rule(Add, factor_op)
