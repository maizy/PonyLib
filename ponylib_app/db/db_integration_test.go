package db_test

import (
	"context"
	"net/url"
	"os"
	"testing"
	"time"

	"github.com/gofrs/uuid/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/require"

	"dev.maizy.ru/ponylib/fb2_parser"
	"dev.maizy.ru/ponylib/fb2_scanner/resource"
	"dev.maizy.ru/ponylib/ponylib_app/db"
	"dev.maizy.ru/ponylib/ponylib_app/search"
)

// TestPostgresRoundTrip uses an isolated schema in the explicitly supplied test database.
func TestPostgresRoundTrip(t *testing.T) {
	databaseURL := os.Getenv("PONYLIB_TEST_DATABASE_URL")
	if databaseURL == "" {
		t.Skip("set PONYLIB_TEST_DATABASE_URL to run PostgreSQL integration tests")
	}
	ctx, cancel := context.WithTimeout(t.Context(), 30*time.Second)
	defer cancel()
	admin, err := pgxpool.New(ctx, databaseURL)
	require.NoError(t, err)
	t.Cleanup(admin.Close)
	schema := "ponylib_test_" + uuid.Must(uuid.NewV4()).String()[0:8]
	_, err = admin.Exec(ctx, "create schema "+schema)
	require.NoError(t, err)
	t.Cleanup(func() {
		cleanupCtx, cleanupCancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cleanupCancel()
		_, err := admin.Exec(cleanupCtx, "drop schema "+schema+" cascade")
		require.NoError(t, err)
	})
	parsed, err := url.Parse(databaseURL)
	require.NoError(t, err)
	params := parsed.Query()
	params.Set("search_path", schema)
	params.Set("pool_max_conns", "1")
	params.Set("statement_timeout", "10000")
	parsed.RawQuery = params.Encode()
	t.Setenv("DATABASE_URL", parsed.String())
	t.Setenv("FTS_LANGUAGE", "english")
	pool, err := db.Connect()
	require.NoError(t, err)
	t.Cleanup(pool.Close)
	// A second migration run must also succeed with a single connection.
	require.NoError(t, db.Migrate(pool))
	require.NoError(t, db.Migrate(pool))
	targetID := uuid.Must(uuid.NewV4()).String()
	bookID := uuid.Must(uuid.NewV4()).String()
	rid := resource.RId{Scheme: "file", Path: "/library/example.fb2"}
	metadata := fb2_parser.Fb2Metadata{Book: &fb2_parser.Book{Title: "Galactic adventures", Lang: new("en")}}
	_, err = pool.Exec(ctx, "insert into target (id, scanned_at, rid) values ($1, now(), $2)", targetID, rid.String())
	require.NoError(t, err)
	_, err = pool.Exec(ctx, "insert into book (id, target_id, rid, metadata) values ($1, $2, $3, $4)", bookID, targetID, rid.String(), metadata)
	require.NoError(t, err)
	book, err := db.GetBook(pool, bookID)
	require.NoError(t, err)
	require.Equal(t, bookID, book.UUID)
	require.Equal(t, rid, book.RId)
	require.Equal(t, metadata, book.Metadata)
	query := &search.BookSearchQuery{TextMatch: "Galactic"}
	count, err := search.CountBooks(pool, query)
	require.NoError(t, err)
	require.Equal(t, 1, count)
	matches, err := search.SearchBooks(pool, query, 0, 10)
	require.NoError(t, err)
	require.Len(t, matches.Matches, 1)
	require.Equal(t, metadata, matches.Matches[0].Metadata)
	require.Equal(t, bookID, matches.Matches[0].UUID)
}
