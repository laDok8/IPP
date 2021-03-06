<?php

#check file existence and readability
function tryopen($file,$mode,$ret){
    $fp = fopen($file,$mode) or exit($ret);
    fclose($fp);
}
#MAIN

#parsing arguments
ini_set('display_errors', 'stderr');
$longopts  = array(
    "help",
    "directory:",
    "recursive",
    "parse-script:",
    "int-script:",
    "parse-only",
    "int-only",
    "jexamxml:",
    "jexamcfg:"
);
$options = getopt("hd:r", $longopts);
if(array_key_exists('h',$options) or  array_key_exists('help',$options)){
    if($argc > 2){
        fprintf(STDERR,"arg error\n");
        exit(10);
    }
    echo "usage: test.php [-h] [-d DIRECTORY] [-r] [--parse-script PARSER] [--int-script INTERPRET] [--parse-only] [--int-only] [--jexamxml JEXAMXML] [--jexamcfg JEXAMCFG]\n
IPP performs automatic interepret test consists from up to 4 files .src and optional ( .in .out .rc) 
results are stored in .HTML file in working directory\n
optional arguments:
  -h, --help                    show this help message and exit
  -d , --directory DIRECTORY    specify directory with test files
  -r , --recursive              also search for test in subdirectories
  --parse-script PARSER         specify parser file, defaults to 'parse.php'
  --int-script INTERPRET        specify interpret file, defaults to 'interpret.py'
  --parse-only                  run only parser
  --int-only                    run only interpret
  --jexamxml JEXAMXML           specify A7Soft .jar file, defaults to '/pub/courses/ipp/jexamxml/jexamxml.jar'
  --jexamcfg JEXAMCFG           specify A7Soft cfg file, defaults to '/pub/courses/ipp/jexamxml/options'";
    exit(0);
}
$dir = '.';
if(array_key_exists('d',$options))
   $dir = $options['d'];

if(array_key_exists('directory',$options))
    $dir = $options['directory'];
if(!is_dir($dir))
    exit(41);

$parse_script = 'parse.php';
if(array_key_exists('parse-script',$options))
    $parse_script = $options['parse-script'];
tryopen($parse_script,'r',41);

$int_script = 'interpret.py';
if(array_key_exists('int-script',$options))
    $int_script = $options['int-script'];
tryopen($int_script,'r',41);

$parse_only = false;
if(array_key_exists('parse-only',$options))
    $parse_only = true;

$int_only = false;
if(array_key_exists('int-only',$options))
    $int_only = true;

$jexamxml = '/pub/courses/ipp/jexamxml/jexamxml.jar';
if(array_key_exists('jexamxml',$options))
    $jexamxml = $options['jexamxml'];

$jexamcfg = '/pub/courses/ipp/jexamxml/options';
if(array_key_exists('jexamcfg',$options))
    $jexamcfg = $options['jexamcfg'];

$recurse = false;
if(array_key_exists('recursive',$options) or array_key_exists('r',$options))
    $recurse = true;

if($int_only and $parse_only)
    exit(41);


//files contains all found files and their paths
//$files[i]['path'], $files[i]['filename'],
$iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dir));
if($recurse == false)
    $iterator->setMaxDepth(0);
$files = [];
foreach ($iterator as $filename => $file) {
    $path = pathinfo($filename);
    #we only need existence of src file ( assuming all other files are in same directory)
    if(array_key_exists('extension',$path) == false or $path['extension'] != 'src')
        continue;
    $files[] = array('path' => $path['dirname'],'filename' => $path['filename']);
}

#create HTML header
$dom = new DOMDocument('1.0');
$dom->formatOutput = true;
$html = $dom->createElement('html');
$dom->appendChild($html);
$head = $dom->createElement('head');
$head->appendChild($dom->createElement('title','Vyhodnoceni testu IPP'));
$meta = $dom->createElement('meta');
$meta->setAttribute('charset','UTF-8');
$head->appendChild($meta);
$html->appendChild($head);
$body = $dom->createElement('body');
$html->appendChild($body);
$css = '.green{color:#008000;}
        .red{color:#ef2c2c}
        body{background-color:#f2f2f2}
        h1{text-align: center;}
        #body,h1,h2,h3,h4,h5,h6{font-family: Arial,Helvetica,Arial,sans-serif;margin: 0 0 25px 0;}
        div{margin: 12px 25px 75px 100px;display: flex;flex-wrap: wrap;}
        div > p {margin: 0 0 10px 10px;}';
$style = $dom->createElement('style', $css);
$body->appendChild($style);
$header = $dom->createElement('h1', 'vysledky automatickych testu IPP21');
$body->appendChild($header);

$pass_count = 0;
$fail_count = 0;
$res_arr =[];
#testing
if($parse_only == true) {
    $delta = tempnam('.','IPP21_delta');
}
foreach ($files as $iter){
    $retval = null;
    $output = null;
    $file = $iter['filename'];
    $path = $iter['path'];
    $tmp = tempnam('.','IPP21');

    $p = $dom->createElement('p',"$file");

    #check readability
    if(!is_readable($path))
        exit(41);
    tryopen("$path/$file.src",'r',11);
    #create empty .in .out and .rc
    if(file_exists("$path/$file.in") == false)
        tryopen("$path/$file.in",'w',11);
    if(file_exists("$path/$file.out") == false)
        tryopen("$path/$file.out",'w',11);
    $frc = null;
    if(file_exists("$path/$file.rc") == false) {
        $frc = fopen("$path/$file.rc",'w+') or exit(11);
        fwrite($frc, '0');
    }
    else
        $frc = fopen("$path/$file.rc",'r') or exit(11);

    #expected retval
    fseek($frc,0,SEEK_SET);
    $rcval = intval(fread($frc,filesize("$path/$file.rc")));
    $pass = true;
    fclose($frc);

    if($parse_only == true){
        #file exist ?
        tryopen($jexamxml,'r',41);
        tryopen($jexamcfg,'r',41);
        exec("php $parse_script < $path/$file.src > $tmp",$output,$retval);
        if( $retval == 0 || $retval!=$rcval)
            exec("timeout 1s java -jar $jexamxml $tmp $path/$file.out $delta $jexamcfg", $output, $retval);
        if($retval==$rcval){
            $pass_count++;
            $p->setAttribute('class','green');
        } else{
            $fail_count++;
            $p->setAttribute('class','red');
        }
    } elseif($int_only == true){
        exec("python3 $int_script --source $path/$file.src  --input $path/$file.in > $tmp",$output,$retval);
        if($retval == 0 || $retval!=$rcval){
            exec("timeout 1s diff $path/$file.out $tmp",$output,$retval);
        }
        if($retval==$rcval){
            $pass_count++;
            $p->setAttribute('class', 'green');
        } else{
            $fail_count++;
            $p->setAttribute('class','red');
        }
    } else{
        $tmp_out = tempnam('.','IPP21_2');
        #parse & int
        exec("php $parse_script < $path/$file.src > $tmp",$output,$retval);
        if( $retval == 0 || $retval!=$rcval)
            exec("timeout 3s python3 $int_script --source $tmp  --input $path/$file.in > $tmp_out",$output,$retval);
        if( $retval == 0 || $retval!=$rcval)
            exec("timeout 1s diff $path/$file.out $tmp_out",$output,$retval);
        if($retval==$rcval) {
            $pass_count++;
            $p->setAttribute('class', 'green');
        }else{
            $fail_count++;
            $p->setAttribute('class','red');
        }

        unlink($tmp_out);
    }
    #add files to dir structure for HTML creation
    if(!array_key_exists($path,$res_arr))
        $res_arr[$path] = [];
    array_push($res_arr[$path],$p);
    unlink($tmp);

}
if($parse_only == true){
    unlink($delta);
}

#total test info
$total_count = $pass_count+$fail_count;
$sum = $dom->createElement('p',"passed: $pass_count / $total_count");
$sum->setAttribute('class','green');
$body->appendChild($sum);
$sum = $dom->createElement('p',"failed: $fail_count / $total_count");
$sum->setAttribute('class','red');
$body->appendChild($sum);
$sum = $dom->createElement('p',"___________________________________________");
$body->appendChild($sum);

#outputing each dir separately
foreach($res_arr as $key => $res_dirs){
    $h2 = $dom->createElement('h2',"$key");
    $body->appendChild($h2);
    $div = $dom->createElement('div');
    $body->appendChild($div);
    $pass_count = 0;
    $fail_count = 0;
    foreach($res_dirs as $result){
        $div->appendChild($result);
        $clr = $result->getAttribute('class');
        if($clr == 'green'){
            $pass_count++;
        } else{
            $fail_count++;
        }
    }
    $total_count = $pass_count+$fail_count;
    $sum = $dom->createElement('p',"passed: $pass_count / $total_count");
    $sum->setAttribute('class','green');
    $body->appendChild($sum);
    $sum = $dom->createElement('p',"failed: $fail_count / $total_count \n");
    $sum->setAttribute('class','red');
    $body->appendChild($sum);
}

#outputing html file
echo $dom->saveHTML();
?>