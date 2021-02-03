import org.apache.spark.sql.types._
import org.apache.spark.sql.functions._
import spark.implicits._
import org.apache.spark.sql.Row
import org.graphframes._


val fretes = Seq(
                ("DF", "GO", 275, 200),
                ("DF", "RJ",1700, 1200),
                ("DF", "SP",1800, 1700),
                ("RJ", "DF",1700, 2000),
                ("RJ", "SP",150, 130),
                ("SP", "DF",1800, 2500),
                ("SP", "GO",1400, 1000),
                ("GO", "DF",275, 130),
                ("GO", "BH",780, 1300),
                ("BH", "DF",700, 800),
                ("BH", "SP",600, 700)
                ).toDF("UF_ori", "UF_dst", "Km", "Preco")

val fretes_key = fretes.withColumn("key_ori",md5(trim(upper(concat($"UF_ori"))))).
withColumn("key_dst",md5(trim(upper(concat($"UF_dst"))))).
select("key_ori","UF_ori", "key_dst","UF_dst", "Km", "Preco")

//fretes_key.show(false)


//Para gerar um DataFrame com elementos únicos, da coluna de origem e destino.

val estados = fretes_key.select("key_ori", "UF_ori").withColumnRenamed("key_ori", "keys").
withColumnRenamed("UF_ori", "UF").
union(fretes_key.select("key_dst","UF_dst").withColumnRenamed("key_dst", "keys")).
withColumnRenamed("UF_dst", "UF").
groupBy("keys","UF").count().sort(asc("UF")).
select("keys","UF","count")

//estados.show(false)



fretes_key.drop("UF_ori").drop("UF_dst").createOrReplaceTempView("tbl_fretes")
estados.createOrReplaceTempView("tbl_estados")

spark.sql("SELECT * FROM tbl_fretes").show(false)
spark.sql("SELECT * FROM tbl_estados").show(false)


spark.sql("SELECT e1.UF as src, e2.UF as dst, Km, Preco, Preco/km AS Preco_KM FROM tbl_fretes f " +
  "INNER JOIN tbl_estados e1 ON e1.keys = f.key_ori " +
  "INNER JOIN tbl_estados e2 ON e2.keys = f.key_dst").
show(false)

val vertices = spark.sql("SELECT keys as id FROM tbl_estados")
val arestas = spark.sql("SELECT key_ori AS src, key_dst as dst FROM tbl_fretes")

val gx_fretes = GraphFrame(vertices, arestas)


gx_fretes.inDegrees.createOrReplaceTempView("tbl_indegrees")
gx_fretes.outDegrees.createOrReplaceTempView("tbl_outdegrees")

spark.sql("SELECT e.UF, f.inDegree AS Recebe FROM tbl_indegrees f " +
  "INNER JOIN tbl_estados e ON f.id = e.keys").
show()

spark.sql("SELECT e.UF, f.outDegree as Destina FROM tbl_outdegrees f " +
  "INNER JOIN tbl_estados e ON f.id = e.keys").
show()


gx_fretes.triangleCount.run().createOrReplaceTempView("tbl_triangle_count")

spark.sql("SELECT e.UF, f.count as qtd_triangulos FROM tbl_triangle_count f " +
  "INNER JOIN tbl_estados e ON f.id = e.keys").
show()


//fretes_key_clean.show(false)
//estados.show(false)
/*
gx_fretes.vertices.show(false)
gx_fretes.edges.show(false)
gx_fretes.inDegrees.show(false)
gx_fretes.outDegrees.show(false)
gx_fretes.edges.filter("src == 2").show()
gx_fretes.outDegrees.filter("src == 2")show(false)
gx_fretes.edges.filter("src == 2").count()
gx_fretes.inDegrees.filter("inDegree >= 10").show(false)
gx_fretes.inDegrees.groupBy("inDegree").count().sort(desc("inDegree")).show(false)
gx_fretes.outDegrees.groupBy("outDegree").count().sort(desc("outDegree")).show(false)
val result = gx_fretes.stronglyConnectedComponents.maxIter(5).run()

*/

/*

#Caso queiroa inserir numero de linhas mas a função window move todos os dados para um simples partição.

import org.apache.spark.sql.expressions.Window

val estados = fretes_key.select("key_ori", "UF_ori").withColumnRenamed("key_ori", "keys_distintas").
withColumnRenamed("UF_ori", "UF").
union(fretes_key.select("key_dst","UF_dst").withColumnRenamed("key_dst", "keys_distintas")).
withColumnRenamed("UF_dst", "UF").
groupBy("keys_distintas","UF").count().sort(asc("UF")).
withColumn("index", row_number() over Window.orderBy("UF")).
select("index","keys_distintas","UF","count")
*/


//fretes.withColumn("hash_value",sha2(concat($"UF_ori"),256)).show(false)

/*
fretes_key.select("key_ori","UF_ori").withColumnRenamed("key_ori", "keys_distintas").
withColumnRenamed("UF_ori", "UF").
union(fretes_key.select("key_dst", "UF_dst").withColumnRenamed("key_ori", "keys_distintas").
withColumnRenamed(("UF_dst", "UF").
distinct.show(false)
*/

/*
spark-shell -i --master "spark://spark-master:7077" --name "Graphframe" --packages graphframes:graphframes:0.8.1-spark3.0-s_2.12 --driver-memory 10G --executor-memory 5G
:load /opt/workspace/scripts/fretes.scala
*/