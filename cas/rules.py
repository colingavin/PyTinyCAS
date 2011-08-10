from cas.nodes import *
from cas.utils import *
from copy import copy


class IndeterminateFormException(Exception):
    def __init__(self, form):
        self.form=form      
    def __str__(self):
        return "An indeterminate form was encoutered: %s." % (str(self.form))
    def __repr__(self):
        return str(self)

class Rule(object):
    def __init__(self, match_class, apply_function):
        self.match_class = match_class
        self.apply_function = apply_function        
    
    @classmethod
    def is_a(self, node, some_class):
        return isinstance(node, some_class)
    
    @classmethod
    def is_const_equal(self, node, value):
        return Rule.is_a(node, Const) and node.value() == value
    
    @classmethod
    def some_are(self, nodes, some_class):
        for node in nodes:
            if self.is_a(node, self_class):
                return True
        return False
    
    @classmethod
    def all_are(self, nodes, some_class):
        for node in nodes:
            if not self.is_a(node, some_class):
                return False
        return True    
        
    @classmethod
    def all_equal(self, nodes):
        return len(set(nodes)) == 1
    
    def apply(self, node):
        if isinstance(node, self.match_class):
            ret = self.apply_function(node)
            if not ret is False:
                return ret
            return node
        else:
            return node

#--- Rules for Add nodes ---

def addition_identity_op(matched):
    new_args = []
    for arg in matched.args:
        if Rule.is_a(arg, Const) and arg.value() == 0:
            continue
        else:
            new_args.append(arg)
    if len(new_args) > 1:
        return Add(*new_args)
    elif len(new_args) == 0:
        return Const(0)
    else:
        return new_args[0]
        
addition_identity = Rule(Add, addition_identity_op)

def join_const_add_op(matched):
    new_args = []
    const_args = []
    for arg in matched.args:
        if Rule.is_a(arg, Const):
            const_args.append(arg)
        else:
            new_args.append(arg)
    const_val = Add(*const_args).apply({})
    if const_val.value() != 0:
        new_args.append(const_val)
    if len(new_args) > 1:
        return Add(*new_args)
    else:
        return const_val
    
join_add_consts = Rule(Add, join_const_add_op)

def merge_adds_op(matched):
    new_args = []
    for arg in matched.args:
        if isinstance(arg, Add):
            new_args = new_args + arg.args
        else:
            new_args.append(arg)
    return Add(*new_args)
    
merge_adds = Rule(Add, merge_adds_op)

def add_to_mult_op(matched):
    addends = {}
    for arg in matched.args:
        if arg in addends:
            addends[arg] += 1
        else:
            addends[arg] = 1
    new_args = []
    for term in addends:
        if addends[term] == 1:
            new_args.append(term)
        else:
            new_args.append(Multiply(Const(addends[term]), term))
    if len(new_args) > 1:
        return Add(*new_args)
    else:
        return new_args[0]

add_to_mult = Rule(Add, add_to_mult_op)

#--- Rules for Multiply nodes ---

def mult_zero_op(matched):
    for arg in matched.args:
        if Rule.is_a(arg, Const) and arg.value() == 0:
            return Const(0)
    return matched
    
mult_zero = Rule(Multiply, mult_zero_op)

def mult_identity_op(matched):
    new_args = []
    for arg in matched.args:
        if Rule.is_a(arg, Const) and arg.value() == 1:
            continue
        else:
            new_args.append(arg)
    if len(new_args) > 1:
        return Multiply(*new_args)
    elif len(new_args) == 0:
        return Const(1)
    else:
        return new_args[0]
        
mult_identity = Rule(Multiply, mult_identity_op)

def join_const_mult_op(matched):
    new_args = []
    const_args = []
    for arg in matched.args:
        if Rule.is_a(arg, Const):
            const_args.append(arg)
        else:
            new_args.append(arg)
    const_val = Multiply(*const_args).apply({})
    if not const_val.value() == 1:
        new_args.append(const_val)
    if len(new_args) > 1:
        return Multiply(*new_args)
    else:
        return const_val
    
join_mult_consts = Rule(Multiply, join_const_mult_op)
        
def merge_mult_op(matched):
    new_args = []
    for arg in matched.args:
        if isinstance(arg, Multiply):
            new_args = new_args + arg.args
        else:
            new_args.append(arg)
    return Multiply(*new_args)
        
merge_mults = Rule(Multiply, merge_mult_op)

def mult_to_power_op(matched):
    prod_terms = {}
    for arg in matched.args:
        if arg in prod_terms:
            prod_terms[arg] += 1
        else:
            prod_terms[arg] = 1
    new_args = []
    for term in prod_terms:
        if prod_terms[term] == 1:
            new_args.append(term)
        else:
            new_args.append(Power(term, Const(prod_terms[term])))
    if len(new_args) > 1:
        return Multiply(*new_args)
    else:
        return new_args[0]
        
mult_to_power = Rule(Multiply, mult_to_power_op)

def merge_power_terms_op(matched):
    pairs = every_pair(matched.args)
    new_args = copy(matched.args)
    for pair in pairs:
        arg_pair = list(pair)
        if not Rule.is_a(pair[0], Power):
            pair = (Power(pair[0], Const(1)), pair[1])
        if not Rule.is_a(pair[1], Power):
            pair = (pair[0], Power(pair[1], Const(1)))
        if Rule.all_equal([arg.base() for arg in pair]):
            new_args.remove(arg_pair[0])
            new_args.remove(arg_pair[1])
            new_args.append(Power(pair[0].base(), Add(pair[0].exponent(), pair[1].exponent())))
            break
    if len(new_args) > 1:
        return Multiply(*new_args)
    else:
        return new_args[0]
        
merge_power_terms = Rule(Multiply, merge_power_terms_op)

#--- Rules for Power nodes ---

def pow_unitary_op(matched):
    if Rule.is_const_equal(matched.exponent(), 0):
        if not Rule.is_const_equal(matched.base(), 0):
            return Const(1)
        else:
            raise IndeterminateFormException(matched)
    else:
        return False
        
elim_unitary_power = Rule(Power, pow_unitary_op)

def pow_zero_op(matched):
    if Rule.is_const_equal(matched.base(), 0):
        if not Rule.is_const_equal(matched.exponent(), 0):
            return Const(0)
        else:
            raise IndeterminateFormException(matched)
    else:
        return False
        
elim_zero_power = Rule(Power, pow_zero_op)

def pow_ident_op(matched):
    if Rule.is_const_equal(matched.exponent(), 1):
        return matched.base()
    else:
        return False
        
elim_ident_power = Rule(Power, pow_ident_op)

def join_const_pow_op(matched):
    if Rule.all_are(matched.args, Const):
        if Rule.is_const_equal(matched.exponent(), 0) and Rule.is_const_equal(matched.base(), 0):
            raise IndeterminateFormException(matched)
        else:
            return matched.apply({})
    else:
        return False
        
join_power_consts = Rule(Power, join_const_pow_op)

def collapse_power_tree_op(matched):
    if Rule.is_a(matched.base(), Power):
        return Power(matched.base().base(), Multiply(matched.base().exponent(), matched.exponent()))
    else:
        return False
        
collapse_power_tree = Rule(Power, collapse_power_tree_op)

def uncombine_power_base_op(matched):
    if Rule.is_a(matched.base(), Multiply):
        return Multiply(*[Power(term, matched.exponent()) for term in matched.base().args])
    else:
        return False

uncombine_power_base = Rule(Power, uncombine_power_base_op)

import cas.factor as factor

simplify_rules = [
    addition_identity, 
    mult_identity, 
    mult_zero, 
    join_add_consts, 
    join_mult_consts, 
    join_power_consts, 
    merge_adds, 
    add_to_mult, 
    merge_mults, 
    mult_to_power,
    elim_unitary_power,
    elim_zero_power,
    elim_ident_power,
    uncombine_power_base,
    collapse_power_tree,
    merge_power_terms,
    factor.factor
]
