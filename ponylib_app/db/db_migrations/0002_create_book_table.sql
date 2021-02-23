create table book (
    id uuid primary key,
    scan_id uuid not null,
    metadata jsonb not null
);
