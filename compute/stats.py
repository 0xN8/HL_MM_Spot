
import math
from decimal import Decimal, ROUND_HALF_UP



def roundSigFigs(value, figures):
    if value == 0:
        return 0
    else:
        # Determine the scale of the number
        scale = int(math.floor(math.log10(abs(value))))
        # Adjust the scale of the number
        scaled_value = value / Decimal(10 ** scale)
        # Round the scaled number
        rounded_scaled_value = scaled_value.quantize(Decimal('1.' + '0' * (figures - 1)), rounding=ROUND_HALF_UP)
        # Adjust the scale of the number back to its original scale
        result = Decimal(rounded_scaled_value * Decimal(10 ** scale))
        return result.normalize()
    


# def volatility(closePices):
#     closePricesNp = np.array(closePrices)

#     ratios = closePricesNp[1:] / closePricesNp[:-1]
#     logReturns = np.log(ratios)

#     return np.std(logReturns)