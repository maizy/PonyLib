package cmd

import (
	"os"

	"github.com/spf13/cobra"

	"dev.maizy.ru/ponylib/ponylib_app/db"
)

func init() {
	rootCmd.AddCommand(scanCmd)
}

var scanCmd = &cobra.Command{
	Use:   "scan",
	Short: "Add fb2 books to library",
	Run: func(cmd *cobra.Command, args []string) {
		conn := connectToDbOrExit()
		defer db.CloseConnection(conn)

		if os.Getenv("DB_SKIP_MIGRATIONS") != "1" {
			migrateOrExit(conn)
		}

		printErrF("TODO: scan books")
		os.Exit(1)
	},
}
