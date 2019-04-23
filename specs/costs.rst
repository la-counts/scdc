Estimated Hosting Costs
=======================

Based on AWS pricing in the US-West Oregon region:
https://calculator.s3.amazonaws.com/index.html


Each service hosted on a seperate instance:

+------+--------+----------------------+
|$16.84| web    |t2.small              |
+------+--------+----------------------+
|$26.36| search |t2.small.elasticsearch|
+------+--------+----------------------+
|$24.89| cache  |cache.t2.small (redis)|
+------+--------+----------------------+
|$26.36| db     |db.t2.small (postgres)|
+------+--------+----------------------+

Total: $94.45 Total Ram: 8GB

Alternatively host search & cache on the same instance:

+------+-------+---------------------------------------+
|$68.81| docker| t2.large (web + elasticsearch + redis)|
+------+-------+---------------------------------------+
|$26.36| db    | db.t2.small (postgres)                |
+------+-------+---------------------------------------+

Total $95.17  Total Ram: 10GB

A slimmer alternative:

+------+-------+----------------------------------------+
|$34.41| docker| t2.medium (web + elasticsearch + redis)|
+------+-------+----------------------------------------+
|$26.36| db    | db.t2.small (postgres)                 |
+------+-------+----------------------------------------+

Total $60.77  Total Ram: 6GB
