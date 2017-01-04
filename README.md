Bilgisayar programı yardımıyla dişli kutusu boyutlandırma
====
Python (PyQT) ile profil kaydırmalı ve düz silindirik dişliler için 2 kademeli dişli kutusu boyutlandırma uygulamasıdır. Makine Mühendisliği bitirme tezi çalışmasıdır.

Program tek sayfadan oluşmaktadır. Tüm hesapları buradan yapabilirsiniz. İşlemler iki aşamada gerçekleştirilir.
Redüktörün çalışmasına ait bilgiler girildiğinde, dişli çarklar için uygun diş sayıları hesaplanır.
Diş sayıları belirlendikten sonra sıfır dişli için bu diş sayılarına uygun diş forma faktörleri belirlenir.

1.Aşama
-----
Redüktör bilgileri ve gerekli faktörler ve verim değerleri.
Sırayla boş alanları dolduruyoruz. İlk olarak tahrik gücünü giriyoruz. Daha sonra giriş ve çıkış için istenen devir sayılarını, çalışma durumuna göre işletme faktörü ve emniyet katsayısını belirliyoruz.

![alt tag](https://github.com/marzochi/disli-kutusu-boyutlandirma/blob/master/Screenshots/2.png)

İşletme faktörü Redüktörün çalışma şartına göre değişiklik gösteren bir etkendir. Bu nedenle ![alt tag](https://github.com/marzochi/disli-kutusu-boyutlandirma/blob/master/Screenshots/4.png) butonuna tıklayıp açılan tablodan şartlarınıza uygun işletme faktörünü değeri seçmelisiniz.

![alt tag](https://github.com/marzochi/disli-kutusu-boyutlandirma/blob/master/Screenshots/5.png)

Yazı alanlarına tıkladığında birim ve değer ile ilgili bilgi baloncuk içinde gösterilir. 
Emniyet katsayısı ve işletme faktörünü seçerken kaydırma çubuğunu kullanmalısınız. Bu şekilde standart veya uygun değerlerden sapmanız engellenir ve kolaylık sağlar. Bu kaydırma işlemini yapmak için fare ile tutup sürükleyebilir veya klavyedeki ok tuşlarını kullanabilirsiniz. Değişiklik yapıldığında kaydırma çubuğunun sağ tarafından seçilen değeri kolayca okuyabilirsiniz.
Daha sonra kademeler için girmeniz gereken bilgileri hemen alttaki alanlara girebilirsiniz.
Birinci ve üçüncü dişlinin diş sayılarını, verimleri bunun yanında rulman yatağı için de verim belirleyebilirsiniz. Eğer rulman yatağı veriminin etkili olmasını istemiyorsanız, verimini bir alabilirsiniz.
Her bir kademe için ayrı ayrı malzeme seçebilirsiniz. Malzemeyi seçtiğiniz anda, seçim kutusunun hemen altından seçilen malzeme ile ilgili mukavemet değerlerini görebilirsiniz. Bu sayede malzemeler arasında karşılaştırma da yapabilirsiniz.
Malzeme seçiminin ardından tekrar malzeme ile ilgili bilgileri girmeniz gerekmekte bunun için seçim kutusu ve dikey kaydırma çubuğunu kullanarak genişlik faktörünü belirleyebilirsiniz. İlk olarak seçim kutusundan malzemeye uygulanan işlemi belirtip ardından dikey kaydırma çubuğu ile genişlik faktörünü belirleyebilirsiniz.

![alt tag](https://github.com/marzochi/disli-kutusu-boyutlandirma/blob/master/Screenshots/3.png)
 Bu kısıma kadar anlatılan değerleri tam olarak girdiğinizde, program otomatik olarak her dişlinin diş sayısını hesaplayacaktır

2.Aşama
----
![alt tag](https://github.com/marzochi/disli-kutusu-boyutlandirma/blob/master/Screenshots/6.png)

Diş sayıları hesaplandıktan sonra, profil kaydırma ve buna bağlı olarak diş form faktörünü seçmelisiniz. Profil kaydırma miktarını ilk 0,0 aldıktan sonra emniyet durumuna göre sonradan değiştirmeniz etkisini görmek açısından yararlı olacaktır. Diş forma faktörü diş sayısı ve profil kaydırma miktarına göre belirlenen bir değerdir. Bunun için tablo kullanacağız. Tabloyu açmak için [Resim-4] butonuna tıklıyoruz. Açılan pencereden sırayla;
X ekseninden hesaplanan diş sayısına tıklıyoruz. Program otomatik olarak tıklanan noktanın X-Y eksenlerini kırmızı çizgiler ile belirginleştirecektir.
Çizginin, belirlediğiniz profil kaydırma miktarını gösteren eğri ile kesiştiği noktaya tıklayın. Bu aşamada Y ekseninde diş form faktörünüz belirlenmiş olacaktır.
ESC tuşu veya ![alt tag](https://github.com/marzochi/disli-kutusu-boyutlandirma/blob/master/Screenshots/7.png)’ya tıklayarak pencereyi kapatabilirsiniz.
Seçtiğiniz değer yüksek bir hassasiyetle program tarafından belirlenecektir. Diş form faktörü alanına tıkladığınızda belirlenen değer otomatik olarak girilecektir.

![alt tag](https://github.com/marzochi/disli-kutusu-boyutlandirma/blob/master/Screenshots/8.png)

Gerekli tüm değerler girildikten sonra Hesapla butonuna tıklayarak işlemi bitirebilirsiniz.

![alt tag](https://github.com/marzochi/disli-kutusu-boyutlandirma/blob/master/Screenshots/9.png)

Program anlık olarak hesap yapabilecek şekilde tasarlanmıştır. Örneğin; Tüm değerleri girdikten sonra işletme faktörü, emniyet katsayısı, malzeme ve özellikleri, verimler değiştirildiğinde tekrar Hesapla butonuna tıklamanıza gerek kalmadan otomatik olarak hesaplamalar yapılır. Her dişli ve kademe için bulunan değerler yerlerine yazılır. Girilen değerlerde değişim yaparak farkı kolayca görebilirsiniz.
Dişliler için yapılan güvenlik hesaplarına göre dişlinin emniyetli olup olmadığını görebilirsiniz.
Aşağıdaki resimde bir adet emniyetli ve bir adet emniyetsiz dişli görünmektedir.
![alt tag](https://github.com/marzochi/disli-kutusu-boyutlandirma/blob/master/Screenshots/10.png)

Güvenlik Hesapları butonuna tıklayarak, dişli için yapılan güvenlik hesaplarını görüntüleyebilirsiniz.

![alt tag](https://github.com/marzochi/disli-kutusu-boyutlandirma/blob/master/Screenshots/11.png)

Hız ve dinamik faktör seçimi eklenecek

Temizle butonu: Temizle butonuna tıklayarak forma girilmiş tüm değerleri silebilirsiniz. Böylece her hesaplamadan sonra programı kapatıp açmak zorunda kalmazsınız.
Kaydet butonu: Yapılan tüm hesapları Excel çalışma sayfası (xls) olarak kaydetme imkanı sunar. XLS dosyasını kaydetmeniz için açılan pencerede bir klasör seçmelisiniz.

Gerenkenler
----
Python 2.7+
PyQt4
OS: Linux/Windows/MacOS
