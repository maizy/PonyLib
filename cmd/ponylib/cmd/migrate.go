package cmd

import (
	"os"

	"github.com/spf13/cobra"

	"dev.maizy.ru/ponylib/ponylib_app/db"
)

func init() {
	rootCmd.AddCommand(migrateCmd)
}

var migrateCmd = &cobra.Command{
	Use:   "migrate",
	Short: "Migrate database",
	Run: func(cmd *cobra.Command, args []string) {
		conn := connectToDbOrExit()
		defer db.CloseConnection(conn)

		migrateOrExit(conn)
		os.Exit(0)
	},
}
