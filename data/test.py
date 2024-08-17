import collections
from decimal import Decimal

diffBook = collections.deque(maxlen=200)
avgDelay = collections.deque(maxlen=200)

def avgBookTime(bookTime):
    average = 0

    for i in range(1, len(bookTime) - 1):
        diffBook.append(bookTime[i]['time'] - bookTime[i-1]['time'])

    for i in range(0, len(bookTime) - 1):
        avgDelay.append(bookTime[i]['currTime'] - bookTime[i]['time'])


        bookAvg = sum(diffBook) / len(diffBook)
        delayAvg = sum(avgDelay) / len(avgDelay)


    print ("Average Book Time: " + str(bookAvg))
    print ("Average Delay: " + str(delayAvg))

    