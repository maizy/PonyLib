create table target (
    id uuid not null primary key,
    scanned_at timestamp with time zone not null,
    rid text not null
);
