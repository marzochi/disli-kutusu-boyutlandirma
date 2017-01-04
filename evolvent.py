# -*- coding: utf-8 -*-
'''
@author  : Mehmet Hanoğlu
@mail    : mail@mehmethanoglu.com.tr
@date    : 04.01.2014
@site    : http://mehmethanoglu.com.tr
@license : GPL ( General Public License )
@desc    : Evolvent( alfa ) fonksiyonu için değer bulma
'''

import math


def p(x) : print x.decode("utf8")
def cos( x ) : return math.cos( math.radians( x ) )
def sin( x ) : return math.sin( math.radians( x ) )
def tan( x ) : return math.tan( math.radians( x ) )
def rad( x ) : return math.radians( x )

def evolvent( alfa0 ) : return tan( alfa0 ) - rad( alfa0 )

def get_evolvents( start, finish, step, fact ) :
    evolvents = {}
    for x in xrange( start, finish+step, step ) :
        ind1,ind2 = x / fact, (x+step) / fact
        evolvents[ind1] = {'i1' : ind1, 'i2' : ind2, 'ev1' : evolvent(ind1), 'ev2' : evolvent(ind2)}
    return evolvents

def find_evolventalfa( ev_alfa, step, times = 1 ) :
    global alfa
    if step :
        evolvents = get_evolvents( step[0], step[1], step[2], step[3] )
        for x in evolvents :
            ev = evolvents[x]
            if ( ev_alfa >= ev['ev1'] and ev_alfa <= ev['ev2'] ) :
                if ( round( ev_alfa, 7 ) == round( ev['ev1'], 7 ) ) :
                    if ( ev_alfa - ev['i1'] > ev['ev2'] - ev_alfa ) :
                        alfa = ev['i2']
                    else :
                        alfa = ev['i1']
                    print "Hata yuzdesi: %3.7f" %( ((ev_alfa - evolvent( alfa )) / ev_alfa)*100.0  )
                else :
                    pow = 10.0**(times)
                    if ( times == 5 ) :
                        pow2 = 10.0**(times-4)
                    elif ( times == 4 ) :
                        pow2 = 10.0**(times-3)
                    elif ( times == 3 ) :
                        pow2 = 10.0**(times-2)
                    else :
                        pow2 = 10.0**(times-1)
                    find_evolventalfa( ev_alfa, [int(ev['i1']*pow), int(ev['i2']*pow), 1, step[3]*pow2], times = times+1 )

            else :
                pass


ev_alfa = 0.014904383
step = [10,    451,    5,    10.0]
find_evolventalfa( ev_alfa, step )
print alfa
