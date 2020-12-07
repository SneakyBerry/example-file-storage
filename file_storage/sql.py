def upload_data_query():
    """
    Insert new data and return hash.

    On case when hash already exists.
    """
    return """SELECT hash FROM upload_file($1) hash;"""


def insert_meta_query():
    """Save meta data for uploaded file."""
    return """
    INSERT INTO files_meta (uuid, content_type, hash) VALUES ($1, $2, $3);
    """


def retrieve_data_by_uuid():
    """Retrieve file by uuid."""
    return """
    SELECT 
        uf.data, 
        files_meta.content_type 
    FROM files_meta 
    JOIN uploaded_files uf ON uf.hash = files_meta.hash 
    WHERE uuid = $1;
    """
