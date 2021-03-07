package cmd

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/gofrs/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/spf13/cobra"

	"dev.maizy.ru/ponylib/fb2_scanner"
	"dev.maizy.ru/ponylib/internal/u"
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

const reportBatchSize = 100

func addBookAndSummarize(conn *pgxpool.Pool, results <-chan fb2_scanner.ScannerResult, done chan<- summary) {
	sum := summary{}
	processed := 0
	lastBatchStart := time.Now()
	for res := range results {
		processed++
		if processed != 0 && processed%reportBatchSize == 0 {
			sinceLastBatch := time.Since(lastBatchStart)
			lastBatchStart = time.Now()
			log.Printf("%d books processed, %0.2f book/sec ..",
				processed, float64(reportBatchSize)/sinceLastBatch.Seconds())
		}
		if res.IsSuccess() {
			if res.FromTarget == nil {
				panic("result without FromTarget not expected")
			}
			mayBeTargetUUID := res.FromTarget.GetUUID()
			if mayBeTargetUUID == nil {
				panic("target without UUID not expected")
			}
			targetUUID := *mayBeTargetUUID
			bookUUID := uuid.Must(uuid.NewV4()).String()
			bookRId := res.Source.RId()

			startDBQuery := time.Now()
			if _, err := conn.Exec(
				context.Background(),
				"insert into book (id, target_id, rid, metadata) values ($1, $2, $3, $4)",
				// metadata converted to json because pgx has embedded jsonb support
				bookUUID, targetUUID, bookRId.String(), res.Metadata); err != nil {
				printErrF("unable to insert book to DB, skip book: %s", err)
				sum.totalErrorsTimers.Add(&res.Timers)
				sum.errors += 1
				sum.dbInsertTimeNs += time.Since(startDBQuery).Nanoseconds()
				continue
			}

			sum.totalSuccessTimers.Add(&res.Timers)
			sum.successfullyParsed += 1
			sum.dbInsertTimeNs += time.Since(startDBQuery).Nanoseconds()
		} else {
			log.Printf("unable to parse: %s", *res.Error)

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
				log.Printf("unable to open target: %s", err)
				unavailableEntries++
				continue
			}
			targetRId := target.RId()
			if _, err := conn.Exec(
				context.Background(),
				"insert into target (id, scanned_at, rid) values ($1, $2, $3)",
				target.GetUUID(), start, targetRId.String()); err != nil {
				log.Printf("unable to insert target to DB, skip target: %s", err)
				continue
			}
			log.Printf("scan target %s", targetRId.String())
			scanner.Scan(target)
		}
		scanner.WaitUntilFinish()
		sum := <-done

		totalDuration := time.Since(start)
		anyParsed := sum.successfullyParsed > 0
		log.Println("done")

		fmt.Println("\nStatistics:")
		if anyParsed {
			fmt.Printf("\tSuccessfully parsed %d %s in %0.2fs, avg %0.2f books/sec.\n",
				sum.successfullyParsed, u.FormatNum(sum.successfullyParsed, "book", "books"),
				totalDuration.Seconds(), float64(sum.successfullyParsed)/totalDuration.Seconds())
		} else {
			fmt.Printf("\tBooks not found, scan time %0.2fs.\n", totalDuration.Seconds())
		}
		fmt.Printf("\tUnable to open %d %s.\n", unavailableEntries, u.FormatNum(unavailableEntries, "entry", "entries"))
		fmt.Printf("\tUnable to process %d %s.\n", sum.errors, u.FormatNum(sum.errors, "book", "books"))
		if anyParsed {
			fmt.Printf("\tTotal parse time for successfully parsed books %0.2fs, avg %d ms per book.\n",
				u.TotalSec(sum.totalSuccessTimers.ParseTimeNs),
				u.AvgMs(sum.totalSuccessTimers.ParseTimeNs, sum.successfullyParsed))
			fmt.Printf("\tTotal DB operations time for successfully parsed books %0.2fs, avg %d ms per book.\n",
				u.TotalSec(sum.dbInsertTimeNs),
				u.AvgMs(sum.dbInsertTimeNs, sum.successfullyParsed))
		}

		os.Exit(0)
	},
}
