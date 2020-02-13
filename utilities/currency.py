class Currency:
    """
    A class for storing currency as integer dollars and cents.
    Support for constructing from Currency object, dollars/cents int tuple, float, int, and string values. Left
    empty, the return value will be a zero value currency object.
    """
    def __init__(self, value=None):
        if isinstance(value, Currency):
            self.dollars = value.dollars
            self.cents = value.cents
        elif isinstance(value, tuple):
            if isinstance(value[0], int) and isinstance(value[1], int):
                self.dollars, self.cents = value
        elif isinstance(value, float):
            self.dollars = int(value)
            self.cents = self._extract_cents(value)
        elif isinstance(value, int):
            self.dollars = value
            self.cents = 0
        elif isinstance(value, str):
            float_val = float(value)
            self.dollars = int(float_val)
            self.cents = self._extract_cents(float_val)
        elif value is None:
            self.dollars = 0
            self.cents = 0
        else:
            raise TypeError

    def _extract_cents(self, float_amount):
        return int(round((float_amount - self.dollars), 2) * 100)

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
            return Currency((dollar_sum, cent_sum))
        elif isinstance(other, float) or isinstance(other, int):
            return Currency(self.__float__() + other)
        else:
            raise TypeError

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-other)

    def __rsub__(self, other):
        return (self.__neg__()).__add__(other)

    def __str__(self):
        return f"{self.dollars}.{abs(self.cents)}"

    def __float__(self):
        return self.dollars + (self.cents / 100.0)

    def __neg__(self):
        return Currency((-self.dollars, -self.cents))
