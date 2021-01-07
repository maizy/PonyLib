package fb2_scanner

import (
	"runtime"

	"dev.maizy.ru/ponylib/internal/u"
)

type ScannerContext struct {
	openFileSemaphore chan struct{}
}

func (c *ScannerContext) AquireFileSemaphore() {
	c.openFileSemaphore <- struct{}{}
}

func (c *ScannerContext) ReleaseFileSemaphore() {
	<-c.openFileSemaphore
}

func NewScannerContext() ScannerContext {
	return ScannerContext{make(chan struct{}, u.IntMax(runtime.NumCPU(), 4))}
}
