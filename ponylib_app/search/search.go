package search

import (
	"context"
	"errors"
	"fmt"
	"strconv"

	"github.com/jackc/pgx/v4/pgxpool"

	"dev.maizy.ru/ponylib/fb2_parser"
	"dev.maizy.ru/ponylib/fb2_scanner/resource"
	"dev.maizy.ru/ponylib/ponylib_app"
)

type BookMatch struct {
	UUID     string
	RId      resource.RId
	Metadata fb2_parser.Fb2Metadata
	Position int
}

type BookSearchResult struct {
	Matches []BookMatch
	Offset  int
	Limit   int
}

func CountBooks(conn *pgxpool.Pool, query *BookSearchQuery) (int, error) {
	ftsQuery, params := buildBookSearchFTSQuery(query, 1)
	var sqlQuery = "select count(1) as cnt from book where " + ftsQuery + " @@ fts_vectors"
	var count int
	err := conn.QueryRow(context.Background(), sqlQuery, params...).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("query error: %w", err)
	}
	return count, nil
}

// pass limit=-1 to return all matches
func SearchBooks(conn *pgxpool.Pool, query *BookSearchQuery, offset int, limit int) (*BookSearchResult, error) {
	if offset < 0 {
		return nil, errors.New("offset cannot be lower than 0")
	}
	if limit == 0 {
		return &BookSearchResult{nil, offset, limit}, nil
	}
	var subsIndex = 1
	fts_query, params := buildBookSearchFTSQuery(query, subsIndex)
	subsIndex += len(params)
	var sqlQuery = "select" +
		"  id, rid, metadata " +
		"from book, " + fts_query + " as query " +
		"where query @@ fts_vectors " +
		"order by ts_rank_cd(fts_vectors, query) desc " +
		"offset $" + strconv.Itoa(subsIndex)
	params = append(params, offset)
	if limit > 0 {
		sqlQuery = sqlQuery + " limit $" + strconv.Itoa(subsIndex+1)
		params = append(params, limit)
	}

	rows, err := conn.Query(context.Background(), sqlQuery, params...)
	if err != nil {
		return nil, fmt.Errorf("unable to get search results: %w", err)
	}
	defer rows.Close()
	var matches []BookMatch
	position := offset
	for rows.Next() {
		position += 1
		var uuid string
		var rawRid string
		var metadata fb2_parser.Fb2Metadata
		err = rows.Scan(&uuid, &rawRid, &metadata)
		if err != nil {
			return nil, fmt.Errorf("unable to deserialize search result item for position %d: %w", position, err)
		}
		rid, err := resource.DecodeRId(rawRid)
		if err != nil {
			return nil, fmt.Errorf("unable to deserialize RId result item for position %d: %w", position, err)
		}
		matches = append(matches, BookMatch{UUID: uuid, RId: *rid, Metadata: metadata, Position: position})
	}
	if rows.Err() != nil {
		return nil, fmt.Errorf("unable to iterate over applied migrations: %w", rows.Err())
	}
	return &BookSearchResult{Matches: matches, Offset: offset, Limit: limit}, nil
}

func buildBookSearchFTSQuery(query *BookSearchQuery, substitutionIndex int) (string, []interface{}) {
	return "websearch_to_tsquery(" +
			"$" + strconv.Itoa(substitutionIndex) + ", " +
			"$" + strconv.Itoa(substitutionIndex+1) +
			")",
		[]interface{}{
			ponylib_app.GetFTSLanguage(),
			query.TextMatch,
		}
}
