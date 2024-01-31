CREATE DATABASE gps_db;
\c gps_db ;


/* On donne tous les droits à l'utilisateur */
CREATE USER utilisateur WITH ENCRYPTED PASSWORD 'kafkacestcool';

/*On crée une table avec toutes les données nécessaires */
CREATE TABLE gps_data (
    id SERIAL PRIMARY KEY,
    ip VARCHAR(15),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    timestamp_ TIMESTAMP
);
GRANT ALL PRIVILEGES ON DATABASE gps_db TO utilisateur; 
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO utilisateur;
GRANT INSERT, DELETE, UPDATE, SELECT ON gps_data TO utilisateur;
