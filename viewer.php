<?php
$link = mysql_connect("localhost","user","passwd")
or die(mysql_error());

mysql_select_db("jabberlogbot")
or die (mysql_error());


function display_db_table($tablename, $connection)
{
$query_string = "SELECT * FROM $tablename";
$result_id = mysql_query($query_string, $connection);
$column_count = mysql_num_fields($result_id);
print("<TABLE BORDER=1>\n");
while ($row = mysql_fetch_row($result_id))
{
print("<TR ALIGN=LEFT VALIGN=TOP>");
for ($column_num = 0;
$column_num < $column_count;
$column_num++)
print("<TD>$row[$column_num]</TD>\n");
print("</TR>\n");
}
print("</TABLE>\n");
}
?>
<HTML>
<HEAD>
<TITLE>messages</TITLE>
</HEAD>
<BODY>
<TABLE><TR><TD>
<?php display_db_table("logs", $link); ?>
</TD><TD>
</TABLE></BODY></HTML>