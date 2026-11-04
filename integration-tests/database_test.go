//go:build integration

package integration_test

import (
	"context"
	"net/url"
	"os"
	"testing"
	"time"

	"github.com/gofrs/uuid/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/require"
)

func isolatedDatabase(t *testing.T) string {
	t.Helper()
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
	return parsed.String()
}
