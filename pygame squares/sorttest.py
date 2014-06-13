import time
import random
random.seed()
ARRAY_SIZE = 5000


import atexit
from time import clock

def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % \
        reduce(lambda ll,b : divmod(ll[0],b) + ll[1:],
            [(t*1000,),1000,60,60])

line = "="*40
def log(s, elapsed=None):
    print line
    print secondsToStr(clock()), '-', s
    if elapsed:
        print "Elapsed time:", elapsed
    print line
    print

def endlog():
    end = clock()
    elapsed = end-start
    log("End Program", secondsToStr(elapsed))

def now():
    return secondsToStr(clock())

start = clock()
atexit.register(endlog)
log("Start Program")


def shellSort(array):
   "Shell sort using Shell's (original) gap sequence: n/2, n/4, ..., 1."
   gap = len(array) // 2
   # loop over the gaps
   while gap > 0:
      # do the insertion sort
      for i in range(gap, len(array)):
         val = array[i]
         j = i
         while j >= gap and array[j - gap] > val:
            array[j] = array[j - gap]
            j -= gap
         array[j] = val
      gap //= 2

numbers = [random.randint(0, 1000) for x in xrange(ARRAY_SIZE)]


# shellSort(numbers)

# print 'Shellsort time: %s' % (time.time() - start)


numbers.sort()

# print 'Python sort time: %s' % (time.time() - start)