# -*- coding: utf-8 -*-
'''
@name     : Bilgisayar programı yardımıyla dişli kutusu boyutlandırma
@author   : Mehmet Hanoğlu < mail@mehmethanoglu.com.tr >
@group    : Ahmet Burak Özdemir < burakozdemir@gmail.com >, Mehmet Hanoğlu < mail@mehmethanoglu.com.tr >
@license  : GPL ( General Public License )
@desc     :
- Diş kalınlığı ve genişliğinde sıkıntı var
- 1.dişlinin diş sayısı 17 den küçükse veya ikisinin toplamı 28 den küçükse alt kesilme olur.
- 2 Kademe için max çevrim oranı 40 olmalı
'''

import sys, os, time, math
from PyQt4 import QtCore, QtGui, uic

try:
    _t = QtCore.QString.fromUtf8
except AttributeError:
    _t = lambda s: s

def cos( x ) : return math.cos( math.radians( x ) )
def sin( x ) : return math.sin( math.radians( x ) )
def tan( x ) : return math.tan( math.radians( x ) )
def rad( x ) : return math.radians( x )
def sqrt( x ) : return math.sqrt( x )

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
                else :
                    pow = 10.0**(times)
                    if ( times == 5 ) : pow2 = 10.0**(times-4)
                    elif ( times == 4 ) : pow2 = 10.0**(times-3)
                    elif ( times == 3 ) : pow2 = 10.0**(times-2)
                    else : pow2 = 10.0**(times-1)
                    find_evolventalfa( ev_alfa, [int(ev['i1']*pow), int(ev['i2']*pow), 1, step[3]*pow2], times = times+1 )
            else :
                pass

def EmniyetKontrolu( O, disli, dind, kademe, kind ) :
    v1 = ( math.pi * disli[str(dind)]['n'] / 30.0 ) * disli[str(dind)]['d0'] / ( 2.0 * 1000.0 )
    if ( v1 < 3.0 ) : O['Kv'] = 1
    elif ( v1 >= 3.0 and v1 < 8.0 ) : O['Kv'] = 1.1
    elif ( v1 >= 8.0 and v1 < 12.0 ) : O['Kv'] = 1.2
    elif ( v1 >= 12.0 and v1 < 18.0 ) : O['Kv'] = 1.25
    elif ( v1 >= 18.0 and v1 < 25.0 ) : O['Kv'] = 1.3
    else : O['Kv'] = 1.4
    Ft = ( 2000.0 * disli[str(dind)]['Md'] ) / disli[str(dind)]['d0']
    Fr = Ft * tan( kademe[str(kind)]['alfa0'] )
    SFy = ( Ft * disli[str(dind)]['Yf'] ) / ( disli[str(dind)]['m'] *  kademe[str(kind)]['Fid'] * disli[str(dind)]['d0'] )
    Keps1 = 0.25 + ( 0.75 / kademe[str(kind)]['eps'] )
    SFh = SFy * O['Kc'] * O['Kv'] * Keps1
    SFem = O['M'][str(kind)]['SFlim'] / SFh
    Keps2 = math.sqrt( ( 4.0 - kademe[str(kind)]['eps'] ) / 3.0 )
    SHy = math.sqrt( ( Ft * O['Kc'] * O['Kv'] ) / ( ( disli[str(dind)]['Yf'] * disli[str(dind)]['d0'] ) * disli[str(dind)]['d0'] ) ) * kademe[str(kind)]['Ki']
    SHh = SHy * Keps2 * O['Ke']
    SHem = O['M'][str(kind)]['SHlim'] / SHh
    SFd = ( Ft * disli[str(dind)]['Yf'] ) / ( disli[str(dind)]['m'] * disli[str(dind)]['b'] )
    SFhd = SFd * O['Kc'] * O['Kv'] * Keps1
    SHdem = O['M'][str(kind)]['SFlim'] / SFhd
    SHyd = math.sqrt( ( Ft * O['Kc'] * O['Kv'] ) / ( disli[str(dind)]['b'] * disli[str(dind)]['d0'] ) ) * kademe[str(kind)]['Ki']
    SHdh = SHyd * O['Ke'] * Keps1
    SHde = O['M'][str(kind)]['SHlim'] / SHdh

    return {
        'v'  : v1,
        'Kv' : O['Kv'],
        'Ft' : Ft,
        'Fr' : Fr,
        'SFy' : SFy,
        'SFh' : SFh,
        'SFem' : SFem,
        'SHy' : SHy,
        'SHh' : SHh,
        'SHem' : SHem,
        'SFd' : SFd,
        'SFhd' : SFhd,
        'SHdem' : SHdem,
        'SHyd' : SHyd,
        'SHdh' : SHdh,
        'SHde' : SHde,
        'Keps1' : Keps1,
        'Keps2' : Keps2,
    }

class ClipBoard :

    def __init__(self):
        self.text = {}

    def set( self, table, text ) : self.text[table] = text

    def get( self, table ) :
        if table in self.text.keys() :
            return self.text[table]
        else :
            return ""

clipboard = ClipBoard()


class MessageBox( QtGui.QMainWindow ) :
    def __init__( self ):
        QtGui.QMainWindow.__init__( self )
        self.ui = uic.loadUi( os.path.dirname( sys.argv[0] ) + "/MessageBox.ui", self )
        self.ui.keyPressEvent = self.keyPressEvent
        self.width, self.height = self.ui.geometry().width(), self.ui.geometry().height()
        self.ui.resizeEvent = self.onResize

    def onResize(self, e):
        self.width, self.height = self.ui.geometry().width(), self.ui.geometry().height()
        self.tableWidget.resize(self.width-10, self.height-10)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def Show(self, data = {}, S = 1.0, title = _t("Dişlinin güvenlik hesapları") ) :
        self.ui.setWindowTitle( _t("%s,  Emniyet katsayısı: S = %.3f" %(title, S)) )
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        control = [ 8, 13, 18, 23 ]
        g_icon = QtGui.QIcon()
        g_icon.addPixmap(QtGui.QPixmap( os.path.dirname( sys.argv[0] ) + "/icons/gear.png" ), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        w_icon = QtGui.QIcon()
        w_icon.addPixmap(QtGui.QPixmap( os.path.dirname( sys.argv[0] ) + "/icons/warning.png" ), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        s_icon = QtGui.QIcon()
        s_icon.addPixmap(QtGui.QPixmap( os.path.dirname( sys.argv[0] ) + "/icons/tick.png" ), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        for row in data.keys() :
            key = data[row][0]
            val = data[row][1]
            self.tableWidget.insertRow(row)
            if ( val != "" ) :
                a = QtGui.QTableWidgetItem( _t( key ) )
                b = QtGui.QTableWidgetItem( str( round( val, 4 ) ) )
                if ( row in control ) :
                    if ( val >= S ) :
                        a.setBackgroundColor( QtGui.QColor("green") )
                        a.setTextColor( QtGui.QColor("white") )
                        a.setIcon( s_icon )
                    else :
                        a.setBackgroundColor( QtGui.QColor("red") )
                        a.setTextColor( QtGui.QColor("white") )
                        a.setIcon( w_icon )
                self.tableWidget.setItem(row, 0, a)
                self.tableWidget.setItem(row, 1, b)
            else :
                a = QtGui.QTableWidgetItem( _t( key ) )
                a.setBackgroundColor( QtGui.QColor("blue") )
                a.setTextColor( QtGui.QColor("white") )
                a.setIcon( g_icon )
                self.tableWidget.setItem(row, 0, a)
        self.ui.show()

class TableWindow( QtGui.QMainWindow ) :

    def __init__( self ):
        QtGui.QMainWindow.__init__( self )
        self.ui = uic.loadUi( os.path.dirname( sys.argv[0] ) + "/TableWindow.ui", self )

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def setTitle( self, title ) :
        self.ui.setWindowTitle( title )

    def set( self, table, index ) :
        self.index = index
        if ( table == '1' ) :
            image = "tables/Yf.png"
            self.showXY = True
        elif ( table == '2' ) :
            image = "tables/Kc.png"
            self.showXY = False

        self.pic = QtGui.QPixmap(image)
        self._w, self._h = self.pic.width(), self.pic.height()
        self.graphicsView.setGeometry(QtCore.QRect(5, 5, self._w + 5, self._h + 5))
        self.scene = QtGui.QGraphicsScene()
        self.scene.setSceneRect(0, 0, self._w, self._h)
        self.pic_scene = QtGui.QGraphicsPixmapItem(self.pic)
        if ( self.showXY ) : self.pic_scene.mousePressEvent = self.ShowPen
        self.scene.addItem(self.pic_scene)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setRenderHint(QtGui.QPainter.Antialiasing)
        self.graphicsView.show()
        self.ui.resize(self._w + 10, self._h + 10)
        # Fixed Window Size
        self.ui.setMinimumSize(QtCore.QSize(self._w + 10, self._h + 10))
        self.ui.setMaximumSize(QtCore.QSize(self._w + 10, self._h + 10))

    def ShowPen(self, event):
        position = QtCore.QPointF(event.scenePos())
        self.scene = QtGui.QGraphicsScene()
        self.scene.setSceneRect(0, 0, self._w, self._h)
        self.pic_scene = QtGui.QGraphicsPixmapItem(self.pic)
        self.pic_scene.mousePressEvent = self.ShowPen
        self.scene.addItem(self.pic_scene)
        linex = QtGui.QGraphicsLineItem(0, position.y(), self._w + 30, position.y() )
        liney = QtGui.QGraphicsLineItem(position.x(), 0, position.x(), self._h + 30 )
        linex.setPen(QtGui.QPen(QtGui.QColor(QtCore.Qt.red), 2.1))
        liney.setPen(QtGui.QPen(QtGui.QColor(QtCore.Qt.red), 2.1))
        self.scene.addItem(linex)
        self.scene.addItem(liney)
        self.graphicsView.setScene(self.scene)
        currentVal = 3.6 - ( (1.9) * ( ( position.y()-5.0 ) / 600.0 ) )
        try : clipboard.set( self.index, str( round( currentVal, 4 ) ) )
        except : pass


class MainWindow( QtGui.QMainWindow ) :

    def __init__( self ):
        QtGui.QMainWindow.__init__( self )
        self.MSG = MessageBox()
        self.ui = uic.loadUi( os.path.dirname( sys.argv[0] ) + "/MainWindow.ui", self )
        self.About = 0
        self.FIX = 4
        self.O = { 'n' : { '1' : 0.98, '2' : 0.98, 'r1' : 0.95, 'r2' : 0.95 }, 'M' : {}, 'disli' : { } }
        self.__VarsayilanVeriler()
        self.__MalzemeleriEkle()
        self.__GenislikFaktorleriEkle()

        QtCore.QObject.connect( self.pushButton_11, QtCore.SIGNAL( _t("clicked()") ), self.Kaydet )
        QtCore.QObject.connect( self.pushButton_13, QtCore.SIGNAL( _t("clicked()") ), self.MalzemeEkle )
        QtCore.QObject.connect( self.button_about, QtCore.SIGNAL( _t("clicked()") ), self.Hakkinda )
        QtCore.QObject.connect( self.pushButton, QtCore.SIGNAL( _t("clicked()") ), self.ButtonHesapla )
        QtCore.QObject.connect( self.pushButton_2, QtCore.SIGNAL( _t("clicked()") ), self.Temizle )
        QtCore.QObject.connect( self.pushButton_7, QtCore.SIGNAL( _t("clicked()") ), lambda:self.GuvenlikHesaplari('1') )
        QtCore.QObject.connect( self.pushButton_8, QtCore.SIGNAL( _t("clicked()") ), lambda:self.GuvenlikHesaplari('2') )
        QtCore.QObject.connect( self.pushButton_9, QtCore.SIGNAL( _t("clicked()") ), lambda:self.GuvenlikHesaplari('3') )
        QtCore.QObject.connect( self.pushButton_10, QtCore.SIGNAL( _t("clicked()") ), lambda:self.GuvenlikHesaplari('4') )
        QtCore.QObject.connect( self.pushButton_3, QtCore.SIGNAL( _t("clicked()") ), lambda:self.TabloGoster('1', '1') )
        QtCore.QObject.connect( self.pushButton_4, QtCore.SIGNAL( _t("clicked()") ), lambda:self.TabloGoster('1', '3') )
        QtCore.QObject.connect( self.pushButton_5, QtCore.SIGNAL( _t("clicked()") ), lambda:self.TabloGoster('1', '2') )
        QtCore.QObject.connect( self.pushButton_6, QtCore.SIGNAL( _t("clicked()") ), lambda:self.TabloGoster('1', '4') )
        QtCore.QObject.connect( self.pushButton_12, QtCore.SIGNAL( _t("clicked()") ), lambda:self.TabloGoster('2', '5') )
        QtCore.QObject.connect( self.horizontalSlider_10, QtCore.SIGNAL( _t("valueChanged(int)") ), self.FaktorIsletme )
        QtCore.QObject.connect( self.horizontalSlider_2, QtCore.SIGNAL( _t("valueChanged(int)") ), self.FaktorEmniyet )
        QtCore.QObject.connect( self.horizontalSlider_3, QtCore.SIGNAL( _t("valueChanged(int)") ), lambda:self.DisVerim('1') )
        QtCore.QObject.connect( self.horizontalSlider_4, QtCore.SIGNAL( _t("valueChanged(int)") ), lambda:self.DisVerim('2') )
        QtCore.QObject.connect( self.horizontalSlider_9, QtCore.SIGNAL( _t("valueChanged(int)") ), lambda:self.RulmanVerim('1') )
        QtCore.QObject.connect( self.horizontalSlider_8, QtCore.SIGNAL( _t("valueChanged(int)") ), lambda:self.RulmanVerim('2') )
        QtCore.QObject.connect( self.doubleSpinBox_1, QtCore.SIGNAL( _t("valueChanged(double)") ), lambda:self.ProfilKaydirma('1') )
        QtCore.QObject.connect( self.doubleSpinBox_2, QtCore.SIGNAL( _t("valueChanged(double)") ), lambda:self.ProfilKaydirma('2') )
        QtCore.QObject.connect( self.doubleSpinBox_3, QtCore.SIGNAL( _t("valueChanged(double)") ), lambda:self.ProfilKaydirma('3') )
        QtCore.QObject.connect( self.doubleSpinBox_4, QtCore.SIGNAL( _t("valueChanged(double)") ), lambda:self.ProfilKaydirma('4') )
        QtCore.QObject.connect( self.comboBox_1, QtCore.SIGNAL( _t("currentIndexChanged(int)") ), lambda:self.MalzemeSecim('1') )
        QtCore.QObject.connect( self.comboBox_2, QtCore.SIGNAL( _t("currentIndexChanged(int)") ), lambda:self.MalzemeSecim('2') )
        QtCore.QObject.connect( self.lineEdit_4, QtCore.SIGNAL( _t("textEdited(QString)") ), lambda:self.DisliSayisi('1', self.lineEdit_4) )
        QtCore.QObject.connect( self.lineEdit_5, QtCore.SIGNAL( _t("textEdited(QString)") ), lambda:self.DisliSayisi('3', self.lineEdit_5) )
        QtCore.QObject.connect( self.lineEdit_6, QtCore.SIGNAL( _t("textEdited(QString)") ), lambda:self.TextDuzenleme('alfa0', self.lineEdit_6 ) )
        QtCore.QObject.connect( self.lineEdit_7, QtCore.SIGNAL( _t("textEdited(QString)") ), lambda:self.DisFormFaktoru('1', self.lineEdit_7) )
        QtCore.QObject.connect( self.lineEdit_9, QtCore.SIGNAL( _t("textEdited(QString)") ), lambda:self.DisFormFaktoru('2', self.lineEdit_9) )
        QtCore.QObject.connect( self.lineEdit_8, QtCore.SIGNAL( _t("textEdited(QString)") ), lambda:self.DisFormFaktoru('3', self.lineEdit_8) )
        QtCore.QObject.connect( self.lineEdit_10, QtCore.SIGNAL( _t("textEdited(QString)") ), lambda:self.DisFormFaktoru('4', self.lineEdit_10) )

        QtCore.QObject.connect( self.verticalSlider, QtCore.SIGNAL( _t("valueChanged(int)") ), lambda:self.GenislikFaktoruSlider('1') )
        QtCore.QObject.connect( self.verticalSlider_2, QtCore.SIGNAL( _t("valueChanged(int)") ), lambda:self.GenislikFaktoruSlider('2') )
        QtCore.QObject.connect( self.comboBox_3, QtCore.SIGNAL( _t("currentIndexChanged(int)") ), lambda:self.GenislikFaktoru('1') )
        QtCore.QObject.connect( self.comboBox_4, QtCore.SIGNAL( _t("currentIndexChanged(int)") ), lambda:self.GenislikFaktoru('2') )

        self.lineEdit_7.mousePressEvent = self.__TabloPanosu1
        self.lineEdit_9.mousePressEvent = self.__TabloPanosu2
        self.lineEdit_8.mousePressEvent = self.__TabloPanosu3
        self.lineEdit_10.mousePressEvent = self.__TabloPanosu4

        self.lineEdit_69.setValidator( QtGui.QDoubleValidator( 0.0, 999999999999999999, 4, self.lineEdit_69 ) )
        self.lineEdit_70.setValidator( QtGui.QDoubleValidator( 0.0, 999999999999999999, 4, self.lineEdit_70 ) )
        self.lineEdit_71.setValidator( QtGui.QDoubleValidator( 0.0, 999999999999999999, 4, self.lineEdit_71 ) )
        self.lineEdit_72.setValidator( QtGui.QDoubleValidator( 0.0, 999999999999999999, 4, self.lineEdit_72 ) )
        self.lineEdit_73.setValidator( QtGui.QDoubleValidator( 0.0, 999999999999999999, 4, self.lineEdit_73 ) )
        self.lineEdit_74.setValidator( QtGui.QDoubleValidator( 0.0, 999999999999999999, 4, self.lineEdit_74 ) )

        QtCore.QObject.connect( self.lineEdit_69, QtCore.SIGNAL( _t("textEdited(QString)") ), lambda:self.ManuelMalzemeBilgisi('1', 'SHlim', self.lineEdit_69) )
        QtCore.QObject.connect( self.lineEdit_70, QtCore.SIGNAL( _t("textEdited(QString)") ), lambda:self.ManuelMalzemeBilgisi('1', 'SFlim', self.lineEdit_70) )
        QtCore.QObject.connect( self.lineEdit_71, QtCore.SIGNAL( _t("textEdited(QString)") ), lambda:self.ManuelMalzemeBilgisi('1', 'E', self.lineEdit_71) )
        QtCore.QObject.connect( self.lineEdit_72, QtCore.SIGNAL( _t("textEdited(QString)") ), lambda:self.ManuelMalzemeBilgisi('2', 'SHlim', self.lineEdit_72) )
        QtCore.QObject.connect( self.lineEdit_73, QtCore.SIGNAL( _t("textEdited(QString)") ), lambda:self.ManuelMalzemeBilgisi('2', 'E', self.lineEdit_73) )
        QtCore.QObject.connect( self.lineEdit_74, QtCore.SIGNAL( _t("textEdited(QString)") ), lambda:self.ManuelMalzemeBilgisi('2', 'SFlim', self.lineEdit_74) )


        #self.lineEdit_6.setValidator( QtGui.QIntValidator( 0, 100, self ) )
        self.lineEdit_6.setValidator( QtGui.QDoubleValidator(-360.0, 360.0, 2, self.lineEdit_6 ) )
        self.lineEdit_7.setValidator( QtGui.QDoubleValidator( 1.8, 3.6, 4, self.lineEdit_7 ) )
        self.lineEdit_8.setValidator( QtGui.QDoubleValidator( 1.8, 3.6, 4, self.lineEdit_8 ) )
        self.lineEdit_9.setValidator( QtGui.QDoubleValidator( 1.8, 3.6, 4, self.lineEdit_9 ) )
        self.lineEdit_10.setValidator( QtGui.QDoubleValidator( 1.8, 3.6, 4, self.lineEdit_10 ) )


    @QtCore.pyqtSlot()
    def __TabloPanosu1( self, event ) :
        if ( clipboard.get('1') != "" ) : self.lineEdit_7.setText( clipboard.get('1') )
        self.O['disli']['1']['Yf'] = float( self.lineEdit_7.text() )

    def __TabloPanosu2( self, event ) :
        if ( clipboard.get('2') != "" ) : self.lineEdit_9.setText( clipboard.get('2') )
        self.O['disli']['2']['Yf'] = float( self.lineEdit_9.text() )

    def __TabloPanosu3( self, event ) :
        if ( clipboard.get('3') != "" ) : self.lineEdit_8.setText( clipboard.get('3') )
        self.O['disli']['3']['Yf'] = float( self.lineEdit_8.text() )

    def __TabloPanosu4( self, event ) :
        if ( clipboard.get('4') != "" ) : self.lineEdit_10.setText( clipboard.get('4') )
        self.O['disli']['4']['Yf'] = float( self.lineEdit_10.text() )

    def __VarsayilanVeriler( self ) :
        self.O['alfa0'] = 20.0
        self.O['Kc'] = 1.5
        self.O['S'] = 1.5
        self.ADDITINONAL = {}
        self.MAXX = 0
        self.O['kademe'] = {}
        self.O['kademe']['1'] = {}
        self.O['kademe']['2'] = {}
        self.O['kademe']['1']['cut'] = False
        self.O['kademe']['2']['cut'] = False
        for x in range( 1, len( self.O['kademe'] ) * 2 + 1, 1 ) : self.O['disli'][ str(x) ] = { 'Md': 0.0, 'e': {}, 'db': 0.0, 's0': 0.0, 'm': 0.0, 'ht': 0.0, 'Yf': 0.0, 'dg': 0.0, 'h': 0.0, 'hb': 0.0, 'x': 0.0, 'dt': 0.0, 'z': 0.0, 'd0': 0.0 }
        self.O['SMod'] = {
            '1' : [0.05,0.06,0.08,0.1,0.12,0.15,0.2,0.3,0.4,0.5,0.6,0.8,1.0,1.25,1.5,2.0,2.5,3.0,4.0,5.0,6.0,8.0,10.0,12.0,16.0,20.0,25.0,32.0,40.0,50.0,60.0,80.0,100.0],
            '2' : [0.055,0.07,0.09,0.11,0.14,0.18,0.22,0.28,0.35,0.45,0.55,0.7,0.9,1.125,1.375,1.75,2.25,2.75,3.5,4.5,5.5,7.0,9.0,11.0,14.0,18.0,22.0,28.0,36.0,45.0,55.0,70.0,90.0]
        }
        self.verticalSlider.setHidden( 1 )
        self.verticalSlider_2.setHidden( 1 )
        self.Kontrol1_is = False

    def Kaydet( self ) :
        print "Kaydet"

        if ( 'SHde' in self.O['disli']['1']['e'].keys() ) :
            from xlwt import *
            try : sdir = os.getenv("HOME") + "/Desktop/"
            except: sdir = ""
            dir = QtGui.QFileDialog.getExistingDirectory(self, _t("Kaydedilecek Klasörü Seçin"), sdir)
            dir = str( dir ) + "/"
            fname = dir + "Hesaplamalar" + str( time.strftime("%d%m%y_%H%M%S") ) + ".xls"
            wb = Workbook()
            ws0 = wb.add_sheet('0')

            line = 0
            for disli in range( 1,5 ) :
                disli = str(disli)
                ws0.write(line, 0, disli + ".Disli icin veriler")
                line += 1
                for x in self.O['disli']['1'] :
                    if x != "e" :
                        ws0.write(line, 0, x)
                        ws0.write(line, 1, str( round( self.O['disli']['1'][x])))
                        line += 1
                ws0.write(line, 0, disli + ".Disli icin guvenlik hesaplari")
                line += 1
                for y in self.O['disli']['1']['e'] :
                    ws0.write(line, 0, y)
                    ws0.write(line, 1, str( round( self.O['disli']['1']['e'][y], 4 ) ))
                    line += 1

            wb.save( fname )
            query = QtGui.QMessageBox( QtGui.QMessageBox.NoIcon, _t("Bilgilendirme"), _t("Dosya kaydedildi.") )
            query.setStandardButtons( QtGui.QMessageBox.Ok );
            icon = QtGui.QIcon( )
            icon.addPixmap(QtGui.QPixmap( os.path.dirname( sys.argv[0] ) + "/icons/tick.png" ), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            query.setWindowIcon( icon )
            query.exec_()
        else :
            query = QtGui.QMessageBox( QtGui.QMessageBox.NoIcon, _t("Hata"), _t("Hesaplama işlemlerinden sonra kayıt fonksiyonu aktif olacaktır.") )
            query.setStandardButtons( QtGui.QMessageBox.Ok );
            icon = QtGui.QIcon( )
            icon.addPixmap(QtGui.QPixmap( os.path.dirname( sys.argv[0] ) + "/icons/warning.png" ), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            query.setWindowIcon( icon )
            query.exec_()

    def MalzemeEkle( self ) :
        print "MalzemeEkle"
        try : sdir = os.environ["USERPROFILE"] + "/Desktop/"
        except: sdir = ""
        fname = QtGui.QFileDialog.getOpenFileName(self, _t("Dosya Seç"), sdir, _t("Metin Belgesi (*.txt)"))
        try :
            fname = str( fname )
            ofile = open( fname, "r" )
            content = ofile.read()
            ofile.close()
            content = content.replace("\xef\xbb\xbf", "")
            try :
                content.decode("cp1254")
                content = content.decode("cp1254")
            except :
                content = content
            list = content.replace("\r\n", "\n").split("\n")
            ind = 0
            for x in list :
                if ( x.startswith("#") or x.startswith("//") or x == "" ) : pass
                else :
                    name,e,sflim,shlim = x.split(",")
                    self.ADDITINONAL[ind] = { 'name' : _t( name.strip() ), 'E' : float( e.strip() ), 'SFlim' : float( sflim.strip() ), 'SHlim' : float( shlim.strip() ) }
                    ind += 1
            self.__MalzemeleriEkle()
            query = QtGui.QMessageBox( QtGui.QMessageBox.NoIcon, _t("Bilgilendirme"), _t("Seçtiğiniz dosyadaki malzemeler programa başarıyla eklendi.") )
            query.setStandardButtons( QtGui.QMessageBox.Ok );
            icon = QtGui.QIcon( )
            icon.addPixmap(QtGui.QPixmap( os.path.dirname( sys.argv[0] ) + "/icons/tick.png" ), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            query.setWindowIcon( icon )
            query.exec_()
        except Exception, error :
            query = QtGui.QMessageBox( QtGui.QMessageBox.NoIcon, _t("Hata"), _t("Seçtiğiniz dosya açılamıyor ya da içerisindeki veriler uygun şekilde yazılmamış.") )
            query.setStandardButtons( QtGui.QMessageBox.Ok );
            icon = QtGui.QIcon( )
            icon.addPixmap(QtGui.QPixmap( os.path.dirname( sys.argv[0] ) + "/icons/warning.png" ), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            query.setWindowIcon( icon )
            query.exec_()
            print error
        #print self.ADDITINONAL


    def __MalzemeleriEkle( self ) :
        # Malzeme Listesi
        self.comboBox_1.clear()
        self.comboBox_2.clear()
        self.MALZEME = {
            0 : { 'SFlim': "", 'SHlim': "", 'E': "", 'name': '-- Malzeme Seçiniz'},
            1 : { 'SFlim': 40.0, 'SHlim': 300.0, 'E': 120000, 'name': 'Lamel Grafitli Dökme Demir - GG20'},
            2 : { 'SFlim': 55.0, 'SHlim': 330.0, 'E': 120000, 'name': 'Lamel Grafitli Dökme Demir - GG25'},
            3 : { 'SFlim': 165.0, 'SHlim': 320.0, 'E':150000, 'name': 'Siyah Temper Döküm GTS 35-10'},
            4 : { 'SFlim': 205.0, 'SHlim': 460.0, 'E':150000, 'name': 'Siyah Temper Döküm GTS 65'},
            5 : { 'SFlim': 185.0, 'SHlim': 370.0, 'E': 173000, 'name': 'Küresel Grafitli DD GGG 40'},
            6 : { 'SFlim': 225.0, 'SHlim': 490.0, 'E': 173000, 'name': 'Küresel Grafitli DD GGG 60'},
            7 : { 'SFlim': 260.0, 'SHlim': 700.0, 'E': 173000, 'name': 'Küresel Grafitli DD GGG 100'},
            8 : { 'SFlim': 140.0, 'SHlim': 320.0, 'E': 202000, 'name': 'Çelik Döküm GS 52'},
            9 : { 'SFlim': 140.0, 'SHlim': 320.0, 'E': 202000, 'name': 'Çelik Döküm GS 52.1'},
            10 : { 'SFlim': 160.0, 'SHlim': 380.0, 'E': 202000, 'name': 'Çelik Döküm GS 60'},
            11 : { 'SFlim': 160.0, 'SHlim': 380.0, 'E': 202000, 'name': 'Çelik Döküm GS 60.1'},
            12 : { 'SFlim': 125.0, 'SHlim': 320.0, 'E': 202000, 'name': 'Genel İmalat Çeliği St 37'},
            13 : { 'SFlim': 140.0, 'SHlim': 360.0, 'E': 202000, 'name': 'Genel İmalat Çeliği St 50'},
            14 : { 'SFlim': 160.0, 'SHlim': 370.0, 'E': 206000, 'name': 'Genel İmalat Çeliği St 50-2'},
            15 : { 'SFlim': 150.0, 'SHlim': 380.0, 'E': 206000, 'name': 'Genel İmalat Çeliği St 60'},
            16 : { 'SFlim': 175.0, 'SHlim': 430.0, 'E': 206000, 'name': 'Genel İmalat Çeliği St 60-2'},
            17 : { 'SFlim': 200.0, 'SHlim': 450.0, 'E': 206000, 'name': 'Genel İmalat Çeliği St 70'},
            18 : { 'SFlim': 205.0, 'SHlim': 460.0, 'E': 206000, 'name': 'Genel İmalat Çeliği St 70-2'},
            19 : { 'SFlim': 155.0, 'SHlim': 470.0, 'E': 206000, 'name': 'Islah Çelikleri Ck45'},
            20 : { 'SFlim': 115.0, 'SHlim': 390.0, 'E':206000 , 'name': 'Islah Çelikleri  Ck45 Döküm'},
            21 : { 'SFlim': 220.0, 'SHlim': 630.0, 'E': 206000, 'name': 'Islah Çelikleri 34CrMo4'},
            22 : { 'SFlim': 180.0, 'SHlim': 550.0, 'E': 206000, 'name': 'Islah Çelikleri 34CrMo4 Döküm'},
            23 : { 'SFlim': 225.0, 'SHlim': 680.0, 'E': 206000, 'name': 'Islah Çelikleri 42CrMo4'},
            24 : { 'SFlim': 185.0, 'SHlim': 600.0, 'E': 206000, 'name': 'Islah Çelikleri 42CrMo4 Döküm'},
            25 : { 'SFlim': 225.0, 'SHlim': 680.0, 'E': 206000, 'name': 'Islah Çelikleri 34CrNiMo6'},
            26 : { 'SFlim': 185.0, 'SHlim': 600.0, 'E': 206000, 'name': 'Islah Çelikleri 34CrNiMo6 Döküm'},
            27 : { 'SFlim': 230.0, 'SHlim': 700.0, 'E':206000 , 'name': 'Islah Çelikleri 30CrNiMo8'},
            28 : { 'SFlim': 190.0, 'SHlim': 620.0, 'E': 206000, 'name': 'Islah Çelikleri 30CrNiMo8 Döküm'},
            29 : { 'SFlim': 240.0, 'SHlim': 750.0, 'E': 206000, 'name': 'Islah Çelikleri 34CrNiMo16'},
            30 : { 'SFlim': 250.0, 'SHlim': 1000.0, 'E': 206000, 'name': 'Islah Çelikleri (Alevle veya indüksiyonla sertleştirilmiş) Ck 45'},
            31 : { 'SFlim': 250.0, 'SHlim': 1000.0, 'E':206000 , 'name': 'Islah Çelikleri (Alevle veya indüksiyonla diş dibi de sertleştirilmiş) 34CrMo4'},
            32 : { 'SFlim': 150.0, 'SHlim': 1000.0, 'E': 206000, 'name': 'Islah Çelikleri (Alevle veya indüksiyonla diş dibi sertleştirilmemiş) 34CrMo4'},
            33 : { 'SFlim': 250.0, 'SHlim': 1000.0, 'E': 206000, 'name': 'Islah Çelikleri (Alevle veya indüksiyonla diş dibi de sertleştirilmiş) 34CrMo6'},
            34 : { 'SFlim': 150.0, 'SHlim': 1000.0, 'E':206000 , 'name': 'Islah Çelikleri (Alevle veya indüksiyonla diş dibi sertleştirilmemiş) 34CrMo6'},
            35 : { 'SFlim': 270.0, 'SHlim': 1000.0, 'E': 206000, 'name': 'Uzun süre gazla nitrürlenmiş ıslah ve sementasyon çeliği 42CrMo4'},
            36 : { 'SFlim': 270.0, 'SHlim': 1000.0, 'E':206000 , 'name': 'Uzun süre gazla nitrürlenmiş ıslah ve sementasyon çeliği 31CrMo9'},
            37 : { 'SFlim': 270.0, 'SHlim': 1000.0, 'E':206000 , 'name': 'Uzun süre gazla nitrürlenmiş ıslah ve sementasyon çeliği 42CrMo4'},
            38 : { 'SFlim': 300.0, 'SHlim': 780.0, 'E':206000 , 'name': 'Uzun süre gazla nitratlanmış ıslah ve sementasyon çeliği 42CrMo4'},
            39 : { 'SFlim': 370.0, 'SHlim': 1000.0, 'E':206000 , 'name': 'Uzun süre gazla nitrürlenmiş ıslah ve sementasyon çeliği 16MnCr5'},
            40 : { 'SFlim': 220.0, 'SHlim': 650.0, 'E': 206000, 'name': 'Kısa süre gazla nitratlanmış ıslah ve sementasyon çeliği C45N'},
            41 : { 'SFlim': 220.0, 'SHlim': 650.0, 'E': 206000, 'name': 'Kısa süre gazla nitratlanmış ıslah ve sementasyon çeliği 42CrMo4'},
            42 : { 'SFlim': 220.0, 'SHlim': 650.0, 'E':206000 , 'name': 'Kısa süre gazla nitratlanmış ıslah ve sementasyon çeliği 16MnCr5'},
            43 : { 'SFlim': 1200.0, 'SHlim': 1350.0, 'E':206000 , 'name': 'Kısa süre gazla nitratlanmış ıslah ve sementasyon çeliği 34Cr4'},
            44 : { 'SFlim': 310.0, 'SHlim': 1300.0, 'E':206000 , 'name': 'Sertleştirilmiş Sementasyon Çelikleri 16MnCr5'},
            45 : { 'SFlim': 310.0, 'SHlim': 1300.0, 'E': 206000, 'name': 'Sertleştirilmiş Sementasyon Çelikleri 15CrNi6'},
            46 : { 'SFlim': 315.0, 'SHlim': 1300.0, 'E': 206000, 'name': 'Sertleştirilmiş Sementasyon Çelikleri 17CrNiMo6'},
        }

        if ( len( self.ADDITINONAL ) > 0 ) :
            ind = max( self.MALZEME.keys() ) + 1
            for x in self.ADDITINONAL :
                MALZEME = self.ADDITINONAL[x]
                self.MALZEME[ind] = MALZEME
                ind += 1

        maxx = max( self.MALZEME.keys() )
        self.MAXX = maxx+1
        self.MALZEME[self.MAXX] = { 'SFlim': 0, 'SHlim': 0, 'E': 0, 'name': '-- Diğer ( Kullanıcı Girebilir )'}

        for x in self.MALZEME :
            MALZEME = self.MALZEME[x]
            self.comboBox_1.addItem(_t(""))
            self.comboBox_2.addItem(_t(""))
            self.comboBox_1.setItemText(x, QtGui.QApplication.translate("MainWindow", MALZEME['name'], None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_2.setItemText(x, QtGui.QApplication.translate("MainWindow", MALZEME['name'], None, QtGui.QApplication.UnicodeUTF8))

    def Hakkinda( self ) :
        query = QtGui.QMessageBox( QtGui.QMessageBox.NoIcon, _t("Program Hakkında Bilgi"), _t("Karadeniz Teknik Üniversitesi > Mühendislik Fakültesi > Makine Mühendisliği\n\nBilgisayar Programı Yardımı ile Dişli Kutusu Boyutlandırılması\n\nMehmet HANOĞLU (E-Mail: m.hanoglu@yandex.com.tr)\nAhmet Burak ÖZDEMİR (E-Mail: ozdemirbr@gmail.com)\n\nDanışman: Öğr. Gör. Mustafa Sabri DUMAN\n") )
        query.setStandardButtons( QtGui.QMessageBox.Ok );
        icon = QtGui.QIcon( )
        icon.addPixmap(QtGui.QPixmap( os.path.dirname( sys.argv[0] ) + "/icons/about.png" ), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        query.setWindowIcon( icon )
        query.exec_()
        print "Hakkinda"

    def Temizle( self ) :
        print "Temizle"
        self.lineEdit.setText("")
        self.lineEdit_2.setText("")
        self.lineEdit_3.setText("")
        self.lineEdit_4.setText("")
        self.lineEdit_5.setText("")
        self.lineEdit_6.setText("20.0")
        self.lineEdit_7.setText("")
        self.lineEdit_8.setText("")
        self.lineEdit_9.setText("")
        self.lineEdit_10.setText("")
        self.lineEdit_11.setText("")
        self.lineEdit_12.setText("")
        self.lineEdit_13.setText("")
        self.lineEdit_14.setText("")
        self.lineEdit_16.setText("")
        self.lineEdit_18.setText("")
        self.lineEdit_19.setText("")
        self.lineEdit_20.setText("")
        self.lineEdit_21.setText("")
        self.lineEdit_22.setText("")
        self.lineEdit_23.setText("")
        self.lineEdit_24.setText("")
        self.lineEdit_25.setText("")
        self.lineEdit_26.setText("")
        self.lineEdit_27.setText("")
        self.lineEdit_28.setText("")
        self.lineEdit_29.setText("")
        self.lineEdit_30.setText("")
        self.lineEdit_31.setText("")
        self.lineEdit_32.setText("")
        self.lineEdit_33.setText("")
        self.lineEdit_34.setText("")
        self.lineEdit_35.setText("")
        self.lineEdit_36.setText("")
        self.lineEdit_37.setText("")
        self.lineEdit_38.setText("")
        self.lineEdit_39.setText("")
        self.lineEdit_40.setText("")
        self.lineEdit_41.setText("")
        self.lineEdit_42.setText("")
        self.lineEdit_43.setText("")
        self.lineEdit_44.setText("")
        self.lineEdit_45.setText("")
        self.lineEdit_46.setText("")
        self.lineEdit_47.setText("")
        self.lineEdit_48.setText("")
        self.lineEdit_49.setText("")
        self.lineEdit_50.setText("")
        self.lineEdit_51.setText("")
        self.lineEdit_52.setText("")
        self.lineEdit_53.setText("")
        self.lineEdit_54.setText("")
        self.lineEdit_55.setText("")
        self.lineEdit_56.setText("")
        self.lineEdit_57.setText("")
        self.lineEdit_58.setText("")
        self.lineEdit_59.setText("")
        self.lineEdit_60.setText("")
        self.lineEdit_61.setText("")
        self.lineEdit_62.setText("")
        self.lineEdit_63.setText("")
        self.lineEdit_64.setText("")
        self.lineEdit_65.setText("")
        self.lineEdit_66.setText("")
        self.lineEdit_67.setText("")
        self.lineEdit_68.setText("")
        self.lineEdit_69.setText("")
        self.lineEdit_70.setText("")
        self.lineEdit_71.setText("")
        self.lineEdit_72.setText("")
        self.lineEdit_73.setText("")
        self.lineEdit_74.setText("")
        self.lineEdit_75.setText("")
        self.lineEdit_76.setText("")
        self.lineEdit_77.setText("")
        self.lineEdit_78.setText("")
        self.lineEdit_79.setText("")
        #self.lineEdit_80.setText("")
        #self.lineEdit_81.setText("")
        #self.lineEdit_82.setText("")
        #self.lineEdit_83.setText("")
        self.lineEdit_84.setText("")
        self.lineEdit_85.setText("")
        self.lineEdit_86.setText("")
        self.lineEdit_169.setText("")
        self.lineEdit_170.setText("")
        self.lineEdit_171.setText("")
        self.lineEdit_172.setText("")
        self.label_17.setText("")
        self.horizontalSlider_2.setProperty("value", 15)
        self.horizontalSlider_3.setProperty("value", 98)
        self.horizontalSlider_4.setProperty("value", 95)
        self.horizontalSlider_8.setProperty("value", 95)
        self.horizontalSlider_9.setProperty("value", 95)
        self.horizontalSlider_10.setProperty("value", 150)
        self.comboBox_1.setCurrentIndex(0)
        self.comboBox_2.setCurrentIndex(0)
        self.comboBox_3.setCurrentIndex(0)
        self.comboBox_4.setCurrentIndex(0)
        self.textBrowser.setStyleSheet(_t("background: #fff; color: #fff; border: 2px solid #000; text-align: center;"))
        self.textBrowser_2.setStyleSheet(_t("background: #fff; color: #fff; border: 2px solid #000; text-align: center;"))
        self.textBrowser_3.setStyleSheet(_t("background: #fff; color: #fff; border: 2px solid #000; text-align: center;"))
        self.textBrowser_4.setStyleSheet(_t("background: #fff; color: #fff; border: 2px solid #000; text-align: center;"))
        self.__VarsayilanVeriler()
        self.__ButtonGuvenlikHesaplari( False )

    def ManuelMalzemeBilgisi( self, index, key, item ) :
        print "ManuelMalzemeBilgisi", index, key, item.text()
        val = float( item.text() )
        self.O['M'][index][key] = val
        self.ButtonHesapla()


    def GenislikFaktoruSlider( self, index ) :
        if ( index == '1' ) :
            val = self.verticalSlider.value()
            self.label_340.setText( str( round( val / 10.0, 2 ) ) )
        elif ( index == '2' ) :
            val = self.verticalSlider_2.value()
            self.label_341.setText( str( round( val / 10.0, 2 ) ) )
        self.O['kademe'][index]['Fid'] = val / 10.0
        self.ButtonHesapla()

    def GenislikFaktoru( self, index ) :
        if ( index == '1' ) :
            current = self.comboBox_3.currentIndex()
            if ( self.GENISLIK[current]['x'] == 0 ) :
                self.verticalSlider.setHidden( 1 )
                self.label_340.setText( "" )
            else :
                self.verticalSlider.setHidden( 0 )
                self.verticalSlider.setSingleStep( 1 )
                self.verticalSlider.setPageStep( 1 )
                self.verticalSlider.setRange( 0, self.GENISLIK[current]['max']*10 )
                self.verticalSlider.setValue( self.GENISLIK[current]['max']*5 )
        elif ( index == '2' ) :
            current = self.comboBox_4.currentIndex()
            if ( self.GENISLIK[current]['x'] == 0 ) :
                self.verticalSlider_2.setHidden( 1 )
                self.label_341.setText( "" )
            else :
                self.verticalSlider_2.setHidden( 0 )
                self.verticalSlider_2.setSingleStep( 1 )
                self.verticalSlider_2.setPageStep( 1 )
                self.verticalSlider_2.setRange( 0, self.GENISLIK[current]['max']*10 )
                self.verticalSlider_2.setValue( self.GENISLIK[current]['max']*5 )


    def __GenislikFaktorleriEkle( self ) :
        self.GENISLIK_TITLE = [0,1,6,11,16,21]
        self.GENISLIK = {
            0  : { 'x': 0, 'max' : 0, 'name': '-- Genişlik faktörü'},
            1  : { 'x': 0, 'max' : 0, 'name': 'İki uçtan yataklanmış (Simetrik)'},
            2  : { 'x': 1.0, 'max' : 1.6, 'name': ' - Normalize ( HB < 180 )'},
            3  : { 'x': 1.0, 'max' : 1.4, 'name': ' - Islah Edilmiş ( HB < 180 )'},
            4  : { 'x': 1.0, 'max' : 1.1, 'name': ' - Sementasyon'},
            5  : { 'x': 1.0, 'max' : 0.8, 'name': ' - Nitrürlenmiş'},
            6  : { 'x': 0, 'max' : 0, 'name': 'Ok Dişli'},
            7  : { 'x': 1.0, 'max' : 1.6*1.8, 'name': ' - Normalize ( HB < 180 )'},
            8  : { 'x': 1.0, 'max' : 1.4*1.8, 'name': ' - Islah Edilmiş ( HB < 180 )'},
            9  : { 'x': 1.0, 'max' : 1.1*1.8, 'name': ' - Sementasyon'},
            10 : { 'x': 1.0, 'max' : 0.8*1.8, 'name': ' - Nitrürlenmiş'},
            11 : { 'x': 0, 'max' : 0, 'name': 'İki uçtan yataklanmış (Asimetrik)'},
            12 : { 'x': 1.0, 'max' : 1.6*0.8, 'name': ' - Normalize ( HB < 180 )'},
            13 : { 'x': 1.0, 'max' : 1.4*0.8, 'name': ' - Islah Edilmiş ( HB < 180 )'},
            14 : { 'x': 1.0, 'max' : 1.1*0.8, 'name': ' - Sementasyon'},
            15 : { 'x': 1.0, 'max' : 0.8*0.8, 'name': ' - Nitrürlenmiş'},
            16 : { 'x': 0, 'max' : 0, 'name': 'İki dişli aynı boyda ( i = 1 )'},
            17 : { 'x': 1.0, 'max' : 1.6*1.2, 'name': ' - Normalize ( HB < 180 )'},
            18 : { 'x': 1.0, 'max' : 1.4*1.2, 'name': ' - Islah Edilmiş ( HB < 180 )'},
            19 : { 'x': 1.0, 'max' : 1.1*1.2, 'name': ' - Sementasyon'},
            20 : { 'x': 1.0, 'max' : 0.8*1.2, 'name': ' - Nitrürlenmiş'},
            21 : { 'x': 0, 'max' : 0, 'name': 'Tek taraftan yataklı'},
            22 : { 'x': 1.0, 'max' : 1.6*0.5, 'name': ' - Normalize ( HB < 180 )'},
            23 : { 'x': 1.0, 'max' : 1.4*0.5, 'name': ' - Islah Edilmiş ( HB < 180 )'},
            24 : { 'x': 1.0, 'max' : 1.1*0.5, 'name': ' - Sementasyon'},
            25 : { 'x': 1.0, 'max' : 0.8*0.5, 'name': ' - Nitrürlenmiş'},
            26 : { 'x': 0, 'max' : 0, 'name': 'Çelik konst. gövde simetrik yataklanmış, sertleştirilmemiş'},
            27 : { 'x': 1.0, 'max' : 1.3, 'name': ' - Kalite 5-6'},
            28 : { 'x': 1.0, 'max' : 1.1, 'name': ' - Kalite 7-8'},
            29 : { 'x': 1.0, 'max' : 0.9, 'name': ' - Kalite 9-10'},
        }
        for x in self.GENISLIK :
            GENISLIK = self.GENISLIK[x]
            self.comboBox_3.addItem(_t(""))
            self.comboBox_4.addItem(_t(""))
            self.comboBox_3.setItemText(x, _t(GENISLIK['name']))
            self.comboBox_4.setItemText(x, _t(GENISLIK['name']))


    def __Kontrol1( self ) :
        stop = False;
        if ( self.lineEdit.text() == "" ) : stop = True
        if ( self.lineEdit_2.text() == "" ) : stop = True
        if ( self.lineEdit_3.text() == "" ) : stop = True
        if ( self.lineEdit_4.text() == "" ) : stop = True
        if ( self.lineEdit_5.text() == "" ) : stop = True
        if ( self.comboBox_1.currentIndex() == 0 ) : stop = True
        if ( self.comboBox_2.currentIndex() == 0 ) : stop = True
        if ( self.comboBox_3.currentIndex() in self.GENISLIK_TITLE ) : stop = True
        if ( self.comboBox_4.currentIndex() in self.GENISLIK_TITLE ) : stop = True

        return stop

    def __Kontrol2( self ) :
        stop = False;
        if ( self.lineEdit.text() == "" ) : stop = True
        if ( self.lineEdit_2.text() == "" ) : stop = True
        if ( self.lineEdit_3.text() == "" ) : stop = True
        if ( self.lineEdit_4.text() == "" ) : stop = True
        if ( self.lineEdit_5.text() == "" ) : stop = True
        if ( self.lineEdit_6.text() == "" ) : stop = True
        if ( self.lineEdit_7.text() == "" ) : stop = True
        if ( self.lineEdit_8.text() == "" ) : stop = True
        if ( self.lineEdit_9.text() == "" ) : stop = True
        if ( self.lineEdit_10.text() == "" ) : stop = True
        if ( self.comboBox_1.currentIndex() == 0 ) : stop = True
        if ( self.comboBox_2.currentIndex() == 0 ) : stop = True
        if ( self.comboBox_3.currentIndex() in self.GENISLIK_TITLE ) : stop = True
        if ( self.comboBox_4.currentIndex() in self.GENISLIK_TITLE ) : stop = True

        return stop

    def __ButtonGuvenlikHesaplari( self, status ) :
        self.pushButton_7.setEnabled(status)
        self.pushButton_8.setEnabled(status)
        self.pushButton_9.setEnabled(status)
        self.pushButton_10.setEnabled(status)

    def __AlanMalzemeBilgisi( self, status, index ) :
        print status, index
        if ( index == '1' ) :
            self.lineEdit_69.setEnabled(status)
            self.lineEdit_70.setEnabled(status)
            self.lineEdit_71.setEnabled(status)
            self.lineEdit_69.setReadOnly(status^1)
            self.lineEdit_70.setReadOnly(status^1)
            self.lineEdit_71.setReadOnly(status^1)
        if ( index == '2' ) :
            self.lineEdit_72.setEnabled(status)
            self.lineEdit_73.setEnabled(status)
            self.lineEdit_74.setEnabled(status)
            self.lineEdit_72.setReadOnly(status^1)
            self.lineEdit_73.setReadOnly(status^1)
            self.lineEdit_74.setReadOnly(status^1)

    def DegerleriGir( self ) :
        self.lineEdit.setText("1.5")
        self.lineEdit_2.setText("750")
        self.lineEdit_3.setText("75")
        self.lineEdit_4.setText("18")
        self.lineEdit_5.setText("20")
        self.O['disli']['1']['z'] = 18
        self.O['disli']['3']['z'] = 20
        self.O['Pg'] = 1.5
        self.O['ng'] = 750
        self.O['nc'] = 75
        self.lineEdit_7.setText("2.72")
        self.lineEdit_8.setText("2.05")
        self.lineEdit_9.setText("2.35")
        self.lineEdit_10.setText("2.75")
        self.O['disli']['1']['Yf'] = 2.2
        self.O['disli']['2']['Yf'] = 2.2
        self.O['disli']['3']['Yf'] = 2.2
        self.O['disli']['4']['Yf'] = 2.2
        self.comboBox_1.setCurrentIndex(1)
        self.comboBox_2.setCurrentIndex(2)
        self.ButtonHesapla()

    def TextDuzenleme( self, index, item ) :
        self.O[index] = float( item.text() )

    def FaktorEmniyet( self ) :
        self.O['S'] = float( self.horizontalSlider_2.value() / 10.0 )
        self.label_35.setText(QtGui.QApplication.translate("MainWindow", str(self.O['S']), None, QtGui.QApplication.UnicodeUTF8))
        self.ButtonHesapla()

    def FaktorIsletme( self ) :
        self.O['Kc'] = float( self.horizontalSlider_10.value() / 100.0 )
        self.label_49.setText(QtGui.QApplication.translate("MainWindow", str(self.O['Kc']), None, QtGui.QApplication.UnicodeUTF8))
        self.ButtonHesapla()

    def DisVerim( self, index ) :
        if ( index == '1' ) :
            self.O['n']['1'] = self.horizontalSlider_3.value() / 100.0
            self.label_31.setText(QtGui.QApplication.translate("MainWindow", str(self.O['n']['1']), None, QtGui.QApplication.UnicodeUTF8))
        elif ( index == '2' ) :
            self.O['n']['2'] = self.horizontalSlider_4.value() / 100.0
            self.label_32.setText(QtGui.QApplication.translate("MainWindow", str(self.O['n']['2']), None, QtGui.QApplication.UnicodeUTF8))
        self.ButtonHesapla()

    def RulmanVerim( self, index ) :
        if ( index == '1' ) :
            self.O['n']['r1'] = self.horizontalSlider_9.value() / 100.0
            self.label_33.setText(QtGui.QApplication.translate("MainWindow", str(self.O['n']['r1']), None, QtGui.QApplication.UnicodeUTF8))
        elif ( index == '2' ) :
            self.O['n']['r2'] = self.horizontalSlider_8.value() / 100.0
            self.label_34.setText(QtGui.QApplication.translate("MainWindow", str(self.O['n']['r2']), None, QtGui.QApplication.UnicodeUTF8))
        self.ButtonHesapla()

    def ProfilKaydirma( self, index ) :
        if ( index == '1' ) : val = self.doubleSpinBox_1.value()
        elif ( index == '2' ) : val = self.doubleSpinBox_2.value()
        elif ( index == '3' ) : val = self.doubleSpinBox_3.value()
        elif ( index == '4' ) : val = self.doubleSpinBox_4.value()
        self.O['disli'][index]['x'] = float( round( val, 2 ) )
        self.ButtonHesapla()
        print "ProfilKaydirma:", index, self.O['disli'][index]['x']

    def MalzemeSecim( self, index ) :
        if ( index == '1' ) :
            selected = self.comboBox_1.currentIndex()
            current = self.MALZEME[ selected ]
            if ( selected == self.MAXX ) :
                self.__AlanMalzemeBilgisi( True, index )
                self.lineEdit_69.setText("")
                self.lineEdit_70.setText("")
                self.lineEdit_71.setText("")
            else :
                self.__AlanMalzemeBilgisi( False, index )
                self.lineEdit_69.setText(str(current['SHlim']))
                self.lineEdit_70.setText(str(current['SFlim']))
                self.lineEdit_71.setText(str(current['E']))
        elif ( index == '2' ) :
            selected = self.comboBox_2.currentIndex()
            current = self.MALZEME[ selected ]
            if ( selected == self.MAXX ) :
                self.__AlanMalzemeBilgisi( True, index )
                self.lineEdit_69.setText("")
                self.lineEdit_70.setText("")
                self.lineEdit_71.setText("")
            else :
                self.__AlanMalzemeBilgisi( False, index )
                self.lineEdit_72.setText(str(current['SHlim']))
                self.lineEdit_74.setText(str(current['SFlim']))
                self.lineEdit_73.setText(str(current['E']))
        self.O['M'][index] = current
        if ( selected != 1 or selected != self.MAXX ) : self.ButtonHesapla()

    def DisliSayisi( self, index, item ) :
        self.O['disli'][index]['z'] = int( item.text() )
        print "DisliSayisi:", index, item.text()
        self.ButtonHesapla()

    def DisFormFaktoru( self, index, item ) :
        self.O['disli'][index]['Yf'] = float( item.text() )
        print "DisFormFaktoru:", index, item.text()

    def DisGenisligi( self, index, item ) :
        self.O['disli'][index]['b'] = float( item.text() )
        print "DisGenisligi:", index, item.text()

    def GuvenlikHesaplari( self, index ) :
        table = self.__GuvenlikHesaplariAl( index )
        title = str( index ) + ". Dişliye ait veriler"
        self.MSG.Show( table, self.O['S'], title = title )

    def TabloGoster( self, index, table ) :
        tableWindow = TableWindow()
        tableWindow.set( index, table )
        if ( index == '1' ) :
            tableWindow.setTitle( _t("x=%s ve z=%d için Diş form faktörünü seçiniz" %(self.O['disli'][table]['x'], self.O['disli'][table]['z']) ) )
        tableWindow.show()
        print "TabloGoster:", index, table


    def __GuvenlikHesaplariAl( self, index ) :
        data = self.O['disli'][index]['e']
        table = {
            0 : ["Çevresel Hız [m/s]", data['v'] ],
            1 : ["Dinamik Faktör [Seçildi]" , data['Kv'] ],
            2 : ["Diş Dibi Kırılmasına Göre Emniyet Kontrolü", "" ],
            3 : ["Çevresel Kuvvet [N]" , data['Ft'] ],
            4 : ["Radyal Kuvvet [N]", data['Fr'] ],
            5 : ["Yerel Diş Dibi Kırılma Gerilmesi [MPa]" , data['SFy'] ],
            6 : ["Kavrama Faktörü" , data['Keps1'] ],
            7 : ["Hesaplanan Diş Dibi Kırılma Gerilmesi [MPa]", data['SFh'] ],
            8 : ["Diş Dibi Kırılma Emniyet Faktörü", data['SFem'] ],
            9 : ["Dişlerin Yüzey Ezilmesine Göre Emniyet Kontrolü", "" ],
            10 : ["Kavrama Faktörü", data['Keps2'] ],
            11 : ["Yerel Diş Yanağı Gerilmesi [MPa]", data['SHy'] ],
            12 : ["Hesaplanan Diş Yanağı Gerilmesi [MPa]", data['SHh'] ],
            13 : ["Diş Yüzeyi Ezilme Emniyet Faktörü", data['SHem'] ],
            14 : ["Diş Dibi Kırılmasına Göre Emniyet Kontrolü", "" ],
            15 : ["Yerel Diş Dibi Kırılma Gerilmesi [MPa]", data['SFd'] ],
            16 : ["Kavrama Faktörü", data['Keps1'] ],
            17 : ["Hesaplanan Diş Dibi Kırılma Gerilmesi [MPa]", data['SFhd'] ],
            18 : ["Diş Dibi Kırılma Emniyet Faktörü", data['SHdem'] ],
            19 : ["Diş Yanağı Ezilmesine Göre Emniyet Kontrolü", "" ],
            20 : ["Kavrama Faktörü" , data['Keps2'] ],
            21 : ["Yerel Diş Yanağı Gerilmesi [MPa]", data['SHyd'] ],
            22 : ["Hesaplanan Diş Dibi Kırılma Gerilmesi [MPa]", data['SHdh'] ],
            23 : ["Diş Diş Dibi Kırılma Emniyet Faktörü", data['SHde'] ],
        }
        return table


    def ButtonHesapla( self ) :
        self.label_17.setText("")

        if not self.__Kontrol1() :
            self.O['Pg'] = float( self.lineEdit.text() )
            self.O['nt'] = self.O['n']['1'] * self.O['n']['2'] * self.O['n']['r1'] * self.O['n']['r2']
            self.O['Pc'] = self.O['nt'] * self.O['Pg']
            self.O['Pk'] = self.O['Pg'] - self.O['Pc']
            self.O['ng'] = int( self.lineEdit_2.text() )
            self.O['nc'] = int( self.lineEdit_3.text() )
            self.O['it'] = self.O['ng'] * 1.0 / self.O['nc'] * 1.0
            self.O['kademe']['1']['i'] = 0.7 * math.pow( self.O['it'], 0.7 )
            self.O['kademe']['2']['i'] = self.O['it'] / self.O['kademe']['1']['i']
            self.O['kademe']['1']['n'] = self.O['n']['1'] * self.O['n']['r1']
            self.O['kademe']['2']['n'] = self.O['n']['2'] * self.O['n']['r2']
            self.O['kademe']['1']['Ki'] = sqrt( ( self.O['kademe']['1']['i'] + 1.0 ) / self.O['kademe']['1']['i'] )
            self.O['kademe']['2']['Ki'] = sqrt( ( self.O['kademe']['2']['i'] + 1.0 ) / self.O['kademe']['2']['i'] )

            self.O['Ke'] = math.sqrt( 0.175 * self.O['M']['1']['E'] )                                 # Elastisite faktörü
            self.O['Ka'] = math.sqrt( 1.0 / ( cos( self.O['alfa0'] ) * sin( self.O['alfa0'] ) ) )    # Yuvarlanma noktası faktörü

            self.O['disli']['2']['z'] = math.ceil( self.O['disli']['1']['z'] * self.O['kademe']['1']['i'] )
            self.O['disli']['4']['z'] = math.ceil( self.O['disli']['3']['z'] * self.O['kademe']['2']['i'] )
            self.O['disli']['1']['Md'] = 9550 * ( self.O['Pg'] / self.O['ng'] ) * self.O['Kc'] * self.O['kademe']['1']['n'] * self.O['n']['r1']
            self.O['disli']['2']['Md'] = self.O['disli']['1']['Md'] * self.O['kademe']['1']['i']
            self.O['disli']['3']['Md'] = self.O['disli']['2']['Md']
            self.O['disli']['4']['Md'] = 9550 * ( self.O['Pc'] / self.O['nc'] ) * self.O['Kc'] * self.O['kademe']['2']['n'] * self.O['n']['r2']
            self.O['disli']['1']['n'] = self.O['ng']
            self.O['disli']['2']['n'] = self.O['disli']['1']['n'] * ( self.O['disli']['1']['z'] / self.O['disli']['2']['z'] )
            self.O['disli']['3']['n'] = self.O['disli']['2']['n']
            self.O['disli']['4']['n'] = self.O['disli']['3']['n'] * ( self.O['disli']['3']['z'] / self.O['disli']['4']['z'] )

            self.lineEdit_44.setText( str( self.O['disli']['1']['z'] ) )
            self.lineEdit_49.setText( str( self.O['disli']['2']['z'] ) )
            self.lineEdit_56.setText( str( self.O['disli']['3']['z'] ) )
            self.lineEdit_64.setText( str( self.O['disli']['4']['z'] ) )

            if ( self.Kontrol1_is == False ) :
                query = QtGui.QMessageBox( QtGui.QMessageBox.Information, _t("Uyarı"), _t("Her dişli için Diş Form faktörleri ve profil kaydırma değerlerini giriniz") )
                query.setStandardButtons( QtGui.QMessageBox.Ok );
                icon = QtGui.QIcon( )
                icon.addPixmap(QtGui.QPixmap( os.path.dirname( sys.argv[0] ) + "/icons/gear.png" ), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                query.setWindowIcon( icon )
                query.exec_()
                self.Kontrol1_is = True
        else :
            self.label_17.setText(_t("Girilmesi gereken tüm veriler girilmedi !"))

        if not self.__Kontrol2() :
            self.__ButtonGuvenlikHesaplari( True )
            self.progressBar.setEnabled(1)
            self.progressBar.setValue(5)

            self.O['Pg'] = float( self.lineEdit.text() )
            self.O['nt'] = self.O['n']['1'] * self.O['n']['2'] * self.O['n']['r1'] * self.O['n']['r2']
            self.O['Pc'] = self.O['nt'] * self.O['Pg']
            self.O['Pk'] = self.O['Pg'] - self.O['Pc']
            self.O['ng'] = int( self.lineEdit_2.text() )
            self.O['nc'] = int( self.lineEdit_3.text() )
            self.O['it'] = self.O['ng'] * 1.0 / self.O['nc'] * 1.0
            self.O['kademe']['1']['i'] = 0.7 * math.pow( self.O['it'], 0.7 )
            self.O['kademe']['2']['i'] = self.O['it'] / self.O['kademe']['1']['i']
            self.O['kademe']['1']['n'] = self.O['n']['1'] * self.O['n']['r1']
            self.O['kademe']['2']['n'] = self.O['n']['2'] * self.O['n']['r2']
            self.O['kademe']['1']['Ki'] = sqrt( ( self.O['kademe']['1']['i'] + 1.0 ) / self.O['kademe']['1']['i'] )
            self.O['kademe']['2']['Ki'] = sqrt( ( self.O['kademe']['2']['i'] + 1.0 ) / self.O['kademe']['2']['i'] )

            self.O['Ke'] = math.sqrt( 0.175 * self.O['M']['1']['E'] )                                 # Elastisite faktörü
            self.O['Ka'] = math.sqrt( 1.0 / ( cos( self.O['alfa0'] ) * sin( self.O['alfa0'] ) ) )    # Yuvarlanma noktası faktörü

            self.O['disli']['2']['z'] = math.ceil( self.O['disli']['1']['z'] * self.O['kademe']['1']['i'] )
            self.O['disli']['4']['z'] = math.ceil( self.O['disli']['3']['z'] * self.O['kademe']['2']['i'] )
            self.O['disli']['1']['Md'] = 9550 * ( self.O['Pg'] / self.O['ng'] ) * self.O['Kc'] * self.O['kademe']['1']['n'] * self.O['n']['r1']
            self.O['disli']['2']['Md'] = self.O['disli']['1']['Md'] * self.O['kademe']['1']['i']
            self.O['disli']['3']['Md'] = self.O['disli']['2']['Md']
            self.O['disli']['4']['Md'] = 9550 * ( self.O['Pc'] / self.O['nc'] ) * self.O['Kc'] * self.O['kademe']['2']['n'] * self.O['n']['r2']
            self.O['disli']['1']['n'] = self.O['ng']
            self.O['disli']['2']['n'] = self.O['disli']['1']['n'] * ( self.O['disli']['1']['z'] / self.O['disli']['2']['z'] )
            self.O['disli']['3']['n'] = self.O['disli']['2']['n']
            self.O['disli']['4']['n'] = self.O['disli']['3']['n'] * ( self.O['disli']['3']['z'] / self.O['disli']['4']['z'] )


            self.lineEdit_44.setText( str( self.O['disli']['1']['z'] ) )
            self.lineEdit_49.setText( str( self.O['disli']['2']['z'] ) )
            self.lineEdit_56.setText( str( self.O['disli']['3']['z'] ) )
            self.lineEdit_64.setText( str( self.O['disli']['4']['z'] ) )

            self.progressBar.setValue(10)

            # ---------------- BİRİNCİ KADEME -----------------------
            # Diş dibi mukavemetine göre modül hesabı
            m1 = math.pow( ( 2.0 * 1000.0 * self.O['disli']['1']['Md'] * self.O['disli']['1']['Yf'] ) / ( self.O['disli']['1']['z']**2 * self.O['kademe']['1']['Fid'] * self.O['M']['1']['SFlim'] ), 1.0 / 3.0)
            # Yüzey ezilmesi göre modül hesabı
            m2 = ( 1.0 / self.O['disli']['1']['z'] ) * math.pow( ( 2.0 * 1000.0 * self.O['disli']['1']['Md'] * self.O['Ke']**2 * self.O['Ka']**2 * self.O['kademe']['1']['Ki'] ) / ( self.O['kademe']['1']['Fid'] * self.O['M']['1']['SHlim']**2 ), 1.0 / 3.0 )

            if ( m1 > m2 ) : self.O['disli']['1']['m'] = m1
            else : self.O['disli']['1']['m'] = m2

            for x in range( len ( self.O['SMod']['1'] ) - 1 ) :
                if ( self.O['disli']['1']['m'] >= self.O['SMod']['1'][x] and self.O['disli']['1']['m'] <= self.O['SMod']['1'][x+1] ) :
                    self.O['disli']['1']['m'] = self.O['SMod']['1'][x+1]
                    break

            self.progressBar.setValue(15)
            # ---------------- İKİNCİ KADEME -----------------------
            # Diş dibi mukavemetine göre modül hesabı
            m1 = math.pow( ( 2.0 * 1000.0 * self.O['disli']['2']['Md'] * self.O['disli']['2']['Yf'] ) / ( self.O['disli']['2']['z']**2 * ( self.O['kademe']['1']['Fid'] ) * ( self.O['M']['1']['SFlim'] ) ) , 1.0 / 3.0)
            # Yüzey ezilmesi göre modül hesabı
            m2 = ( 1.0 / self.O['disli']['2']['z'] ) * math.pow( ( 2.0 * 1000.0 * self.O['disli']['2']['Md'] * self.O['Ke']**2 * self.O['Ka']**2 * self.O['kademe']['1']['Ki'] ) / ( self.O['kademe']['1']['Fid'] * ( self.O['M']['1']['SHlim'] )**2 ), 1.0 / 3.0 )

            if ( m1 > m2 ) : self.O['disli']['2']['m'] = m1
            else : self.O['disli']['2']['m'] = m2

            for x in range( len ( self.O['SMod']['1'] ) - 1 ) :
                if ( self.O['disli']['2']['m'] >= self.O['SMod']['1'][x] and self.O['disli']['2']['m'] <= self.O['SMod']['1'][x+1] ) :
                    self.O['disli']['2']['m'] = self.O['SMod']['1'][x+1]
                    break

            # Eş çalışan dişliler için modül hesabı
            if ( self.O['disli']['1']['m'] > self.O['disli']['2']['m'] ) : self.O['disli']['2']['m'] = self.O['disli']['1']['m']
            else : self.O['disli']['1']['m'] = self.O['disli']['2']['m']

            # Diş dibi mukavemetine göre modül hesabı
            m1 = math.pow( ( 2.0 * 1000.0 * self.O['disli']['3']['Md'] * self.O['disli']['3']['Yf'] ) / ( self.O['disli']['3']['z']**2 * self.O['kademe']['2']['Fid'] * self.O['M']['2']['SFlim'] ) , 1.0 / 3.0)
            # Yüzey ezilmesi göre modül hesabı
            m2 = ( 1.0 / self.O['disli']['3']['z'] ) * math.pow( ( 2.0 * 1000.0 * self.O['disli']['3']['Md'] * self.O['Ke']**2 * self.O['Ka']**2 * self.O['kademe']['2']['Ki'] ) / ( self.O['kademe']['2']['Fid'] * self.O['M']['2']['SHlim']**2 ), 1.0 / 3.0 )

            if ( m1 > m2 ) : self.O['disli']['3']['m'] = m1
            else : self.O['disli']['3']['m'] = m2

            for x in range( len ( self.O['SMod']['2'] ) - 1 ) :
                if ( self.O['disli']['3']['m'] >= self.O['SMod']['2'][x] and self.O['disli']['3']['m'] <= self.O['SMod']['2'][x+1] ) :
                    self.O['disli']['3']['m'] = self.O['SMod']['2'][x+1]
                    break

            # Diş dibi mukavemetine göre modül hesabı
            m1 = math.pow( ( 2.0 * 1000.0 * self.O['disli']['4']['Md'] * self.O['disli']['4']['Yf'] ) / ( self.O['disli']['4']['z']**2 * ( self.O['kademe']['2']['Fid'] ) * ( self.O['M']['2']['SFlim'] ) ) , 1.0 / 3.0)
            # Yüzey ezilmesi göre modül hesabı
            m2 = ( 1.0 / self.O['disli']['4']['z'] ) * math.pow( ( 2.0 * 1000.0 * self.O['disli']['4']['Md'] * self.O['Ke']**2 * self.O['Ka']**2 * self.O['kademe']['2']['Ki'] ) / ( self.O['kademe']['2']['Fid'] * ( self.O['M']['2']['SHlim'] )**2 ), 1.0 / 3.0 )

            if ( m1 > m2 ) : self.O['disli']['4']['m'] = m1
            else : self.O['disli']['4']['m'] = m2

            for x in range( len ( self.O['SMod']['2'] ) - 1 ) :
                if ( self.O['disli']['4']['m'] >= self.O['SMod']['2'][x] and self.O['disli']['4']['m'] <= self.O['SMod']['2'][x+1] ) :
                    self.O['disli']['4']['m'] = self.O['SMod']['2'][x+1]
                    break

            # Eş çalışan dişliler için modül hesabı
            if ( self.O['disli']['3']['m'] > self.O['disli']['4']['m'] ) : self.O['disli']['4']['m'] = self.O['disli']['3']['m']
            else : self.O['disli']['3']['m'] = self.O['disli']['4']['m']


            ######################### 1. ve 2. Dişli için #################################
            self.progressBar.setValue(20)
            # Sıfır dişli çark
            if ( self.O['disli']['1']['x'] == self.O['disli']['2']['x'] == 0.0 ) :
                self.O['kademe']['1']['type'] = "Sıfır dişli çark"

                # Birinci Dişli
                self.O['disli']['1']['d0'] = self.O['disli']['1']['m'] * self.O['disli']['1']['z']             # Taksimat dairesi
                self.O['disli']['1']['db'] = self.O['disli']['1']['d0'] + 2 * self.O['disli']['1']['m']        # Baş dairesi
                self.O['disli']['1']['dt'] = self.O['disli']['1']['d0'] - 2.5 * self.O['disli']['1']['m']      # Taban dairesi
                self.O['disli']['1']['s0'] = math.pi * self.O['disli']['1']['m'] / 2.0                          # Diş kalınlığı

                # İkinci Dişli
                self.O['disli']['2']['d0'] = self.O['disli']['2']['m'] * self.O['disli']['2']['z']             # Taksimat dairesi
                self.O['disli']['2']['db'] = self.O['disli']['2']['d0'] + 2 * self.O['disli']['2']['m']        # Baş dairesi
                self.O['disli']['2']['dt'] = self.O['disli']['2']['d0'] - 2.5 * self.O['disli']['2']['m']      # Taban dairesi
                self.O['disli']['2']['s0'] = math.pi * self.O['disli']['2']['m'] / 2.0                          # Diş kalınlığı

                self.O['kademe']['1']['a0'] = self.O['disli']['1']['m'] * ( self.O['disli']['1']['z'] + self.O['disli']['2']['z'] ) / 2.0
                self.O['kademe']['1']['a'] = self.O['kademe']['1']['a0']
                self.O['kademe']['1']['alfa0'] = self.O['alfa0']
                self.O['kademe']['1']['alfa'] = self.O['kademe']['1']['alfa0']

                ev_alfa0 = evolvent( self.O['kademe']['1']['alfa0'] )
                ev_alfa = tan( self.O['kademe']['1']['alfa0'] ) + ev_alfa0
                self.O['kademe']['1']['ev_alfa0'] = ev_alfa0
                self.O['kademe']['1']['ev_alfa'] = ev_alfa

                self.O['disli']['1']['d'] = self.O['disli']['1']['d0']
                self.O['disli']['2']['d'] = self.O['disli']['2']['d0']

                self.O['disli']['1']['hb'] = self.O['disli']['2']['hb'] = self.O['disli']['1']['m']
                self.O['disli']['1']['ht'] = self.O['disli']['2']['ht'] = 1.25 * self.O['disli']['1']['m']
                self.O['disli']['1']['h'] = self.O['disli']['2']['h'] = 2.25 * self.O['disli']['1']['m']

            # Sıfır kaydırmalı K-0
            elif ( self.O['disli']['1']['x'] + self.O['disli']['2']['x'] == 0.0 ) :
                self.O['kademe']['1']['type'] = "Sıfır kaydırmalı (K-0)"

                self.O['kademe']['1']['a0'] = self.O['disli']['1']['m'] * ( self.O['disli']['1']['z'] + self.O['disli']['2']['z'] ) / 2
                self.O['kademe']['1']['a'] = self.O['kademe']['1']['a0']
                self.O['kademe']['1']['alfa0'] = self.O['alfa0']
                self.O['kademe']['1']['alfa'] = self.O['kademe']['1']['alfa0']

                ev_alfa0 = evolvent( self.O['kademe']['1']['alfa0'] )
                ev_alfa = tan( self.O['kademe']['1']['alfa0'] ) + ev_alfa0
                self.O['kademe']['1']['ev_alfa0'] = ev_alfa0
                self.O['kademe']['1']['ev_alfa'] = ev_alfa

                if ( self.O['disli']['1']['x'] >= 0.0 ) :
                    # Artı Dişli : 1
                    self.O['disli']['1']['d0'] = self.O['disli']['1']['m'] * self.O['disli']['1']['z']
                    self.O['disli']['1']['db'] = self.O['disli']['1']['d0'] + 2 * self.O['disli']['1']['m'] * ( 1 + self.O['disli']['1']['x'] )
                    self.O['disli']['1']['dt'] = self.O['disli']['1']['d0'] - 2 * self.O['disli']['1']['m'] * ( 1.25 - self.O['disli']['1']['x'] )
                    self.O['disli']['1']['s0'] = ( math.pi * self.O['disli']['1']['m'] / 2.0 ) + ( 2 * self.O['disli']['1']['x'] * tan( self.O['kademe']['1']['alfa0'] ) )
                    self.O['disli']['1']['hb'] = self.O['disli']['1']['m'] * ( 1 + self.O['disli']['1']['x'] )
                    self.O['disli']['1']['ht'] = self.O['disli']['1']['m'] * ( 1.25 - self.O['disli']['1']['x'] )
                    self.O['disli']['1']['h'] = self.O['disli']['1']['ht'] + self.O['disli']['1']['hb']

                    # Eksi Dişli : 2
                    self.O['disli']['2']['d0'] = self.O['disli']['2']['m'] * self.O['disli']['2']['z']
                    self.O['disli']['2']['db'] = self.O['disli']['2']['d0'] + 2 * self.O['disli']['2']['m'] * ( 1 - self.O['disli']['1']['x'] )
                    self.O['disli']['2']['dt'] = self.O['disli']['2']['d0'] - 2 * self.O['disli']['2']['m'] * ( 1.25 + self.O['disli']['1']['x'] )
                    self.O['disli']['2']['s0'] = ( math.pi * self.O['disli']['1']['m'] / 2.0 ) - ( 2 * self.O['disli']['2']['x'] * tan( self.O['kademe']['1']['alfa0'] ) )
                    self.O['disli']['2']['hb'] = self.O['disli']['2']['m'] * ( 1 - self.O['disli']['2']['x'] )
                    self.O['disli']['2']['ht'] = self.O['disli']['2']['m'] * ( 1.25 + self.O['disli']['2']['x'] )
                    self.O['disli']['2']['h'] = self.O['disli']['2']['ht'] + self.O['disli']['2']['hb']

                else :
                    # Eksi Dişli : 1
                    self.O['disli']['1']['d0'] = self.O['disli']['1']['m'] * self.O['disli']['1']['z']
                    self.O['disli']['1']['db'] = self.O['disli']['1']['d0'] + 2 * self.O['disli']['1']['m'] * ( 1 - self.O['disli']['1']['x'] )
                    self.O['disli']['1']['dt'] = self.O['disli']['1']['d0'] - 2 * self.O['disli']['1']['m'] * ( 1.25 + self.O['disli']['1']['x'] )
                    self.O['disli']['1']['s0'] = ( math.pi * self.O['disli']['1']['m'] / 2.0 ) - ( 2 * self.O['disli']['1']['x'] * tan( self.O['kademe']['1']['alfa0'] ) )
                    self.O['disli']['1']['hb'] = self.O['disli']['1']['m'] * ( 1 - self.O['disli']['1']['x'] )
                    self.O['disli']['1']['ht'] = self.O['disli']['1']['m'] * ( 1.25 + self.O['disli']['1']['x'] )
                    self.O['disli']['1']['h'] = self.O['disli']['1']['ht'] + self.O['disli']['1']['hb']

                    # Artı Dişli : 2
                    self.O['disli']['2']['d0'] = self.O['disli']['2']['m'] * self.O['disli']['2']['z']
                    self.O['disli']['2']['db'] = self.O['disli']['2']['d0'] + 2 * self.O['disli']['2']['m'] * ( 1 + self.O['disli']['2']['x'] )
                    self.O['disli']['2']['dt'] = self.O['disli']['2']['d0'] - 2 * self.O['disli']['2']['m'] * ( 1.25 - self.O['disli']['2']['x'] )
                    self.O['disli']['2']['s0'] = ( math.pi * self.O['disli']['2']['m'] / 2.0 ) + ( 2 * self.O['disli']['2']['x'] * tan( self.O['kademe']['1']['alfa0'] ) )
                    self.O['disli']['2']['hb'] = self.O['disli']['2']['m'] * ( 1 + self.O['disli']['2']['x'] )
                    self.O['disli']['2']['ht'] = self.O['disli']['2']['m'] * ( 1.25 - self.O['disli']['2']['x'] )
                    self.O['disli']['2']['h'] = self.O['disli']['2']['ht'] + self.O['disli']['2']['hb']

                self.O['disli']['1']['d'] = self.O['disli']['1']['d0']
                self.O['disli']['2']['d'] = self.O['disli']['2']['d0']

            # Kaydırmalı K
            else :
                self.O['kademe']['1']['type'] = "Kaydırmalı (K)"

                if ( self.O['disli']['1']['x'] >= 0 ) :
                    # Artı Dişli : 1
                    self.O['disli']['1']['d0'] = self.O['disli']['1']['m'] * self.O['disli']['1']['z']
                    self.O['disli']['1']['db'] = self.O['disli']['1']['d0'] + 2 * self.O['disli']['1']['m'] * ( 1 + self.O['disli']['1']['x'] )
                    self.O['disli']['1']['dt'] = self.O['disli']['1']['d0'] - 2 * self.O['disli']['1']['m'] * ( 1.25 - self.O['disli']['1']['x'] )
                    self.O['disli']['1']['s0'] = ( math.pi * self.O['disli']['1']['m'] / 2.0 ) + ( 2 * x * tan( self.O['alfa0'] ) )
                else :
                    # Eksi Dişli : 1
                    self.O['disli']['1']['d0'] = self.O['disli']['1']['m'] * self.O['disli']['1']['z']
                    self.O['disli']['1']['db'] = self.O['disli']['1']['d0'] + 2 * self.O['disli']['1']['m'] * ( 1 + self.O['disli']['1']['x'] )
                    self.O['disli']['1']['dt'] = self.O['disli']['1']['d0'] - 2 * self.O['disli']['1']['m'] * ( 1.25 - self.O['disli']['1']['x'] )
                    self.O['disli']['1']['s0'] = ( math.pi * self.O['disli']['1']['m'] / 2.0 ) + ( 2 * x * tan( self.O['alfa0'] ) )
                #
                if ( self.O['disli']['2']['x'] > 0 ) :
                    # Artı Dişli : 2
                    self.O['disli']['2']['d0'] = self.O['disli']['2']['m'] * self.O['disli']['2']['z']
                    self.O['disli']['2']['db'] = self.O['disli']['2']['d0'] + 2 * self.O['disli']['2']['m'] * ( 1 + self.O['disli']['2']['x'] )
                    self.O['disli']['2']['dt'] = self.O['disli']['2']['d0'] - 2 * self.O['disli']['2']['m'] * ( 1.25 - self.O['disli']['2']['x'] )
                    self.O['disli']['2']['s0'] = ( math.pi * self.O['disli']['2']['m'] / 2.0 ) + ( 2 * x * tan( self.O['alfa0'] ) )
                else :
                    # Eksi Dişli : 2
                    self.O['disli']['2']['d0'] = self.O['disli']['2']['m'] * self.O['disli']['2']['z']
                    self.O['disli']['2']['db'] = self.O['disli']['2']['d0'] + 2 * self.O['disli']['2']['m'] * ( 1 + self.O['disli']['1']['x'] )
                    self.O['disli']['2']['dt'] = self.O['disli']['2']['d0'] - 2 * self.O['disli']['2']['m'] * ( 1.25 - self.O['disli']['1']['x'] )
                    self.O['disli']['2']['s0'] = ( math.pi * self.O['disli']['1']['m'] / 2.0 ) + ( 2 * x * tan( self.O['alfa0'] ) )

                self.O['kademe']['1']['a0'] = ( self.O['disli']['1']['m'] * ( self.O['disli']['1']['z'] + self.O['disli']['2']['z'] ) ) / 2
                self.O['kademe']['1']['alfa0'] = self.O['alfa0']

                ev_alfa0 = evolvent( self.O['kademe']['1']['alfa0'] )
                ev_alfa = 2 * ( ( self.O['disli']['1']['x'] + self.O['disli']['2']['x'] ) / ( self.O['disli']['1']['z'] + self.O['disli']['2']['z'] ) ) * tan( self.O['kademe']['1']['alfa0'] ) + ev_alfa0
                self.O['kademe']['1']['ev_alfa0'] = ev_alfa0
                self.O['kademe']['1']['ev_alfa'] = ev_alfa

                # Evolventi bulma fonksiyonu
                find_evolventalfa( self.O['kademe']['1']['ev_alfa'], [10, 451, 5, 10.0] )

                #Linux Error
                alfa = 20.0;

                self.O['kademe']['1']['alfa'] = alfa
                self.O['kademe']['1']['a'] = self.O['kademe']['1']['a0'] * ( cos( self.O['kademe']['1']['alfa0'] ) / cos( self.O['kademe']['1']['alfa'] ) )

                # Baş kısaltma yapılması - kontrolü
                if ( self.O['disli']['1']['x'] >= 0 ) :pass
                    # Artı Dişli : 1
                    # Eksi Dişli : 2
                else :pass
                    # Artı Dişli : 2
                    # Eksi Dişli : 1

                db1k = 2 * ( self.O['kademe']['1']['a'] + self.O['disli']['1']['m'] - ( self.O['disli']['2']['x'] * self.O['disli']['1']['m'] ) ) - self.O['disli']['2']['d0']
                db2k = 2 * ( self.O['kademe']['1']['a'] + self.O['disli']['1']['m'] - ( self.O['disli']['1']['x'] * self.O['disli']['1']['m'] ) ) - self.O['disli']['1']['d0']
                dt1k = self.O['disli']['1']['d0'] - ( 2 * self.O['disli']['1']['m'] * ( 1.25 - self.O['disli']['1']['x'] ) )
                dt2k = self.O['disli']['2']['d0'] - ( 2 * self.O['disli']['1']['m'] * ( 1.25 - self.O['disli']['2']['x'] ) )

                sb = self.O['kademe']['1']['a'] - ( ( db1k + dt2k ) / 2 )
                if ( sb >= ( 0.1 * self.O['disli']['1']['m'] ) and sb <= ( 0.3 * self.O['disli']['1']['m'] ) ) : self.O['kademe']['1']['cut'] = False
                else :
                    self.O['disli']['1']['dbk'] = db1k
                    self.O['disli']['1']['dtk'] = dt1k
                    self.O['disli']['2']['dbk'] = db2k
                    self.O['disli']['2']['dtk'] = dt2k

                if ( self.O['disli']['1']['x'] > 0 ) :
                    self.O['disli']['1']['hb'] = self.O['disli']['1']['m'] * ( 1 + self.O['disli']['1']['x'] )
                    self.O['disli']['1']['ht'] = self.O['disli']['1']['m'] * ( 1.25 - self.O['disli']['1']['x'] )
                    self.O['disli']['1']['h'] = self.O['disli']['1']['hb'] + self.O['disli']['1']['ht']
                else :
                    self.O['disli']['1']['hb'] = self.O['disli']['1']['m'] * ( 1 - self.O['disli']['1']['x'] )
                    self.O['disli']['1']['ht'] = self.O['disli']['1']['m'] * ( 1.25 + self.O['disli']['1']['x'] )
                    self.O['disli']['1']['h'] = self.O['disli']['1']['hb'] + self.O['disli']['1']['ht']

                if ( self.O['disli']['2']['x'] > 0 ) :
                    self.O['disli']['2']['hb'] = self.O['disli']['2']['m'] * ( 1 + self.O['disli']['2']['x'] )
                    self.O['disli']['2']['ht'] = self.O['disli']['2']['m'] * ( 1.25 - self.O['disli']['2']['x'] )
                    self.O['disli']['2']['h'] = self.O['disli']['2']['hb'] + self.O['disli']['2']['ht']
                else :
                    self.O['disli']['2']['hb'] = self.O['disli']['2']['m'] * ( 1 - self.O['disli']['2']['x'] )
                    self.O['disli']['2']['ht'] = self.O['disli']['2']['m'] * ( 1.25 + self.O['disli']['2']['x'] )
                    self.O['disli']['2']['h'] = self.O['disli']['2']['hb'] + self.O['disli']['2']['ht']


            self.progressBar.setValue(30)
            ######################### 3. ve 4. Dişli için #################################
            # Sıfır dişli çark
            if ( self.O['disli']['3']['x'] == self.O['disli']['4']['x'] == 0 ) :
                self.O['kademe']['2']['type'] = "Sıfır dişli çark"

                # Birinci Dişli
                self.O['disli']['3']['d0'] = self.O['disli']['3']['m'] * self.O['disli']['3']['z']             # Taksimat dairesi
                self.O['disli']['3']['db'] = self.O['disli']['3']['d0'] + 2 * self.O['disli']['3']['m']        # Baş dairesi
                self.O['disli']['3']['dt'] = self.O['disli']['3']['d0'] - 2.5 * self.O['disli']['3']['m']      # Taban dairesi
                self.O['disli']['3']['s0'] = math.pi * self.O['disli']['3']['m'] / 2.0                          # Diş kalınlığı

                # İkinci Dişli
                self.O['disli']['4']['d0'] = self.O['disli']['4']['m'] * self.O['disli']['4']['z']             # Taksimat dairesi
                self.O['disli']['4']['db'] = self.O['disli']['4']['d0'] + 2 * self.O['disli']['4']['m']        # Baş dairesi
                self.O['disli']['4']['dt'] = self.O['disli']['4']['d0'] - 2.5 * self.O['disli']['4']['m']      # Taban dairesi
                self.O['disli']['4']['s0'] = math.pi * self.O['disli']['4']['m'] / 2.0                          # Diş kalınlığı

                self.O['kademe']['2']['a0'] = self.O['disli']['3']['m'] * ( self.O['disli']['3']['z'] + self.O['disli']['4']['z'] ) / 2.0
                self.O['kademe']['2']['a'] = self.O['kademe']['2']['a0']
                self.O['kademe']['2']['alfa0'] = self.O['alfa0']
                self.O['kademe']['2']['alfa'] = self.O['kademe']['2']['alfa0']

                ev_alfa0 = evolvent( self.O['kademe']['2']['alfa0'] )
                ev_alfa = tan( self.O['kademe']['2']['alfa0'] ) + ev_alfa0
                self.O['kademe']['2']['ev_alfa0'] = ev_alfa0
                self.O['kademe']['2']['ev_alfa'] = ev_alfa

                self.O['disli']['3']['d'] = self.O['disli']['3']['d0']
                self.O['disli']['4']['d'] = self.O['disli']['4']['d0']

                self.O['disli']['3']['hb'] = self.O['disli']['4']['hb'] = self.O['disli']['3']['m']
                self.O['disli']['3']['ht'] = self.O['disli']['4']['ht'] = 1.25 * self.O['disli']['3']['m']
                self.O['disli']['3']['h'] = self.O['disli']['4']['h'] = 2.25 * self.O['disli']['3']['m']

            # Sıfır kaydırmalı K-0
            elif ( self.O['disli']['3']['x'] + self.O['disli']['4']['x'] == 0 ) :
                self.O['kademe']['2']['type'] = "Sıfır kaydırmalı (K-0)"

                self.O['kademe']['2']['a0'] = self.O['disli']['3']['m'] * ( self.O['disli']['3']['z'] + self.O['disli']['4']['z'] ) / 2
                self.O['kademe']['2']['a'] = self.O['kademe']['2']['a0']
                self.O['kademe']['2']['alfa0'] = self.O['alfa0']
                self.O['kademe']['2']['alfa'] = self.O['kademe']['2']['alfa0']

                ev_alfa0 = evolvent( self.O['kademe']['2']['alfa0'] )
                ev_alfa = tan( self.O['kademe']['2']['alfa0'] ) + ev_alfa0
                self.O['kademe']['2']['ev_alfa0'] = ev_alfa0
                self.O['kademe']['2']['ev_alfa'] = ev_alfa

                if ( self.O['disli']['3']['x'] >= 0.0 ) :
                    # Artı Dişli : 1
                    self.O['disli']['3']['d0'] = self.O['disli']['3']['m'] * self.O['disli']['3']['z']
                    self.O['disli']['3']['db'] = self.O['disli']['3']['d0'] + 2 * self.O['disli']['3']['m'] * ( 1 + self.O['disli']['3']['x'] )
                    self.O['disli']['3']['dt'] = self.O['disli']['3']['d0'] - 2 * self.O['disli']['3']['m'] * ( 1.25 - self.O['disli']['3']['x'] )
                    self.O['disli']['3']['s0'] = ( math.pi * self.O['disli']['3']['m'] / 2.0 ) + ( 2 * self.O['disli']['3']['x'] * tan( self.O['kademe']['2']['alfa0'] ) )
                    self.O['disli']['3']['hb'] = self.O['disli']['3']['m'] * ( 1 + self.O['disli']['3']['x'] )
                    self.O['disli']['3']['ht'] = self.O['disli']['3']['m'] * ( 1.25 - self.O['disli']['3']['x'] )
                    self.O['disli']['3']['h'] = self.O['disli']['3']['ht'] + self.O['disli']['3']['hb']

                    # Eksi Dişli : 2
                    self.O['disli']['4']['d0'] = self.O['disli']['4']['m'] * self.O['disli']['4']['z']
                    self.O['disli']['4']['db'] = self.O['disli']['4']['d0'] + 2 * self.O['disli']['4']['m'] * ( 1 - self.O['disli']['3']['x'] )
                    self.O['disli']['4']['dt'] = self.O['disli']['4']['d0'] - 2 * self.O['disli']['4']['m'] * ( 1.25 + self.O['disli']['3']['x'] )
                    self.O['disli']['4']['s0'] = ( math.pi * self.O['disli']['3']['m'] / 2.0 ) - ( 2 * self.O['disli']['4']['x'] * tan( self.O['kademe']['2']['alfa0'] ) )
                    self.O['disli']['4']['hb'] = self.O['disli']['4']['m'] * ( 1 - self.O['disli']['4']['x'] )
                    self.O['disli']['4']['ht'] = self.O['disli']['4']['m'] * ( 1.25 + self.O['disli']['4']['x'] )
                    self.O['disli']['4']['h'] = self.O['disli']['4']['ht'] + self.O['disli']['4']['hb']

                else :
                    # Eksi Dişli : 1
                    self.O['disli']['3']['d0'] = self.O['disli']['3']['m'] * self.O['disli']['3']['z']
                    self.O['disli']['3']['db'] = self.O['disli']['3']['d0'] + 2 * self.O['disli']['3']['m'] * ( 1 - self.O['disli']['3']['x'] )
                    self.O['disli']['3']['dt'] = self.O['disli']['3']['d0'] - 2 * self.O['disli']['3']['m'] * ( 1.25 + self.O['disli']['3']['x'] )
                    self.O['disli']['3']['s0'] = ( math.pi * self.O['disli']['3']['m'] / 2.0 ) - ( 2 * self.O['disli']['3']['x'] * tan( self.O['kademe']['2']['alfa0'] ) )
                    self.O['disli']['3']['hb'] = self.O['disli']['3']['m'] * ( 1 - self.O['disli']['3']['x'] )
                    self.O['disli']['3']['ht'] = self.O['disli']['3']['m'] * ( 1.25 + self.O['disli']['3']['x'] )
                    self.O['disli']['3']['h'] = self.O['disli']['3']['ht'] + self.O['disli']['3']['hb']

                    # Artı Dişli : 2
                    self.O['disli']['4']['d0'] = self.O['disli']['4']['m'] * self.O['disli']['4']['z']
                    self.O['disli']['4']['db'] = self.O['disli']['4']['d0'] + 2 * self.O['disli']['4']['m'] * ( 1 + self.O['disli']['4']['x'] )
                    self.O['disli']['4']['dt'] = self.O['disli']['4']['d0'] - 2 * self.O['disli']['4']['m'] * ( 1.25 - self.O['disli']['4']['x'] )
                    self.O['disli']['4']['s0'] = ( math.pi * self.O['disli']['4']['m'] / 2.0 ) + ( 2 * self.O['disli']['4']['x'] * tan( self.O['kademe']['2']['alfa0'] ) )
                    self.O['disli']['4']['hb'] = self.O['disli']['4']['m'] * ( 1 + self.O['disli']['4']['x'] )
                    self.O['disli']['4']['ht'] = self.O['disli']['4']['m'] * ( 1.25 - self.O['disli']['4']['x'] )
                    self.O['disli']['4']['h'] = self.O['disli']['4']['ht'] + self.O['disli']['4']['hb']
                #

                self.O['disli']['3']['d'] = self.O['disli']['3']['d0']
                self.O['disli']['4']['d'] = self.O['disli']['4']['d0']

            # Kaydırmalı K
            else :
                self.O['kademe']['2']['type'] = "Kaydırmalı (K)"

                # Birinci Dişli
                self.O['disli']['3']['d0'] = self.O['disli']['3']['m'] * self.O['disli']['3']['z']
                self.O['disli']['3']['db'] = self.O['disli']['3']['d0'] + 2 * self.O['disli']['3']['m'] * ( 1 + self.O['disli']['3']['x'] )
                self.O['disli']['3']['dt'] = self.O['disli']['3']['d0'] - 2 * self.O['disli']['3']['m'] * ( 1.25 - self.O['disli']['3']['x'] )
                self.O['disli']['3']['s0'] = ( math.pi * self.O['disli']['3']['m'] / 2.0 ) + ( 2 * x * tan( self.O['alfa0'] ) )

                # İkinci Dişli
                self.O['disli']['4']['d0'] = self.O['disli']['4']['m'] * self.O['disli']['4']['z']
                self.O['disli']['4']['db'] = self.O['disli']['4']['d0'] + 2 * self.O['disli']['4']['m'] * ( 1 + self.O['disli']['3']['x'] )
                self.O['disli']['4']['dt'] = self.O['disli']['4']['d0'] - 2 * self.O['disli']['4']['m'] * ( 1.25 - self.O['disli']['3']['x'] )
                self.O['disli']['4']['s0'] = ( math.pi * self.O['disli']['3']['m'] / 2.0 ) + ( 2 * x * tan( self.O['alfa0'] ) )

                self.O['kademe']['2']['a0'] = ( self.O['disli']['3']['m'] * ( self.O['disli']['3']['z'] + self.O['disli']['4']['z'] ) ) / 2
                self.O['kademe']['2']['alfa0'] = self.O['alfa0']

                ev_alfa0 = evolvent( self.O['kademe']['2']['alfa0'] )
                ev_alfa = 2 * ( ( self.O['disli']['3']['x'] + self.O['disli']['4']['x'] ) / ( self.O['disli']['3']['z'] + self.O['disli']['4']['z'] ) ) * tan( self.O['kademe']['2']['alfa0'] ) + ev_alfa0

                # Gerekirse kullanılacak
                self.O['kademe']['2']['ev_alfa0'] = ev_alfa0
                self.O['kademe']['2']['ev_alfa'] = ev_alfa

                # Evolventi bulma fonksiyonu
                find_evolventalfa( ev_alfa, [10, 451, 5, 10.0] )

                self.O['kademe']['2']['alfa'] = alfa
                self.O['kademe']['2']['a'] = self.O['kademe']['2']['a0'] * ( cos( self.O['kademe']['2']['alfa0'] ) / cos( alfa ) )

                # Baş kısaltma yapılması - kontrolü
                db1k = 2 * ( self.O['kademe']['2']['a'] + self.O['disli']['3']['m'] - ( self.O['disli']['4']['x'] * self.O['disli']['3']['m'] ) ) - self.O['disli']['4']['d0']
                db2k = 2 * ( self.O['kademe']['2']['a'] + self.O['disli']['3']['m'] - ( self.O['disli']['3']['x'] * self.O['disli']['3']['m'] ) ) - self.O['disli']['3']['d0']
                dt1k = self.O['disli']['3']['d0'] - ( 2 * self.O['disli']['3']['m'] * ( 1.25 - self.O['disli']['3']['x'] ) )
                dt2k = self.O['disli']['4']['d0'] - ( 2 * self.O['disli']['3']['m'] * ( 1.25 - self.O['disli']['4']['x'] ) )

                sb = self.O['kademe']['2']['a'] - ( ( db1k + dt2k ) / 2 )
                if ( sb >= ( 0.1 * self.O['disli']['3']['m'] ) and sb <= ( 0.3 * self.O['disli']['3']['m'] ) ) : self.O['kademe']['2']['cut'] = False
                else :
                    self.O['disli']['3']['dbk'] = db1k
                    self.O['disli']['3']['dtk'] = dt1k
                    self.O['disli']['4']['dbk'] = db2k
                    self.O['disli']['4']['dtk'] = dt2k

                if ( self.O['disli']['3']['x'] > 0 ) :
                    self.O['disli']['3']['hb'] = self.O['disli']['3']['m'] * ( 1 + self.O['disli']['3']['x'] )
                    self.O['disli']['3']['ht'] = self.O['disli']['3']['m'] * ( 1.25 - self.O['disli']['3']['x'] )
                    self.O['disli']['3']['h'] = self.O['disli']['3']['hb'] + self.O['disli']['3']['ht']
                else :
                    self.O['disli']['3']['hb'] = self.O['disli']['3']['m'] * ( 1 - self.O['disli']['3']['x'] )
                    self.O['disli']['3']['ht'] = self.O['disli']['3']['m'] * ( 1.25 + self.O['disli']['3']['x'] )
                    self.O['disli']['3']['h'] = self.O['disli']['3']['hb'] + self.O['disli']['3']['ht']
                #
                if ( self.O['disli']['4']['x'] > 0 ) :
                    self.O['disli']['4']['hb'] = self.O['disli']['4']['m'] * ( 1 + self.O['disli']['4']['x'] )
                    self.O['disli']['4']['ht'] = self.O['disli']['4']['m'] * ( 1.25 - self.O['disli']['4']['x'] )
                    self.O['disli']['4']['h'] = self.O['disli']['4']['hb'] + self.O['disli']['4']['ht']
                else :
                    self.O['disli']['4']['hb'] = self.O['disli']['4']['m'] * ( 1 - self.O['disli']['4']['x'] )
                    self.O['disli']['4']['ht'] = self.O['disli']['4']['m'] * ( 1.25 + self.O['disli']['4']['x'] )
                    self.O['disli']['4']['h'] = self.O['disli']['4']['hb'] + self.O['disli']['4']['ht']
            #

            self.progressBar.setValue(45)
            self.O['disli']['1']['dg'] = self.O['disli']['1']['d0'] * cos( self.O['kademe']['1']['alfa0'] )
            self.O['disli']['2']['dg'] = self.O['disli']['2']['d0'] * cos( self.O['kademe']['1']['alfa0'] )
            self.O['disli']['3']['dg'] = self.O['disli']['3']['d0'] * cos( self.O['kademe']['2']['alfa0'] )
            self.O['disli']['4']['dg'] = self.O['disli']['4']['d0'] * cos( self.O['kademe']['2']['alfa0'] )

            self.O['disli']['1']['P'] = self.O['disli']['1']['m'] * math.pi
            self.O['disli']['2']['P'] = self.O['disli']['2']['m'] * math.pi
            self.O['disli']['3']['P'] = self.O['disli']['3']['m'] * math.pi
            self.O['disli']['4']['P'] = self.O['disli']['4']['m'] * math.pi

            self.O['disli']['1']['b'] = self.O['kademe']['1']['Fid'] * self.O['disli']['1']['d0']
            self.O['disli']['2']['b'] = self.O['kademe']['1']['Fid'] * self.O['disli']['2']['d0']
            self.O['disli']['3']['b'] = self.O['kademe']['2']['Fid'] * self.O['disli']['3']['d0']
            self.O['disli']['4']['b'] = self.O['kademe']['2']['Fid'] * self.O['disli']['4']['d0']


            self.progressBar.setValue(50)
            ##################### 1. self.O['kademe'] İÇİN ###########################
            self.O['kademe']['1']['eps'] = ( \
                math.sqrt( ( self.O['disli']['1']['db'] / 2 )**2 - ( self.O['disli']['1']['dt'] / 2 )**2 ) + \
                math.sqrt( ( self.O['disli']['2']['db'] / 2 )**2 - ( self.O['disli']['2']['dt'] / 2 )**2 ) - \
                self.O['kademe']['1']['a'] * sin( self.O['kademe']['1']['alfa'] ) ) / \
                ( self.O['disli']['1']['m'] * math.pi * cos( self.O['kademe']['1']['alfa'] ) )

            self.O['disli']['1']['e'] = EmniyetKontrolu( self.O, self.O['disli'], '1', self.O['kademe'], '1' )
            self.O['disli']['2']['e'] = EmniyetKontrolu( self.O, self.O['disli'], '2', self.O['kademe'], '1' )

            ##################### 2. self.O['kademe'] İÇİN ###########################
            self.O['kademe']['2']['eps'] = ( \
                math.sqrt( ( self.O['disli']['3']['db'] / 2 )**2 - ( self.O['disli']['3']['dt'] / 2 )**2 ) + \
                math.sqrt( ( self.O['disli']['4']['db'] / 2 )**2 - ( self.O['disli']['4']['dt'] / 2 )**2 ) - \
                self.O['kademe']['2']['a'] * sin( self.O['kademe']['2']['alfa'] ) ) / \
                ( self.O['disli']['3']['m'] * math.pi * cos( self.O['kademe']['2']['alfa'] ) )

            self.O['disli']['3']['e'] = EmniyetKontrolu( self.O, self.O['disli'], '3', self.O['kademe'], '2' )
            self.O['disli']['4']['e'] = EmniyetKontrolu( self.O, self.O['disli'], '4', self.O['kademe'], '2' )

            self.progressBar.setValue(60)
            # 1.Dişlinin Değerleri
            self.lineEdit_44.setText( str( self.O['disli']['1']['z'] ) )
            self.lineEdit_37.setText( str( round( self.O['disli']['1']['Md'], self.FIX ) ) )
            self.lineEdit_38.setText( str( round( self.O['disli']['1']['db'], self.FIX ) ) )
            self.lineEdit_39.setText( str( round( self.O['disli']['1']['d0'], self.FIX ) ) )
            self.lineEdit_40.setText( str( round( self.O['disli']['1']['dt'], self.FIX ) ) )
            self.lineEdit_41.setText( str( round( self.O['disli']['1']['hb'], self.FIX ) ) )
            self.lineEdit_42.setText( str( round( self.O['disli']['1']['ht'], self.FIX ) ) )
            self.lineEdit_43.setText( str( round( self.O['disli']['1']['h'], self.FIX ) ) )
            self.lineEdit_77.setText( str( round( self.O['disli']['1']['s0'], self.FIX ) ) )
            self.lineEdit_169.setText( str( round( self.O['disli']['1']['b'], self.FIX ) ) )
            self.lineEdit_85.setText( str( round( self.O['disli']['1']['n'], self.FIX ) ) )

            self.progressBar.setValue(65)
            # 2.Dişlinin Değerleri
            self.lineEdit_49.setText( str( self.O['disli']['2']['z'] ) )
            self.lineEdit_46.setText( str( round( self.O['disli']['2']['Md'], self.FIX ) ) )
            self.lineEdit_47.setText( str( round( self.O['disli']['2']['db'], self.FIX ) ) )
            self.lineEdit_48.setText( str( round( self.O['disli']['2']['d0'], self.FIX ) ) )
            self.lineEdit_52.setText( str( round( self.O['disli']['2']['dt'], self.FIX ) ) )
            self.lineEdit_50.setText( str( round( self.O['disli']['2']['hb'], self.FIX ) ) )
            self.lineEdit_51.setText( str( round( self.O['disli']['2']['ht'], self.FIX ) ) )
            self.lineEdit_45.setText( str( round( self.O['disli']['2']['h'], self.FIX ) ) )
            self.lineEdit_76.setText( str( round( self.O['disli']['2']['s0'], self.FIX ) ) )
            self.lineEdit_170.setText( str( round( self.O['disli']['2']['b'], self.FIX ) ) )
            self.lineEdit_86.setText( str( round( self.O['disli']['2']['n'], self.FIX ) ) )

            self.progressBar.setValue(70)
            # 3.Dişlinin Değerleri
            self.lineEdit_56.setText( str( self.O['disli']['3']['z'] ) )
            self.lineEdit_59.setText( str( round( self.O['disli']['3']['Md'], self.FIX ) ) )
            self.lineEdit_57.setText( str( round( self.O['disli']['3']['db'], self.FIX ) ) )
            self.lineEdit_53.setText( str( round( self.O['disli']['3']['d0'], self.FIX ) ) )
            self.lineEdit_66.setText( str( round( self.O['disli']['3']['dt'], self.FIX ) ) )
            self.lineEdit_65.setText( str( round( self.O['disli']['3']['hb'], self.FIX ) ) )
            self.lineEdit_61.setText( str( round( self.O['disli']['3']['ht'], self.FIX ) ) )
            self.lineEdit_62.setText( str( round( self.O['disli']['3']['h'], self.FIX ) ) )
            self.lineEdit_78.setText( str( round( self.O['disli']['3']['s0'], self.FIX ) ) )
            self.lineEdit_171.setText( str( round( self.O['disli']['3']['b'], self.FIX ) ) )
            self.lineEdit_79.setText( str( round( self.O['disli']['3']['n'], self.FIX ) ) )

            self.progressBar.setValue(75)
            # 4.Dişlinin Değerleri
            self.lineEdit_64.setText( str( self.O['disli']['4']['z'] ) )
            self.lineEdit_55.setText( str( round( self.O['disli']['4']['Md'], self.FIX ) ) )
            self.lineEdit_54.setText( str( round( self.O['disli']['4']['db'], self.FIX ) ) )
            self.lineEdit_63.setText( str( round( self.O['disli']['4']['d0'], self.FIX ) ) )
            self.lineEdit_68.setText( str( round( self.O['disli']['4']['dt'], self.FIX ) ) )
            self.lineEdit_60.setText( str( round( self.O['disli']['4']['hb'], self.FIX ) ) )
            self.lineEdit_58.setText( str( round( self.O['disli']['4']['ht'], self.FIX ) ) )
            self.lineEdit_67.setText( str( round( self.O['disli']['4']['h'], self.FIX ) ) )
            self.lineEdit_75.setText( str( round( self.O['disli']['4']['s0'], self.FIX ) ) )
            self.lineEdit_172.setText( str( round( self.O['disli']['4']['b'], self.FIX ) ) )
            self.lineEdit_84.setText( str( round( self.O['disli']['4']['n'], self.FIX ) ) )

            self.progressBar.setValue(80)
            # 1.Kademe Değerleri
            self.lineEdit_16.setText(str(round(self.O['kademe']['1']['i'],self.FIX)))
            self.lineEdit_18.setText(str(round(self.O['kademe']['1']['n'],self.FIX)))
            self.lineEdit_19.setText(str(round(self.O['kademe']['1']['alfa'],self.FIX)))
            self.lineEdit_20.setText(str(round(self.O['kademe']['1']['alfa0'],self.FIX)))
            self.lineEdit_21.setText(str(round(self.O['kademe']['1']['ev_alfa'],self.FIX)))
            self.lineEdit_22.setText(str(round(self.O['kademe']['1']['ev_alfa0'],self.FIX)))
            self.lineEdit_23.setText(str(round(self.O['kademe']['1']['a'],self.FIX)))
            self.lineEdit_24.setText(str(round(self.O['kademe']['1']['a0'],self.FIX)))
            self.lineEdit_33.setText(str(round(self.O['kademe']['1']['eps'],self.FIX)))
            if ( self.O['kademe']['1']['cut'] ) : self.label_59.setText(_t("Yapıldı"))
            else : self.label_59.setText(_t("Yapılmadı"))
            self.label_58.setText(_t(self.O['kademe']['1']['type']))
            self.lineEdit_35.setText(str(round(self.O['disli']['1']['m'],self.FIX)))


            self.progressBar.setValue(85)
            # 2.Kademe Değerleri
            self.lineEdit_26.setText(str(round(self.O['kademe']['2']['i'],self.FIX)))
            self.lineEdit_31.setText(str(round(self.O['kademe']['2']['n'],self.FIX)))
            self.lineEdit_32.setText(str(round(self.O['kademe']['2']['alfa'],self.FIX)))
            self.lineEdit_29.setText(str(round(self.O['kademe']['2']['alfa0'],self.FIX)))
            self.lineEdit_25.setText(str(round(self.O['kademe']['2']['ev_alfa'],self.FIX)))
            self.lineEdit_27.setText(str(round(self.O['kademe']['2']['ev_alfa0'],self.FIX)))
            self.lineEdit_28.setText(str(round(self.O['kademe']['2']['a'],self.FIX)))
            self.lineEdit_30.setText(str(round(self.O['kademe']['2']['a0'],self.FIX)))
            self.lineEdit_34.setText(str(round(self.O['kademe']['2']['eps'],self.FIX)))
            if ( self.O['kademe']['2']['cut'] ) : self.label_70.setText(_t("Yapıldı"))
            else : self.label_70.setText(_t("Yapılmadı"))
            self.label_77.setText(_t(self.O['kademe']['2']['type']))
            self.lineEdit_36.setText(str(round(self.O['disli']['3']['m'],self.FIX)))

            self.lineEdit_11.setText(str(round(self.O['nt'],self.FIX)))
            self.lineEdit_12.setText(str(round(self.O['it'],self.FIX)))
            self.lineEdit_13.setText(str(round(self.O['Pc'],self.FIX)))
            self.lineEdit_14.setText(str(round(self.O['Pk'],self.FIX)))

            self.progressBar.setValue(90)
            control = [ 8, 13, 18, 23 ]
            for index in self.O['disli'].keys() :
                status = True
                table = self.__GuvenlikHesaplariAl( index )
                for row in table.keys() :
                    key = table[row][0]
                    val = table[row][1]
                    if ( row in control ) :
                        if ( val < self.O['S'] ) :
                            status = False
                if ( index == '1' ) :
                    if ( status ) :
                        self.textBrowser.setStyleSheet(_t("background: #00cc00; color: #fff; border: 2px solid #000; text-align: center;"))
                        self.textBrowser.setHtml(QtGui.QApplication.translate("MainWindow", "Emniyetli", None, QtGui.QApplication.UnicodeUTF8))
                    else :
                        self.textBrowser.setStyleSheet(_t("background: #ff0000; color: #fff; border: 2px solid #000; text-align: center;"))
                        self.textBrowser.setHtml(QtGui.QApplication.translate("MainWindow", "Emniyetli Değil", None, QtGui.QApplication.UnicodeUTF8))
                elif ( index == '2' ) :
                    if ( status ) :
                        self.textBrowser_2.setStyleSheet(_t("background: #00cc00; color: #fff; border: 2px solid #000; text-align: center;"))
                        self.textBrowser_2.setHtml(QtGui.QApplication.translate("MainWindow", "Emniyetli", None, QtGui.QApplication.UnicodeUTF8))
                    else :
                        self.textBrowser_2.setStyleSheet(_t("background: #ff0000; color: #fff; border: 2px solid #000; text-align: center;"))
                        self.textBrowser_2.setHtml(QtGui.QApplication.translate("MainWindow", "Emniyetli Değil", None, QtGui.QApplication.UnicodeUTF8))
                elif ( index == '3' ) :
                    if ( status ) :
                        self.textBrowser_4.setStyleSheet(_t("background: #00cc00; color: #fff; border: 2px solid #000; text-align: center;"))
                        self.textBrowser_4.setHtml(QtGui.QApplication.translate("MainWindow", "Emniyetli", None, QtGui.QApplication.UnicodeUTF8))
                    else :
                        self.textBrowser_4.setStyleSheet(_t("background: #ff0000; color: #fff; border: 2px solid #000; text-align: center;"))
                        self.textBrowser_4.setHtml(QtGui.QApplication.translate("MainWindow", "Emniyetli Değil", None, QtGui.QApplication.UnicodeUTF8))
                elif ( index == '4' ) :
                    if ( status ) :
                        self.textBrowser_3.setStyleSheet(_t("background: #00cc00; color: #fff; border: 2px solid #000; text-align: center;"))
                        self.textBrowser_3.setHtml(QtGui.QApplication.translate("MainWindow", "Emniyetli", None, QtGui.QApplication.UnicodeUTF8))
                    else :
                        self.textBrowser_3.setStyleSheet(_t("background: #ff0000; color: #fff; border: 2px solid #000; text-align: center;"))
                        self.textBrowser_3.setHtml(QtGui.QApplication.translate("MainWindow", "Emniyetli Değil", None, QtGui.QApplication.UnicodeUTF8))

            self.progressBar.setValue(100)
            self.progressBar.setEnabled(0)
            self.progressBar.setValue(0)
        else :
            self.label_17.setText(_t("Girilmesi gereken tüm veriler girilmedi !"))


#QtGui.QMessageBox.information(None, self.t("İşletme Faktörü"), str( self.horizontalSlider_10.value() ) )

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow()
    #mainWindow.show()
    mainWindow.showMaximized()
    #mainWindow.showFullScreen()
    sys.exit(app.exec_())
