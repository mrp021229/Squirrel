SELECT percentile_cont ( v1 ) OVER w , json_object_agg ( v1 ) OVER w FROM v0 WINDOW v2 AS ( PARTITION BY v1 ORDER BY v1 DESC ) ;
