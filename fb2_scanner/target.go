package fb2_scanner

import (
	"fmt"
	"os"

	"github.com/gofrs/uuid"

	"dev.maizy.ru/ponylib/fb2_scanner/resource"
	"dev.maizy.ru/ponylib/internal/u"
)

type TargetType string

const (
	FsDir      TargetType = "Directory"
	FsFile                = "File"
	ZipArchive            = "Zip Archive"
	//GzFile = "Gzip File"
)

type ScanTarget interface {
	Type() TargetType
	RId() resource.RId
	Scan(ctx ScannerContext) <-chan ScannerResult
	GetUUID() *string
}

func NewTargetFromEntryPath(entry string, withUUID bool) (ScanTarget, error) {
	stat, err := os.Stat(entry)
	if err != nil {
		return nil, fmt.Errorf("unable to open %s: %w", entry, err)
	}
	var target ScanTarget
	var targetUUID *string
	if withUUID {
		targetUUID = u.StrPtr(uuid.Must(uuid.NewV4()).String())
	}
	switch mode := stat.Mode(); {
	case mode.IsDir():
		target = &DirectoryTarget{entry, targetUUID}

	case mode.IsRegular():
		mayBeArchive := DetectSupportedArchive(entry)
		switch {
		case mayBeArchive != nil && *mayBeArchive == Zip:
			target = &ZipArchiveTarget{entry, targetUUID}
		default:
			target = &FileTarget{entry, targetUUID}
		}
	}
	if target == nil {
		panic("target not defined")
	}
	return target, nil
}
