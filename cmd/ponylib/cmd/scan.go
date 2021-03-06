package cmd

import (
	"fmt"
	"os"
	"time"

	"github.com/gofrs/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/spf13/cobra"

	"dev.maizy.ru/ponylib/fb2_scanner"
	"dev.maizy.ru/ponylib/ponylib_app/db"
)

func init() {
	rootCmd.AddCommand(scanCmd)
}

type summary struct {
	successfullyParsed int
	totalSuccessTimers fb2_scanner.ParseTimers
	errors             int
	totalErrorsTimers  fb2_scanner.ParseTimers
	dbInsertTimeNs     int64
}

func addBookAndSummarize(conn *pgxpool.Pool, results <-chan fb2_scanner.ScannerResult, done chan<- summary) {
	sum := summary{}
	for res := range results {
		sourceRId := res.Source.RId()

		if res.IsSuccess() {
			if res.FromTarget == nil {
				panic("Result without FromTarget not expected")
			}
			mayBeTargetUUID := res.FromTarget.GetUUID()
			if mayBeTargetUUID == nil {
				panic("Target without UUID not expected")
			}
			targetUUID := *mayBeTargetUUID
			targetRId := res.FromTarget.RId()
			bookUUID := uuid.Must(uuid.NewV4()).String()
			fmt.Printf(
				"%s [%s] => %s [%s] title: %s\n",
				targetUUID, &targetRId, bookUUID, &sourceRId, res.Metadata.Book.Title)

			sum.totalSuccessTimers.Add(&res.Timers)
			sum.successfullyParsed += 1
		} else {
			printErrF("%s\n\tunable to parse:\n\t%s\n\n", &sourceRId, *res.Error)

			sum.totalErrorsTimers.Add(&res.Timers)
			sum.errors += 1
		}
	}
	done <- sum
}

var scanCmd = &cobra.Command{
	Use:                   "scan source_dir [source.zip] [source.fb2]",
	Short:                 "Add fb2 books to library",
	Args:                  cobra.MinimumNArgs(1),
	DisableFlagsInUseLine: true,

	Run: func(cmd *cobra.Command, args []string) {
		if len(args) == 0 {
			_ = cmd.Usage()
			os.Exit(2)
		}
		conn := connectToDbOrExit()
		defer db.CloseConnection(conn)

		if os.Getenv("DB_SKIP_MIGRATIONS") != "1" {
			migrateOrExit(conn)
		}

		start := time.Now()
		unavailableEntries := 0

		done := make(chan summary)
		scanner := fb2_scanner.NewFb2Scanner()

		go addBookAndSummarize(conn, scanner.Results, done)

		for _, entry := range args {
			target, err := fb2_scanner.NewTargetFromEntryPath(entry, true)
			if err != nil {
				printErrF("%s\n\tunable to open:\n\t%s\n", entry, err)
				unavailableEntries++
				continue
			}
			scanner.Scan(target)
		}
		scanner.WaitUntilFinish()
		sum := <-done

		totalDuration := time.Since(start)
		// FIXME
		fmt.Printf("sum: %v\n", sum)
		fmt.Printf("unavailable: %d\n", unavailableEntries)
		fmt.Printf("total duration: %d\n", totalDuration)

		os.Exit(0)
	},
}
