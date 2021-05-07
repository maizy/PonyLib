package db

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v4/pgxpool"

	"dev.maizy.ru/ponylib/fb2_parser"
	"dev.maizy.ru/ponylib/fb2_scanner/resource"
)

type BookResult struct {
	UUID     string
	RId      resource.RId
	Metadata fb2_parser.Fb2Metadata
}

func GetBook(conn *pgxpool.Pool, uuid string) (*BookResult, error) {
	var sqlQuery = "select id, rid, metadata from book where id = $1 limit 1"
	rows, err := conn.Query(context.Background(), sqlQuery, uuid)
	if err != nil {
		return nil, fmt.Errorf("unable to get book by uuid='%s': %w", uuid, err)
	}
	defer rows.Close()

	var uuidFromDb string
	var rawRId string
	var bookMetadata fb2_parser.Fb2Metadata
	rows.Next()
	if err := rows.Scan(&uuidFromDb, &rawRId, &bookMetadata); err != nil {
		return nil, fmt.Errorf("book with uuid='%s' not found", uuid)
	}

	bookRId, err := resource.DecodeRId(rawRId)
	if err != nil {
		return nil, fmt.Errorf("unable to deserialize RId for book with uuid='%s': %w", uuid, err)
	}

	return &BookResult{uuidFromDb, *bookRId, bookMetadata}, nil
}
