# Rental-House-Price-Prediction
A machine learning project to predict rental apartment prices in Bursa, Turkey. Data was collected by scraping multiple real estate platforms, followed by preprocessing, analysis, and model development using various regression algorithms.

# 🏠 House Rental Price Prediction – Bursa, Turkey

## 📂 Overview

With the surge in housing demand and fluctuating rent prices, making data-driven decisions in the real estate market has become increasingly vital. This project focuses on **predicting rental apartment prices** in **Bursa, Turkey**, using real estate data scraped from major property platforms.

---

## 🎯 Project Goals

- Scrape real estate listings from Turkish property websites
- Clean and preprocess the data
- Conduct exploratory data analysis (EDA)
- Train and evaluate multiple machine learning regression models
- Identify key features that impact rental prices
- Provide a tool to estimate prices based on apartment features

---

## 🛠️ Tools & Technologies

- **Languages**: Python
- **Libraries**: pandas, numpy, matplotlib, seaborn, plotly, scikit-learn
- **Web Scraping**: BeautifulSoup, Selenium
- **ML Algorithms**: Linear Regression, Decision Tree, Random Forest, SVR, Lasso

---

## 📥 Data Collection

The dataset was constructed by scraping listings from:

- 🏡 [HepsiEmlak](https://www.hepsiemlak.com/)
- 🏢 [Emlakjet](https://www.emlakjet.com/)
- 🏘 [Remax](https://www.remax.com.tr/)

### Main Features

- `price_clean`: Monthly rent (TL)
- `m2_net_clean`: Net usable area
- `oda_clean`: Number of rooms
- `banyo_sayisi_clean`: Number of bathrooms
- `kat_sayisi_clean`: Total floors
- `bulundugu_kat_clean`: Apartment’s floor
- `bina_yasi_clean`: Age of the building
- `Isıtma Türü`: Heating type
- `İlçe`: District
- `eşyalı`: Furnished (Yes/No)
- `site içinde`: Inside site (Yes/No)

---

## 🧹 Data Preprocessing

- Outlier detection using **Interquartile Range (IQR)**
- One-hot encoding for categorical data
- Standard scaling for numerical values
- Train-test split (80/20)

---

## 📊 Data Exploration & Visualization

