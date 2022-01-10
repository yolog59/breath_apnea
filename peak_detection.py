from numpy import NaN, Inf, arange, array

def peakdet(table, delta):
   
    maxtab = []
    mintab = []

    v = table['data']
    x = arange(1, len(v))
    
    mn, mx = Inf, -Inf
    mnpos, mxpos = NaN, NaN
    
    lookformax = True
    
    for i in arange(1, len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = table['n'][i]
        if this < mn:
            mn = this
            mnpos = table['n'][i]
        
        if lookformax:
            if this < mx - delta:
                maxtab.append((mxpos, mx))
                mn = this
                mnpos = table['n'][i]
                lookformax = False
        else:
            if this > mn + delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = table['n'][i]
                lookformax = True

    return array(maxtab), array(mintab)

# проверка
# from matplotlib.pyplot import plot, scatter, show
# series = [0,0,0,2,0,0,0,-2,0,0,0,2,0,0,0,-2,0]
# maxtab, mintab = peakdet(series,.3)
# plot(series)
# scatter(array(maxtab)[:,0], array(maxtab)[:,1], color='blue')
# scatter(array(mintab)[:,0], array(mintab)[:,1], color='red')
# show()