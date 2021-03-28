package ponylib_app

import "os"

func GetFTSLanguage() string {
	var ftsLanguage = os.Getenv("FTS_LANGUAGE")
	if ftsLanguage == "" {
		ftsLanguage = "english"
	}
	return ftsLanguage
}
