package fb2_parser

import "strings"

type MultiLang struct {
	Ru string
	En string
}

func (m *MultiLang) String() string {
	return m.Ru + " / " + m.En
}

type Genre struct {
	MultiLang
	Code  string
	IsEtc bool
}

type GenreCategory struct {
	MultiLang
	Genres []Genre
}

type categoriesArray = [15]GenreCategory

var GenreCategories = categoriesArray{
	{
		MultiLang: MultiLang{En: "Science Fiction & Fantasy", Ru: "Научная фантастика и Фэнтези"},
		Genres: []Genre{
			{Code: "sf_history", MultiLang: MultiLang{En: "Alternative history", Ru: "Альтернативная история"}},
			{Code: "sf_action", MultiLang: MultiLang{En: "Action", Ru: "Боевая фантастика"}},
			{Code: "sf_epic", MultiLang: MultiLang{En: "Epic", Ru: "Эпическая фантастика"}},
			{Code: "sf_heroic", MultiLang: MultiLang{En: "Heroic", Ru: "Героическая фантастика"}},
			{Code: "sf_detective", MultiLang: MultiLang{En: "Detective", Ru: "Детективная фантастика"}},
			{Code: "sf_cyberpunk", MultiLang: MultiLang{En: "Cyberpunk", Ru: "Киберпанк"}},
			{Code: "sf_space", MultiLang: MultiLang{En: "Space", Ru: "Космическая фантастика"}},
			{Code: "sf_social",
				MultiLang: MultiLang{En: "Social-philosophical", Ru: "Социально-психологическая фантастика"}},
			{Code: "sf_horror", MultiLang: MultiLang{En: "Horror & mystic", Ru: "Ужасы и Мистика"}},
			{Code: "sf_humor", MultiLang: MultiLang{En: "Humor", Ru: "Юмористическая фантастика"}},
			{Code: "sf_fantasy", MultiLang: MultiLang{En: "Fantasy", Ru: "Фэнтези"}, IsEtc: true},
			{Code: "sf", MultiLang: MultiLang{En: "Science Fiction", Ru: "Научная Фантастика"}, IsEtc: true},
		},
	},

	{
		MultiLang: MultiLang{En: "Detectives & Thrillers", Ru: "Детективы и Триллеры"},
		Genres: []Genre{
			{Code: "det_classic", MultiLang: MultiLang{En: "Classical detectives", Ru: "Классический детектив"}},
			{Code: "det_police", MultiLang: MultiLang{En: "Police Stories", Ru: "Полицейский детектив"}},
			{Code: "det_action", MultiLang: MultiLang{En: "Action", Ru: "Боевик"}},
			{Code: "det_irony", MultiLang: MultiLang{En: "Ironical detectives", Ru: "Иронический детектив"}},
			{Code: "det_history", MultiLang: MultiLang{En: "Historical detectives", Ru: "Исторический детектив"}},
			{Code: "det_espionage", MultiLang: MultiLang{En: "Espionage detectives", Ru: "Шпионский детектив"}},
			{Code: "det_crime", MultiLang: MultiLang{En: "Crime detectives", Ru: "Криминальный детектив"}},
			{Code: "det_political", MultiLang: MultiLang{En: "Political detectives", Ru: "Политический детектив"}},
			{Code: "det_maniac", MultiLang: MultiLang{En: "Maniacs", Ru: "Маньяки"}},
			{Code: "det_hard", MultiLang: MultiLang{En: "Hard-boiled", Ru: "Крутой детектив"}},
			{Code: "thriller", MultiLang: MultiLang{En: "Thrillers", Ru: "Триллер"}, IsEtc: true},
			{Code: "detective", MultiLang: MultiLang{En: "Detectives", Ru: "Детектив"}, IsEtc: true},
		},
	},

	{
		MultiLang: MultiLang{En: "Prose", Ru: "Проза"},
		Genres: []Genre{
			{Code: "prose_classic", MultiLang: MultiLang{En: "Classics prose", Ru: "Классическая проза"}},
			{Code: "prose_history", MultiLang: MultiLang{En: "Historical prose", Ru: "Историческая проза"}},
			{Code: "prose_contemporary", MultiLang: MultiLang{En: "Contemporary prose", Ru: "Современная проза"}},
			{Code: "prose_counter", MultiLang: MultiLang{En: "Counterculture", Ru: "Контркультура"}},
			{Code: "prose_rus_classic", MultiLang: MultiLang{En: "Russial classics prose", Ru: "Русская классическая проза"}},
			{Code: "prose_su_classics", MultiLang: MultiLang{En: "Soviet classics prose", Ru: "Советская классическая проза"}},
		},
	},

	{
		MultiLang: MultiLang{En: "Romance", Ru: "Любовные романы"},
		Genres: []Genre{
			{Code: "love_contemporary",
				MultiLang: MultiLang{En: "Contemporary Romance", Ru: "Современные любовные романы"}},
			{Code: "love_history",
				MultiLang: MultiLang{En: "Historical Romance", Ru: "Исторические любовные романы"}},
			{Code: "love_detective",
				MultiLang: MultiLang{En: "Detective Romance", Ru: "Остросюжетные любовные романы"}},
			{Code: "love_short", MultiLang: MultiLang{En: "Short Romance", Ru: "Короткие любовные романы"}},
			{Code: "love_erotica", MultiLang: MultiLang{En: "Erotica", Ru: "Эротика"}},
		},
	},

	{
		MultiLang: MultiLang{En: "Adventure", Ru: "Приключения"},
		Genres: []Genre{
			{Code: "adv_western", MultiLang: MultiLang{En: "Western", Ru: "Вестерн"}},
			{Code: "adv_history", MultiLang: MultiLang{En: "History", Ru: "Исторические приключения"}},
			{Code: "adv_indian", MultiLang: MultiLang{En: "Indians", Ru: "Приключения про индейцев"}},
			{Code: "adv_maritime", MultiLang: MultiLang{En: "Maritime Fiction", Ru: "Морские приключения"}},
			{Code: "adv_geo", MultiLang: MultiLang{En: "Travel & geography", Ru: "Путешествия и география"}},
			{Code: "adv_animal", MultiLang: MultiLang{En: "Nature & animals", Ru: "Природа и животные"}},
			{Code: "adventure", MultiLang: MultiLang{En: "Other", Ru: "Прочие приключения"}, IsEtc: true},
		},
	},

	{
		MultiLang: MultiLang{En: "Children's", Ru: "Детское"},
		Genres: []Genre{
			{Code: "child_tale", MultiLang: MultiLang{En: "Fairy Tales", Ru: "Сказка"}},
			{Code: "child_verse", MultiLang: MultiLang{En: "Verses", Ru: "Детские стихи"}},
			{Code: "child_prose", MultiLang: MultiLang{En: "Prose", Ru: "Детскиая проза"}},
			{Code: "child_sf", MultiLang: MultiLang{En: "Science Fiction", Ru: "Детская фантастика"}},
			{Code: "child_det", MultiLang: MultiLang{En: "Detectives & Thrillers", Ru: "Детские остросюжетные"}},
			{Code: "child_adv", MultiLang: MultiLang{En: "Adventures", Ru: "Детские приключения"}},
			{Code: "child_education",
				MultiLang: MultiLang{En: "Educational", Ru: "Детская образовательная литература"}},
			{Code: "children", MultiLang: MultiLang{En: "Other", Ru: "Прочая детская литература"}, IsEtc: true},
		},
	},

	{
		MultiLang: MultiLang{En: "Poetry & Dramaturgy", Ru: "Поэзия, Драматургия"},
		Genres: []Genre{
			{Code: "poetry", MultiLang: MultiLang{En: "Poetry", Ru: "Поэзия"}},
			{Code: "dramaturgy", MultiLang: MultiLang{En: "Dramaturgy", Ru: "Драматургия"}},
		},
	},

	{
		MultiLang: MultiLang{En: "Antique literature", Ru: "Старинное"},
		Genres: []Genre{
			{Code: "antique_ant", MultiLang: MultiLang{En: "Antique", Ru: "Античная литература"}},
			{Code: "antique_european", MultiLang: MultiLang{En: "European", Ru: "Европейская старинная литература"}},
			{Code: "antique_russian", MultiLang: MultiLang{En: "Old russian", Ru: "Древнерусская литература"}},
			{Code: "antique_east", MultiLang: MultiLang{En: "Old east", Ru: "Древневосточная литература"}},
			{Code: "antique_myths", MultiLang: MultiLang{En: "Myths. Legends. Epos", Ru: "Мифы. Легенды. Эпос"}},
			{Code: "antique", MultiLang: MultiLang{En: "Other", Ru: "Прочая старинная литература"}, IsEtc: true},
		},
	},

	{
		MultiLang: MultiLang{En: "Scientific-educational", Ru: "Наука, Образование"},
		Genres: []Genre{
			{Code: "sci_history", MultiLang: MultiLang{En: "History", Ru: "История"}},
			{Code: "sci_psychology", MultiLang: MultiLang{En: "Psychology", Ru: "Психология"}},
			{Code: "sci_culture", MultiLang: MultiLang{En: "Cultural science", Ru: "Культурология"}},
			{Code: "sci_religion", MultiLang: MultiLang{En: "Religious studies", Ru: "Религиоведение"}},
			{Code: "sci_philosophy", MultiLang: MultiLang{En: "Philosophy", Ru: "Философия"}},
			{Code: "sci_politics", MultiLang: MultiLang{En: "Politics", Ru: "Политика"}},
			{Code: "sci_business", MultiLang: MultiLang{En: "Business literature", Ru: "Деловая литература"}},
			{Code: "sci_juris", MultiLang: MultiLang{En: "Jurisprudence", Ru: "Юриспруденция"}},
			{Code: "sci_linguistic", MultiLang: MultiLang{En: "Linguistics", Ru: "Языкознание"}},
			{Code: "sci_medicine", MultiLang: MultiLang{En: "Medicine", Ru: "Медицина"}},
			{Code: "sci_phys", MultiLang: MultiLang{En: "Physics", Ru: "Физика"}},
			{Code: "sci_math", MultiLang: MultiLang{En: "Mathematics", Ru: "Математика"}},
			{Code: "sci_chem", MultiLang: MultiLang{En: "Chemistry", Ru: "Химия"}},
			{Code: "sci_biology", MultiLang: MultiLang{En: "Biology", Ru: "Биология"}},
			{Code: "sci_tech", MultiLang: MultiLang{En: "Technical", Ru: "Технические науки"}},
			{Code: "science", MultiLang: MultiLang{En: "Other", Ru: "Прочая научная литература"}, IsEtc: true},
		},
	},

	{
		MultiLang: MultiLang{En: "Computers & Internet", Ru: "Компьютеры и Интернет"},
		Genres: []Genre{
			{Code: "comp_www", MultiLang: MultiLang{En: "Internet", Ru: "Интернет"}},
			{Code: "comp_programming", MultiLang: MultiLang{En: "Programming", Ru: "Программирование"}},
			{Code: "comp_hard", MultiLang: MultiLang{En: "Hardware",
				Ru: "Компьютерное \"железо\" (аппаратное обеспечение)"}},
			{Code: "comp_soft", MultiLang: MultiLang{En: "Software", Ru: "Программы"}},
			{Code: "comp_db", MultiLang: MultiLang{En: "Databases", Ru: "Базы данных"}},
			{Code: "comp_osnet", MultiLang: MultiLang{En: "OS & Networking", Ru: "ОС и Сети"}},
			{Code: "computers", MultiLang: MultiLang{En: "Other", Ru: "Прочая околокомпьтерная литература"},
				IsEtc: true},
		},
	},

	{
		MultiLang: MultiLang{En: "Reference", Ru: "Справочная литература"},
		Genres: []Genre{
			{Code: "ref_encyc", MultiLang: MultiLang{En: "Encyclopedias", Ru: "Энциклопедии"}},
			{Code: "ref_dict", MultiLang: MultiLang{En: "Dictionaries", Ru: "Словари"}},
			{Code: "ref_ref", MultiLang: MultiLang{En: "Reference", Ru: "Справочники"}},
			{Code: "ref_guide", MultiLang: MultiLang{En: "Guidebooks", Ru: "Руководства"}},
			{Code: "reference", MultiLang: MultiLang{En: "Other", Ru: "Прочая справочная литература"}},
		},
	},

	{
		MultiLang: MultiLang{En: "Nonfiction", Ru: "Документальная литература"},
		Genres: []Genre{
			{Code: "nonf_biography", MultiLang: MultiLang{En: "Biography & Memoirs", Ru: "Биографии и Мемуары"}},
			{Code: "nonf_publicism", MultiLang: MultiLang{En: "Publicism", Ru: "Публицистика"}},
			{Code: "nonf_criticism", MultiLang: MultiLang{En: "Criticism", Ru: "Критика"}},
			{Code: "design", MultiLang: MultiLang{En: "Art & design", Ru: "Искусство и Дизайн"}},
			{Code: "nonfiction", MultiLang: MultiLang{En: "Other", Ru: "Прочая документальная литература"}},
		},
	},

	{
		MultiLang: MultiLang{En: "Religion & Inspiration", Ru: "Религия и духовность"},
		Genres: []Genre{
			{Code: "religion_rel", MultiLang: MultiLang{En: "Religion", Ru: "Религия"}},
			{Code: "religion_esoterics", MultiLang: MultiLang{En: "Esoterics", Ru: "Эзотерика"}},
			{Code: "religion_self", MultiLang: MultiLang{En: "Self-improvement", Ru: "Самосовершенствование"}},
			{Code: "religion", MultiLang: MultiLang{En: "Other", Ru: "Прочая религионая литература"}, IsEtc: true},
		},
	},

	{
		MultiLang: MultiLang{En: "Humor", Ru: "Юмор"},
		Genres: []Genre{
			{Code: "humor_anecdote", MultiLang: MultiLang{En: "Anecdote (funny stories)", Ru: "Анекдоты"}},
			{Code: "humor_prose", MultiLang: MultiLang{En: "Prose", Ru: "Юмористическая проза"}},
			{Code: "humor_verse", MultiLang: MultiLang{En: "Verses", Ru: "Юмористические стихи"}},
			{Code: "humor", MultiLang: MultiLang{En: "Other", Ru: "Прочий юмор"}, IsEtc: true},
		},
	},

	{
		MultiLang: MultiLang{En: "Home & Family", Ru: "Дом и семья"},
		Genres: []Genre{
			{Code: "home_cooking", MultiLang: MultiLang{En: "Cooking", Ru: "Кулинария"}},
			{Code: "home_pets", MultiLang: MultiLang{En: "Pets", Ru: "Домашние животные"}},
			{Code: "home_crafts", MultiLang: MultiLang{En: "Hobbies & Crafts", Ru: "Хобби и ремесла"}},
			{Code: "home_entertain", MultiLang: MultiLang{En: "Entertaining", Ru: "Развлечения"}},
			{Code: "home_health", MultiLang: MultiLang{En: "Health", Ru: "Здоровье"}},
			{Code: "home_garden", MultiLang: MultiLang{En: "Garden", Ru: "Сад и огород"}},
			{Code: "home_diy", MultiLang: MultiLang{En: "Do it yourself", Ru: "Сделай сам"}},
			{Code: "home_sport", MultiLang: MultiLang{En: "Sports", Ru: "Спорт"}},
			{Code: "home_sex", MultiLang: MultiLang{En: "Erotica & sex", Ru: "Эротика, Секс"}},
			{Code: "home", MultiLang: MultiLang{En: "Other", Ru: "Прочиее домоводство"}, IsEtc: true},
		},
	},
}

type GenreIndexEntity struct {
	Genre    Genre
	Category GenreCategory
}

func (g *GenreIndexEntity) String() string {
	var sb strings.Builder
	sb.WriteString("[")
	sb.WriteString(g.Genre.Code)
	sb.WriteString("] ")
	sb.WriteString(g.Category.En)
	sb.WriteString(" :: ")
	sb.WriteString(g.Genre.En)
	sb.WriteString(" (")
	sb.WriteString(g.Category.Ru)
	sb.WriteString(" :: ")
	sb.WriteString(g.Genre.Ru)
	sb.WriteString(")")
	return sb.String()
}

func createGeneryIndex(categories categoriesArray) map[string]GenreIndexEntity {
	index := make(map[string]GenreIndexEntity)
	for _, category := range &categories {
		for _, genry := range category.Genres {
			index[genry.Code] = GenreIndexEntity{genry, category}
		}
	}
	return index
}

var GenryIndexByCode = createGeneryIndex(GenreCategories)
