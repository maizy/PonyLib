alter table book
    add column fts_vectors tsvector
        generated always as (
            setweight(
                to_tsvector(
                    '{{FTS_LANGUAGE}}',
                    case when metadata #>> '{book,title}' is null then '' else metadata #>> '{book,title}' end
                ) ||
                to_tsvector(
                    '{{FTS_LANGUAGE}}',
                    case when metadata #> '{authors}' is null then '[]' :: jsonb else metadata #> '{authors}' end
                ),
                'A'
            ) ||
            setweight(
                to_tsvector(
                    '{{FTS_LANGUAGE}}',
                    case when not jsonb_path_exists(metadata, '$.sequences[*].name') then '[]' :: jsonb else jsonb_path_query_array(metadata, '$.sequences[*].name') end
                ),
                'B'
            ) ||
            setweight(
                to_tsvector(
                    '{{FTS_LANGUAGE}}',
                    case when metadata #>> '{annotation}' is null then '' else metadata #>> '{annotation}' end
                ) ||
                to_tsvector(
                    '{{FTS_LANGUAGE}}',
                    case when metadata #>> '{pub_info,publisher}' is null then '' else metadata #>> '{pub_info,publisher}' end
                ),
                'C'
            )
        ) stored;
