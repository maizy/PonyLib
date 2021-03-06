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

func (s *Fb2Scanner) Scan(target ScanTarget) {
	targetResultsChannel := target.Scan(s.ctx)
	s.scanTargetsWG.Add(1)
	go func() {
		for res := range targetResultsChannel {
			s.resultChannel <- res
		}
		s.scanTargetsWG.Done()
	}()
}

func (s *Fb2Scanner) WaitUntilFinish() {
	s.scanTargetsWG.Wait()
	close(s.resultChannel)
}
