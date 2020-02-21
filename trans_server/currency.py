from json import JSONEncoder

def _extract_decimal_rounded(float_amount):
    """Removes whole number using int() and rounds remainder to 2 decimal places"""
    if isinstance(float_amount, float):
        return int(round(float_amount - int(float_amount), 2) * 100)


class Currency(JSONEncoder):
    """
    A class for storing currency as integer dollars and cents.
    Support for constructing from Currency object, float, int, and string values. Left
    empty, the return value will be a zero value currency object.
    """
    def __init__(self, value=None, **kwargs):
        super().__init__(**kwargs)
        if isinstance(value, Currency):
            self.dollars = value.dollars
            self.cents = value.cents
        elif isinstance(value, float):
            self.dollars = int(value)
            self.cents = _extract_decimal_rounded(value)
        elif isinstance(value, int):
            self.dollars = value
            self.cents = 0
        elif isinstance(value, str):
            float_val = float(value)
            self.dollars = int(float_val)
            self.cents = _extract_decimal_rounded(float_val)
        elif value is None:
            self.dollars = 0
            self.cents = 0
        else:
            raise ValueError(f"Valid 'Currency' initializer argument types are: "
                             f"<Currency>,<float>,<int>,<str representation of float/int>")

    def __add__(self, other):
        if isinstance(other, Currency):
            cent_sum = self.cents + other.cents
            if cent_sum >= 100:
                dollar_sum = self.dollars + other.dollars + 1
                cent_sum -= 100
            elif cent_sum < 0:
                dollar_sum = self.dollars + other.dollars - 1
                cent_sum += 100
            else:
                dollar_sum = self.dollars + other.dollars
            new_currency = Currency()
            new_currency.dollars = dollar_sum
            new_currency.cents = cent_sum
            return new_currency
        elif isinstance(other, float) or isinstance(other, int):
            return Currency(self.__float__() + other)
        else:
            raise TypeError(f"unsupported operand type(s) for +: 'Currency' and '{type(other)}'")

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-other)

    def __rsub__(self, other):
        return (self.__neg__()).__add__(other)

    def __iadd__(self, other):
        return self.__add__(other)

    def __isub__(self, other):
        return self.__sub__(other)

    def __lt__(self, other):
        if isinstance(other, Currency):
            return (self.dollars < other.dollars) or (self.dollars == other.dollars and self.cents < other.cents)
        elif isinstance(other, float):
            other_dollars = int(other)
            other_cents = _extract_decimal_rounded(other)
            return (self.dollars < other_dollars) or (self.dollars == other_dollars and self.cents < other_cents)
        elif isinstance(other, int):
            return self.dollars < other
        else:
            raise TypeError(f"unsupported operand type(s) for <: 'Currency' and '{type(other)}'")

    def __gt__(self, other):
        return not self.__lt__(other) and not self.__eq__(other)

    def __le__(self, other):
        return not self.__gt__(other)

    def __ge__(self, other):
        return not self.__lt__(other)

    def __eq__(self, other):
        if isinstance(other, Currency):
            return self.dollars == other.dollars and self.cents == other.cents
        elif isinstance(other, float):
            return self.dollars == int(other) and self.cents == _extract_decimal_rounded(other)
        elif isinstance(other, int):
            return self.dollars == other and self.cents == 0
        else:
            raise TypeError(f"unsupported operand type(s) for ==: 'Currency' and '{type(other)}'")

    def __ne__(self, other):
        return not self.__eq__(other)

    def __neg__(self):
        return Currency(-self.__float__())

    def __str__(self):
        return '{0:.2f}'.format(self.__float__())

    def __repr__(self):
        return '{0:.2f}'.format(self.__float__())

    def __float__(self):
        return float(self.dollars) + (float(self.cents) / 100.0)

    def __mul__(self, other):
        return Currency(other * self.dollars) + Currency(other * self.cents)

    def __rmul__(self, other):
        return self.__mul__(other)

    def default(self, o):
        if isinstance(o, Currency):
            return o.__float__()

        return JSONEncoder.default(self, o)
