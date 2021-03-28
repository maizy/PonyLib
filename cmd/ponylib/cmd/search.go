package cmd

import (
	"fmt"
	"os"
	"strconv"

	"github.com/spf13/cobra"

	"dev.maizy.ru/ponylib/internal/u"
	"dev.maizy.ru/ponylib/ponylib_app/db"
	"dev.maizy.ru/ponylib/ponylib_app/search"
)

// flags
var (
	searchQuery string
	from        int
	limit       int
)

const defaultLimit = 20

func init() {
	searchCmd.PersistentFlags().StringVarP(&searchQuery, "query", "q", "", "search query")
	searchCmd.PersistentFlags().IntVarP(&from, "from", "f", 1, "display results from this position")
	searchCmd.PersistentFlags().IntVarP(&limit, "results", "n", defaultLimit, "results amount")
	rootCmd.AddCommand(searchCmd)
}

var searchCmd = &cobra.Command{
	Use:   "search",
	Short: "Search in library",
	Run: func(cmd *cobra.Command, args []string) {
		conn := connectToDbOrExit()
		defer db.CloseConnection(conn)

		if from < 1 {
			printErrF("from should be great than 1")
			os.Exit(2)
		}

		if limit < 0 {
			printErrF("limit should be great than 0")
			os.Exit(2)
		}

		query := &search.BookSearchQuery{
			TextMatch: searchQuery,
		}

		count, err := search.CountBooks(conn, query)
		if err != nil {
			printErrF("Unable to count matches: %s", err)
			os.Exit(1)
		}
		if count > 0 {
			fmt.Printf("Found %d %s\n", count, u.FormatNum(count, "book", "books"))
		} else {
			fmt.Println("Books not found")
		}

		if count > 0 {
			var lastPosition int
			fmt.Printf("Results %d-%d\n\n", from, u.IntMin(from+limit-1, count))
			results, err := search.SearchBooks(conn, query, from-1, limit)
			if err != nil {
				printErrF("Unable to get search results: %s", err)
				os.Exit(1)
			}
			for _, result := range (*results).Matches {
				fmt.Printf("%d. %s\n%s\n\n", result.Position, result.RId.String(), result.Metadata.String())
				lastPosition = result.Position
			}
			if lastPosition != 0 && count-1 > lastPosition {
				var limitStr string
				if limit != defaultLimit {
					limitStr = " -n " + strconv.Itoa(limit)
				}
				fmt.Printf(
					"To display next results\n    ponylib search -q '%s' -f %d%s\n",
					searchQuery, lastPosition+1, limitStr)
			}
		}

	},
}
