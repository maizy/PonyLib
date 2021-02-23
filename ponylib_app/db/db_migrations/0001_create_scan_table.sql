create table scan (
    id uuid not null primary key,
    scanned_at timestamp with time zone not null,
    target text not null
);
