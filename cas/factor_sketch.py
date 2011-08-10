def mult_common_terms(pair):
    common = []
    for fact in pair[0].args:
        if fact in pair[1].args:
            common.append(fact)
    return common
    
def mult_atom_common_terms(pair):
    new_pair = (pair[0], Multiply(Const(1), pair[1]))
    return mult_common_terms(new_pair)
    
def pow_common_terms(pair):
    if not Rule.all_equal([term.base() for term in pair]):
        return []
    if Rule.all_are([term.exponent() for term in pair], Var):
        return []
    common_in_exp = common_terms((pair[0].exponent(), pair[1].exponent()))
    if len(common_in_exp) > 0:
        return Power(pair[0].base(), Multiply(*common_in_exp))
    else:
        return []
        
def pow_atom_common_terms(pair):
    if Rule.is_a(pair[1], Const):
        return []
    if pair[0].base() != pair[1]:
        return []
    return [pair[1]]
    
def mult_pow_common_terms(pair):
    

def common_terms(pair):
    if Rule.all_are(pair, Const):
        return []
    if Rule.all_are(pair, Var):
        if pair[0] == pair[1]:
            return [pair[0]]
        else:
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

def factor_op(matched):
    pairs = every_pair(matched.args)
    new_args = copy(matched.args)
    for pair in pairs:
        commons = common_terms(pair)
        if len(commons) > 0:
            new_args.remove(pair[0])
            new_args.remove(pair[1])
            pulled = Multiply(*commons)
            inv_pulled = Power(pulled, Const(-1))
            new_args.append(Multiply(pulled, Add(Multiply(inv_pulled, pair[0]), Multiply(inv_pulled, pair[1]))))
            break