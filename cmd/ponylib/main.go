package main

import (
	"fmt"
	"log"
	"os"

	"dev.maizy.ru/ponylib/ponylib_app/db"
)

func printErrF(format string, a ...interface{}) {
	_, _ = fmt.Fprintf(os.Stderr, format+"\n", a...)
}

func main() {
	conn, err := db.Connect()
	defer func() {
		_ = db.CloseConnection(conn)
	}()
	if err != nil {
		printErrF("unable to open DB connection. is DATABASE_URL defined?")
		os.Exit(2)
	}

	if os.Getenv("DB_SKIP_MIGRATIONS") != "1" {
		log.Println("Migrate DB")
		if err = db.Migrate(conn); err != nil {
			printErrF("unable to migrate DB: %s", err)
			os.Exit(2)
		}
		log.Println("Migration done")
	}

	os.Exit(0)
}
