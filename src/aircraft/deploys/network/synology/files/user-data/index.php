<?php
error_log($_SERVER['REMOTE_ADDR']);
error_log($_SERVER['REQUEST_METHOD'] . ' ' . $_SERVER['REQUEST_URI']);
error_log($_SERVER['QUERY_STRING']);
$headers =  getallheaders();
foreach($headers as $key=>$val){
  error_log ($key . ': ' . $val);
}
readfile($_SERVER['REMOTE_ADDR'])
?>
