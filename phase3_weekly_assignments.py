import sqlite3
import datetime
import random

DB = "digital_classroom.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

print("\n" + "="*70)
print("📝 PHASE 3 — WEEKLY ASSIGNMENTS")
print("="*70 + "\n")

# ============================================================
# STEP 1: Create the assignments tables
# ============================================================
print("1️⃣  Creating assignment tables...")

c.execute("""
    CREATE TABLE IF NOT EXISTS weekly_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        week_number INTEGER NOT NULL,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        grade_form TEXT NOT NULL,
        total_questions INTEGER DEFAULT 15,
        score INTEGER DEFAULT 0,
        percentage REAL DEFAULT 0,
        completed INTEGER DEFAULT 0,
        generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        completed_at TEXT,
        UNIQUE(student_id, week_number, subject, topic)
    )
""")
print("   ✅ weekly_assignments table ready")

c.execute("""
    CREATE TABLE IF NOT EXISTS weekly_assignment_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER NOT NULL,
        question_number INTEGER NOT NULL,
        question TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        student_answer TEXT,
        marks INTEGER DEFAULT 1,
        awarded_marks INTEGER DEFAULT 0,
        topic TEXT,
        difficulty TEXT DEFAULT 'medium',
        FOREIGN KEY (assignment_id) REFERENCES weekly_assignments(id)
    )
""")
print("   ✅ weekly_assignment_questions table ready")

# ============================================================
# STEP 2: Question bank per topic
# ============================================================
print("\n2️⃣  Building question bank...")

QUESTION_BANK = {
    # ================ MATHS ================
    ("Maths", "Fractions"): [
        ("What is 1/2 + 1/4?", "3/4"),
        ("What is 2/5 + 1/5?", "3/5"),
        ("Simplify 6/8.", "3/4"),
        ("What is 1/3 of 18?", "6"),
        ("Convert 0.5 to a fraction.", "1/2"),
        ("Add: 3/7 + 2/7.", "5/7"),
        ("Subtract: 5/6 - 1/6.", "4/6 = 2/3"),
        ("What is the numerator in 3/4?", "3"),
        ("Compare 1/2 and 1/3. Which is larger?", "1/2"),
        ("Find 1/4 of 20.", "5"),
        ("Simplify 10/15.", "2/3"),
        ("What is 2/3 + 1/6?", "5/6"),
        ("Subtract 1/2 from 3/4.", "1/4"),
        ("Convert 1/5 to a decimal.", "0.2"),
        ("Is 3/6 equal to 1/2?", "Yes"),
    ],
    ("Maths", "Decimals"): [
        ("What is 2.5 + 1.3?", "3.8"),
        ("What is 6.8 - 2.4?", "4.4"),
        ("Convert 0.25 to a fraction.", "1/4"),
        ("What is 4.5 + 0.75?", "5.25"),
        ("Round 4.67 to one decimal place.", "4.7"),
        ("What is 3.2 × 10?", "32"),
        ("What is 9.6 ÷ 2?", "4.8"),
        ("Compare 0.5 and 0.45. Which is larger?", "0.5"),
        ("Write 3.05 in words.", "Three point zero five"),
        ("What is 1.1 + 2.2 + 3.3?", "6.6"),
        ("Subtract 0.7 from 1.0.", "0.3"),
        ("Convert 1/2 to a decimal.", "0.5"),
        ("What is 10 - 4.5?", "5.5"),
        ("What is 0.9 + 0.1?", "1.0"),
        ("Is 0.7 greater than 0.65?", "Yes"),
    ],
    ("Maths", "Algebra"): [
        ("Solve for x: x + 5 = 12.", "x = 7"),
        ("Solve for x: 2x = 18.", "x = 9"),
        ("Solve for x: 3x + 4 = 19.", "x = 5"),
        ("Simplify: 3x + 2x.", "5x"),
        ("Simplify: 6y - 2y.", "4y"),
        ("Expand: 3(x + 4).", "3x + 12"),
        ("Solve: x - 7 = 15.", "x = 22"),
        ("What is 5x + 3 when x = 2?", "13"),
        ("Simplify: 4a + 3a - 2a.", "5a"),
        ("Expand: 2(2x + 3).", "4x + 6"),
        ("Solve: 4x = 24.", "x = 6"),
        ("Solve: 2x + 1 = 9.", "x = 4"),
        ("Simplify: 7m - 3m + m.", "5m"),
        ("What is 2x - 3 when x = 5?", "7"),
        ("Solve: x/2 = 6.", "x = 12"),
    ],

    # ================ ENGLISH ================
    ("English", "Grammar"): [
        ("What is a noun?", "A naming word (person, place, thing)"),
        ("What is a verb?", "An action or state word"),
        ("What is an adjective?", "A word that describes a noun"),
        ("What is an adverb?", "A word that describes a verb"),
        ("Identify the noun in: 'The dog ran.'", "dog"),
        ("Identify the verb in: 'She sings.'", "sings"),
        ("Identify the adjective in: 'The tall tree.'", "tall"),
        ("What is a pronoun?", "A word that replaces a noun"),
        ("Give one example of a pronoun.", "he/she/it/they/we"),
        ("What is a conjunction?", "A word that joins sentences or clauses"),
        ("Give one example of a conjunction.", "and/but/or/because"),
        ("Identify the pronoun in: 'They are playing.'", "They"),
        ("What is the past tense of 'run'?", "ran"),
        ("What is the plural of 'child'?", "children"),
        ("What is the past tense of 'eat'?", "ate"),
    ],
    ("English", "Comprehension"): [
        ("What does 'comprehension' mean?", "Understanding what you read"),
        ("What should you do first when reading a passage?", "Read it once to get the general idea"),
        ("Why should you read questions before reading a passage?", "To know what to look for"),
        ("How many times should you read a passage?", "At least twice"),
        ("What is a 'main idea'?", "The most important point of a passage"),
        ("What is a 'supporting detail'?", "Information that explains the main idea"),
        ("What is 'inference'?", "A conclusion based on evidence in the text"),
        ("True or false: You should copy sentences directly when answering.", "False"),
        ("Why is it important to answer in your own words?", "Shows understanding"),
        ("What is a 'title'?", "The name of a passage or book"),
        ("What is a 'paragraph'?", "A group of sentences about one idea"),
        ("What is the purpose of a 'summary'?", "To briefly state the main points"),
        ("What does 'skim' mean?", "Read quickly to get the general idea"),
        ("What does 'scan' mean?", "Look for specific information"),
        ("What is a 'heading'?", "A title for a section of text"),
    ],

    # ================ SCIENCE ================
    ("Science", "Living Things"): [
        ("What are the 7 characteristics of living things?", "Movement, respiration, sensitivity, growth, reproduction, excretion, nutrition"),
        ("What is a cell?", "The basic unit of life"),
        ("What is the control centre of a cell?", "The nucleus"),
        ("What is the cell wall made of?", "Cellulose"),
        ("What are chloroplasts for?", "Photosynthesis"),
        ("Do animal cells have chloroplasts?", "No"),
        ("Do plant cells have a large vacuole?", "Yes"),
        ("What is cytoplasm?", "Jelly-like substance inside the cell"),
        ("What is the function of the cell membrane?", "Controls what enters and leaves the cell"),
        ("Name 3 organelles found in plant cells.", "Nucleus, cytoplasm, cell membrane, chloroplasts, vacuole, cell wall"),
        ("What is a unicellular organism?", "An organism made of one cell"),
        ("Give one example of a unicellular organism.", "Amoeba"),
        ("What is a multicellular organism?", "An organism made of many cells"),
        ("Name 2 systems in the human body.", "Digestive, respiratory, circulatory"),
        ("What is photosynthesis?", "Process where plants make food using sunlight"),
    ],
    ("Science", "Matter"): [
        ("What are the 3 states of matter?", "Solid, liquid, gas"),
        ("Which state has a fixed shape?", "Solid"),
        ("Which state takes the shape of its container?", "Liquid"),
        ("Which state has particles far apart?", "Gas"),
        ("What is melting?", "Solid → Liquid"),
        ("What is freezing?", "Liquid → Solid"),
        ("What is evaporation?", "Liquid → Gas"),
        ("What is condensation?", "Gas → Liquid"),
        ("Give an example of a solid.", "Ice, wood, metal"),
        ("Give an example of a liquid.", "Water, oil, milk"),
        ("Give an example of a gas.", "Air, oxygen, steam"),
        ("What happens to ice when heated?", "It melts into water"),
        ("What is the boiling point of water?", "100°C"),
        ("What is the freezing point of water?", "0°C"),
        ("Is air matter?", "Yes, it takes up space and has mass"),
    ],

    # ================ GEOGRAPHY ================
    ("Geography", "Rivers"): [
        ("What is a river?", "A natural stream of water flowing to a sea or lake"),
        ("Name the 3 stages of a river.", "Youthful, mature, old age"),
        ("What is a meander?", "A bend in a river"),
        ("What is erosion?", "Wearing away of land by water/wind/ice"),
        ("What is deposition?", "Dropping of sediment when energy decreases"),
        ("What is a floodplain?", "Flat land beside a river"),
        ("What is a delta?", "Land formed at a river's mouth"),
        ("What is a tributary?", "A smaller stream joining a larger river"),
        ("What is a source?", "Where a river begins"),
        ("What is a mouth?", "Where a river meets a sea or lake"),
        ("What is a gorge?", "A narrow, steep valley cut by a river"),
        ("What is a waterfall?", "Where a river drops vertically over hard rock"),
        ("Name 2 causes of river flooding.", "Heavy rain, deforestation"),
        ("What is a levee?", "A raised bank beside a river"),
        ("What is hydraulic action?", "Force of water against river banks"),
    ],
    ("Geography", "Climate"): [
        ("What is weather?", "Condition of the atmosphere at a specific time and place"),
        ("What is climate?", "Average weather over a long period"),
        ("Name 3 elements of weather.", "Temperature, rainfall, wind"),
        ("What is the hottest month in Zimbabwe?", "October or November"),
        ("Which part of Zimbabwe is the wettest?", "Eastern Highlands"),
        ("What is the coldest part of Zimbabwe?", "Eastern Highlands"),
        ("What is the Lowveld climate like?", "Hot and dry"),
        ("What is the Highveld climate like?", "Cool and wet"),
        ("What is a rain shadow?", "Dry area on the leeward side of a mountain"),
        ("What is drought?", "Prolonged period of low rainfall"),
        ("Name 2 effects of climate change.", "Drought, floods"),
        ("What is temperature measured in?", "Degrees Celsius (°C)"),
        ("What is rainfall measured in?", "Millimetres (mm)"),
        ("What is the instrument for measuring rainfall?", "Rain gauge"),
        ("What is the instrument for measuring temperature?", "Thermometer"),
    ],

    # ================ HISTORY ================
    ("History", "Early Zimbabwe"): [
        ("Who were the earliest inhabitants of Zimbabwe?", "The San (Bushmen)"),
        ("What did the San do for food?", "Hunted and gathered"),
        ("When did Bantu-speaking people arrive in Zimbabwe?", "Around 300 AD"),
        ("What was the Iron Age?", "Period when people used iron tools"),
        ("Where were iron tools made in Zimbabwe?", "Various sites including Great Zimbabwe area"),
        ("What was Great Zimbabwe?", "A major ancient city in Zimbabwe"),
        ("When was Great Zimbabwe built?", "1100–1450 AD"),
        ("What was Great Zimbabwe made of?", "Stone walls (no mortar)"),
        ("What was traded at Great Zimbabwe?", "Gold, ivory, copper"),
        ("Who did Great Zimbabwe trade with?", "Swahili and Arab traders"),
        ("What caused the decline of Great Zimbabwe?", "Trade route changes, environmental factors"),
        ("What is the Zimbabwe Bird?", "A stone sculpture found at Great Zimbabwe"),
        ("What was the Kingdom of Mutapa?", "A successor state to Great Zimbabwe"),
        ("Who was Mzilikazi?", "Founder of the Ndebele kingdom in Zimbabwe"),
        ("When did the Ndebele settle in Zimbabwe?", "Around 1838"),
    ],

    # ================ BIOLOGY ================
    ("Biology", "Cells"): [
        ("What is a cell?", "Basic unit of life"),
        ("What is the nucleus?", "Control centre of the cell"),
        ("What is cytoplasm?", "Jelly-like substance filling the cell"),
        ("What is the cell membrane?", "Outer layer controlling entry and exit"),
        ("What is the cell wall?", "Rigid outer layer of plant cells"),
        ("What are chloroplasts?", "Green structures for photosynthesis"),
        ("Do animal cells have chloroplasts?", "No"),
        ("What is a vacuole?", "Storage space in a cell"),
        ("What is the function of mitochondria?", "Release energy from food"),
        ("What is a unicellular organism?", "Made of one cell"),
        ("Give 2 examples of unicellular organisms.", "Amoeba, bacteria"),
        ("What is a multicellular organism?", "Made of many cells"),
        ("What is diffusion?", "Movement from high to low concentration"),
        ("What is osmosis?", "Movement of water across a membrane"),
        ("What are enzymes?", "Biological catalysts that speed up reactions"),
    ],

    # ================ CHEMISTRY ================
    ("Chemistry", "Atoms"): [
        ("What is an atom?", "Smallest unit of an element"),
        ("What is an element?", "Substance made of one type of atom"),
        ("What is a compound?", "Substance made of 2+ elements chemically joined"),
        ("What is the chemical symbol for hydrogen?", "H"),
        ("What is the chemical symbol for oxygen?", "O"),
        ("What is the chemical symbol for carbon?", "C"),
        ("What is the chemical symbol for sodium?", "Na"),
        ("What is the chemical symbol for chlorine?", "Cl"),
        ("What is the atomic number?", "Number of protons in an atom"),
        ("What is the periodic table?", "Chart of all known elements"),
        ("What is a group in the periodic table?", "Vertical column"),
        ("What is a period?", "Horizontal row"),
        ("Name an element in Group 1.", "Sodium, Lithium, Potassium"),
        ("Name an element in Group 0.", "Helium, Neon, Argon"),
        ("What is the charge of a proton?", "Positive"),
    ],

    # ================ PHYSICS ================
    ("Physics", "Motion"): [
        ("What is speed?", "Distance travelled per unit time"),
        ("What is the formula for speed?", "Speed = Distance ÷ Time"),
        ("What is velocity?", "Speed in a given direction"),
        ("What is acceleration?", "Rate of change of velocity"),
        ("What is the unit of speed?", "m/s or km/h"),
        ("What is the unit of acceleration?", "m/s²"),
        ("A car travels 100 km in 2 hours. What is its speed?", "50 km/h"),
        ("What is the SI unit for distance?", "Metre (m)"),
        ("What is the SI unit for time?", "Second (s)"),
        ("What is the difference between speed and velocity?", "Velocity has direction"),
        ("What is uniform motion?", "Motion at constant speed"),
        ("What is deceleration?", "Negative acceleration (slowing down)"),
        ("What is the acceleration due to gravity?", "9.8 m/s²"),
        ("A ball is thrown upward. What happens to its speed?", "It decreases until it stops, then falls"),
        ("What is a scalar quantity?", "A quantity with magnitude only"),
    ],

    # ================ SHONA ================
    ("Shona", "Greetings"): [
        ("How do you say 'Good morning' in Shona?", "Mangwanani"),
        ("How do you say 'Good afternoon' in Shona?", "Masikati"),
        ("How do you say 'Good evening' in Shona?", "Manheru"),
        ("How do you say 'Hello' (respectful) in Shona?", "Mhoroi"),
        ("How do you say 'How are you?' in Shona?", "Wakadini?"),
        ("How do you say 'I am fine' in Shona?", "Ndiripo"),
        ("How do you say 'Goodbye' (to one staying) in Shona?", "Chisarai"),
        ("How do you say 'Go well' in Shona?", "Fambai zvakanaka"),
        ("How do you say 'Stay well' in Shona?", "Sara zvakanaka"),
        ("How do you greet a group of people in Shona?", "Mhoroi vanhu vose"),
        ("How do you say 'Thank you' in Shona?", "Ndatenda / Tatenda"),
        ("How do you say 'Please' in Shona?", "Ndapota"),
        ("How do you say 'Yes' in Shona?", "Ehe / Hongu"),
        ("How do you say 'No' in Shona?", "Aiwa / Kwete"),
        ("How do you say 'Excuse me' in Shona?", "Pamusoroi"),
    ],
    ("Shona", "Numbers"): [
        ("What is 1 in Shona?", "Motsi / Poshi"),
        ("What is 2 in Shona?", "Piri"),
        ("What is 3 in Shona?", "Tatu"),
        ("What is 4 in Shona?", "China"),
        ("What is 5 in Shona?", "Shanu"),
        ("What is 6 in Shona?", "Tanhatu"),
        ("What is 7 in Shona?", "Nomwe"),
        ("What is 8 in Shona?", "Sere"),
        ("What is 9 in Shona?", "Pfumbamwe"),
        ("What is 10 in Shona?", "Gumi"),
        ("What is 20 in Shona?", "Makumi maviri"),
        ("What is 50 in Shona?", "Makumi mashanu"),
        ("What is 100 in Shona?", "Zana"),
        ("What is 11 in Shona?", "Gumi neimwe"),
        ("What is 25 in Shona?", "Makumi maviri neshanu"),
    ],

    # ================ NDEBELE ================
    ("Ndebele", "Greetings"): [
        ("How do you say 'Hello' (one person) in Ndebele?", "Sawubona"),
        ("How do you say 'Hello' (many people) in Ndebele?", "Sanibonani"),
        ("How do you say 'How are you?' in Ndebele?", "Unjani?"),
        ("How do you say 'I am fine' in Ndebele?", "Ngiyaphila"),
        ("How do you say 'Good morning' in Ndebele?", "Lotjha / Ivuka njani?"),
        ("How do you say 'Good afternoon' in Ndebele?", "Litshonile"),
        ("How do you say 'Good evening' in Ndebele?", "Kuhle ebusuku"),
        ("How do you say 'Goodbye' (to one staying) in Ndebele?", "Sala kuhle"),
        ("How do you say 'Go well' in Ndebele?", "Hamba kuhle"),
        ("How do you say 'See you later' in Ndebele?", "Sizobonana"),
        ("How do you say 'Thank you' in Ndebele?", "Ngiyabonga"),
        ("How do you say 'Please' in Ndebele?", "Ngicela"),
        ("How do you say 'Yes' in Ndebele?", "Yebo"),
        ("How do you say 'No' in Ndebele?", "Cha"),
        ("How do you say 'Excuse me' in Ndebele?", "Uxolo"),
    ],
    ("Ndebele", "Numbers"): [
        ("What is 1 in Ndebele?", "Kunye"),
        ("What is 2 in Ndebele?", "Kubili"),
        ("What is 3 in Ndebele?", "Kuthathu"),
        ("What is 4 in Ndebele?", "Kune"),
        ("What is 5 in Ndebele?", "Kuhlanu"),
        ("What is 6 in Ndebele?", "Isithupha"),
        ("What is 7 in Ndebele?", "Isikhombisa"),
        ("What is 8 in Ndebele?", "Isishiyagalombili"),
        ("What is 9 in Ndebele?", "Isishiyagalolunye"),
        ("What is 10 in Ndebele?", "Ishumi"),
        ("What is 20 in Ndebele?", "Amashumi amabili"),
        ("What is 50 in Ndebele?", "Amashumi amahlanu"),
        ("What is 100 in Ndebele?", "Ikhulu"),
        ("What is 11 in Ndebele?", "Ishumi nanye"),
        ("What is 25 in Ndebele?", "Amashumi amabili nahlanu"),
    ],

    # ================ AGRICULTURE ================
    ("Agriculture", "Crops"): [
        ("What is the staple crop in Zimbabwe?", "Maize"),
        ("Name 3 main crops in Zimbabwe.", "Maize, tobacco, cotton"),
        ("What is tobacco used for?", "Export (cigarettes) and foreign currency"),
        ("What is sugarcane used for?", "Making sugar"),
        ("When is the rainy season in Zimbabwe?", "November to April"),
        ("When is maize usually planted?", "November–December"),
        ("When is maize harvested?", "April–June"),
        ("What does 'cash crop' mean?", "Crop grown for sale, not just food"),
        ("Name 2 conditions needed for crops to grow.", "Water, sunlight"),
        ("What is irrigation?", "Artificial watering of crops"),
        ("Name 3 fertilisers used in farming.", "NPK, ammonium nitrate, manure"),
        ("What is crop rotation?", "Planting different crops in sequence"),
        ("Name 1 disease that affects maize.", "Maize streak virus"),
        ("What is a pest?", "Organism that damages crops"),
        ("What is a herbicide?", "Chemical that kills weeds"),
    ],
    ("Agriculture", "Livestock"): [
        ("Name 3 types of livestock in Zimbabwe.", "Cattle, goats, chickens"),
        ("Name 2 indigenous cattle breeds in Zimbabwe.", "Mashona, Nkone"),
        ("What are cattle used for?", "Beef, milk, hides"),
        ("What are chickens used for?", "Eggs, meat"),
        ("What is a 'dip tank' for?", "Tick control on cattle"),
        ("What is 'grazing'?", "Feeding livestock on grass"),
        ("What is a 'paddock'?", "Fenced area for grazing animals"),
        ("Name 2 diseases affecting cattle.", "Foot and mouth, anthrax"),
        ("What is 'vaccination'?", "Injecting animals to prevent disease"),
        ("Name 3 needs of livestock.", "Water, feed, shelter"),
        ("What is a 'culling'?", "Removing weak animals from a herd"),
        ("What is a 'bull'?", "Male cattle used for breeding"),
        ("What is a 'heifer'?", "Young female cow that has not calved"),
        ("What is 'lambing'?", "Birth of a lamb"),
        ("What is 'calving'?", "Birth of a calf"),
    ],

    # ================ COMPUTER STUDIES ================
    ("Computer Studies", "Basic Computer"): [
        ("What does CPU stand for?", "Central Processing Unit"),
        ("What is the 'brain' of the computer?", "The CPU"),
        ("What is an input device?", "A device used to enter data (keyboard, mouse)"),
        ("Name 3 input devices.", "Keyboard, mouse, scanner"),
        ("Name 2 output devices.", "Monitor, printer"),
        ("What is RAM?", "Temporary memory (Random Access Memory)"),
        ("What is a hard drive used for?", "Storing data permanently"),
        ("What is a monitor used for?", "Displaying information"),
        ("What is a laptop?", "Portable computer"),
        ("What is a tablet?", "Touch-screen portable computer"),
        ("What is software?", "Programs that tell the computer what to do"),
        ("What is an operating system?", "Software that manages the computer (Windows, Linux)"),
        ("What is a byte?", "Unit of digital information"),
        ("How many bits in a byte?", "8"),
        ("What is a USB flash drive used for?", "Portable storage"),
    ],

    # ================ HERITAGE STUDIES ================
    ("Heritage Studies", "Zimbabwe History"): [
        ("Who were the earliest inhabitants of Zimbabwe?", "The San (Bushmen)"),
        ("When was Great Zimbabwe built?", "1100–1450 AD"),
        ("When did the Pioneer Column arrive?", "1890"),
        ("What was the First Chimurenga?", "First uprising against colonial rule (1896–97)"),
        ("Who led the Ndebele in the First Chimurenga?", "Nehanda and Kaguvi"),
        ("When did the Second Chimurenga begin?", "1966"),
        ("When was the Lancaster House Agreement?", "1979"),
        ("When did Zimbabwe gain independence?", "18 April 1980"),
        ("Who was the first Prime Minister of Zimbabwe?", "Robert Mugabe"),
        ("What was the First Chimurenga also known as?", "The First War of Liberation"),
        ("What was the Second Chimurenga?", "The Liberation War"),
        ("Who led ZANU during the liberation struggle?", "Robert Mugabe"),
        ("Who led ZAPU during the liberation struggle?", "Joshua Nkomo"),
        ("What is the Zimbabwe Bird?", "National symbol from Great Zimbabwe"),
        ("What does 'Chimurenga' mean?", "Revolutionary struggle"),
    ],

    # ================ COMMERCE ================
    ("Commerce", "Trade"): [
        ("What is trade?", "Buying and selling of goods and services"),
        ("What is home trade?", "Trade within one country"),
        ("What is foreign trade?", "Trade between countries"),
        ("What is wholesale?", "Selling in bulk to retailers"),
        ("What is retail?", "Selling directly to consumers"),
        ("Name 4 stages in the chain of distribution.", "Producer, wholesaler, retailer, consumer"),
        ("What is an export?", "Goods sold to other countries"),
        ("What is an import?", "Goods bought from other countries"),
        ("Name 2 Zimbabwe exports.", "Tobacco, gold"),
        ("Name 2 Zimbabwe imports.", "Fuel, machinery"),
        ("What is a trade surplus?", "Exports greater than imports"),
        ("What is a trade deficit?", "Imports greater than exports"),
        ("What is a tariff?", "Tax on imported goods"),
        ("Why do countries trade?", "To get goods they cannot produce"),
        ("Name 3 benefits of trade.", "Jobs, foreign currency, variety of goods"),
    ],

    # ================ RELIGIOUS STUDIES ================
    ("Religious Studies", "World Religions"): [
        ("Name 4 major world religions.", "Christianity, Islam, Hinduism, Buddhism"),
        ("Which religion has the most followers?", "Christianity"),
        ("What is the holy book of Christianity?", "The Bible"),
        ("What is the holy book of Islam?", "The Qur'an"),
        ("What is the holy book of Hinduism?", "The Vedas"),
        ("Who founded Buddhism?", "Siddhartha Gautama (Buddha)"),
        ("How many Pillars of Islam are there?", "5"),
        ("How many Commandments in Christianity?", "10"),
        ("What is Ramadan?", "Islamic month of fasting"),
        ("What is Diwali?", "Hindu festival of lights"),
        ("What is Christmas?", "Christian celebration of Jesus' birth"),
        ("What is Easter?", "Christian celebration of Jesus' resurrection"),
        ("What is the Torah?", "Holy book of Judaism"),
        ("What is meditation?", "Practice of calming the mind (Buddhism/Hinduism)"),
        ("Name 2 common values across religions.", "Compassion, honesty"),
    ],

    # ================ ENGLISH LITERATURE ================
    ("English", "Literature"): [
        ("What is a simile?", "Comparison using 'like' or 'as'"),
        ("What is a metaphor?", "Direct comparison (without 'like' or 'as')"),
        ("What is personification?", "Giving human qualities to non-human things"),
        ("What is alliteration?", "Repetition of initial consonant sounds"),
        ("What is hyperbole?", "Extreme exaggeration"),
        ("What is a protagonist?", "Main character of a story"),
        ("What is an antagonist?", "Character who opposes the protagonist"),
        ("What is a theme?", "Central message or idea in a story"),
        ("What is a plot?", "Sequence of events in a story"),
        ("What is a setting?", "Time and place of a story"),
        ("What is irony?", "Contrast between what is said and what is meant"),
        ("What is imagery?", "Descriptive language that appeals to senses"),
        ("What is a stanza?", "Group of lines in a poem"),
        ("What is a rhyme?", "Words that sound alike at the end of lines"),
        ("What is foreshadowing?", "Hints about what will happen later"),
    ],

    # ================ MATHS - GEOMETRY ================
    ("Maths", "Geometry"): [
        ("What is a right angle?", "90 degrees"),
        ("How many degrees in a triangle?", "180"),
        ("How many degrees in a straight line?", "180"),
        ("How many degrees around a point?", "360"),
        ("What is an acute angle?", "Less than 90 degrees"),
        ("What is an obtuse angle?", "Between 90 and 180 degrees"),
        ("What is the perimeter of a square with side 4 cm?", "16 cm"),
        ("What is the area of a rectangle 6 cm × 3 cm?", "18 cm²"),
        ("What is the perimeter of a rectangle 5 cm × 3 cm?", "16 cm"),
        ("Name 3 types of triangles.", "Equilateral, isosceles, scalene"),
        ("What is an equilateral triangle?", "All sides equal"),
        ("What is an isosceles triangle?", "Two sides equal"),
        ("What is a scalene triangle?", "All sides different"),
        ("What is a circle's circumference?", "Distance around the circle"),
        ("What is the formula for area of a rectangle?", "Length × Width"),
    ],

    # ================ BIOLOGY - NUTRITION ================
    ("Biology", "Nutrition"): [
        ("What are carbohydrates used for?", "Energy"),
        ("Give 2 examples of carbohydrates.", "Maize, rice"),
        ("What are proteins used for?", "Growth and repair"),
        ("Give 2 examples of proteins.", "Meat, beans"),
        ("What are fats used for?", "Storing energy, insulation"),
        ("What are vitamins used for?", "Health and disease prevention"),
        ("What is the main source of vitamin C?", "Citrus fruits"),
        ("What mineral is important for bones?", "Calcium"),
        ("What is a balanced diet?", "Eating the right amounts from all food groups"),
        ("What is deficiency?", "Lack of an essential nutrient"),
        ("What is kwashiorkor?", "Protein deficiency disease"),
        ("What is marasmus?", "Severe malnutrition"),
        ("Why is water important?", "Hydration, digestion, nutrient transport"),
        ("What are the 7 essential nutrients?", "Carbs, proteins, fats, vitamins, minerals, fibre, water"),
        ("What is fibre used for?", "Digestion"),
    ],
}

# ============================================================
# STEP 3: Auto-generate assignments for all students
# ============================================================
print("\n3️⃣  Auto-generating assignments for all students...")

# Get all students
c.execute("SELECT id, name, grade_form, subject FROM students")
students = c.fetchall()

print(f"   👥 Found {len(students)} student(s)")

# Get the current ISO week number
def week_number():
    return int(datetime.datetime.now().isocalendar()[1])

WEEK = week_number()
print(f"   📅 Current week: {WEEK}")

assignments_created = 0

for student in students:
    student_id, name, grade_form, primary_subject = student
    print(f"\n   🎓 {name} (Grade: {grade_form})")

    # Get subjects available for this grade from the curriculum
    c.execute("""
        SELECT DISTINCT subject FROM curriculum
        WHERE grade_form = ?
    """, (grade_form,))
    subjects = [r[0] for r in c.fetchall()]

    # Limit to 3 subjects per week for a manageable load
    # Prioritize the student's primary subject
    if primary_subject and primary_subject in subjects:
        other_subjects = [s for s in subjects if s != primary_subject]
        random.shuffle(other_subjects)
        weekly_subjects = [primary_subject] + other_subjects[:2]
    else:
        weekly_subjects = subjects[:3]

    for subject in weekly_subjects:
        # Get a topic for this subject/grade
        c.execute("""
            SELECT topic FROM curriculum
            WHERE grade_form = ? AND subject = ?
            ORDER BY RANDOM() LIMIT 1
        """, (grade_form, subject))
        topic_row = c.fetchone()
        if not topic_row:
            continue
        topic = topic_row[0]

        # Check if already generated this week
        c.execute("""
            SELECT id FROM weekly_assignments
            WHERE student_id = ? AND week_number = ? AND subject = ? AND topic = ?
        """, (student_id, WEEK, subject, topic))
        if c.fetchone():
            continue

        # Get questions from bank
        bank_key = (subject, topic)
        questions = QUESTION_BANK.get(bank_key)

        # If no exact match, use any questions for this subject
        if not questions:
            for (subj, top), qs in QUESTION_BANK.items():
                if subj == subject:
                    questions = qs
                    break

        # If still no questions, skip this assignment
        if not questions:
            continue

        # Take up to 15 questions
        selected = questions[:15]

        # Create assignment
        c.execute("""
            INSERT INTO weekly_assignments
            (student_id, week_number, subject, topic, grade_form, total_questions)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (student_id, WEEK, subject, topic, grade_form, len(selected)))
        assignment_id = c.lastrowid

        # Add questions
        for i, (q, a) in enumerate(selected, 1):
            c.execute("""
                INSERT INTO weekly_assignment_questions
                (assignment_id, question_number, question, correct_answer, topic)
                VALUES (?, ?, ?, ?, ?)
            """, (assignment_id, i, q, a, topic))

        assignments_created += 1
        print(f"      ✅ {subject} — {topic} ({len(selected)} questions)")

conn.commit()

# ============================================================
# STEP 4: Verify
# ============================================================
print("\n" + "="*70)
print("📊 WEEKLY ASSIGNMENTS SUMMARY")
print("="*70)

c.execute("SELECT COUNT(*) FROM weekly_assignments")
total = c.fetchone()[0]
print(f"\n   📝 Total weekly assignments: {total}")

c.execute("SELECT COUNT(*) FROM weekly_assignment_questions")
total_q = c.fetchone()[0]
print(f"   ❓ Total assignment questions: {total_q}")

c.execute("SELECT COUNT(*) FROM weekly_assignments WHERE completed = 1")
completed = c.fetchone()[0]
print(f"   ✅ Completed: {completed}")
print(f"   🟡 Pending:   {total - completed}")

print(f"\n   🆕 Assignments created this run: {assignments_created}")

conn.close()

print("\n" + "="*70)
print("✅ PHASE 3 COMPLETE — WEEKLY ASSIGNMENTS READY")
print("="*70)
print("\n📌 NEXT STEPS:")
print("   1. Restart the student server:")
print("      python student_server.py")
print("   2. Open the homework page:")
print("      http://127.0.0.1:5001/student/1/homework")
print("   3. You should see weekly assignments with 15 questions each.")
print("\n📌 THEN: Phase 4 — Parent-assist flow")
print("="*70 + "\n")
