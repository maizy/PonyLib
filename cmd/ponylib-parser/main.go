package main

import (
	"flag"
	"fmt"
	"math"
	"os"
	"path"
	"time"

	"dev.maizy.ru/ponylib/fb2_scanner"
	"dev.maizy.ru/ponylib/fb2_scanner/targets"
)

type summary struct {
	successfullyParsed int
	totalSuccessTimers fb2_scanner.ParseTimers
	errors             int
	totalErrorsTimers  fb2_scanner.ParseTimers
	printTimeNs        int64
}

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

	go printResultsAndSummarize(scanner.Results, done)

	for _, entry := range files {
		stat, err := os.Stat(entry)
		if err != nil {
			_, _ = fmt.Fprintf(os.Stderr, "unable to open %s: %s\n", entry, err)
			continue
		}
		switch mode := stat.Mode(); {
		case mode.IsDir():
			scanner.Scan(&targets.DirectoryTarget{Path: entry})
		case mode.IsRegular():
			scanner.Scan(&targets.FileTarget{Path: entry})
		}
	}
	scanner.WaitUntilFinish()
	sum := <-done

	totalDuration := time.Since(start)
	anyParsed := sum.successfullyParsed > 0

	printErrF("\nStatistics:")
	if anyParsed {
		printErrF("\tSuccessfully parsed %d %s in %d ms, avg %0.2f books/sec.",
			sum.successfullyParsed, formatNum(sum.successfullyParsed, "book", "books"), totalDuration.Milliseconds(),
			float64(sum.successfullyParsed)/totalDuration.Seconds())
	} else {
		printErrF("\tBooks not found, scan time %d ms", totalDuration.Milliseconds())
	}
	printErrF("\tUnable to parse %d %s.", sum.errors, formatNum(sum.errors, "item", "items"))
	if anyParsed {
		printErrF("\tTotal parse time for successfully parsed books %d ms, avg %d ms per book.",
			totalMs(sum.totalSuccessTimers.ParseTimeNs), avgMs(sum.totalSuccessTimers.ParseTimeNs, sum.successfullyParsed))
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

func formatNum(amount int, one string, many string) string {
	if amount == 1 {
		return one
	}
	return many
}

func totalMs(totalNs int64) int64 {
	return totalNs / int64(math.Pow(10, 6))
}

func avgMs(totalNs int64, files int) int64 {
	return int64(float64(totalNs) / float64(files) / math.Pow(10, 6))
}
