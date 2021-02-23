package cmd

import (
	"os"

	"github.com/spf13/cobra"

	"dev.maizy.ru/ponylib/ponylib_app/db"
)

// flags
var (
	bindPort int
	bindHost string
)

func init() {
	webUiCmd.PersistentFlags().IntVar(&bindPort, "port", 55387, "bind port")
	webUiCmd.PersistentFlags().StringVar(&bindHost, "host", "127.0.0.1", "bind host")

	rootCmd.AddCommand(webUiCmd)
}

var webUiCmd = &cobra.Command{
	Use:   "web-ui",
	Short: "Launch Web UI",
	Run: func(cmd *cobra.Command, args []string) {
		conn := connectToDbOrExit()
		defer db.CloseConnection(conn)

		if os.Getenv("DB_SKIP_MIGRATIONS") != "1" {
			migrateOrExit(conn)
		}

		printErrF("TODO: launch web app at: http://%s:%d", bindHost, bindPort)
		os.Exit(1)
	},
}
