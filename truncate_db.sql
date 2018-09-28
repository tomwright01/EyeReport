CREATE OR REPLACE FUNCTION f_truncate_tables(_username text)
  RETURNS void AS
$func$
DECLARE
   _tbl text;
   _sch text;
BEGIN
   FOR _sch, _tbl IN 
      SELECT schemaname, tablename
      FROM   pg_tables
      WHERE  tableowner = _username
      AND    schemaname = 'public'
   LOOP
      RAISE NOTICE '%',
      -- EXECUTE  -- dangerous, test before you execute!
         format('TRUNCATE TABLE %I.%I CASCADE', _sch, _tbl);
   END LOOP;
END
$func$ LANGUAGE plpgsql;