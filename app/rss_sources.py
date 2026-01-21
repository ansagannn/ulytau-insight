# app/rss_sources.py

# Strict Keywords for Filtering
# News MUST contain at least one of these to be shown.
REGION_KEYWORDS = [
    "Ұлытау", "Улытау", "Ulytau",
    "Жезқазған", "Жезказган", "Zhezkazgan", "Jezkazgan",
    "г. Сатпаев", "город Сатпаев", "Сатпаев қаласы", "Satpayev City",
    "Сәтпаев қаласы", "Сәтпаев қ.", "Сатпаев қ.",
    "Қаражал", "Каражал", "Karazhal",
    "Жаңаарқа", "Жанаарка", "Zhanaarka",
    "Ұлытау ауданы", "Улытауский район",
    "Жезді", "Zhezdi",
    "Ұлытау облысы", "Улытауская область", "Ulytau Region"
]

# Law/Category Keywords
LAW_KEYWORDS = [
    "закон", "указ", "постановление", "бұйрық", "қаулы", "кодекс", 
    "нормативо-правовой", "НПА", "регламент"
]

CONSTITUTION_KEYWORDS = [
    "конституция", "ата заң", "конституциялық", "конституционный"
]

# Exclusion Keywords
# News containing these will be HIDDEN unless they also contain a REGION_KEYWORD.
EXCLUDE_KEYWORDS = [
    # Major Cities (Cyrillic & Latin)
    "Астана", "Astana", "Алматы", "Almaty", 
    "Шымкент", "Shymkent",
    "Қарағанды", "Караганда", "Karaganda", "Qaragandy",
    "Ақтөбе", "Актобе", "Aktobe", 
    "Атырау", "Atyrau", 
    "Тараз", "Taraz", 
    "Қызылорда", "Кызылорда", "Kyzylorda", 
    "Орал", "Уральск", "Uralsk", "Oral",
    "Өскемен", "Усть-Каменогорск", "Oskemen", 
    "Павлодар", "Pavlodar", 
    "Петропавл", "Петропавловск", "Petropavlovsk", 
    "Қостанай", "Костанай", "Kostanay", 
    "Талдықорған", "Талдыкорган", "Taldykorgan", 
    "Түркістан", "Туркестан", "Turkestan", 
    "Көкшетау", "Кокшетау", "Kokshetau",
    "Ақтау", "Актау", "Aktau",
    "Алатау", "Alatau", "G4 City",
    
    # International & Others
    "Киев", "Kiev", "Kyiv", "Украина", "Ukraine",
    "Россия", "РФ", "Russia", "Москва", "Moscow",
    "США", "USA", "Америка",
    "Ташкент", "Tashkent", "Узбекистан", "Uzbekistan",
    "Бишкек", "Bishkek", "Кыргызстан", "Kyrgyzstan"
]

# Source Configuration
# Types: 'rss', 'html_list', 'google_rss'
SOURCES = [
    # --- RSS SOURCES ---
    {
        "name": "Ulytaunews.kz (Local RSS)",
        "url": "https://ulytaunews.kz/feed/",
        "type": "rss"
    },
    {
        "name": "Kapital.kz",
        "url": "https://kapital.kz/feed",
        "type": "rss"
    },
    {
        "name": "Inform.kz (RSS RU)",
        "url": "https://www.inform.kz/rss/ru.xml", 
        "type": "rss"
    },
    
    # --- GOOGLE NEWS RSS (Smart Entry) ---
    {
        "name": "Google News: Ulytau Region",
        "url": "https://news.google.com/rss/search?q=%D0%A3%D0%BB%D1%8B%D1%82%D0%B0%D1%83+%D0%BE%D0%B1%D0%BB%D1%8B%D1%81%D1%8B&hl=ru&gl=KZ&ceid=KZ:ru",
        "type": "google_rss"
    },
    {
        "name": "Google News: Zhezkazgan",
        "url": "https://news.google.com/rss/search?q=%D0%96%D0%B5%D0%B7%D0%BA%D0%B0%D0%B7%D0%B3%D0%B0%D0%BD&hl=ru&gl=KZ&ceid=KZ:ru",
        "type": "google_rss"
    },
    {
        "name": "Google News: Satpayev",
        "url": "https://news.google.com/rss/search?q=%D0%A1%D0%B0%D1%82%D0%BF%D0%B0%D0%B5%D0%B2&hl=ru&gl=KZ&ceid=KZ:ru",
        "type": "google_rss"
    },
    {
        "name": "Google News: Karazhal",
        "url": "https://news.google.com/rss/search?q=%D0%9A%D0%B0%D1%80%D0%B0%D0%B6%D0%B0%D0%BB&hl=ru&gl=KZ&ceid=KZ:ru",
        "type": "google_rss"
    },
    {
        "name": "Google News: Zhanaarka",
        "url": "https://news.google.com/rss/search?q=%D0%96%D0%B0%D0%BD%D0%B0%D0%B0%D1%80%D0%BA%D0%B0&hl=ru&gl=KZ&ceid=KZ:ru",
        "type": "google_rss"
    },
    {
        "name": "Google News: Constitution & Laws RK",
        "url": "https://news.google.com/rss/search?q=%D0%9A%D0%BE%D0%BD%D1%81%D1%82%D0%B8%D1%82%D1%83%D1%86%D0%B8%D1%8F+%D0%9A%D0%B0%D0%B7%D0%B0%D1%85%D1%81%D1%82%D0%B0%D0%BD%D0%B0+%D0%B8%D0%BB%D0%B8+%D0%97%D0%B0%D0%BA%D0%BE%D0%BD%D1%8B+%D0%A0%D0%9A&hl=ru&gl=KZ&ceid=KZ:ru",
        "type": "google_rss"
    },

    # --- HTML SOURCES (Official & National Tags) ---
    {
        "name": "Tengrinews: Ulytau",
        "url": "https://tengrinews.kz/tag/область_улытау/",
        "type": "html_list"
    },
    {
        "name": "Zakon.kz: Ulytau",
        "url": "https://www.zakon.kz/oblast/ulytauskaya-oblast/",
        "type": "html_list"
    },
    {
        "name": "24.kz: Ulytau",
        "url": "https://24.kz/ru/tags/tag/Улытауская%20область",
        "type": "html_list"
    },
    {
        "name": "Baq.kz: Ulytau",
        "url": "https://rus.baq.kz/teg/ulytau/",
        "type": "html_list"
    },
    {
        "name": "Gov.kz: Ulytau Region",
        "url": "https://www.gov.kz/memleket/entities/ulytau/press/news?lang=ru",
        "type": "html_list"
    },
    {
        "name": "Gov.kz: Zhezkazgan",
        "url": "https://www.gov.kz/memleket/entities/ulytau-zhezkazgan/press/news?lang=ru",
        "type": "html_list"
    },
    {
        "name": "Gov.kz: Satpayev",
        "url": "https://www.gov.kz/memleket/entities/ulytau-satpaev/press/news?lang=ru",
        "type": "html_list"
    },
    {
        "name": "News20.kz (Zhezkazgan Vestnik)",
        "url": "https://news20.kz/news-mainnews",
        "type": "html_list"
    },

    # --- TELEGRAM SOURCES (Public Web View) ---
    {
        "name": "ZTB QAZAQSTAN",
        "url": "https://t.me/s/ztb_qaz",
        "type": "telegram"
    },
    {
        "name": "Akorda (Official)",
        "url": "https://t.me/s/aqorda_resmi",
        "type": "telegram"
    },
    {
        "name": "DCHS Ulytau",
        "url": "https://t.me/s/dchsulytau",
        "type": "telegram"
    },
    {
        "name": "Orda.kz",
        "url": "https://t.me/s/orda_kz",
        "type": "telegram"
    },
    {
        "name": "Zakon.kz (Telegram)",
        "url": "https://t.me/s/zakonkz",
        "type": "telegram"
    },
    {
        "name": "Tengrinews (Telegram)",
        "url": "https://t.me/s/tengrinews",
        "type": "telegram"
    },
    {
        "name": "Kazakh Inform",
        "url": "https://t.me/s/kazakh_inform",
        "type": "telegram"
    }
]
