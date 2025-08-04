# Coffee Forecast App

Bu proje, kahve satış verilerini analiz eden ve geleceğe dönük gelir tahmini yapan bir Streamlit uygulamasıdır. Uygulama hem geçmiş tarihli analizler yapabilir, hem de Prophet modeli ile gelecek için gelir tahmini yapabilir.

## Özellikler

- 📊 Geçmiş bir gün için gelir, en çok satılan kahve ve ödeme yöntemi analizi
- 📈 Belirli bir tarih aralığı için toplam gelir ve özet bilgiler
- ☕ Belirli bir kahve türü için detaylı satış analizi
- 🔮 Prophet ile gelecek tarihler için gelir tahmini
- 🤖 RandomForest ile tahmini en çok satılacak kahve türü

## 🖼 Arayüz

<p align="center">
  <img src="coffeeimg1.jpeg" alt="Coffee App Screenshot 1" width="45%" style="margin-right: 10px;"/>
  <img src="coffeeimg2.jpeg" alt="Coffee App Screenshot 2" width="45%"/>
</p>

## 📦 Gereksinimler

Aşağıdaki kütüphaneleri yüklemek için:

```bash
pip install -r requirements.txt

## Çalıştırmak için

python -m streamlit run Coffee_Analysis.py

