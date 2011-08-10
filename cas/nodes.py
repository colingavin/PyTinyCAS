import cas

class Node(object):
    def __init__(self, *args):
        self.args = list(args)
        
    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, ", ".join([str(arg) for arg in self.args]))
        
    def __repr__(self):
        return str(self)    
        
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.args == other.args
        
    def __ne__(self, other):
        return not self.__eq__(other)    
        
    def __hash__(self):
        hash_val = id(self.__class__)
        for arg in self.args:
            hash_val = hash_val | arg.__hash__()
        return hash_val
        
    def pretty_print(self):
        return str(self)
        
    def apply_rule(self, rule):
        modified_args = [arg.apply_rule(rule) for arg in self.args]
        new_self = self.__class__(*modified_args)
        return rule.apply(new_self)
        
    def apply_rules_until_fixed(self, rules):
        new_self = self
        for rule in rules:
            new_self = new_self.apply_rule(rule)
        print "new: " + new_self.pretty_print()
        if new_self != self:
            return new_self.apply_rules_until_fixed(rules)
        else:
            return new_self
        
    def apply(self, vals):
        return None
        
    def simplify(self):
        print "simplifying: " + self.pretty_print()
        return self.apply_rules_until_fixed(cas.rules.simplify_rules)


class Atom(Node):
    pass

class Const(Atom):
    def __init__(self, value):
        super(Const, self).__init__(value)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.args[0] == other.args[0]

    def pretty_print(self):
        return str(self.value())

    def value(self):
        return self.args[0]
        
    def apply_rule(self, rule):
        return self
        
    def apply(self, vals):
        return self
        

class Var(Atom):
    def __init__(self, name):
        super(Var, self).__init__(name)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.args[0] == other.args[0]

    def pretty_print(self):
        return str(self.name())

    def name(self):
        return self.args[0]

    def apply_rule(self, rule):
        return self
        
    def apply(self, vals):
        if self in vals:
            return Const(vals[self])
        elif self.name() in vals:
            return Const(vals[self.name()])
        else:
            return None
        
        
class Add(Node):
    def __init__(self, *args):
        super(Add, self).__init__(*args)
        
    def pretty_print(self):
        return " + ".join([arg.pretty_print() for arg in self.args])
        
    def apply(self, vals):
        return Const(sum([arg.apply(vals).value() for arg in self.args]))

        
class Multiply(Node):
    def __init__(self, *args):
        super(Multiply, self).__init__(*args)
    
    def pretty_print(self):
        strs = []
        for arg in self.args:
            if not isinstance(arg, Atom):
                strs.append("(%s)" % (arg.pretty_print()))
            else:
                strs.append(arg.pretty_print())
        return " * ".join(strs)
        
    def apply(self, vals):
        applied_args = [arg.apply(vals).value() for arg in self.args]
        prod = 1
        for value in applied_args: prod = prod * value
        return Const(prod)

class Power(Node):
    def __init__(self, *args):
        super(Power, self).__init__(*args)
        
    def pretty_print(self):
        if not isinstance(self.base(), Atom):
            base_str = "(%s)" % (self.base().pretty_print())
        else:
            base_str = self.base().pretty_print()
        if not isinstance(self.exponent(), Atom):
            expt_str = "(%s)" % (self.exponent().pretty_print())
        else:
            expt_str = self.exponent().pretty_print()
        return "%s^%s" % (base_str, expt_str)
    
    def base(self):
        return self.args[0]
    
    def exponent(self):
        return self.args[1]
        
    def apply(self, vals):
        return Const(pow(self.base().apply(vals).value(), self.exponent().apply(vals).value()))

def Divide(numer, denom):
    return Multiply(numer, Power(denom, Const(-1)))
