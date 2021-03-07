package cmd

import (
	"fmt"
	"os"

	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/spf13/cobra"

	"dev.maizy.ru/ponylib/ponylib_app"
	"dev.maizy.ru/ponylib/ponylib_app/db"
)

var rootCmd = &cobra.Command{
	Use: "ponylib",
}

func Execute(appVersion string) error {
	rootCmd.SetVersionTemplate(`{{printf "%s version: %s\n" .Name .Version}}`)
	rootCmd.Version = ponylib_app.NormalizeVersion(appVersion)
	return rootCmd.Execute()
}

func printErrF(format string, a ...interface{}) {
	_, _ = fmt.Fprintf(os.Stderr, format+"\n", a...)
}

func connectToDbOrExit() *pgxpool.Pool {
	conn, err := db.Connect()
	if err != nil {
		printErrF("unable to open DB connection. is DATABASE_URL defined?")
		os.Exit(2)
	}
	return conn
}

func migrateOrExit(conn *pgxpool.Pool) {
	if err := db.Migrate(conn); err != nil {
		printErrF("unable to migrate DB: %s", err)
		os.Exit(2)
	}
}
