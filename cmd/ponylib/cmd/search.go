package cmd

import (
	"os"

	"github.com/spf13/cobra"

	"dev.maizy.ru/ponylib/ponylib_app/db"
)

// flags
var (
	searchQuery string
)

func init() {
	searchCmd.PersistentFlags().StringVarP(&searchQuery, "query", "q", "", "search query")
	rootCmd.AddCommand(searchCmd)
}

var searchCmd = &cobra.Command{
	Use:   "search",
	Short: "Search in library",
	Run: func(cmd *cobra.Command, args []string) {
		conn := connectToDbOrExit()
		defer db.CloseConnection(conn)

		printErrF("TODO: search library: '%s'", searchQuery)
		os.Exit(1)
	},
}
