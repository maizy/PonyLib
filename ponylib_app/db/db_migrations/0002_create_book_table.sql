create table book (
    id uuid primary key,
    target_id uuid not null references target,
    rid text not null,
    metadata jsonb not null
);
