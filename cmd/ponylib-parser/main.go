package main

import (
	"flag"
	"fmt"
	"os"
	"path"
	"time"

	"dev.maizy.ru/ponylib/fb2_scanner"
	"dev.maizy.ru/ponylib/internal/u"
)

type summary struct {
	successfullyParsed int
	totalSuccessTimers fb2_scanner.ParseTimers
	errors             int
	totalErrorsTimers  fb2_scanner.ParseTimers
	printTimeNs        int64
}

var Version string = "unknown"

func main() {
	flag.Parse()
	files := flag.Args()
	if len(files) < 1 {
		printErrF("Usage: %s FILE_OR_DIR [FILE_OR_DIR]\n", path.Base(os.Args[0]))
		os.Exit(2)
	}
	start := time.Now()
	done := make(chan summary)
	scanner := fb2_scanner.NewFb2Scanner()
	unavailableEntries := 0

	go printResultsAndSummarize(scanner.Results, done)

	for _, entry := range files {
		target, err := fb2_scanner.NewTargetFromEntryPath(entry, false)
		if err != nil {
			_, _ = fmt.Fprintf(os.Stderr, "%s\n", err)
			unavailableEntries++
			continue
		}
		scanner.Scan(target)
	}
	scanner.WaitUntilFinish()
	sum := <-done

	totalDuration := time.Since(start)
	anyParsed := sum.successfullyParsed > 0

	printErrF("\nStatistics:")
	if anyParsed {
		printErrF("\tSuccessfully parsed %d %s in %d ms, avg %0.2f books/sec.",
			sum.successfullyParsed, u.FormatNum(sum.successfullyParsed, "book", "books"), totalDuration.Milliseconds(),
			float64(sum.successfullyParsed)/totalDuration.Seconds())
	} else {
		printErrF("\tBooks not found, scan time %d ms", totalDuration.Milliseconds())
	}
	printErrF("\tUnable to open %d %s.", unavailableEntries, u.FormatNum(unavailableEntries, "entry", "entries"))
	printErrF("\tUnable to parse %d %s.", sum.errors, u.FormatNum(sum.errors, "book", "books"))
	if anyParsed {
		printErrF("\tTotal parse time for successfully parsed books %d ms, avg %d ms per book.",
			u.TotalMs(sum.totalSuccessTimers.ParseTimeNs),
			u.AvgMs(sum.totalSuccessTimers.ParseTimeNs, sum.successfullyParsed))
	}
}

func printResultsAndSummarize(results <-chan fb2_scanner.ScannerResult, done chan<- summary) {
	sum := summary{}
	for res := range results {
		start := time.Now()
		rid := res.Source.RId()
		if res.IsSuccess() {
			fmt.Printf("%s\n%s\n\n", rid.String(), res.Metadata.String())

			sum.totalSuccessTimers.Add(&res.Timers)
			sum.successfullyParsed += 1
		} else {
			printErrF("%s\n\tunable to parse:\n\t%s\n\n", rid.String(), *res.Error)

			sum.totalErrorsTimers.Add(&res.Timers)
			sum.errors += 1
		}
		sum.printTimeNs += time.Since(start).Nanoseconds()
	}
	done <- sum
}

func printErrF(format string, a ...interface{}) {
	_, _ = fmt.Fprintf(os.Stderr, format+"\n", a...)
}
