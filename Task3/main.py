import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import zscore

students = pd.read_excel('students_performance.xlsx')

# 1. Sürətli baxış:

# print(students.head(5))
# print(students.tail(5))
# print(students.sample(3))

# 2. Struktur yoxlaması:

# print(students.info())
# print("\nBos deyerleri:")
# print(students.isnull().sum())
# print("\nDtypes:")
# print(students.dtypes)

# print(students.select_dtypes(include=np.number).columns)

# 3.Statistik icmal:

# print(students.describe())
#
# print("GPA Mean:",students["GPA"].mean())
# print("GPA Median:",students["GPA"].median())
# print("GPA STD:",students["GPA"].std())
#
# print("MathScore Mean:",students["MathScore"].mean())
# print("MathScore Median:",students["MathScore"].median())
# print("MathScore STD:",students["MathScore"].std())

# if abs(students["GPA"].mean() - students["GPA"].median()) > 0.1:
#     print("GPA texminen simmetrikdir")
# else:
#     print("GPA eyri paylanib")

# 4.Tip düzəlişi:

# if students["HasScholarship"].dtype == "object":
#     students["HasScholarship"] = students["HasScholarship"].map({
#         "Yes" : True,
#         "No" : False
#     })
#
# if students["AttendanceRate"].dtype == "object":
#     students["AttendanceRate"]=pd.to_numeric(students["AttendanceRate"],errors="coerce")
#
# print(students.dtypes)

# 5. Boş dəyərləri analiz et:

# print(students.isnull().sum())
#
# gpa = students["GPA"]=students["GPA"].fillna(
#     students["GPA"].median()
# )
#
# department = students["Department"] = students["Department"].fillna(
#     students["Department"].mode()[0]
# )
#
# print(gpa)
# print(department)


# 6.Departament üzrə tələbə sayı:

# dept_counts = students["Department"].value_counts()
# print(dept_counts)
#
# print("En cox telebe:")
# print(dept_counts.idxmax())

# 7. Mean vs Median (MathScore):

# mean_math = students["MathScore"].mean()
# median_math = students["MathScore"].median()

# print("Mean:", mean_math)
# print("Median:",median_math)

# if abs(mean_math - median_math) > 0.2:
#     print("Outlier tesiri mumkundur")

# 8. Scholarship təsiri:

# scholarship_gpa = students.groupby("HasScholarship")["GPA"].mean()
# print(scholarship_gpa)

# 9.Korelyasiya:

# corr = students[
#     [
#         "GPA",
#         "MathScore",
#         "ReadingScore",
#         "WritingScore",
#         "AttendanceRate"
#     ]
# ].corr()
# print(corr)

# 10.Outlier (IQR metodu):

# Q1 = students["MathScore"].quantile(0.25)
# Q3 = students["MathScore"].quantile(0.75)
#
# IQR = Q3 - Q1
#
# lower = Q1 - 1.5 * IQR
# upper = Q3 + 1.5 * IQR
#
# print("Lower:",lower, "Upper:",upper)
#
# outliers_iqr = students[(students["MathScore"] < lower) | (students["MathScore"] > upper)]
# print(outliers_iqr)

# print(outliers_iqr.nsmallest(1,"MathScore"))
# print(outliers.nlargest(1, "MathScore"))

# 11.Outlier (Z-score metodu):

# students["Math_Z"] = zscore(students["MathScore"])
# students["GPA_Z"] = zscore(students["GPA"])
#
# z_outliers = students[
#     (abs(students["Math_Z"]) > 3) |
#     (abs(students["GPA_Z"]) > 3)
# ]
# print(z_outliers)

# 12.Departament üzrə GPA müqayisəsi:

# dept_gpa = (
#     students.groupby("Department")["GPA"]
#     .agg(["mean", "median", "count"])
# )
# print(dept_gpa)

# 13.Gender fərqləri:

# gender_stats = (
#     students.groupby("Gender")[["GPA","MathScore"]]
#     .agg("median")
# )
#
# print(gender_stats)

# 14. Vizual analiz:

# Histogram:
# plt.hist(students['GPA'],bins=15)
# plt.title("GPA Distribution")
# plt.figure(figsize=(6,4))
# plt.show()
#
# plt.hist(students['MathScore'],bins=15)
# plt.title("MathScore Distribution")
# plt.figure(figsize=(6,4))
# plt.show()

# Boxplot

import seaborn as sns

plt.title("Department and GPA Boxplot")
sns.boxplot(x="Department", y="GPA" ,data=students)
plt.figure(figsize=(8,5))
plt.show()

# Scatterplot

plt.title("AttendanceRate vs GPA")
sns.scatterplot(x="AttendanceRate", y="GPA", hue="HasScholarship", data=students)
plt.figure(figsize=(8,5))
plt.show()


# 15 Mini nəticə hesabatı:

print("""
Dataset 120 tələbə məlumatından və 10 sütundan ibarətdir. Analiz zamanı müəyyən olundu ki, bəzi sütunlarda boş dəyərlər mövcuddur. GPA sütunundakı boş xanalar median ilə, Department sütunundakı boş xana isə ən çox təkrarlanan dəyərlə əvəz edildi.

Statistik göstəricilərə əsasən GPA-nın orta qiyməti ilə medianı bir-birinə çox yaxındır. Bu da GPA göstəricilərinin balanslı paylandığını göstərir. MathScore nəticələrində isə median ortalamadan bir qədər yüksəkdir ki, bu da aşağı balların orta göstəriciyə təsir etdiyini göstərir.

Outlier araşdırması həm IQR, həm də Z-score metodları ilə aparıldı. Nəticədə MathScore üzrə ciddi kənar dəyər aşkar edilmədi. Bu isə məlumatların ümumilikdə stabil olduğunu göstərir.

Korrelyasiya analizində GPA ilə davamiyyət (AttendanceRate) arasında ən güclü müsbət əlaqə müşahidə edildi. Yazı və riyaziyyat nəticələri də GPA ilə nəzərəçarpacaq əlaqəyə malikdir. Riyaziyyat və yazı balları arasında isə ən yüksək qarşılıqlı əlaqə qeydə alındı.

Fakültələr üzrə müqayisədə Economics tələbələri ən yüksək orta GPA göstəricisinə sahibdir. Tələbə sayına görə isə IT fakültəsi digərlərindən daha çox təmsil olunmuşdur.

Təqaüd alan tələbələrin orta GPA göstəricisi təqaüd almayanlardan yüksəkdir. Lakin bu nəticə təqaüdün birbaşa səbəb olduğunu deyil, uğurlu tələbələrin daha çox təqaüd alma ehtimalını göstərə bilər.

Ümumi qiymətləndirməyə əsasən tələbə performansına ən çox təsir göstərən faktorlar davamiyyət səviyyəsi və akademik nəticələrdir. Xüsusilə yüksək davamiyyət GPA-nın yüksəlməsi ilə əlaqələndirilir.
""")


