from cas import *

a = Var("a")
b = Var("b")
c = Var("c")
x = Var("x")
y = Var("y")
z = Var("z")

one = Const(1)
two = Const(2)
three = Const(3)

demo_exprs = [
    Add(two, two),
    Add(x, x),
    Add(x, x, y, y),
    Add(Multiply(two, x), two),
    Power(Power(x, two), Divide(one, two)),
    Add(x, Power(x, two), Power(x, three)),
    Divide(
        Add(Multiply(two, x), Multiply(two, Power(x, three))),
        Power(x, two)
    ),
    Power(
        Add(
            Multiply(Const(4), Power(x, two)),
            Multiply(Const(4), Power(x, three))
        ),
        Divide(one, two)
    )
]

def demo_simplification():
    print "Simplification demo, press return to start:"
    raw_input()
    for expr in demo_exprs:
        print "Going to simplify: " + expr.pretty_print()
        print "Press return to simplify."
        raw_input()
        print "Result: " + expr.simplify().pretty_print() + "\n"
        print "Press return to continue."
        raw_input()        

if __name__ == '__main__':
    demo_simplification()