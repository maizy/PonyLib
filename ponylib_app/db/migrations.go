package db

import (
	"context"
	"embed"
	"fmt"
	"log"
	"os"
	"path"
	"sort"
	"strings"

	"github.com/jackc/pgx/v4/pgxpool"
)

//go:embed db_migrations/*.sql
var migrationsFS embed.FS

const migrationDir = "db_migrations"
const migrationTable = "app_migrations"

type Migration struct {
	Id      string
	Content string
}

func getMigrations() ([]Migration, error) {
	entries, err := migrationsFS.ReadDir(migrationDir)
	if err != nil {
		return nil, fmt.Errorf("unable to open migrations dir: %w", err)
	}
	var migrations []Migration
	for _, entry := range entries {
		name := entry.Name()
		if entry.Type().IsRegular() {
			buf, err := migrationsFS.ReadFile(path.Join(migrationDir, name))
			if err == nil {
				migrations = append(
					migrations,
					Migration{Id: strings.TrimSuffix(name, ".sql"), Content: string(buf)},
				)
			} else {
				return nil, fmt.Errorf("unable to read migration %s: %w", name, err)
			}
		}
	}
	sort.SliceStable(migrations, func(i, j int) bool {
		return migrations[i].Id < migrations[j].Id
	})
	return migrations, nil
}

func getAppliedMigrationsIds(db *pgxpool.Pool) (map[string]bool, error) {
	rows, err := db.Query(context.Background(), fmt.Sprintf(`select id from "%s" order by id`, migrationTable))
	if err != nil {
		return nil, fmt.Errorf("unable to get applied migrations: %w", err)
	}
	defer rows.Close()
	applied := make(map[string]bool)
	for rows.Next() {
		var id string
		err = rows.Scan(&id)
		if err != nil {
			return nil, fmt.Errorf("unable to get applied migration id: %w", err)
		}
		applied[id] = true
	}
	if rows.Err() != nil {
		return nil, fmt.Errorf("unable to iterate over applied migrations: %w", rows.Err())
	}
	return applied, nil
}

func prepareMigration(content string) string {
	var ftsLanguage = os.Getenv("FTS_LANGUAGE")
	if ftsLanguage == "" {
		ftsLanguage = "english"
	}
	return strings.ReplaceAll(content, "{{FTS_LANGUAGE}}", ftsLanguage)
}

// Very simple migration processing
func Migrate(db *pgxpool.Pool) error {
	log.Println("start DB migration")
	migrations, err := getMigrations()
	if err != nil {
		return fmt.Errorf("unable to get migrations: %w", err)
	}
	dbVersion := len(migrations)

	_, err = db.Query(
		context.Background(),
		fmt.Sprintf(
			`create table if not exists "%s" (
				id varchar(255) not null primary key,
				applied_at timestamp with time zone not null
			)`,
			migrationTable,
		),
	)
	if err != nil {
		return fmt.Errorf("unable to create migration table: %w", err)
	}

	applied, err := getAppliedMigrationsIds(db)
	if err != nil {
		return fmt.Errorf("unable to get applied migrations: %w", err)
	}
	if len(applied) != dbVersion {
		log.Printf("expected %d migrations", dbVersion)
		log.Printf("found %d applied migrations", len(applied))
	}

	var processed int
	for _, migration := range migrations {
		if !applied[migration.Id] {
			log.Printf("apply migration: %s", migration.Id)
			if _, err := db.Exec(context.Background(), prepareMigration(migration.Content)); err != nil {
				return fmt.Errorf("unable to apply migration %s: %w", migration.Id, err)
			}
			_, err := db.Exec(context.Background(),
				fmt.Sprintf(`insert into "%s" (id, applied_at) values ($1, now())`, migrationTable),
				migration.Id)
			if err != nil {
				return fmt.Errorf(
					"unable to insert applied migration row for %s. DB will be in inconsistent state: %w",
					migration.Id, err)
			}
			processed++
		}
	}
	if processed > 0 {
		log.Printf("%d migrations have been applied", processed)
	} else {
		log.Println("DB migration done, nothing to do")
	}

	return nil
}
