"""

"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS "uploaded_files" (
            "id" BIGSERIAL PRIMARY KEY,
            "data" bytea NOT NULL,
            "hash" varchar(32) NOT NULL
        );
        COMMENT ON TABLE "uploaded_files" IS 'Mapping hash to uploaded file.';
        CREATE UNIQUE INDEX uploaded_files_hash_idx ON uploaded_files (hash); 
        CREATE TABLE IF NOT EXISTS "files_meta" (
            "id" BIGSERIAL PRIMARY KEY,
            "uuid" uuid NOT NULL UNIQUE,
            "content_type" TEXT NOT NULL,
            "hash" varchar(32),
        FOREIGN KEY (hash) REFERENCES uploaded_files (hash) 
        );
        COMMENT ON TABLE "files_meta" IS 'Mapping uuid to name and hash of uploaded file.';
        CREATE UNIQUE INDEX files_meta_uuid ON files_meta (uuid); 
        
        -- Database procedure for update file to database and get hash
        CREATE OR REPLACE FUNCTION upload_file(data bytea) RETURNS varchar(32) as $$
        DECLARE computed_hash varchar(32);
        BEGIN 
            computed_hash = md5(data);
            INSERT INTO uploaded_files (data, hash) VALUES (data::bytea, computed_hash)
            ON CONFLICT (hash) DO NOTHING;
            RETURN computed_hash;
        END;
        $$ LANGUAGE plpgsql;
        """,
        """
        DROP TABLE IF EXISTS "files_meta" CASCADE;
        DROP INDEX IF EXISTS "files_meta_uuid";
        DROP TABLE IF EXISTS "uploaded_files" CASCADE;
        DROP INDEX IF EXISTS "uploaded_files_hash_idx";
        DROP FUNCTION IF EXISTS "upload_file";
        """,
    )
]
