import numpy as np

def roundSigFigs(num, sigFigs):
    if num != 0:
        return round(num, sigFigs - int(np.floor(np.log10(abs(num))) - 1))
    else:
        return 0


# def volatility(closePices):
#     closePricesNp = np.array(closePrices)

#     ratios = closePricesNp[1:] / closePricesNp[:-1]
#     logReturns = np.log(ratios)

#     return np.std(logReturns)