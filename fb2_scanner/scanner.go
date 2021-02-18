package fb2_scanner

import (
	"sync"
)

type Fb2Scanner struct {
	Results       <-chan ScannerResult
	resultChannel chan<- ScannerResult
	scanTargetsWG sync.WaitGroup
	ctx           ScannerContext
}

func NewFb2Scanner() Fb2Scanner {
	channel := make(chan ScannerResult)
	return Fb2Scanner{channel, channel, sync.WaitGroup{}, NewScannerContext()}
}

type TargetType string

const (
	FsDir      TargetType = "Directory"
	FsFile                = "File"
	ZipArchive            = "Zip Archive"
	//GzFile = "Gzip File"
)

type ScanTarget interface {
	Type() TargetType
	Spec() string
	Scan(ctx ScannerContext) <-chan ScannerResult
}

func (s *Fb2Scanner) Scan(target ScanTarget) {
	resultsChannel := target.Scan(s.ctx)
	s.scanTargetsWG.Add(1)
	go func() {
		defer s.scanTargetsWG.Done()
		for res := range resultsChannel {
			s.resultChannel <- res
		}
	}()
}

func (s *Fb2Scanner) WaitUntilFinish() {
	s.scanTargetsWG.Wait()
	close(s.resultChannel)
}