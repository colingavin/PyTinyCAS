from cas.rules import Rule
from cas.nodes import *
from cas.utils import *
import fractions
from copy import copy

def const_common_terms(pair):
    if pair[0] == pair[1]:
        return [pair[0]]
    elif isinstance(pair[0].value(), int) and isinstance(pair[1].value(), int):
        fact = fractions.gcd(pair[0].value(), pair[1].value())
        if fact > 1:
            return [Const(fact)]
        else:
            return []
    else:
        return []

def mult_common_terms(pair):
#    print "mult_common_terms: finding common terms of " + str(pair)
    common = []
    for fact in pair[0].args:
        common = common + common_terms((fact, pair[1]))
    return common

def mult_atom_common_terms(pair):
#    print "mult_atom_common_terms: finding common terms of " + str(pair)
    common = []
    for fact in pair[0].args:
        common = common + common_terms((fact, pair[1]))
    return common

def pow_common_terms(pair):
#    print "pow_common_terms: finding common terms of " + str(pair)
    if not Rule.all_equal([term.base() for term in pair]):
        return []
    if Rule.all_are([term.exponent() for term in pair], Var):
        return []
    if Rule.all_are([term.exponent() for term in pair], Const):
        if Rule.all_are([term.exponent().value() for term in pair], int):
            v1 = pair[0].exponent().value()
            v2 = pair[1].exponent().value()
            return [Power(pair[0].base(), Const(min(v1, v2)))]
    common_in_exp = common_terms((pair[0].exponent(), pair[1].exponent()))
    if len(common_in_exp) > 0:
        if len(common_in_exp) > 1:
            mults = Multiply(*common_in_exp)
        else:
            mults = common_in_exp[0]
        return [Power(pair[0].base(), mults)]
    return []
   
def pow_atom_common_terms(pair):
#    print "pow_atom_common_terms: finding common terms of " + str(pair)
    if Rule.is_a(pair[1], Const):
        return []
    if pair[0].base() != pair[1]:
        return []
    return [pair[1]]

def mult_pow_common_terms(pair):
#    print "mult_pow_common_terms: finding common terms of " + str(pair)
    common = []
    for fact in pair[0].args:
        common += common_terms((fact, pair[1]))
    return common

def pull_pow_from_mult(power, mult):
    new_args = []
    for fact in mult.args:
        if Rule.is_a(fact, Power) and fact.base() == power.base():
            new_args.append(pull(power, fact))
        else:
            new_args.append(fact)
    if len(new_args) == 0:
        return Const(1)
    elif len(new_args) == 1:
        return new_args[0]
    else:
        return Multiply(*new_args)
    
def pull_factor_from_mult(fact, mult):
    new_args = []
    for mfact in mult.args:
        new_args.append(pull(fact, mfact))
    if len(new_args) == 0:
        return Const(1)
    elif len(new_args) == 1:
        return new_args[0]
    else:
        return Multiply(*new_args)

def pull(factor, value):
    if Rule.is_a(factor, Const):
        #it's only possible to pull a constant out of a const or a multiplication
        if Rule.is_a(value, Const) and float(value.value()) % float(factor.value()) == 0:
            return Const(value.value() / factor.value())
        elif Rule.is_a(value, Multiply):
            return pull_factor_from_mult(factor, value)
    elif Rule.is_a(factor, Var):
        #a var can be pulled out of a var, a multiplication, or a power
        if Rule.is_a(value, Var) and value == factor:
            return Const(1)
        elif Rule.is_a(value, Multiply):
            return pull_factor_from_mult(factor, value)
        elif Rule.is_a(value, Power):
            return Power(value.base(), Add(value.exponent(), Const(-1)))
    elif Rule.is_a(factor, Add):
        #an addition can be pulled out of a multiplication or a power
        if Rule.is_a(value, Multiply):
            return pull_factor_from_mult(factor, value)
        elif Rule.is_a(value, Power):
            return Power(value.base(), Add(value.exponent(), Const(-1)))
    elif Rule.is_a(factor, Power):
        #a power can be pulled out of a multiply or a power
        if Rule.is_a(value, Multiply):
            return pull_pow_from_mult(factor, value)
        elif Rule.is_a(value, Power):
            return Power(value.base(), Add(value.exponent(), Multiply(Const(-1), factor.exponent())))
    return value
    
def pull_facts(factors, value):
    current_value = value
#    print "Pull: starting with " + str(current_value)
    for fact in factors:
#        print "Pull: factor " + str(fact)
        current_value = pull(fact, current_value)
#        print "Pull: next " + str(current_value)
    return current_value

def common_terms(pair):
#    print "common_terms: finding common terms of " + str(pair)
    if Rule.all_are(pair, Const):
        return const_common_terms(pair)
    if Rule.all_are(pair, Var):
        if pair[0] == pair[1]:
            return [pair[0]]
        else:
            return []
    if Rule.all_are(pair, Atom):
        return []
    if Rule.all_are(pair, Multiply):
        return mult_common_terms(pair)
    if Rule.is_a(pair[0], Multiply) and Rule.is_a(pair[1], Atom):
        return mult_atom_common_terms(pair)
    if Rule.is_a(pair[0], Atom) and Rule.is_a(pair[1], Multiply):
        return mult_atom_common_terms((pair[1], pair[0]))
    if Rule.all_are(pair, Power):
        return pow_common_terms(pair)
    if Rule.is_a(pair[0], Power) and Rule.is_a(pair[1], Atom):
        return pow_atom_common_terms(pair)
    if Rule.is_a(pair[0], Atom) and Rule.is_a(pair[1], Power):
        return pow_atom_common_terms((pair[1], pair[0]))
    if Rule.is_a(pair[0], Multiply) and Rule.is_a(pair[1], Power):
        return mult_pow_common_terms(pair)
    if Rule.is_a(pair[0], Power) and Rule.is_a(pair[1], Multiply):
        return mult_pow_common_terms((pair[1], pair[0]))
    return []

def factor_op(matched):
    pairs = every_pair(matched.args)
    new_args = copy(matched.args)
    for pair in pairs:
        commons = common_terms(pair)
#        print "--- Got commons: " + str(commons)
        if len(commons) > 0:
            new_args.remove(pair[0])
            new_args.remove(pair[1])
            if len(commons) > 1:
                pulled = Multiply(*commons)
            else:
                pulled = commons[0]
#            print "--- Factor to pull: " + str(pulled)
            lhs = pull_facts(commons, pair[0])
#            print "--- LHS: " + str(pair[0])
#            print "--- Pulled from lhs: " + str(lhs)
#            print "--- RHS: " + str(pair[1])
            rhs = pull_facts(commons, pair[1])
#            print "--- Pulled from rhs: " + str(rhs)
            new_args.append(Multiply(pulled, Add(lhs, rhs)));
            break
#    print "Returning " + Add(*new_args).pretty_print()
    if len(new_args) > 1:
        return Add(*new_args)
    else:
        return new_args[0]

factor = Rule(Add, factor_op)
