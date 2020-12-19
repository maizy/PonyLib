package main

import (
	"flag"
	"fmt"
	"math"
	"os"
	"path"
	"path/filepath"
	"time"

	"dev.maizy.ru/ponylib/fb2_parser/metadata"
)

type parseFileTimers struct {
	parseTimeNs int64
	printTimeNs int64
}

func (t *parseFileTimers) add(other *parseFileTimers) {
	if other != nil {
		t.parseTimeNs += other.parseTimeNs
		t.printTimeNs += other.printTimeNs
	}
}

func main() {
	flag.Parse()
	files := flag.Args()
	if len(files) < 1 {
		_, _ = fmt.Fprintf(os.Stderr, "Usage: %s FILE_OR_DIR [FILE_OR_DIR]\n", path.Base(os.Args[0]))
		os.Exit(2)
	}
	var start = time.Now()
	total := parseFileTimers{}
	var processedFiles int
	for _, entry := range files {
		stat, err := os.Stat(entry)
		if err != nil {
			_, _ = fmt.Fprintf(os.Stderr, "%s: unable to open. %s\n", entry, err)
			continue
		}
		switch mode := stat.Mode(); {
		case mode.IsDir():
			err := filepath.Walk(entry,
				func(filePath string, info os.FileInfo, err error) error {
					if info.IsDir() {
						return nil
					}
					if err != nil {
						return err
					}
					// TODO: filter by extension
					timers := parseFile(filePath)
					total.add(timers)
					processedFiles += 1
					return nil
				})
			if err != nil {
				_, _ = fmt.Fprintf(os.Stderr, "%s: unable to list dir. %s\n", entry, err)
			}
		case mode.IsRegular():
			timers := parseFile(entry)
			total.add(timers)
			processedFiles += 1
		}
	}

	var totalDuration = time.Since(start)
	var filesLabel = "files"
	if processedFiles == 1 {
		filesLabel = "file"
	}
	fmt.Fprintf(os.Stderr, "\n Statistics:\n\tParsed %d %s in %d ms, avg %0.2f files/sec.\n",
		processedFiles, filesLabel, totalDuration.Milliseconds(), float64(processedFiles)/totalDuration.Seconds())
	fmt.Fprintf(os.Stderr, "\tTotal parse time %d ms, avg %d ms per file.\n",
		totalMs(total.parseTimeNs), avgMs(total.parseTimeNs, processedFiles))
	//fmt.Fprintf(os.Stderr, "\tTotal print time %d ms, avg %d ms per file.\n",
	//	totalMs(total.printTimeNs), avgMs(total.printTimeNs, processedFiles))
}

func totalMs(totalNs int64) int64 {
	return totalNs / int64(math.Pow(10, 6))
}
func avgMs(totalNs int64, files int) int64 {
	return int64(float64(totalNs) / float64(files) / math.Pow(10, 6))
}

func parseFile(path string) *parseFileTimers {
	var parseStart = time.Now()
	fp, err := os.Open(path)
	defer fp.Close()
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "%s: unable to open file. %s\n", path, err)
		return nil
	}
	parseMetadata, err := metadata.ParseMetadata(fp)
	var parseTime = time.Since(parseStart).Nanoseconds()
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "%s: unable to parse metadata: %s\n", path, err)
		return nil
	}

	var printStart = time.Now()
	fmt.Printf("%s: %s\n", path, parseMetadata)
	var printTime = time.Since(printStart).Nanoseconds()
	return &parseFileTimers{parseTime, printTime}
}
