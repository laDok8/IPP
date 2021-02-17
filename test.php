<?php
#main
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
  -r , recursive                also search for test in subdirectories
  --parse-script PARSER         specify parser file, defaults to 'parse.php'
  --int-script INTERPRET        specify interpret file, defaults to 'interpret.py'
  --parse-only                  run only parser
  --int-only                    run only interpret
  --jexamxml JEXAMXML           specify A7Soft .jar file, defaults to '/pub/courses/ipp/jexamxml/jexamxml.jar'
  --jexamcfg JEXAMCFG           specify A7Soft cfg file, defaults to '/pub/courses/ipp/jexamxml/options'";
    exit(0);
}
$dir = '.';#getcwd()
if(array_key_exists('d',$options))
   $dir = $options['d'];

if(array_key_exists('directory',$options))
    $dir = $options['directory'];
if(!is_dir($dir))
    exit(41);

$parse_script = 'parse.php';
if(array_key_exists('parse_script',$options))
    $parse_script = $options['parse_script'];
fopen($parse_script,'r') or exit(41);

$int_script = 'interpret.py';
if(array_key_exists('int-script',$options))
    $int_script = $options['int-script'];
fopen($int_script,'r') or exit(41);

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
$iterator = new RecursiveDirectoryIterator($dir);
$files = [];
foreach ($iterator as $filename => $file) {
    $path = pathinfo($filename);
    if($path['filename'] == '.' or $path['basename'] == '.')
        continue;
    if($recurse == false and $path['dirname'] != $dir)
        continue;
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
        div{margin: 12px 25px 75px 100px;}';
$style = $dom->createElement('style', $css);
$body->appendChild($style);
$header = $dom->createElement('h1', 'vysledky automatickych testu IPP21');
$body->appendChild($header);

$pass_count = 0;
$fail_count = 0;
#testing
foreach ($files as $iter){
    $retval = null;
    $output = null;
    $file = $iter['filename'];
    $path = $iter['path'];
    $tmp = tempnam('.','IPP21');

    $p = $dom->createElement('p',"$dir/$file.src");
    $body->appendChild($p);

    #create empty .in .out and .rc
    if(file_exists("$dir/$file.in") == false)
        fopen("$dir/$file.in",'w');
    if(file_exists("$dir/$file.out") == false)
        fopen("$dir/$file.out",'w');
    $frc = null;
    if(file_exists("$dir/$file.rc") == false) {
        $frc = fopen("$dir/$file.rc",'w+');
        fwrite($frc, '0');
    }
    else
        $frc = fopen("$dir/$file.rc",'r');

    #expected retval
    $rcval = intval(fread($frc,filesize("$dir/$file.rc")));
    $pass = true;

    if($parse_only == true){
        #file exist ?
        fopen($jexamxml,'r') or exit(41);
        if(!is_dir($jexamcfg))
            exit(41);

        exec("php $parse_script < $dir/$file.src > $tmp",$output,$retval);
        if( $retval == 0 || $retval!=$rcval)
            #java -jar /pub/courses/ipp/jexamxml/jexamxml.jar vas_vystup.xml referencni.xml delta.xml /pub/courses/ipp/jexamxml/options
            exec("timeout 1s java -jar $jexamxml $tmp $dir/$file.out delta.xml $jexamcfg", $output, $retval);
        if($retval == 0 || $retval==$rcval){
            $pass_count++;
            $p->setAttribute('class','green');
        } else{
            $fail_count++;
            $p->setAttribute('class','red');
        }
    } elseif($int_only == true){
        exec("python3 $int_script --source $dir/$file.src  --input $dir/$file.in > $tmp",$output,$retval);
        if($retval == 0 || $retval!=$rcval){
            exec("timeout 1s diff $dir/$file.out $tmp",$output,$retval);
        }
        if($retval == 0 || $retval==$rcval){
            $pass_count++;
            $p->setAttribute('class', 'green');
        } else{
            $fail_count++;
            $p->setAttribute('class','red');
        }
    } else{
        $tmp_out = tempnam('.','IPP21_2');
        #parse & int

        exec("php $parse_script < $dir/$file.src > $tmp",$output,$retval);
        if( $retval == 0 || $retval!=$rcval)
            exec("timeout 5s python3 $int_script --source $tmp  --input $dir/$file.in > $tmp_out",$output,$retval);
        if( $retval == 0 || $retval!=$rcval)
            exec("timeout 1s diff $dir/$file.out $tmp_out",$output,$retval);
        if( $retval == 0 || $retval==$rcval) {
            $pass_count++;
            $p->setAttribute('class', 'green');
        }else{
            $fail_count++;
            $p->setAttribute('class','red');
        }

        unlink($tmp_out);
    }




    unlink($tmp);

}




$total_count = $pass_count+$fail_count;
$sum = $dom->createElement('p',"___________________________________________");
$body->appendChild($sum);
$sum = $dom->createElement('p',"passed: $pass_count / $total_count");
$sum->setAttribute('class','green');
$body->appendChild($sum);
$sum = $dom->createElement('p',"failed: $fail_count / $total_count");
$sum->setAttribute('class','red');
$body->appendChild($sum);

$html_file = fopen('tests.html','w');
fprintf($html_file,"<!DOCTYPE html>\n".$dom->saveHTML());
?>