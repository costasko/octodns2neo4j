:auto USING PERIODIC COMMIT 2000
LOAD CSV FROM "file:///domains.csv" AS line
MERGE (z:Zone {value:line[0]})
MERGE (r:Record {value:line[1], rtype:line[2], owner:line[3]})
CREATE (z)-[:POINTS_TO]->(r)