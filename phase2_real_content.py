import sqlite3

DB = "digital_classroom.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

print("\n" + "="*70)
print("📚 PHASE 2 — REAL LESSON CONTENT")
print("="*70 + "\n")

# ============================================================
# FULL LESSON CONTENT — Real teaching material
# ============================================================
REAL_LESSONS = {

    # ---------------- SHONA ----------------
    ("Shona", "Alphabet"): {
        "goal": "Learn the Shona alphabet and how each letter sounds.",
        "content": (
            "🇿🇼 SHONA ALPHABET (Mavara)\n\n"
            "Shona uses the same 26 letters as English, but they are pronounced differently.\n\n"
            "VOWELS (Mavhawero): A, E, I, O, U\n"
            "• A — as in 'father'\n"
            "• E — as in 'bed'\n"
            "• I — as in 'sit'\n"
            "• O — as in 'or'\n"
            "• U — as in 'put'\n\n"
            "CONSONANTS include special combinations:\n"
            "• Bh (like 'b' with breath) — bhabha\n"
            "• Ch (like 'ch' in 'church') — chikoro\n"
            "• Dh (like 'd' with breath) — dhadha\n"
            "• Dz (like 'ds') — dzidza\n"
            "• Sv (whistled 'sw') — svondo\n"
            "• Zh (like 'zh') — zhou\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Write down 3 Shona words that start with 'ch'."
        ),
    },
    ("Shona", "Greetings"): {
        "goal": "Learn how to greet people in Shona at different times of day.",
        "content": (
            "🇿🇼 SHONA GREETINGS (Kukwazisa)\n\n"
            "Morning:\n"
            "• 'Mangwanani' — Good morning\n"
            "• 'Mangwanani, wakadini?' — Good morning, how are you?\n"
            "• 'Ndiripo, wakadiniwo?' — I am fine, how are you?\n\n"
            "Afternoon:\n"
            "• 'Masikati' — Good afternoon\n\n"
            "Evening:\n"
            "• 'Manheru' — Good evening\n\n"
            "General:\n"
            "• 'Mhoro' — Hello (to one person)\n"
            "• 'Mhoroi' — Hello (respectful / to elder)\n"
            "• 'Mhoroi vanhu vose' — Hello everyone\n\n"
            "Saying goodbye:\n"
            "• 'Chisarai' — Goodbye (to one staying)\n"
            "• 'Fambai zvakanaka' — Go well\n"
            "• 'Sara zvakanaka' — Stay well\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "How do you greet an elder in the morning?"
        ),
    },
    ("Shona", "Numbers"): {
        "goal": "Learn to count and write numbers in Shona from 1 to 100.",
        "content": (
            "🇿🇼 SHONA NUMBERS (Nhamba)\n\n"
            "1 — Motsi / Poshi\n"
            "2 — Piri\n"
            "3 — Tatu\n"
            "4 — China\n"
            "5 — Shanu\n"
            "6 — Tanhatu\n"
            "7 — Nomwe\n"
            "8 — Sere\n"
            "9 — Pfumbamwe\n"
            "10 — Gumi\n\n"
            "11 — Gumi neimwe\n"
            "12 — Gumi nembiri\n"
            "20 — Makumi maviri\n"
            "30 — Makumi matatu\n"
            "50 — Makumi mashanu\n"
            "100 — Zana\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Write the Shona word for 25, 40, and 77."
        ),
    },
    ("Shona", "Family"): {
        "goal": "Learn Shona words for family members.",
        "content": (
            "🇿🇼 SHONA FAMILY (Mhuri)\n\n"
            "Baba — Father\n"
            "Amai / Mai — Mother\n"
            "Mwanakomana — Son\n"
            "Mwanasikana — Daughter\n"
            "Mukoma — Older brother/sister\n"
            "Munin'ina — Younger brother/sister\n"
            "Sekuru — Grandfather\n"
            "Mbuya — Grandmother\n"
            "Tete — Aunt (father's sister)\n"
            "Mainini — Aunt (mother's younger sister)\n"
            "Babamukuru — Uncle (father's older brother)\n"
            "Muroora — Daughter-in-law\n"
            "Mukwasha — Son-in-law\n"
            "Muzukuru — Grandchild / niece / nephew\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "What is the Shona word for 'grandmother'?"
        ),
    },
    ("Shona", "Nouns"): {
        "goal": "Understand the Shona noun classes (mupanda).",
        "content": (
            "🇿🇼 SHONA NOUNS (Mazita)\n\n"
            "Shona nouns belong to different classes (mupanda). Each class has its own "
            "singular and plural prefixes.\n\n"
            "Class 1/2 (Munhu/Vanhu — People):\n"
            "• Mu- / Va- \n"
            "• munhu (person) → vanhu (people)\n"
            "• mukomana (boy) → vakomana (boys)\n\n"
            "Class 3/4 (Muti/Miti — Trees/Objects):\n"
            "• Mu- / Mi-\n"
            "• muti (tree) → miti (trees)\n\n"
            "Class 5/6 (Ziso/Meso):\n"
            "• (no prefix) / Ma-\n"
            "• ziso (eye) → meso (eyes)\n\n"
            "Class 7/8 (Chinhu/Zvinhu — Things):\n"
            "• Chi- / Zvi-\n"
            "• chikoro (school) → zvikoro (schools)\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Give the plural form of 'mukomana' and 'chikoro'."
        ),
    },
    ("Shona", "Verbs"): {
        "goal": "Understand Shona verb structure and tenses.",
        "content": (
            "🇿🇼 SHONA VERBS (Zviito)\n\n"
            "A Shona verb is made of several parts:\n"
            "[subject prefix] + [tense marker] + [root] + [ending]\n\n"
            "Present tense:\n"
            "ndino- (I) + -dy- (eat) + -a = ndinodya (I eat)\n"
            "uno- (you) + -dy- + -a = unodya (you eat)\n"
            "ano- (he/she) + -dy- + -a = anodya (he eats)\n\n"
            "Past tense:\n"
            "ndaka- + -dy- + -a = ndakadya (I ate)\n"
            "waka- = wakadya (you ate)\n"
            "aka- = akadya (he ate)\n\n"
            "Future tense:\n"
            "ndicha- = ndichadya (I will eat)\n"
            "ucha- = uchadya (you will eat)\n"
            "acha- = achadya (he will eat)\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Change 'ndinodya' (I eat) into past tense."
        ),
    },
    ("Shona", "Sentences"): {
        "goal": "Build correct Shona sentences.",
        "content": (
            "🇿🇼 SHONA SENTENCES (Mitsara)\n\n"
            "Shona sentence structure: Subject + Verb + Object\n\n"
            "Simple sentences:\n"
            "• Ndiri kudya sadza. — I am eating sadza.\n"
            "• Mwana ari kutamba. — The child is playing.\n"
            "• Amai vari kubika. — Mother is cooking.\n"
            "• Baba vanoshandan. — Father works.\n\n"
            "Questions:\n"
            "• Uri kuenda kupi? — Where are you going?\n"
            "• Wakaita sei? — What did you do?\n"
            "• Unoda chii? — What do you want?\n\n"
            "Negatives:\n"
            "• Handidi. — I don't want.\n"
            "• Haasi kufara. — He is not happy.\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Translate into Shona: 'The child is going to school.'"
        ),
    },
    ("Shona", "Reading"): {
        "goal": "Read and understand a Shona passage.",
        "content": (
            "🇿🇼 SHONA READING (Kuverenga)\n\n"
            "Read this short passage:\n\n"
            "'Kwaiva nemukomana ainzi Tinashe. Aigara nemhuri yake mumusha weZvimba. "
            "Mangwanani oga oga, aimuka kwaedza, osuka kumeso, odya kudya kwemangwanani, "
            "oenda kuchikoro. Aida zvikuru kudzidza. Akaedza nesimba muzvidzidzo zvake, "
            "uye akapasa bvunzo dzake nemazvakanaka.'\n\n"
            "Translation:\n"
            "There was a boy named Tinashe. He lived with his family in Zvimba village. "
            "Every morning, he woke up early, washed his face, ate breakfast, and went "
            "to school. He loved learning very much. He worked hard in his studies, and "
            "he passed his exams very well.\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "What does the passage say Tinashe did every morning?"
        ),
    },
    ("Shona", "Writing"): {
        "goal": "Write a short Shona composition.",
        "content": (
            "🇿🇼 SHONA WRITING (Kunyora)\n\n"
            "Writing a Shona composition (rondedzero):\n\n"
            "Structure:\n"
            "1. Musoro (Title)\n"
            "2. Sumo (Introduction) — introduce the topic\n"
            "3. Muviri (Body) — the main story, with details\n"
            "4. Mhedziso (Conclusion) — end the story\n\n"
            "Useful connectors:\n"
            "• Uye — and\n"
            "• Asi — but\n"
            "• Nekuti — because\n"
            "• Saka — so\n"
            "• Zvakare — also\n\n"
            "Example paragraph:\n"
            "'Ndakasvika kumba kwasekuru mangwanani. Takadya sadza nenyama. "
            "Mushure mekudya, takaenda kurwizi kunoredza. Takabata hove zhinji.'\n\n"
            "Translation: 'I arrived at my uncle's home in the morning. We ate sadza "
            "with meat. After eating, we went to the river to fish. We caught many fish.'\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Write a 5-sentence paragraph in Shona about your school day."
        ),
    },
    ("Shona", "Culture"): {
        "goal": "Learn about Shona traditions, customs, and proverbs.",
        "content": (
            "🇿🇼 SHONA CULTURE (Tsika nemagariro)\n\n"
            "Shona PROVERBS (Tsumo):\n"
            "• 'Kusaziva kufa.' — Not knowing is death (ignorance is dangerous).\n"
            "• 'Chara chimwe hachitswanyi inda.' — One finger cannot crush a louse "
            "(teamwork is important).\n"
            "• 'Rume rimwe harikombi churu.' — One man cannot surround an anthill.\n"
            "• 'Mwana asingachemi anofira mumbereko.' — A child who doesn't cry dies "
            "in a sling (speak up for yourself).\n\n"
            "CUSTOMS:\n"
            "• Kurova guva — ceremony for bringing back the spirit of a deceased person.\n"
            "• Lobola / Roora — bride price ceremony.\n"
            "• Bira — traditional ceremony for spirits.\n"
            "• Kugadzira — establishing a new homestead.\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Explain the meaning of the proverb 'Chara chimwe hachitswanyi inda'."
        ),
    },

    # ---------------- NDEBELE ----------------
    ("Ndebele", "Alphabet"): {
        "goal": "Learn the Ndebele alphabet and pronunciation.",
        "content": (
            "🇿🇼 NDEBELE ALPHABET (Izinhlamvu)\n\n"
            "Ndebele uses Latin letters but has special sounds:\n\n"
            "VOWELS: A, E, I, O, U\n\n"
            "SPECIAL CLICKS (unique to Ndebele and Zulu):\n"
            "• C — a dental click (like 'tsk tsk')\n"
            "• Q — an alveolar click\n"
            "• X — a lateral click\n\n"
            "Examples:\n"
            "• icici — earring\n"
            "• iqaqa — skunk\n"
            "• ixoxo — frog\n\n"
            "OTHER SPECIAL SOUNDS:\n"
            "• Dl — like 'dl' in 'handful'\n"
            "• Hl — a breathy 'hl'\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Write 3 Ndebele words that contain click sounds."
        ),
    },
    ("Ndebele", "Greetings"): {
        "goal": "Learn Ndebele greetings for all times of day.",
        "content": (
            "🇿🇼 NDEBELE GREETINGS (Ukuqalisa)\n\n"
            "Morning:\n"
            "• 'Lotjha' / 'Ivuka njani?' — Good morning\n\n"
            "Afternoon:\n"
            "• 'Litshonile' — Good afternoon\n\n"
            "Evening:\n"
            "• 'Kuhle ebusuku' — Good evening\n\n"
            "General:\n"
            "• 'Sawubona' — Hello (to one person)\n"
            "• 'Sanibonani' — Hello (to many)\n"
            "• 'Unjani?' — How are you?\n"
            "• 'Ngiyaphila, unjani?' — I am well, how are you?\n\n"
            "Goodbye:\n"
            "• 'Sala kuhle' — Stay well\n"
            "• 'Hamba kuhle' — Go well\n"
            "• 'Sizobonana' — We will see each other\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "How do you say 'Good morning' to a group of people?"
        ),
    },
    ("Ndebele", "Numbers"): {
        "goal": "Count in Ndebele from 1 to 100.",
        "content": (
            "🇿🇼 NDEBELE NUMBERS (Izinombolo)\n\n"
            "1 — Kunye\n"
            "2 — Kubili\n"
            "3 — Kuthathu\n"
            "4 — Kune\n"
            "5 — Kuhlanu\n"
            "6 — Isithupha\n"
            "7 — Isikhombisa\n"
            "8 — Isishiyagalombili\n"
            "9 — Isishiyagalolunye\n"
            "10 — Ishumi\n\n"
            "11 — Ishumi nanye\n"
            "12 — Ishumi nambili\n"
            "20 — Amashumi amabili\n"
            "30 — Amashumi amathathu\n"
            "50 — Amashumi amahlanu\n"
            "100 — Ikhulu\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Write the Ndebele words for 15, 30, and 100."
        ),
    },
    ("Ndebele", "Family"): {
        "goal": "Learn Ndebele family vocabulary.",
        "content": (
            "🇿🇼 NDEBELE FAMILY (Umndeni)\n\n"
            "Ubaba — Father\n"
            "Umama — Mother\n"
            "Indodana — Son\n"
            "Indodakazi — Daughter\n"
            "Umfowethu — My brother\n"
            "Udadwethu — My sister\n"
            "Umkhulu — Grandfather\n"
            "Ugogo — Grandmother\n"
            "Umamkhulu — Aunt\n"
            "Ubabomkhulu — Uncle\n"
            "Umzukulu — Grandchild\n"
            "Umkhwenyana — Son-in-law\n"
            "Umalokazana — Daughter-in-law\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "What is the Ndebele word for 'my grandfather'?"
        ),
    },
    ("Ndebele", "Nouns"): {
        "goal": "Understand Ndebele noun classes.",
        "content": (
            "🇿🇼 NDEBELE NOUNS (Amabizo)\n\n"
            "Ndebele nouns belong to classes with different prefixes:\n\n"
            "Class 1/2 (Umuntu/Abantu — People):\n"
            "• Um- / Aba-\n"
            "• umuntu (person) → abantu (people)\n"
            "• umfana (boy) → abafana (boys)\n\n"
            "Class 3/4 (Umuthi/Imithi — Trees):\n"
            "• Um- / Imi-\n"
            "• umuthi (tree) → imithi (trees)\n\n"
            "Class 7/8 (Isinto/Izinto — Things):\n"
            "• Isi- / Izi-\n"
            "• isikolo (school) → izikolo (schools)\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Give the plural form of 'umfana' and 'isikolo'."
        ),
    },
    ("Ndebele", "Verbs"): {
        "goal": "Learn Ndebele verb construction and tenses.",
        "content": (
            "🇿🇼 NDEBELE VERBS (Izenzo)\n\n"
            "Ndebele verbs use prefixes for subject and tense:\n\n"
            "Present tense:\n"
            "ngi- (I) + -dla (eat) + -a = ngidla (I eat)\n"
            "u- = udla (you eat)\n"
            "u- (he/she) = udla\n\n"
            "Past tense:\n"
            "nga- = ngadla (I ate)\n"
            "wa- = wadla (you ate)\n"
            "wa- = wadla (he ate)\n\n"
            "Future tense:\n"
            "ngi-zo- = ngizodla (I will eat)\n"
            "u-zo- = uzodla (you will eat)\n"
            "u-zo- = uzodla (he will eat)\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Change 'ngidla' (I eat) into past tense."
        ),
    },
    ("Ndebele", "Sentences"): {
        "goal": "Build correct Ndebele sentences.",
        "content": (
            "🇿🇼 NDEBELE SENTENCES (Imisho)\n\n"
            "Structure: Subject + Verb + Object\n\n"
            "Simple sentences:\n"
            "• Ngiyafunda. — I am reading.\n"
            "• Umfana uyadlala. — The boy is playing.\n"
            "• Umama uyapheka. — Mother is cooking.\n"
            "• Ubaba uyasebenza. — Father is working.\n\n"
            "Questions:\n"
            "• Uya ngaphi? — Where are you going?\n"
            "• Wenzani? — What are you doing?\n"
            "• Ufuna ini? — What do you want?\n\n"
            "Negatives:\n"
            "• Angifuni. — I don't want.\n"
            "• Akajabulile. — He is not happy.\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Translate into Ndebele: 'The child is going to school.'"
        ),
    },
    ("Ndebele", "Reading"): {
        "goal": "Read and understand a Ndebele passage.",
        "content": (
            "🇿🇼 NDEBELE READING (Ukufunda)\n\n"
            "Read this short passage:\n\n"
            "'Kwakukhona umfana ogama lakhe linguTinashe. Wayehlala nomndeni wakhe "
            "emzaneni waseZvimba. Njalo ekuseni wayevuka ekuseni, ageze ubuso, adle "
            "ukudla kwasekuseni, bese eya esikolo. Wayethanda ukufunda kakhulu. "
            "Wasebenza ngezandla zombili ezifundweni zakhe, futhi waphasa izivivinyo "
            "zakhe kuhle kakhulu.'\n\n"
            "Translation:\n"
            "There was a boy named Tinashe. He lived with his family in Zvimba village. "
            "Every morning he woke up early, washed his face, ate breakfast, and went "
            "to school. He loved learning very much. He worked hard in his studies, and "
            "he passed his exams very well.\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "What does the passage say Tinashe did every morning?"
        ),
    },
    ("Ndebele", "Writing"): {
        "goal": "Write a short Ndebele composition.",
        "content": (
            "🇿🇼 NDEBELE WRITING (Ukubhala)\n\n"
            "Structure of a Ndebele composition (isibhalo):\n"
            "1. Isihloko (Title)\n"
            "2. Isingeniso (Introduction)\n"
            "3. Umzimba (Body)\n"
            "4. Isiphetho (Conclusion)\n\n"
            "Useful connectors:\n"
            "• Futhi — and\n"
            "• Kodwa — but\n"
            "• Ngoba — because\n"
            "• Ngakho — so\n"
            "• Futhi — also\n\n"
            "Example:\n"
            "'Ngafika ekhaya likamalume ekuseni. Sadla ipapa nenyama. Emva kokudla, "
            "saya emfuleni siyodoba. Sabamba inhlanzi eziningi.'\n\n"
            "Translation: 'I arrived at my uncle's home in the morning. We ate pap and "
            "meat. After eating, we went to the river to fish. We caught many fish.'\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Write a 5-sentence paragraph in Ndebele about your school day."
        ),
    },
    ("Ndebele", "Culture"): {
        "goal": "Learn Ndebele traditions, customs, and proverbs.",
        "content": (
            "🇿🇼 NDEBELE CULTURE (Amasiko)\n\n"
            "Ndebele PROVERBS (Izaga):\n"
            "• 'Inyoni ayikhalelwa emoyeni.' — Don't plan a bird's flight for it.\n"
            "• 'Izandla ziyagezana.' — Hands wash each other (help each other).\n"
            "• 'Umuntu ngumuntu ngabantu.' — A person is a person through others.\n"
            "• 'Ukuphila kuwukulwa.' — Life is a struggle.\n\n"
            "CUSTOMS:\n"
            "• Umembeso — traditional wedding ceremony.\n"
            "• Ukubuyisa — ceremony to bring back a deceased person's spirit.\n"
            "• Umhlanga / Reed Dance — traditional ceremony.\n"
            "• Umgubho — celebration ceremony.\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Explain the meaning of the proverb 'Izandla ziyagezana'."
        ),
    },

    # ---------------- HERITAGE STUDIES ----------------
    ("Heritage Studies", "Zimbabwe History"): {
        "goal": "Understand Zimbabwe's history from ancient times to independence.",
        "content": (
            "🇿🇼 ZIMBABWE HISTORY\n\n"
            "ANCIENT ZIMBABWE:\n"
            "• The San (Bushmen) were the earliest inhabitants.\n"
            "• Bantu-speaking farmers arrived around 300 AD.\n"
            "• Great Zimbabwe was built between 1100–1450 AD.\n\n"
            "COLONIAL ERA:\n"
            "• 1890 — Pioneer Column arrived.\n"
            "• 1896–97 — First Chimurenga (resistance war).\n"
            "• 1923 — Southern Rhodesia became a self-governing colony.\n\n"
            "LIBERATION STRUGGLE:\n"
            "• 1966 — Second Chimurenga began.\n"
            "• 1979 — Lancaster House Agreement.\n"
            "• 18 April 1980 — Zimbabwe gained independence.\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Name the year Zimbabwe gained independence and the first Prime Minister."
        ),
    },
    ("Heritage Studies", "Culture"): {
        "goal": "Learn Zimbabwe's cultural traditions and values.",
        "content": (
            "🇿🇼 ZIMBABWE CULTURE\n\n"
            "Zimbabwe is home to diverse cultures:\n\n"
            "SHONA CULTURE:\n"
            "• Mbira music and traditional dance\n"
            "• Sadza as staple food\n"
            "• Respect for elders (kuremekedza vakuru)\n\n"
            "NDEBELE CULTURE:\n"
            "• Isitshwala as staple food\n"
            "• Traditional dance (isitshikitsha)\n"
            "• Strong family values (umndeni)\n\n"
            "SHARED VALUES:\n"
            "• Ubuntu / Hunhu — humanity, respect, dignity\n"
            "• Hospitality (kugamuchira vaeni)\n"
            "• Communal living (kubatana)\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Explain what 'Ubuntu' means in Zimbabwean culture."
        ),
    },
    ("Heritage Studies", "Citizenship"): {
        "goal": "Understand the rights and responsibilities of Zimbabwean citizens.",
        "content": (
            "🇿🇼 CITIZENSHIP\n\n"
            "RIGHTS of a Zimbabwean citizen:\n"
            "• Right to life and dignity\n"
            "• Right to education\n"
            "• Right to vote\n"
            "• Right to freedom of expression\n"
            "• Right to property\n\n"
            "RESPONSIBILITIES:\n"
            "• Obey the law\n"
            "• Pay taxes\n"
            "• Protect the environment\n"
            "• Respect other people's rights\n"
            "• Defend the country when needed\n\n"
            "NATIONAL SYMBOLS:\n"
            "• Zimbabwe Bird\n"
            "• National Flag (green, yellow, red, black, white)\n"
            "• National Anthem ('Simudzai Mureza wedu weZimbabwe')\n"
            "• Coat of Arms\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Name 2 rights and 2 responsibilities of a Zimbabwean citizen."
        ),
    },
    ("Heritage Studies", "Environment"): {
        "goal": "Learn about Zimbabwe's natural environment and conservation.",
        "content": (
            "🇿🇼 THE ENVIRONMENT\n\n"
            "Zimbabwe's natural features:\n"
            "• Victoria Falls (Mosi-oa-Tunya) — largest waterfall in the world\n"
            "• Great Zimbabwe Ruins\n"
            "• Lake Kariba — largest man-made lake\n"
            "• Matopos Hills\n\n"
            "WILDLIFE:\n"
            "• Big Five: Elephant, Lion, Leopard, Buffalo, Rhino\n"
            "• Hwange National Park, Mana Pools, Gonarezhou\n\n"
            "CONSERVATION:\n"
            "• Protecting endangered species (rhino, wild dog)\n"
            "• Fighting deforestation\n"
            "• Managing water resources\n"
            "• Environmental education\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Name the 'Big Five' animals and one major national park in Zimbabwe."
        ),
    },
    ("Heritage Studies", "National Symbols"): {
        "goal": "Learn Zimbabwe's national symbols and what they mean.",
        "content": (
            "🇿🇼 NATIONAL SYMBOLS\n\n"
            "THE ZIMBABWE BIRD:\n"
            "• Found at Great Zimbabwe Ruins\n"
            "• Represents ancient Zimbabwean civilization\n"
            "• Appears on the national flag and coat of arms\n\n"
            "THE FLAG:\n"
            "• Green — agriculture and vegetation\n"
            "• Yellow — mineral wealth (gold)\n"
            "• Red — blood shed during liberation\n"
            "• Black — African heritage\n"
            "• White triangle — peace\n"
            "• Zimbabwe Bird and red star inside triangle\n\n"
            "COAT OF ARMS:\n"
            "• Shows two kudu, a shield, and the Zimbabwe Bird\n"
            "• Motto: 'Unity, Freedom, Work'\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "What do the green, yellow, and red colours on the Zimbabwe flag represent?"
        ),
    },

    # ---------------- COMPUTER STUDIES ----------------
    ("Computer Studies", "Basic Computer"): {
        "goal": "Understand the parts of a computer.",
        "content": (
            "💻 BASIC COMPUTER\n\n"
            "A computer is an electronic device that processes data.\n\n"
            "MAIN PARTS:\n"
            "• CPU (Central Processing Unit) — the 'brain'\n"
            "• Monitor — displays information\n"
            "• Keyboard — input device\n"
            "• Mouse — pointing device\n"
            "• Hard drive — stores data\n"
            "• RAM — temporary memory\n\n"
            "TYPES:\n"
            "• Desktop — stationary\n"
            "• Laptop — portable\n"
            "• Tablet — touch screen\n"
            "• Smartphone — pocket-sized\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Name 3 input devices and 2 output devices of a computer."
        ),
    },
    ("Computer Studies", "Typing"): {
        "goal": "Learn touch typing and keyboard skills.",
        "content": (
            "⌨️ TOUCH TYPING\n\n"
            "HOME ROW:\n"
            "Left hand: A S D F\n"
            "Right hand: J K L ;\n\n"
            "The F and J keys have bumps to help you find home position without looking.\n\n"
            "FINGER ASSIGNMENTS:\n"
            "• Index fingers — F, G, H, J\n"
            "• Middle fingers — D, K\n"
            "• Ring fingers — S, L\n"
            "• Pinky fingers — A, ;\n\n"
            "TIPS:\n"
            "• Sit up straight\n"
            "• Wrists slightly raised\n"
            "• Don't look at the keyboard\n"
            "• Practice 15 minutes every day\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Which keys are on the 'home row' for the left hand?"
        ),
    },
    ("Computer Studies", "Internet"): {
        "goal": "Understand the internet and how to use it safely.",
        "content": (
            "🌐 THE INTERNET\n\n"
            "The internet is a global network of computers.\n\n"
            "KEY TERMS:\n"
            "• Browser — software to access the web (Chrome, Firefox)\n"
            "• URL — web address (e.g., google.com)\n"
            "• Website — collection of web pages\n"
            "• Search engine — Google, Bing\n"
            "• Email — electronic mail\n"
            "• Wi-Fi — wireless internet\n\n"
            "STAYING SAFE ONLINE:\n"
            "• Never share passwords\n"
            "• Don't talk to strangers\n"
            "• Be careful what you post\n"
            "• Use strong passwords\n"
            "• Log out of shared computers\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Name 3 things you should NEVER do online."
        ),
    },
    ("Computer Studies", "Software"): {
        "goal": "Learn the difference between system and application software.",
        "content": (
            "💾 SOFTWARE\n\n"
            "Software = programs that tell the computer what to do.\n\n"
            "SYSTEM SOFTWARE:\n"
            "• Operating systems (Windows, MacOS, Linux, Android)\n"
            "• Device drivers\n"
            "• Utilities (antivirus, disk cleanup)\n\n"
            "APPLICATION SOFTWARE:\n"
            "• Word processors (Microsoft Word)\n"
            "• Spreadsheets (Excel)\n"
            "• Presentation software (PowerPoint)\n"
            "• Web browsers\n"
            "• Games\n"
            "• Photo editors\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Give 3 examples of system software and 3 of application software."
        ),
    },
    ("Computer Studies", "Hardware"): {
        "goal": "Learn about computer hardware components.",
        "content": (
            "🔧 HARDWARE\n\n"
            "Hardware = the physical parts of a computer.\n\n"
            "INPUT DEVICES:\n"
            "• Keyboard, mouse, scanner, microphone, webcam\n\n"
            "OUTPUT DEVICES:\n"
            "• Monitor, printer, speaker, headphones\n\n"
            "STORAGE DEVICES:\n"
            "• Hard disk drive (HDD)\n"
            "• Solid state drive (SSD)\n"
            "• USB flash drive\n"
            "• CD/DVD\n"
            "• Memory card\n\n"
            "PROCESSING:\n"
            "• CPU — Central Processing Unit\n"
            "• GPU — Graphics Processing Unit\n"
            "• Motherboard — connects everything\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Name 3 input devices and 3 output devices."
        ),
    },
    ("Computer Studies", "Programming Basics"): {
        "goal": "Understand basic programming concepts.",
        "content": (
            "👨‍💻 PROGRAMMING BASICS\n\n"
            "Programming = writing instructions for a computer.\n\n"
            "POPULAR LANGUAGES:\n"
            "• Python — easy to learn\n"
            "• JavaScript — for websites\n"
            "• Java — for apps\n"
            "• C++ — for games and systems\n\n"
            "BASIC CONCEPTS:\n"
            "• Variable — stores a value (e.g., x = 5)\n"
            "• Condition — if/else statements\n"
            "• Loop — repeat instructions\n"
            "• Function — reusable block of code\n\n"
            "EXAMPLE (Python):\n"
            "```python\n"
            "name = 'Tinashe'\n"
            "if name == 'Tinashe':\n"
            "    print('Hello, Tinashe!')\n"
            "```\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "What is a variable in programming?"
        ),
    },

    # ---------------- AGRICULTURE ----------------
    ("Agriculture", "Crops"): {
        "goal": "Learn about crop farming in Zimbabwe.",
        "content": (
            "🌾 CROPS\n\n"
            "MAIN CROPS IN ZIMBABWE:\n"
            "• Maize — staple food\n"
            "• Wheat — bread\n"
            "• Tobacco — export crop\n"
            "• Cotton — textile industry\n"
            "• Sugarcane — sugar\n"
            "• Groundnuts — oil and food\n"
            "• Soya beans — oil and protein\n\n"
            "GROWING SEASON:\n"
            "• Rainy season: November to April\n"
            "• Planting: November–December\n"
            "• Harvesting: April–June\n\n"
            "REQUIREMENTS FOR CROPS:\n"
            "• Good soil\n"
            "• Water (rain or irrigation)\n"
            "• Sunlight\n"
            "• Fertilisers\n"
            "• Pest control\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Name the 3 most important crops in Zimbabwe and what they are used for."
        ),
    },
    ("Agriculture", "Livestock"): {
        "goal": "Learn about livestock farming.",
        "content": (
            "🐄 LIVESTOCK\n\n"
            "TYPES OF LIVESTOCK:\n"
            "• Cattle — beef, milk, hides\n"
            "• Goats — meat, milk\n"
            "• Sheep — wool, meat\n"
            "• Chickens — eggs, meat\n"
            "• Pigs — pork\n\n"
            "CATTLE BREEDS IN ZIMBABWE:\n"
            "• Mashona — indigenous, disease-resistant\n"
            "• Nkone — indigenous, hardy\n"
            "• Tuli — beef breed\n"
            "• Brahman — beef, heat-tolerant\n\n"
            "LIVESTOCK NEEDS:\n"
            "• Clean water\n"
            "• Good grazing or feed\n"
            "• Shelter\n"
            "• Veterinary care\n"
            "• Regular dipping (tick control)\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Name 3 indigenous cattle breeds in Zimbabwe and one advantage each has."
        ),
    },
    ("Agriculture", "Soil"): {
        "goal": "Understand soil types and soil health.",
        "content": (
            "🌱 SOIL\n\n"
            "TYPES OF SOIL:\n"
            "• Sandy soil — drains quickly, low nutrients\n"
            "• Clay soil — holds water, sticky\n"
            "• Loam soil — best for farming (mix of sand, clay, silt)\n\n"
            "SOIL COMPONENTS:\n"
            "• Minerals (from rocks)\n"
            "• Organic matter (dead plants and animals)\n"
            "• Water\n"
            "• Air\n"
            "• Living organisms\n\n"
            "SOIL HEALTH:\n"
            "• Add compost or manure\n"
            "• Rotate crops\n"
            "• Avoid over-farming\n"
            "• Prevent erosion\n"
            "• Test soil pH\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Which soil type is best for farming and why?"
        ),
    },
    ("Agriculture", "Farming Tools"): {
        "goal": "Learn common farming tools and their uses.",
        "content": (
            "🛠️ FARMING TOOLS\n\n"
            "HAND TOOLS:\n"
            "• Hoe (badza) — weeding, digging\n"
            "• Machete (panga) — cutting\n"
            "• Axe (demo) — chopping wood\n"
            "• Rake — gathering leaves\n"
            "• Watering can — watering plants\n"
            "• Wheelbarrow — carrying loads\n\n"
            "MACHINERY:\n"
            "• Tractor — ploughing, transport\n"
            "• Plough — turning soil\n"
            "• Harrow — breaking clods\n"
            "• Combine harvester — harvesting grain\n"
            "• Water pump — irrigation\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Name 5 hand tools used in farming and their uses."
        ),
    },
    ("Agriculture", "Weather and Farming"): {
        "goal": "Understand how weather affects farming.",
        "content": (
            "🌦️ WEATHER & FARMING\n\n"
            "IMPORTANCE OF WEATHER:\n"
            "• Determines planting time\n"
            "• Affects crop growth\n"
            "• Affects livestock health\n"
            "• Impacts harvest quality\n\n"
            "SEASONS IN ZIMBABWE:\n"
            "• Rainy season (Nov–Apr) — planting\n"
            "• Cool dry season (May–Aug) — harvesting\n"
            "• Hot dry season (Sep–Oct) — land preparation\n\n"
            "WEATHER HAZARDS:\n"
            "• Drought — crop failure\n"
            "• Floods — waterlogging\n"
            "• Frost — kills crops\n"
            "• Hailstorms — damage plants\n\n"
            "FARMER ACTIONS:\n"
            "• Plant early with first rains\n"
            "• Use irrigation\n"
            "• Use drought-resistant seeds\n"
            "• Keep weather records\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "How does drought affect farming and what can farmers do?"
        ),
    },
    ("Agriculture", "Farm Management"): {
        "goal": "Learn how to manage a successful farm.",
        "content": (
            "🚜 FARM MANAGEMENT\n\n"
            "KEY AREAS:\n"
            "• Planning — what to grow/raise\n"
            "• Budgeting — money in and out\n"
            "• Labour — workers needed\n"
            "• Equipment — tools and machinery\n"
            "• Records — keeping track\n\n"
            "RECORD KEEPING:\n"
            "• Planting dates\n"
            "• Harvest yields\n"
            "• Costs (seeds, fertiliser, labour)\n"
            "• Sales income\n"
            "• Profits and losses\n\n"
            "SUSTAINABLE FARMING:\n"
            "• Crop rotation\n"
            "• Composting\n"
            "• Water conservation\n"
            "• Integrated pest management\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Why is record keeping important in farming?"
        ),
    },

    # ---------------- COMMERCE ----------------
    ("Commerce", "Trade"): {
        "goal": "Understand the meaning and types of trade.",
        "content": (
            "💱 TRADE\n\n"
            "Trade = buying and selling of goods and services.\n\n"
            "TYPES:\n"
            "• Home trade — within one country\n"
            "• Foreign trade — between countries\n"
            "• Wholesale — selling in bulk\n"
            "• Retail — selling to consumers\n\n"
            "CHANNELS OF DISTRIBUTION:\n"
            "Producer → Wholesaler → Retailer → Consumer\n\n"
            "IMPORTANCE:\n"
            "• Provides goods to consumers\n"
            "• Creates jobs\n"
            "• Earns foreign currency\n"
            "• Encourages production\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Name 4 stages in the channel of distribution of goods."
        ),
    },
    ("Commerce", "Business"): {
        "goal": "Learn about business organisations.",
        "content": (
            "🏢 BUSINESS ORGANISATIONS\n\n"
            "TYPES:\n"
            "• Sole trader — owned by one person\n"
            "• Partnership — 2–20 people\n"
            "• Private limited company (Pvt Ltd) — shareholders\n"
            "• Public limited company (Ltd) — shares on stock exchange\n"
            "• Co-operative — owned by members\n\n"
            "CHOOSING A BUSINESS TYPE:\n"
            "• Amount of capital\n"
            "• Risk tolerance\n"
            "• Need for control\n"
            "• Legal requirements\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Give 2 advantages and 2 disadvantages of a sole trader business."
        ),
    },
    ("Commerce", "Money"): {
        "goal": "Understand the functions and types of money.",
        "content": (
            "💰 MONEY\n\n"
            "FUNCTIONS:\n"
            "• Medium of exchange\n"
            "• Store of value\n"
            "• Unit of account\n"
            "• Standard of deferred payment\n\n"
            "TYPES:\n"
            "• Coins\n"
            "• Banknotes\n"
            "• Electronic money (EcoCash, bank cards)\n"
            "• Mobile money\n\n"
            "QUALITIES OF GOOD MONEY:\n"
            "• Durability\n"
            "• Portability\n"
            "• Divisibility\n"
            "• Acceptability\n"
            "• Scarcity\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Name 4 qualities of good money."
        ),
    },
    ("Commerce", "Banking"): {
        "goal": "Learn about banking services in Zimbabwe.",
        "content": (
            "🏦 BANKING\n\n"
            "TYPES OF BANKS:\n"
            "• Commercial banks (CBZ, Steward, ZB)\n"
            "• Building societies\n"
            "• Merchant banks\n"
            "• Reserve Bank of Zimbabwe (RBZ) — central bank\n\n"
            "SERVICES OFFERED:\n"
            "• Savings accounts\n"
            "• Current accounts\n"
            "• Loans and overdrafts\n"
            "• Foreign exchange\n"
            "• Mobile banking\n\n"
            "CENTRAL BANK FUNCTIONS:\n"
            "• Issues currency\n"
            "• Controls money supply\n"
            "• Regulates banks\n"
            "• Lender of last resort\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Name 4 services offered by commercial banks."
        ),
    },
    ("Commerce", "Marketing"): {
        "goal": "Understand marketing and its importance.",
        "content": (
            "📢 MARKETING\n\n"
            "Marketing = all activities involved in getting goods from producer to consumer.\n\n"
            "THE 4 Ps:\n"
            "• Product — what you sell\n"
            "• Price — how much\n"
            "• Place — where sold\n"
            "• Promotion — how advertised\n\n"
            "PROMOTION METHODS:\n"
            "• Advertising (TV, radio, billboards)\n"
            "• Social media\n"
            "• Sales promotions\n"
            "• Personal selling\n"
            "• Public relations\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Explain what the 4 Ps of marketing mean."
        ),
    },

    # ---------------- RELIGIOUS STUDIES ----------------
    ("Religious Studies", "World Religions"): {
        "goal": "Learn about major world religions.",
        "content": (
            "🌍 WORLD RELIGIONS\n\n"
            "MAJOR RELIGIONS:\n"
            "• Christianity — 2.4 billion followers\n"
            "• Islam — 1.9 billion followers\n"
            "• Hinduism — 1.2 billion followers\n"
            "• Buddhism — 500 million followers\n"
            "• Judaism — 15 million followers\n"
            "• African Traditional Religion — millions\n\n"
            "COMMON VALUES:\n"
            "• Love and compassion\n"
            "• Honesty and justice\n"
            "• Respect for life\n"
            "• Service to others\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Name 4 major world religions and one core belief of each."
        ),
    },
    ("Religious Studies", "African Traditional Religion"): {
        "goal": "Understand African Traditional Religion (ATR).",
        "content": (
            "🌿 AFRICAN TRADITIONAL RELIGION\n\n"
            "KEY BELIEFS:\n"
            "• Belief in a Supreme Being (Mwari / uMvelinqangi)\n"
            "• Belief in ancestral spirits (vadzimu / amadlozi)\n"
            "• Belief in life after death\n"
            "• Respect for nature\n\n"
            "PRACTICES:\n"
            "• Prayer and offerings\n"
            "• Traditional ceremonies (bira)\n"
            "• Consulting spirit mediums\n"
            "• Rites of passage (birth, initiation, marriage, death)\n\n"
            "VALUES:\n"
            "• Respect for elders\n"
            "• Community living\n"
            "• Care for the environment\n"
            "• Hospitality\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Explain the role of ancestors in African Traditional Religion."
        ),
    },
    ("Religious Studies", "Christianity"): {
        "goal": "Learn about Christianity.",
        "content": (
            "✝️ CHRISTIANITY\n\n"
            "CORE BELIEFS:\n"
            "• Belief in one God (Trinity: Father, Son, Holy Spirit)\n"
            "• Jesus Christ is the Son of God\n"
            "• Salvation through faith in Christ\n"
            "• The Bible is the holy book\n\n"
            "MAJOR DENOMINATIONS:\n"
            "• Catholic\n"
            "• Protestant (Anglican, Methodist, Baptist)\n"
            "• Pentecostal\n"
            "• Orthodox\n\n"
            "PRACTICES:\n"
            "• Prayer\n"
            "• Baptism\n"
            "• Holy Communion\n"
            "• Bible study\n"
            "• Charity and service\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Name 3 core beliefs of Christianity."
        ),
    },
    ("Religious Studies", "Islam"): {
        "goal": "Learn about Islam.",
        "content": (
            "☪️ ISLAM\n\n"
            "CORE BELIEFS:\n"
            "• Belief in one God (Allah)\n"
            "• Muhammad is the prophet\n"
            "• The Qur'an is the holy book\n"
            "• Belief in angels, prophets, judgement day\n\n"
            "THE FIVE PILLARS:\n"
            "1. Shahada — declaration of faith\n"
            "2. Salah — prayer 5 times a day\n"
            "3. Zakat — giving to charity\n"
            "4. Sawm — fasting during Ramadan\n"
            "5. Hajj — pilgrimage to Mecca\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Name and explain the 5 Pillars of Islam."
        ),
    },
    ("Religious Studies", "Ethics"): {
        "goal": "Understand moral and ethical principles.",
        "content": (
            "⚖️ ETHICS\n\n"
            "Ethics = moral principles that guide behaviour.\n\n"
            "COMMON VALUES:\n"
            "• Honesty — telling the truth\n"
            "• Integrity — doing the right thing\n"
            "• Compassion — caring for others\n"
            "• Justice — fairness\n"
            "• Respect — treating others well\n\n"
            "APPLIED ETHICS:\n"
            "• Medical ethics (life, death)\n"
            "• Business ethics (honesty, fair trade)\n"
            "• Environmental ethics (caring for the planet)\n"
            "• Digital ethics (online behaviour)\n\n"
            "📄 REAL EXAM QUESTION:\n"
            "Why is honesty important in everyday life?"
        ),
    },
}

# ============================================================
# Insert or update lessons in the curriculum
# ============================================================
print("📥 Inserting real lesson content...\n")

inserted = 0
updated = 0
failed = 0

for (subject, topic), lesson_data in REAL_LESSONS.items():
    # Find all grades that have this subject+topic combination
    c.execute("""
        SELECT id, grade_form FROM curriculum
        WHERE subject = ? AND topic = ?
    """, (subject, topic))
    rows = c.fetchall()

    if not rows:
        print(f"   ⚠️ Not in curriculum: {subject} — {topic}")
        failed += 1
        continue

    for row_id, grade_form in rows:
        try:
            c.execute("""
                UPDATE curriculum
                SET lesson_goal = ?, content = ?
                WHERE id = ?
            """, (lesson_data["goal"], lesson_data["content"], row_id))
            updated += 1
        except Exception as e:
            print(f"   ❌ Error updating {subject}/{topic}: {e}")
            failed += 1

    print(f"   ✅ {subject} — {topic}: updated in {len(rows)} grade(s)")

conn.commit()

print("\n" + "="*70)
print("📊 PHASE 2 COMPLETE")
print("="*70)
print(f"\n   ✅ Updated lessons: {updated}")
print(f"   ⚠️ Failed/skipped:  {failed}")

c.execute("SELECT COUNT(*) FROM curriculum")
print(f"\n   📚 Total lessons: {c.fetchone()[0]}")

c.execute("SELECT COUNT(*) FROM curriculum WHERE length(content) > 300")
rich = c.fetchone()[0]
print(f"   📖 Rich-content lessons (>300 chars): {rich}")

conn.close()

print("\n" + "="*70)
print("✅ PHASE 2 COMPLETE — REAL CONTENT LOADED")
print("="*70)
print("\n📌 NEXT STEPS:")
print("   1. Restart the student server:")
print("      python student_server.py")
print("   2. Open the playbook and test a Shona/Ndebele lesson:")
print("      http://127.0.0.1:5001/student/1/playbook/Shona/Greetings")
print("   3. Check the content quality in your browser.")
print("\n📌 THEN: Phase 3 — Weekly assignments")
print("="*70 + "\n")
