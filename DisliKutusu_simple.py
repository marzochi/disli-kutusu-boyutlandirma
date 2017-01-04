# -*- coding: utf-8 -*-
# Dişli Kutusu Hesabı

import time
import math

def p(x) : print x.decode("utf8")
def cos( x ) : return math.cos( math.radians( x ) )
def sin( x ) : return math.sin( math.radians( x ) )
def tan( x ) : return math.tan( math.radians( x ) )
def rad( x ) : return math.radians( x )


__time_start = time.time()
############# GİRİLEN DEĞERLER ############

Pg = 1.5 # KW     - Giriş gücü
ng = 750 # [d/dk] - Giriş devri
nc = 75  # [d/dk] - Çıkış devri
z1 = 18  # 1.Dişlinin diş sayısı
z3 = 20  # 3.Dişlinin diş sayısı

n = {
    '1' : 0.98,     # 1.Kademe verimi
    '2' : 0.98,     # 2.Kademe verimi
    'r' : 0.98      # Rulman verimi
}

E = 206000      # MPa - Elastisite modülü
Fid = 0.8       # Diş form faktörü
S = 1.5         # Genel emniyet katsayısı

# Malzeme seçilecek
# Malzemeye göre
SFlim = 370.0   # MPa
SHlim = 1000.0  # MPa

############# -- TABLODAN GİRİLEN #############
Kc = 1.5        # İşletme faktörü / çalışma faktörü
alfa0 = 20.0    # Kavrama açısı [Derece] Almanyada standart. [14.5, 15, 20, 22.5, 25]

# Standart modül değerleri
S1_modul = [0.05,0.06,0.08,0.1,0.12,0.15,0.2,0.3,0.4,0.5,0.6,0.8,1.0,1.25,1.5,2.0,2.5,3.0,4.0,5.0,6.0,8.0,10.0,12.0,16.0,20.0,25.0,32.0,40.0,50.0,60.0,80.0,100.0]
S2_modul = [0.055,0.07,0.09,0.11,0.14,0.18,0.22,0.28,0.35,0.45,0.55,0.7,0.9,1.125,1.375,1.75,2.25,2.75,3.5,4.5,5.5,7.0,9.0,11.0,14.0,18.0,22.0,28.0,36.0,45.0,55.0,70.0,90.0]
# Seri 2 de 6.5 değerinin tercih edilmemesi istenildiği için kaldırıldı.

############# PROFİL KAYDIRMA #################
x1 = 0.3
x2 = -0.4
x3 = 0.2
x4 = -0.2
Yf1 = 2.96        # Tablodan z ve x değerine göre bulunur.Profil kaydırma olduğu için pkay = 0.2 için tablodan bakılır
Yf2 = 2.96
Yf3 = 2.96
Yf4 = 2.96

################ FONKSİYONLAR #################
def evolvent( alfa0 ) : return tan( alfa0 ) - rad( alfa0 )

def get_evolvents( start, finish, step, fact ) :
    evolvents = {}
    for x in xrange( start, finish+step, step ) :
        ind1,ind2 = x / fact, (x+step) / fact
        evolvents[ind1] = {'i1' : ind1, 'i2' : ind2, 'ev1' : evolvent(ind1), 'ev2' : evolvent(ind2)}
    return evolvents
#
# Evolvent bulma fonksiyonu - Hata oranı : Max. milyonda 2 ( 7 anlamlı rakama göre kontrol )
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
                    #print "Hata yuzdesi: %3.7f" %( ((ev_alfa - evolvent( alfa )) / ev_alfa)*100.0  )
                else :
                    pow = 10.0**(times)
                    if ( times == 5 ) : pow2 = 10.0**(times-4)
                    elif ( times == 4 ) : pow2 = 10.0**(times-3)
                    elif ( times == 3 ) : pow2 = 10.0**(times-2)
                    else : pow2 = 10.0**(times-1)
                    find_evolventalfa( ev_alfa, [int(ev['i1']*pow), int(ev['i2']*pow), 1, step[3]*pow2], times = times+1 )
            else :
                pass
#

def EmniyetKontrolu( disli, dind, kademe, kind ) :
    global ng, alfa0, Fid, Kc, Kv
    v1 = ( math.pi * ng / 30.0 ) * disli[str(dind)]['d0'] / ( 2.0 * 1000.0 )
    if ( v1 < 3.0 ) :
        Kv = 1
    Ft = ( 2000.0 * disli[str(dind)]['Md'] ) / disli[str(dind)]['d0']
    Fr = Ft * tan( alfa0 )
    SFy = ( Ft * disli['1']['Yf'] ) / ( disli[str(dind)]['m'] * Fid * disli[str(dind)]['d0'] )
    Keps1 = 0.25 + ( 0.75 / kademe[str(kind)]['eps'] )
    SFh = SFy * Kc * Kv * Keps1
    SFem = SFlim / SFh
    Keps2 = math.sqrt( ( 4.0 - kademe[str(kind)]['eps'] ) / 3.0 )
    SHy = math.sqrt( ( Ft * Kc * Kv * kademe[str(kind)]['ki'] ) / ( ( disli[str(dind)]['Yf'] * disli[str(dind)]['d0'] ) * disli[str(dind)]['d0'] ) )
    SHh = SHy * Keps2 * Ke
    SHem = SHlim / SHh
    b1 = disli['1']['Yf'] * disli[str(dind)]['d0']
    SFd = ( Ft * disli[str(dind)]['Yf'] ) / ( disli[str(dind)]['m'] * b1 )
    SFhd = SFd * Kc * Kv * Keps1
    SHdem = SFlim / SFhd
    SHyd = math.sqrt( ( Ft * Kc * Kv ) / ( b1 * disli[str(dind)]['d0'] ) ) * kademe[str(kind)]['ki']
    SHdh = SHyd * Ke * Keps1
    SHde = SHlim / SHdh

    return {
        'v'  : v1,
        'Kv' : Kv,
        'Ft' : Ft,
        'Fr' : Fr,
        'SFy' : SFy,
        'SFh' : SFh,
        'SFem' : SFem,
        'SHy' : SHy,
        'SHh' : SHh,
        'SHem' : SHem,
        'b1' : b1,
        'SFd' : SFd,
        'SFhd' : SFhd,
        'SHdem' : SHdem,
        'SHyd' : SHyd,
        'SHdh' : SHdh,
        'SHde' : SHde,
    }


################ HESAPLAMALAR #################
# Toplam verim
nt = 1.0
for x in n : nt *= n[x]

Pc = nt * Pg
Pk = Pg - Pc

n1 = ng

it = ng / nc
kademe = { }
disli = { }


#Kademe sayısı belirleme
if ( it >=0 and it <= 6 ) :
    kademe['1'] = {}
    kademe['1']['i'] = it
    kademe['1']['cut'] = False
    # Kademelere verim atama
    kademe['1']['n'] = n['1']
elif ( it >= 6 and it <= 45 ) :
    kademe['1'] = {}
    kademe['2'] = {}
    kademe['1']['i'] = 0.7 * math.pow( it, 0.7 )
    kademe['1']['cut'] = False
    kademe['2']['i'] = it / kademe['1']['i']
    kademe['2']['cut'] = False
    # Kademelere verim atama
    kademe['1']['n'] = n['1']
    kademe['2']['n'] = n['2']
    # Kademelere çevrim oranı faktörü atama
    kademe['1']['ki'] = math.sqrt( ( kademe['1']['i'] + 1.0 ) / kademe['1']['i'] )
    kademe['2']['ki'] = math.sqrt( ( kademe['2']['i'] + 1.0 ) / kademe['2']['i'] )

# Dişli alanlarını oluşturma
for x in range( 1, len( kademe ) * 2 + 1, 1 ) : disli[ str(x) ] = {}


# Bir kademeli dişli kutusu için hesaplar
if ( len( kademe ) == 1 ) :
    pass
#
# İki kademeli dişli kutusu için hesaplar
elif ( len( kademe ) == 2 ) :
    kademe_veri1 = kademe['1']
    kademe_veri2 = kademe['2']

    disli['1']['x'] = x1
    disli['2']['x'] = x2
    disli['3']['x'] = x3
    disli['4']['x'] = x4
    disli['1']['Yf'] = Yf1
    disli['2']['Yf'] = Yf2
    disli['3']['Yf'] = Yf3
    disli['4']['Yf'] = Yf4

    ##################  Birinci kademe için hesaplar
    disli['1']['z'] = z1
    disli['2']['z'] = math.ceil( disli['1']['z'] * kademe_veri1['i'] ) + 1.0
    disli['1']['Md'] = 9550 * ( Pg / ng ) * Kc * kademe_veri1['n'] * n['r']
    disli['2']['Md'] = disli['1']['Md'] * kademe_veri1['i']

    Ki = math.sqrt( ( 1.0 + kademe_veri1['i'] ) / kademe_veri1['i'] )    # Çevrim oranı faktörü
    Ke = math.sqrt( 0.175 * E )                                           # Elastisite faktörü
    Ka = math.sqrt( 1.0 / ( cos( alfa0 ) * sin( alfa0 ) ) )              # Yuvarlanma noktası faktörü

    # Diş dibi mukavemetine göre modül hesabı
    m1 = math.pow( ( 2.0 * 1000.0 * disli['1']['Md'] * disli['1']['Yf'] ) / ( disli['1']['z']**2 * Fid * SFlim ) , 1.0 / 3.0)
    # Yüzey ezilmesi göre modül hesabı
    m2 = ( 1.0 / disli['1']['z'] ) * math.pow( ( 2.0 * 1000.0 * disli['1']['Md'] * Ke**2 * Ka**2 * Ki ) / ( Fid * SHlim**2 ), 1.0 / 3.0 )

    if ( m1 > m2 ) : disli['1']['m'] = m1
    else : disli['1']['m'] = m2

    for x in range( len ( S1_modul ) - 1 ) :
        if ( disli['1']['m'] >= S1_modul[x] and disli['1']['m'] <= S1_modul[x+1] ) :
            disli['1']['m'] = S1_modul[x+1]
            break

    # Diş dibi mukavemetine göre modül hesabı
    m1 = math.pow( ( 2.0 * 1000.0 * disli['2']['Md'] * disli['2']['Yf'] ) / ( disli['2']['z']**2 * ( Fid ) * ( SFlim ) ) , 1.0 / 3.0)
    # Yüzey ezilmesi göre modül hesabı
    m2 = ( 1.0 / disli['2']['z'] ) * math.pow( ( 2.0 * 1000.0 * disli['2']['Md'] * Ke**2 * Ka**2 * Ki ) / ( Fid * ( SHlim )**2 ), 1.0 / 3.0 )

    if ( m1 > m2 ) : disli['2']['m'] = m1
    else : disli['2']['m'] = m2

    for x in range( len ( S1_modul ) - 1 ) :
        if ( disli['2']['m'] >= S1_modul[x] and disli['2']['m'] <= S1_modul[x+1] ) :
            disli['2']['m'] = S1_modul[x+1]
            break
    #

    # Eş çalışan dişliler için modül hesabı
    if ( disli['1']['m'] > disli['2']['m'] ) : disli['2']['m'] = disli['1']['m']
    else : disli['1']['m'] = disli['2']['m']

    ##################  İkinci kademe için hesaplar
    disli['3']['z'] = z3
    disli['4']['z'] = math.ceil( disli['3']['z'] * kademe_veri2['i'] ) + 1.0
    disli['3']['Md'] = disli['2']['Md']
    disli['4']['Md'] = 9550 * ( Pc / nc ) * Kc * kademe_veri2['n'] * n['r']

    Ki = math.sqrt( ( 1.0 + kademe_veri2['i'] ) / kademe_veri2['i'] )    # Çevrim oranı faktörü
    Ke = math.sqrt( 0.175 * E )                                           # Elastisite faktörü
    Ka = math.sqrt( 1.0 / ( cos( alfa0 ) * sin( alfa0 ) ) )              # Yuvarlanma noktası faktörü

    # Diş dibi mukavemetine göre modül hesabı
    m1 = math.pow( ( 2.0 * 1000.0 * disli['3']['Md'] * disli['3']['Yf'] ) / ( disli['3']['z']**2 * ( Fid ) * ( SFlim ) ) , 1.0 / 3.0)
    # Yüzey ezilmesi göre modül hesabı
    m2 = ( 1.0 / disli['3']['z'] ) * math.pow( ( 2.0 * 1000.0 * disli['3']['Md'] * Ke**2 * Ka**2 * Ki ) / ( Fid * ( SHlim )**2 ), 1.0 / 3.0 )

    if ( m1 > m2 ) : disli['3']['m'] = m1
    else : disli['3']['m'] = m2

    for x in range( len ( S2_modul ) - 1 ) :
        if ( disli['3']['m'] >= S2_modul[x] and disli['3']['m'] <= S2_modul[x+1] ) :
            disli['3']['m'] = S2_modul[x+1]
            break

    # Diş dibi mukavemetine göre modül hesabı
    m1 = math.pow( ( 2.0 * 1000.0 * disli['4']['Md'] * disli['4']['Yf'] ) / ( disli['4']['z']**2 * ( Fid ) * ( SFlim ) ) , 1.0 / 3.0)
    # Yüzey ezilmesi göre modül hesabı
    m2 = ( 1.0 / disli['4']['z'] ) * math.pow( ( 2.0 * 1000.0 * disli['4']['Md'] * Ke**2 * Ka**2 * Ki ) / ( Fid * ( SHlim )**2 ), 1.0 / 3.0 )

    if ( m1 > m2 ) : disli['4']['m'] = m1
    else : disli['4']['m'] = m2

    for x in range( len ( S2_modul ) - 1 ) :
        if ( disli['4']['m'] >= S2_modul[x] and disli['4']['m'] <= S2_modul[x+1] ) :
            disli['4']['m'] = S2_modul[x+1]
            break
    #
    # Eş çalışan dişliler için modül hesabı
    if ( disli['3']['m'] > disli['4']['m'] ) : disli['4']['m'] = disli['3']['m']
    else : disli['3']['m'] = disli['4']['m']

    ######################### 1. ve 2. Dişli için #################################

    # Sıfır dişli çark
    if ( disli['1']['x'] == disli['2']['x'] == 0.0 ) :
        kademe['1']['type'] = "Sıfır dişli çark"

        # Birinci Dişli
        disli['1']['d0'] = disli['1']['m'] * disli['1']['z']             # Taksimat dairesi
        disli['1']['db'] = disli['1']['d0'] + 2 * disli['1']['m']        # Baş dairesi
        disli['1']['dt'] = disli['1']['d0'] - 2.5 * disli['1']['m']      # Taban dairesi
        disli['1']['s0'] = math.pi * disli['1']['m'] / 2.0               # Diş kalınlığı

        # İkinci Dişli
        disli['2']['d0'] = disli['2']['m'] * disli['2']['z']             # Taksimat dairesi
        disli['2']['db'] = disli['2']['d0'] + 2 * disli['2']['m']        # Baş dairesi
        disli['2']['dt'] = disli['2']['d0'] - 2.5 * disli['2']['m']      # Taban dairesi
        disli['2']['s0'] = math.pi * disli['2']['m'] / 2.0               # Diş kalınlığı

        kademe['1']['a0'] = disli['1']['m'] * ( disli['1']['z'] + disli['2']['z'] ) / 2.0
        kademe['1']['a'] = kademe['1']['a0']
        kademe['1']['alfa0'] = alfa0
        kademe['1']['alfa'] = kademe['1']['alfa0']

        ev_alfa0 = evolvent( alfa0 )
        ev_alfa = tan( alfa0 ) + ev_alfa0
        kademe['1']['ev_alfa0'] = ev_alfa0
        kademe['1']['ev_alfa'] = ev_alfa

        disli['1']['d'] = disli['1']['d0']
        disli['2']['d'] = disli['2']['d0']

        disli['1']['hb'] = disli['2']['hb'] = disli['1']['m']
        disli['1']['ht'] = disli['2']['ht'] = 1.25 * disli['1']['m']
        disli['1']['h'] = disli['2']['h'] = 2.25 * disli['1']['m']

    # Sıfır kaydırmalı K-0
    elif ( disli['1']['x'] + disli['2']['x'] == 0.0 ) :
        kademe['1']['type'] = "Sıfır kaydırmalı K-0"

        if ( disli['1']['x'] >= 0.0 ) :
            # Artı Dişli : 1
            disli['1']['d0'] = disli['1']['m'] * disli['1']['z']
            disli['1']['db'] = disli['1']['d0'] + 2 * disli['1']['m'] * ( 1 + disli['1']['x'] )
            disli['1']['dt'] = disli['1']['d0'] - 2 * disli['1']['m'] * ( 1.25 - disli['1']['x'] )
            disli['1']['s0'] = ( math.pi * disli['1']['m'] / 2.0 ) + ( 2 * disli['1']['x'] * tan( alfa0 ) )
            disli['1']['hb'] = disli['1']['m'] * ( 1 + disli['1']['x'] )
            disli['1']['ht'] = disli['1']['m'] * ( 1.25 - disli['1']['x'] )
            disli['1']['h'] = disli['1']['ht'] + disli['1']['hb']

            # Eksi Dişli : 2
            disli['2']['d0'] = disli['2']['m'] * disli['2']['z']
            disli['2']['db'] = disli['2']['d0'] + 2 * disli['2']['m'] * ( 1 - disli['1']['x'] )
            disli['2']['dt'] = disli['2']['d0'] - 2 * disli['2']['m'] * ( 1.25 + disli['1']['x'] )
            disli['2']['s0'] = ( math.pi * disli['1']['m'] / 2.0 ) - ( 2 * disli['2']['x'] * tan( alfa0 ) )
            disli['2']['hb'] = disli['2']['m'] * ( 1 - disli['2']['x'] )
            disli['2']['ht'] = disli['2']['m'] * ( 1.25 + disli['2']['x'] )
            disli['2']['h'] = disli['2']['ht'] + disli['2']['hb']

        else :
            # Eksi Dişli : 1
            disli['1']['d0'] = disli['1']['m'] * disli['1']['z']
            disli['1']['db'] = disli['1']['d0'] + 2 * disli['1']['m'] * ( 1 - disli['1']['x'] )
            disli['1']['dt'] = disli['1']['d0'] - 2 * disli['1']['m'] * ( 1.25 + disli['1']['x'] )
            disli['1']['s0'] = ( math.pi * disli['1']['m'] / 2.0 ) - ( 2 * disli['1']['x'] * tan( alfa0 ) )
            disli['1']['hb'] = disli['1']['m'] * ( 1 - disli['1']['x'] )
            disli['1']['ht'] = disli['1']['m'] * ( 1.25 + disli['1']['x'] )
            disli['1']['h'] = disli['1']['ht'] + disli['1']['hb']

            # Artı Dişli : 2
            disli['2']['d0'] = disli['2']['m'] * disli['2']['z']
            disli['2']['db'] = disli['2']['d0'] + 2 * disli['2']['m'] * ( 1 + disli['2']['x'] )
            disli['2']['dt'] = disli['2']['d0'] - 2 * disli['2']['m'] * ( 1.25 - disli['2']['x'] )
            disli['2']['s0'] = ( math.pi * disli['2']['m'] / 2.0 ) + ( 2 * disli['2']['x'] * tan( alfa0 ) )
            disli['2']['hb'] = disli['2']['m'] * ( 1 + disli['2']['x'] )
            disli['2']['ht'] = disli['2']['m'] * ( 1.25 - disli['2']['x'] )
            disli['2']['h'] = disli['2']['ht'] + disli['2']['hb']
        #

        kademe['1']['a0'] = disli['1']['m'] * ( disli['1']['z'] + disli['2']['z'] ) / 2
        kademe['1']['a'] = kademe['1']['a0']
        kademe['1']['alfa0'] = alfa0
        kademe['1']['alfa'] = kademe['1']['alfa0']

        ev_alfa0 = evolvent( alfa0 )
        ev_alfa = tan( alfa0 ) + ev_alfa0
        kademe['1']['ev_alfa0'] = ev_alfa0
        kademe['1']['ev_alfa'] = ev_alfa

        disli['1']['d'] = disli['1']['d0']
        disli['2']['d'] = disli['2']['d0']

    # Kaydırmalı K
    else :
        kademe['1']['type'] = "Kaydırmalı K"

        if ( disli['1']['x'] >= 0 ) :
            # Artı Dişli : 1
            disli['1']['d0'] = disli['1']['m'] * disli['1']['z']
            disli['1']['db'] = disli['1']['d0'] + 2 * disli['1']['m'] * ( 1 + disli['1']['x'] )
            disli['1']['dt'] = disli['1']['d0'] - 2 * disli['1']['m'] * ( 1.25 - disli['1']['x'] )
            disli['1']['s0'] = ( math.pi * disli['1']['m'] / 2.0 ) + ( 2 * x * tan( alfa0 ) )
        else :
            # Eksi Dişli : 1
            disli['1']['d0'] = disli['1']['m'] * disli['1']['z']
            disli['1']['db'] = disli['1']['d0'] + 2 * disli['1']['m'] * ( 1 + disli['1']['x'] )
            disli['1']['dt'] = disli['1']['d0'] - 2 * disli['1']['m'] * ( 1.25 - disli['1']['x'] )
            disli['1']['s0'] = ( math.pi * disli['1']['m'] / 2.0 ) + ( 2 * x * tan( alfa0 ) )
        #
        if ( disli['2']['x'] > 0 ) :
            # Artı Dişli : 2
            disli['2']['d0'] = disli['2']['m'] * disli['2']['z']
            disli['2']['db'] = disli['2']['d0'] + 2 * disli['2']['m'] * ( 1 + disli['2']['x'] )
            disli['2']['dt'] = disli['2']['d0'] - 2 * disli['2']['m'] * ( 1.25 - disli['2']['x'] )
            disli['2']['s0'] = ( math.pi * disli['2']['m'] / 2.0 ) + ( 2 * x * tan( alfa0 ) )

        else :
            # Eksi Dişli : 2
            disli['2']['d0'] = disli['2']['m'] * disli['2']['z']
            disli['2']['db'] = disli['2']['d0'] + 2 * disli['2']['m'] * ( 1 + disli['1']['x'] )
            disli['2']['dt'] = disli['2']['d0'] - 2 * disli['2']['m'] * ( 1.25 - disli['1']['x'] )
            disli['2']['s0'] = ( math.pi * disli['1']['m'] / 2.0 ) + ( 2 * x * tan( alfa0 ) )

        kademe['1']['a0'] = ( disli['1']['m'] * ( disli['1']['z'] + disli['2']['z'] ) ) / 2
        kademe['1']['alfa0'] = alfa0

        ev_alfa0 = evolvent( kademe['1']['alfa0'] )
        ev_alfa = 2 * ( ( disli['1']['x'] + disli['2']['x'] ) / ( disli['1']['z'] + disli['2']['z'] ) ) * tan( kademe['1']['alfa0'] ) + ev_alfa0
        kademe['1']['ev_alfa0'] = ev_alfa0
        kademe['1']['ev_alfa'] = ev_alfa

        # Evolventi bulma fonksiyonu
        find_evolventalfa( kademe['1']['ev_alfa'], [10, 451, 5, 10.0] )

        kademe['1']['alfa'] = alfa
        kademe['1']['a'] = kademe['1']['a0'] * ( cos( kademe['1']['alfa0'] ) / cos( kademe['1']['alfa'] ) )

        # Baş kısaltma yapılması - kontrolü
        if ( disli['1']['x'] >= 0 ) :pass
            # Artı Dişli : 1
            # Eksi Dişli : 2
        else :pass
            # Artı Dişli : 2
            # Eksi Dişli : 1

        db1k = 2 * ( kademe['1']['a'] + disli['1']['m'] - ( disli['2']['x'] * disli['1']['m'] ) ) - disli['2']['d0']
        db2k = 2 * ( kademe['1']['a'] + disli['1']['m'] - ( disli['1']['x'] * disli['1']['m'] ) ) - disli['1']['d0']
        dt1k = disli['1']['d0'] - ( 2 * disli['1']['m'] * ( 1.25 - disli['1']['x'] ) )
        dt2k = disli['2']['d0'] - ( 2 * disli['1']['m'] * ( 1.25 - disli['2']['x'] ) )

        sb = kademe['1']['a'] - ( ( db1k + dt2k ) / 2 )
        if ( sb >= ( 0.1 * disli['1']['m'] ) and sb <= ( 0.3 * disli['1']['m'] ) ) : kademe['1']['cut'] = False
        else :
            disli['1']['dbk'] = db1k
            disli['1']['dtk'] = dt1k
            disli['2']['dbk'] = db2k
            disli['2']['dtk'] = dt2k
#
        if ( disli['1']['x'] > 0 ) :
            disli['1']['hb'] = disli['1']['m'] * ( 1 + disli['1']['x'] )
            disli['1']['ht'] = disli['1']['m'] * ( 1.25 - disli['1']['x'] )
            disli['1']['h'] = disli['1']['hb'] + disli['1']['ht']
        else :
            disli['1']['hb'] = disli['1']['m'] * ( 1 - disli['1']['x'] )
            disli['1']['ht'] = disli['1']['m'] * ( 1.25 + disli['1']['x'] )
            disli['1']['h'] = disli['1']['hb'] + disli['1']['ht']
        #
        if ( disli['2']['x'] > 0 ) :
            disli['2']['hb'] = disli['2']['m'] * ( 1 + disli['2']['x'] )
            disli['2']['ht'] = disli['2']['m'] * ( 1.25 - disli['2']['x'] )
            disli['2']['h'] = disli['2']['hb'] + disli['2']['ht']
        else :
            disli['2']['hb'] = disli['2']['m'] * ( 1 - disli['2']['x'] )
            disli['2']['ht'] = disli['2']['m'] * ( 1.25 + disli['2']['x'] )
            disli['2']['h'] = disli['2']['hb'] + disli['2']['ht']
    #

    ######################### 3. ve 4. Dişli için #################################
    # Sıfır dişli çark
    if ( disli['3']['x'] == disli['4']['x'] == 0 ) :
        kademe['2']['type'] = "Sıfır dişli çark"

        # Birinci Dişli
        disli['3']['d0'] = disli['3']['m'] * disli['3']['z']             # Taksimat dairesi
        disli['3']['db'] = disli['3']['d0'] + 2 * disli['3']['m']        # Baş dairesi
        disli['3']['dt'] = disli['3']['d0'] - 2.5 * disli['3']['m']      # Taban dairesi
        disli['3']['s0'] = math.pi * disli['3']['m'] / 2.0               # Diş kalınlığı

        # İkinci Dişli
        disli['4']['d0'] = disli['4']['m'] * disli['4']['z']             # Taksimat dairesi
        disli['4']['db'] = disli['4']['d0'] + 2 * disli['4']['m']        # Baş dairesi
        disli['4']['dt'] = disli['4']['d0'] - 2.5 * disli['4']['m']      # Taban dairesi
        disli['4']['s0'] = math.pi * disli['4']['m'] / 2.0               # Diş kalınlığı

        kademe['2']['a0'] = disli['3']['m'] * ( disli['3']['z'] + disli['4']['z'] ) / 2.0
        kademe['2']['a'] = kademe['2']['a0']
        kademe['2']['alfa0'] = alfa0
        kademe['2']['alfa'] = kademe['2']['alfa0']

        ev_alfa0 = evolvent( alfa0 )
        ev_alfa = tan( alfa0 ) + ev_alfa0
        kademe['2']['ev_alfa0'] = ev_alfa0
        kademe['2']['ev_alfa'] = ev_alfa


        disli['3']['d'] = disli['3']['d0']
        disli['4']['d'] = disli['4']['d0']

        disli['3']['hb'] = disli['4']['hb'] = disli['3']['m']
        disli['3']['ht'] = disli['4']['ht'] = 1.25 * disli['3']['m']
        disli['3']['h'] = disli['4']['h'] = 2.25 * disli['3']['m']

    # Sıfır kaydırmalı K-0
    elif ( disli['3']['x'] + disli['4']['x'] == 0 ) :
        kademe['2']['type'] = "Sıfır kaydırmalı K-0"

        if ( disli['3']['x'] >= 0.0 ) :
            # Artı Dişli : 1
            disli['3']['d0'] = disli['3']['m'] * disli['3']['z']
            disli['3']['db'] = disli['3']['d0'] + 2 * disli['3']['m'] * ( 1 + disli['3']['x'] )
            disli['3']['dt'] = disli['3']['d0'] - 2 * disli['3']['m'] * ( 1.25 - disli['3']['x'] )
            disli['3']['s0'] = ( math.pi * disli['3']['m'] / 2.0 ) + ( 2 * disli['3']['x'] * tan( alfa0 ) )
            disli['3']['hb'] = disli['3']['m'] * ( 1 + disli['3']['x'] )
            disli['3']['ht'] = disli['3']['m'] * ( 1.25 - disli['3']['x'] )
            disli['3']['h'] = disli['3']['ht'] + disli['3']['hb']

            # Eksi Dişli : 2
            disli['4']['d0'] = disli['4']['m'] * disli['4']['z']
            disli['4']['db'] = disli['4']['d0'] + 2 * disli['4']['m'] * ( 1 - disli['3']['x'] )
            disli['4']['dt'] = disli['4']['d0'] - 2 * disli['4']['m'] * ( 1.25 + disli['3']['x'] )
            disli['4']['s0'] = ( math.pi * disli['3']['m'] / 2.0 ) - ( 2 * disli['4']['x'] * tan( alfa0 ) )
            disli['4']['hb'] = disli['4']['m'] * ( 1 - disli['4']['x'] )
            disli['4']['ht'] = disli['4']['m'] * ( 1.25 + disli['4']['x'] )
            disli['4']['h'] = disli['4']['ht'] + disli['4']['hb']

        else :
            # Eksi Dişli : 1
            disli['3']['d0'] = disli['3']['m'] * disli['3']['z']
            disli['3']['db'] = disli['3']['d0'] + 2 * disli['3']['m'] * ( 1 - disli['3']['x'] )
            disli['3']['dt'] = disli['3']['d0'] - 2 * disli['3']['m'] * ( 1.25 + disli['3']['x'] )
            disli['3']['s0'] = ( math.pi * disli['3']['m'] / 2.0 ) - ( 2 * disli['3']['x'] * tan( alfa0 ) )
            disli['3']['hb'] = disli['3']['m'] * ( 1 - disli['3']['x'] )
            disli['3']['ht'] = disli['3']['m'] * ( 1.25 + disli['3']['x'] )
            disli['3']['h'] = disli['3']['ht'] + disli['3']['hb']

            # Artı Dişli : 2
            disli['4']['d0'] = disli['4']['m'] * disli['4']['z']
            disli['4']['db'] = disli['4']['d0'] + 2 * disli['4']['m'] * ( 1 + disli['4']['x'] )
            disli['4']['dt'] = disli['4']['d0'] - 2 * disli['4']['m'] * ( 1.25 - disli['4']['x'] )
            disli['4']['s0'] = ( math.pi * disli['4']['m'] / 2.0 ) + ( 2 * disli['4']['x'] * tan( alfa0 ) )
            disli['4']['hb'] = disli['4']['m'] * ( 1 + disli['4']['x'] )
            disli['4']['ht'] = disli['4']['m'] * ( 1.25 - disli['4']['x'] )
            disli['4']['h'] = disli['4']['ht'] + disli['4']['hb']
        #

        kademe['2']['a0'] = disli['3']['m'] * ( disli['3']['z'] + disli['4']['z'] ) / 2
        kademe['2']['a'] = kademe['2']['a0']
        kademe['2']['alfa0'] = alfa0
        kademe['2']['alfa'] = kademe['2']['alfa0']

        ev_alfa0 = evolvent( alfa0 )
        ev_alfa = tan( alfa0 ) + ev_alfa0
        kademe['2']['ev_alfa0'] = ev_alfa0
        kademe['2']['ev_alfa'] = ev_alfa

        disli['3']['d'] = disli['3']['d0']
        disli['4']['d'] = disli['4']['d0']

    # Kaydırmalı K
    else :
        kademe['2']['type'] = "Kaydırmalı K"

        # Birinci Dişli
        disli['3']['d0'] = disli['3']['m'] * disli['3']['z']
        disli['3']['db'] = disli['3']['d0'] + 2 * disli['3']['m'] * ( 1 + disli['3']['x'] )
        disli['3']['dt'] = disli['3']['d0'] - 2 * disli['3']['m'] * ( 1.25 - disli['3']['x'] )
        disli['3']['s0'] = ( math.pi * disli['3']['m'] / 2.0 ) + ( 2 * x * tan( alfa0 ) )

        # İkinci Dişli
        disli['4']['d0'] = disli['4']['m'] * disli['4']['z']
        disli['4']['db'] = disli['4']['d0'] + 2 * disli['4']['m'] * ( 1 + disli['3']['x'] )
        disli['4']['dt'] = disli['4']['d0'] - 2 * disli['4']['m'] * ( 1.25 - disli['3']['x'] )
        disli['4']['s0'] = ( math.pi * disli['3']['m'] / 2.0 ) + ( 2 * x * tan( alfa0 ) )

        kademe['2']['a0'] = ( disli['3']['m'] * ( disli['3']['z'] + disli['4']['z'] ) ) / 2
        kademe['2']['alfa0'] = alfa0

        ev_alfa0 = evolvent( alfa0 )
        ev_alfa = 2 * ( ( disli['3']['x'] + disli['4']['x'] ) / ( disli['3']['z'] + disli['4']['z'] ) ) * tan( alfa0 ) + ev_alfa0

        # Gerekirse kullanılacak
        kademe['2']['ev_alfa0'] = ev_alfa0
        kademe['2']['ev_alfa'] = ev_alfa

        # Evolventi bulma fonksiyonu
        find_evolventalfa( ev_alfa, [10, 451, 5, 10.0] )

        kademe['2']['alfa'] = alfa
        kademe['2']['a'] = kademe['2']['a0'] * ( cos( alfa0 ) / cos( alfa ) )

        # Baş kısaltma yapılması - kontrolü
        db1k = 2 * ( kademe['2']['a'] + disli['3']['m'] - ( disli['4']['x'] * disli['3']['m'] ) ) - disli['4']['d0']
        db2k = 2 * ( kademe['2']['a'] + disli['3']['m'] - ( disli['3']['x'] * disli['3']['m'] ) ) - disli['3']['d0']
        dt1k = disli['3']['d0'] - ( 2 * disli['3']['m'] * ( 1.25 - disli['3']['x'] ) )
        dt2k = disli['4']['d0'] - ( 2 * disli['3']['m'] * ( 1.25 - disli['4']['x'] ) )

        sb = kademe['2']['a'] - ( ( db1k + dt2k ) / 2 )
        if ( sb >= ( 0.1 * disli['3']['m'] ) and sb <= ( 0.3 * disli['3']['m'] ) ) : kademe['2']['cut'] = False
        else :
            disli['3']['dbk'] = db1k
            disli['3']['dtk'] = dt1k
            disli['4']['dbk'] = db2k
            disli['4']['dtk'] = dt2k

        if ( disli['3']['x'] > 0 ) :
            disli['3']['hb'] = disli['3']['m'] * ( 1 + disli['3']['x'] )
            disli['3']['ht'] = disli['3']['m'] * ( 1.25 - disli['3']['x'] )
            disli['3']['h'] = disli['3']['hb'] + disli['3']['ht']
        else :
            disli['3']['hb'] = disli['3']['m'] * ( 1 - disli['3']['x'] )
            disli['3']['ht'] = disli['3']['m'] * ( 1.25 + disli['3']['x'] )
            disli['3']['h'] = disli['3']['hb'] + disli['3']['ht']
        #
        if ( disli['4']['x'] > 0 ) :
            disli['4']['hb'] = disli['4']['m'] * ( 1 + disli['4']['x'] )
            disli['4']['ht'] = disli['4']['m'] * ( 1.25 - disli['4']['x'] )
            disli['4']['h'] = disli['4']['hb'] + disli['4']['ht']
        else :
            disli['4']['hb'] = disli['4']['m'] * ( 1 - disli['4']['x'] )
            disli['4']['ht'] = disli['4']['m'] * ( 1.25 + disli['4']['x'] )
            disli['4']['h'] = disli['4']['hb'] + disli['4']['ht']
    #

    disli['1']['dg'] = disli['1']['d0'] * cos( alfa0 )
    disli['2']['dg'] = disli['2']['d0'] * cos( alfa0 )
    disli['3']['dg'] = disli['3']['d0'] * cos( alfa0 )
    disli['4']['dg'] = disli['4']['d0'] * cos( alfa0 )

    ##################### 1. KADEME İÇİN ###########################
    kademe['1']['eps'] = ( \
        math.sqrt( ( disli['1']['db'] / 2 )**2 - ( disli['1']['dt'] / 2 )**2 ) + \
        math.sqrt( ( disli['2']['db'] / 2 )**2 - ( disli['2']['dt'] / 2 )**2 ) - \
        kademe['1']['a'] * sin( kademe['1']['alfa'] ) ) / \
        ( disli['1']['m'] * math.pi * cos( kademe['1']['alfa'] ) )

    disli['1']['e'] = EmniyetKontrolu( disli, '1', kademe, '1' )
    disli['2']['e'] = EmniyetKontrolu( disli, '2', kademe, '1' )

    ##################### 2. KADEME İÇİN ###########################
    kademe['2']['eps'] = ( \
        math.sqrt( ( disli['3']['db'] / 2 )**2 - ( disli['3']['dt'] / 2 )**2 ) + \
        math.sqrt( ( disli['4']['db'] / 2 )**2 - ( disli['4']['dt'] / 2 )**2 ) - \
        kademe['2']['a'] * sin( kademe['2']['alfa'] ) ) / \
        ( disli['3']['m'] * math.pi * cos( kademe['2']['alfa'] ) )

    disli['3']['e'] = EmniyetKontrolu( disli, '3', kademe, '2' )
    disli['4']['e'] = EmniyetKontrolu( disli, '4', kademe, '2' )
#



p("Toplam verim        : %.3f" %nt )
p("Toplam çevrim oranı : %d" %it )
p("Toplam güç kayıbı   : %.3f  [KW]" %Pk )
p("Kademe sayısı       : %d" %len(kademe) )
p("Dişli sayısı        : %d" %(len(kademe)*2) )


for x in sorted( kademe ) :
    k = kademe[x]
    p("  %s.Kademe için veriler" %(x) )
    print "  " + "-"*35
    p("     Kademe çevrim oranı         : %.3f" %(k['i']) )
    p("     Kademe verimi               : %.3f" %(k['n']) )
    p("     Eksenler arası mesafe (a)   : %.3f" %(k['a']) )
    p("     Eksenler arası mesafe (a0)  : %.3f" %(k['a0']) )
    p("     Alfa açısı                  : %.3f" %(k['alfa']) )
    p("     Alfa0 açısı                 : %.3f" %(k['alfa0']) )
    p("     Evolvent Alfa açısı (alfa)  : %.3f" %(k['ev_alfa']) )
    p("     Evolvent Alfa açısı (alfa0) : %.3f" %(k['ev_alfa0']) )
    p("     Kavrama faktörü             : %.3f" %(k['eps']) )
    p("     Eksenler arası mesafe       : %.3f" %(k['a']) )
    p("     Kaydırma tipi               : %s" %(k['type']) )
    if ( k['cut'] ) :
        p("     [+] Baş kısaltması          : Yapıldı" )
        p("       [+] Baş kısaltması        : Yapıldı" )

        # Diğer / yeni kısaltılmış uzunluklar
    else :
        p("     [-] Baş kısaltması          : Yapılmadı" )

for x in sorted( disli ) :
    d = disli[x]
    p("  %s.Dişli için veriler" %(x) )
    print "  " + "-"*35
    p("     Diş sayısı                  : %d" %(d['z']) )
    p("     Diş kalınlığı               : %.3f" %(d['s0']) )
    p("     Döndürme momenti            : %.3f" %(d['Md']) )
    p("     Modül                       : %.3f" %(d['m']) )
    p("     Diş form faktörü            : %.3f" %(d['Yf']) )
    p("     Profil kaydırma             : %.2f" %(d['x']) )
    p("     Taksimat dairesi çapı (d0)  : %.3f" %(d['d0']) )
    p("     Döndürme momenti      (dg)  : %.3f" %(d['dg']) )
    p("     Baş dairesi çapı            : %.3f" %(d['db']) )
    p("     Taban dairesi çapı          : %.3f" %(d['dt']) )
    p("     hb                          : %.3f" %(d['hb']) )
    p("     ht                          : %.3f" %(d['ht']) )
    p("     h                           : %.3f" %(d['h']) )
    p("     %s.Dişli için güvenlik hesapları" %(x) )
    print "     " + "-"*35
    e = d['e']
    p("     Çevresel hız                     : %.3f" %(e['v']) )
    p("     Teğetsel kuvvet                  : %.3f" %(e['Ft']) )
    p("     Radyal kuvvet                    : %.3f" %(e['Fr']) )
    p("     Yerel diş dibi kırılma ger.      : %.3f" %(e['SFy']) )
    p("     Hesaplanan diş dibi kırılma ger. : %.3f" %(e['SFh']) )
    p("     Diş dibi kırılma ger.            : %.3f" %(e['SFem']) )
    p("     Yerel diş yanağı ger.            : %.3f" %(e['SHy']) )
    p("     Hesaplanan diş yanağı ger.       : %.3f" %(e['SHh']) )
    p("     Diş yüzeyi ezilme emniyet fak.   : %.3f" %(e['SHem']) )
    p("     Yerel diş dibi kırılması         : %.3f" %(e['SFd']) )
    p("     Hesaplanan diş dibi kırılması    : %.3f" %(e['SFhd']) )
    p("     Diş dibi kırılma emniyet fakt.   : %.3f" %(e['SHdem']) )
    p("     Yerel diş yanağı ger.            : %.3f" %(e['SHyd']) )
    p("     Hesaplanan diş yanağı ger.       : %.3f" %(e['SHdh']) )
    p("     Diş yüzeyi ezilme emniyet fakt.  : %.3f" %(e['SHde']) )

    if ( e['SHde'] < S ) :
        p("     [!] Dişli emniyetsizdir     SHem : %.2f < S : %.2f" %( e['SHde'], S ) )
    else :
        p("     [+] Dişli emniyetlidir      SHem : %.2f" %e['SHde'])

    if ( kademe['1']['eps'] < 1.1 ) :
        p("[!] 1.Kademe : Keps < 1.1 ise kavrama oranı düşüktür - Keps : %.3f" %kademe['1']['eps'] )
    if ( kademe['2']['eps'] < 1.1 ) :
        p("[!] 2.Kademe : Keps < 1.1 ise kavrama oranı düşüktür - Keps : %.3f" %kademe['2']['eps'] )


__time_end = time.time()



p("\n--> İşlemler %.4f s sürdü" %( __time_end - __time_start ) )



#raw_input()








#