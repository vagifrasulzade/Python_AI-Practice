import pandas as pd
import numpy as np
from scipy.stats import zscore


df =pd.read_csv('Preview__houses_day1__first_20_rows_.csv')


# 1.Sürətli baxış:

# print(df.head(5))
# print(df.tail(3))
# print(df.sample(3))

# 2.Struktur yoxlaması:

# print(df.info())
# print("\nBos deyerleri:")
# print(df.isnull().sum())
# print("\nDtypes:")
# print(df.dtypes)


#3.Statistik icmal:

# print(df[["Area_m2","Price_AZN"]].describe())

# print("Price Mean:",df["Price_AZN"].mean())
# print("Price Median:",df["Price_AZN"].median())
# print("Price STD:",df["Price_AZN"].std())


# 4.Tip düzəlişi:

# print("Evvel: ")
# print(df.dtypes)
#
# df["Price_AZN"] = pd.to_numeric(df["Price_AZN"], errors='coerce')
# print("\nSonra:")
# print(df.dtypes)

#5.Qiymət outlier-ləri (təxmini):

# top10 = df.sort_values("Price_AZN",ascending=False).head(10)
# print(top10)

# 6. Kateqorik balans:

# print(df["District"].value_counts())

# 7.Rooms distribusiyası:

# print(df["Rooms"].value_counts().sort_index())

# 8.Mean vs Median (Price):

# print("Price Mean:",df["Price_AZN"].mean())
# print("Price Median:",df["Price_AZN"].median())

# 9.Mode və yayılma ölçüləri:

# print("Rooms mode:")
# print(df["Rooms"].mode())

# print("Price variance:")
# print(df["Price_AZN"].var())

# print("Price std:")
# print(df["Price_AZN"].std())


#10.Filter + seçim:

# filtered = df[(df["Rooms"] >=3 )  & (df["Area_m2"] >=100)]
# print(filtered)

# print("Orta qiymeti:")
# print(filtered["Price_AZN"].mean())

#11 District üzrə mərkəz ölçüləri:
# district_stats = (df.groupby("District")["Price_AZN"].agg(["mean","median","count"]))
# print(district_stats)

#12 Outlier aşkarlanması (IQR):

# Q1 = df["Price_AZN"].quantile(0.25)
# Q3 = df["Price_AZN"].quantile(0.75)
#
# IQR = Q3 - Q1
#
# lower = Q1 - 1.5 * IQR
# upper = Q3 + 1.5 * IQR
#
# outliers_iqr = df[(df["Price_AZN"] < lower) | (df["Price_AZN"] > upper)]
# print(outliers_iqr)

# 13.Outlier aşkarlanması (Z-score):

# df["zscore"] = zscore(df["Price_AZN"], nan_policy="omit")
# outliers_z = df[abs(df["zscore"]) > 3]
# print(outliers_z["Price_AZN"])

# 14.Top 10 ən bahalı və ən ucuz evlər:

# top10_expensive = df.sort_values("Price_AZN", ascending=False).head(10)
# top10_cheap = df.sort_values("Price_AZN").head(10)
#
# print(top10_expensive["Price_AZN"])
# print(top10_cheap["Price_AZN"])

# 15.Room-Effect ideyası:

# print(df.groupby("Rooms")["Price_AZN"].median())

# 16.Price per m² (ppm):
# df["ppm"] = np.where(df["Area_m2"] >0,df["Price_AZN"]/df["Area_m2"],np.nan)
# print(df.sort_values("ppm", ascending=False).head(10)["ppm"])

# 17.Kateqorik təmizləmə (map):

# region_map ={
#     "Sabayil": "Prime",
#     "Yasamal": "Central",
#     "Nizami": "Central",
#     "Nasimi": "Central",
#     "Nerimanov": "Central",
#     "Khatai": "Outer",
#     "Binagadi": "Outer"
# }
#
# df["region"] = df["District"].map(region_map)
# print(df.groupby("region")["Price_AZN"].median())

# 18. Tip problemləri və boşluqların təsiri:

# missing_price = df["Price_AZN"].isna()
# print(missing_price)

# 19. Simulyasiya “təmiz” qiymət medianı:

# Q1 = df["Price_AZN"].quantile(0.25)
# Q3 = df["Price_AZN"].quantile(0.75)
#
# IQR = Q3 - Q1
#
# lower = Q1 - 1.5 * IQR
# upper = Q3 + 1.5 * IQR

# clean_df = df[(df["Price_AZN"] >= lower) & (df["Price_AZN"] <= upper)]
# print("Umumi median:",df["Price_AZN"].median())
# print("Temiz median:",clean_df["Price_AZN"].median())

# 20.Kiçik “mini-profil” hesabatı yaz:

print("Shape:")
print(df.shape)

print("\nNulls per column:")
print(df.isnull().sum())

print("\nNumeric Describe:")
print(df.describe())

print("\nDistrict Count:")
print(df["District"].value_counts())

print("\nMean Price:")
print(df["Price_AZN"].mean())

print("\nMedian Price:")
print(df["Price_AZN"].median())

print("\nTop PPM 5:")
df["ppm"] = df["Price_AZN"] / df["Area_m2"]
print(df.sort_values("ppm",ascending=False).head(5))

