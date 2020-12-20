package main

import (
	"flag"
	"fmt"
	"math"
	"os"
	"path"
	"time"

	"dev.maizy.ru/ponylib/fb2_scanner"
	"dev.maizy.ru/ponylib/fb2_scanner/fs"
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
	var start = time.Now()
	done := make(chan summary)
	scanner := fb2_scanner.NewFb2Scanner()

	go printResultsAndSummarize(scanner.Results, done)

	for _, entry := range files {
		stat, err := os.Stat(entry)
		if err != nil {
			_, _ = fmt.Fprintf(os.Stderr, "%s: unable to open. %s\n", entry, err)
			continue
		}
		switch mode := stat.Mode(); {
		case mode.IsDir():
			scanner.Scan(&fs.DirectoryTarget{Path: entry})
		case mode.IsRegular():
			scanner.Scan(&fs.FileTarget{Path: entry})
		}
	}
	scanner.Wait()
	sum := <-done

	var totalDuration = time.Since(start)

	printErrF("\nStatistics:")

	printErrF("\tSuccessfully parsed %d %s in %d ms, avg %0.2f books/sec.",
		sum.successfullyParsed, bookLabel(sum.successfullyParsed), totalDuration.Milliseconds(),
		float64(sum.successfullyParsed)/totalDuration.Seconds())
	printErrF("\tUnable to parse %d %s.", sum.errors, bookLabel(sum.errors))
	printErrF("\tTotal parse time for successfully parsed books %d ms, avg %d ms per book.",
		totalMs(sum.totalSuccessTimers.ParseTimeNs), avgMs(sum.totalSuccessTimers.ParseTimeNs, sum.successfullyParsed))
}

func printResultsAndSummarize(results <-chan fb2_scanner.ScannerResult, done chan<- summary) {
	sum := summary{}
	for res := range results {
		start := time.Now()
		if res.IsSuccess() {
			fmt.Printf("%s: %s\n", res.Source.Spec(), res.Metadata.String())
		} else {
			printErrF("unable to parse %s: %s", res.Source.Spec(), *res.Error)
		}
		sum.printTimeNs += time.Since(start).Nanoseconds()

		if res.IsSuccess() {
			sum.totalSuccessTimers.Add(&res.Timers)
			sum.successfullyParsed += 1
		} else {
			sum.totalErrorsTimers.Add(&res.Timers)
			sum.errors += 1
		}
	}
	done <- sum
}

func printErrF(format string, a ...interface{}) {
	_, _ = fmt.Fprintf(os.Stderr, format+"\n", a...)
}

func bookLabel(amount int) string {
	if amount == 1 {
		return "book"
	}
	return "books"
}

func totalMs(totalNs int64) int64 {
	return totalNs / int64(math.Pow(10, 6))
}

func avgMs(totalNs int64, files int) int64 {
	return int64(float64(totalNs) / float64(files) / math.Pow(10, 6))
}
