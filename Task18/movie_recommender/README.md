# CinemaPicks — Movie Recommender

Django əsaslı film tövsiyə sistemi. İstifadəçi bəyəndiyi filmləri işarələyir, sistem isə **TF-IDF + cosine similarity** ilə ona oxşar filmləri sıralayıb təqdim edir.

Task18 — Python & AI Practice.

## Nə edir

- Filmləri Excel faylından oxuyur, poster/il/janr məlumatını **OMDb API**-dən çəkir
- Başlıq, təsvir və janr üzrə axtarış
- Ürək düyməsi ilə bəyənmə (login tələb olunmur — session-da saxlanılır)
- Bəyəndiklərinə əsasən şəxsi tövsiyələr, **match faizi** ilə birlikdə

## Tövsiyə alqoritmi

[`movies/recommendation.py`](movies/recommendation.py):

1. Hər filmin `description + genre` mətni birləşdirilir
2. `TfidfVectorizer` ilə vektora çevrilir (`ngram_range=(1, 2)`, english stop-words)
3. Bəyənilən filmlərin vektorlarının **ortalaması** istifadəçi profilini yaradır
4. Bu profil bütün filmlərlə `cosine_similarity` ilə müqayisə olunur
5. Artıq bəyənilənlər siyahıdan çıxarılır, qalanlar oxşarlığa görə sıralanır (top 12)

Oxşarlıq balı faizə çevrilib `✓ 87.4% match` şəklində göstərilir.

## Quraşdırma

```bash
cd Task18/movie_recommender

pip install django pandas openpyxl requests scikit-learn numpy python-dotenv
```

OMDb açarını əlavə et — pulsuz açar [buradan](https://www.omdbapi.com/apikey.aspx):

```bash
cp .env.example .env
```

```env
OMDB_API_KEY=sənin_açarın
```

Bazanı qur və filmləri import et:

```bash
python manage.py migrate
python manage.py import_movies
python manage.py runserver
```

http://127.0.0.1:8000

> `import_movies` `real_movies_sample.xlsx` faylından ilk 60 filmi oxuyur (`Title`, `Description`, `ImageUrl` sütunları tələb olunur) və hər biri üçün OMDb-dən poster, il, janr çəkir. Açar olmasa da işləyir — sadəcə poster və janr boş qalır.

## Random import (Excel-siz)

Excel faylına bağlı qalmaq istəmirsənsə, filmləri birbaşa OMDb-dən random çəkə bilərsən:

```bash
python manage.py import_random_movies                    # 60 film
python manage.py import_random_movies --count 20         # 20 film
python manage.py import_random_movies --count 20 --seed 7  # təkrarlana bilən nəticə
```

OMDb-nin random endpoint-i olmadığı üçün belə işləyir: əvvəlcədən hazırlanmış açar söz siyahısından (`love`, `space`, `night`, `ghost`…) random söz seçilir, `s=` axtarışının random səhifəsi çəkilir, nəticələr qarışdırılır və hər film üçün `i=` ilə tam məlumat (plot, janr, il, poster) alınır.

Plot-u `N/A` olan filmlər atlanır — TF-IDF təsvir üzərində işlədiyi üçün boş plot tövsiyəni korlayar.

## Data mənbəyi

`real_movies_sample.xlsx` — 64 sətir, 3 sütun:

| Sütun | Nümunə |
|---|---|
| `Title` | `Interstellar` |
| `Description` | `A team of explorers travels through a wormhole...` |
| `ImageUrl` | placeholder link (istifadə olunmur, aşağıya bax) |

Import `MOVIE_LIMIT = 60` ilə məhdudlaşır, yəni **ilk 60 film** bazaya düşür. `update_or_create` istifadə olunduğu üçün əmri təkrar işlətmək təhlükəsizdir — dublikat yaratmır, mövcud sətirləri yeniləyir.

Excel-dəki `ImageUrl` dəyərləri `via.placeholder.com` linkləridir və artıq açılmır. Buna görə `display_image` əvvəl OMDb posterini qaytarır; OMDb açarı varsa hər 60 film üçün real poster, il və janr gəlir və Excel-dəki şəkil linkinə heç ehtiyac qalmır.

## Səhifələr

| URL | View | Nə göstərir |
|---|---|---|
| `/` | `movie_list` | Bütün filmlər + axtarış (`?q=`) |
| `/liked/` | `liked_movies` | Bəyəndiyin filmlər |
| `/recommendations/` | `recommendations` | Şəxsi tövsiyələr + match faizi |
| `/movies/<id>/like/` | `toggle_like` | POST — bəyənməni aç/bağla |

## Struktur

```
movie_recommender/
├── movie_recommender/          # settings, urls
├── movies/
│   ├── models.py               # Movie modeli
│   ├── views.py                # 4 view + session-based like
│   ├── recommendation.py       # TF-IDF tövsiyə məntiqi
│   ├── omdb.py                 # OMDb API client
│   ├── urls.py
│   ├── management/commands/
│   │   ├── import_movies.py        # Excel + OMDb import
│   │   └── import_random_movies.py # OMDb-dən random import
│   ├── templatetags/
│   │   └── movie_extras.py     # genre_list filtri
│   ├── templates/movies/       # base, movie_list, liked_movies, recommendations
│   └── static/movies/style.css
├── real_movies_sample.xlsx     # mənbə data
└── .env.example
```

### Movie modeli

| Sahə | Tip | Qeyd |
|---|---|---|
| `title` | CharField | unikal |
| `description` | TextField | TF-IDF üçün əsas mətn |
| `image_url` | URLField | Excel-dən gələn şəkil |
| `poster_url` | URLField | OMDb posteri |
| `year` | CharField | OMDb |
| `genre` | CharField | OMDb, vergüllə ayrılmış |

`display_image` property-si əvvəl OMDb posterini, yoxdursa Excel şəklini qaytarır.

## Qeydlər

- **Bəyənmələr session-da saxlanılır** (`liked_movie_ids`) — istifadəçi qeydiyyatı yoxdur, brauzer session-u təmizlənəndə siyahı sıfırlanır.
- Janrlar `genre_list` şablon filtri ilə vergüldən bölünüb ayrı-ayrı chip kimi göstərilir (maksimum 3).
- Poster yüklənməyəndə `onerror` ilə placeholder şəkil qoyulur.
- `.env` və `db.sqlite3` repoya düşmür.
- Yeni `templatetags/` qovluğu əlavə edildikdən sonra dev server **yenidən başladılmalıdır** — Django şablon kitabxanalarını yalnız start zamanı yığır.
