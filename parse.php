<?php

$instruction_set =array(
    "MOVE" => array("var", "symb", ),
    "CREATEFRAME" => array(),
    "PUSHFRAME" => array(),
    "POPFRAME" => array(),
    "DEFVAR" => array("var", ),
    "CALL" => array("label", ),
    "RETURN" => array(),
    "PUSHS" => array("symb", ),
    "POPS" => array("var", ),
    "ADD" => array("var","symb", "symb", ),
    "SUB" => array("var","symb", "symb", ),
    "MUL" => array("var","symb", "symb", ),
    "IDIV" => array("var","symb", "symb", ),
    "LT" => array("var","symb", "symb", ),
    "GT" => array("var","symb", "symb", ),
    "EQ" => array("var","symb", "symb", ),
    "AND" => array("var","symb", "symb", ),
    "OR" => array("var","symb", "symb", ),
    "NOT" => array("var","symb", ),
    "INT2CHAR" => array("var","symb", ),
    "STRI2INT" => array("var","symb", "symb", ),
    "READ" => array("var","type", ),
    "WRITE" => array("symb", ),
    "CONCAT" => array("var","symb", "symb", ),
    "STRLEN" => array("var","symb", ),
    "GETCHAR" => array("var","symb", "symb", ),
    "SETCHAR" => array("var","symb", "symb", ),
    "TYPE" => array("var","symb", ),
    "LABEL" => array("label", ),
    "JUMP" => array("label", ),
    "JUMPIFEQ" => array("label","symb", "symb", ),
    "JUMPIFNEQ" => array("label","symb", "symb", ),
    "EXIT" => array("symb", ),
    "DPRINT" => array("symb", ),
    "BREAK" => array(),

);

    function escaped($string ){
        //regex returns weird 2d array
        preg_match_all('/\\\\/',$string,$m1);
        preg_match_all('/\\\\\d{3}/',$string,$m2);
        return count($m1[0]) == count($m2[0]);

    }
    function sanitize($string){
        $string = str_replace('&','&amp;',$string);
        $string = str_replace('<','&lt;',$string);
        return str_replace('>','&gt;',$string);
    }

    function parseInput(){
        global $instruction_set;

        #debug purposes - prepsat $stdin na STDIN
        #stdin = fopen("ippcode","r");
        $stdin = STDIN;
        $line = fgets($stdin);

        #remove coment and strip
        $line = trim(preg_replace("/(?<!\\\\)#.*/",'',$line));
        if(!preg_match('/^.IPPcode21$/i',$line)){
            fprintf(STDERR,"wrong header\n");
            exit(21);
        }

        $ins_count = 1;
        $doc = new DOMDocument('1.0','UTF-8');
        $doc->formatOutput = true;
        $root = $doc->createElement('program');
        $root->setAttribute('language', "IPPcode21");
        $root = $doc->appendChild($root);

        while( $line = fgets($stdin)) {
            #remove comments
            $line = preg_replace("/(?<!\\\\)#.*/",'',$line);
            preg_match_all("/\S+/",$line, $matches);
            //regex returns weird 2d array
            $matches = $matches[0];
            if( count($matches) == 0)
                continue;
            $matches[0] = strtoupper($matches[0]);

            $inst = $doc->createElement('instruction');
            $inst->setAttribute('order',$ins_count);
            $inst->setAttribute('opcode',$matches[0]);
            $root->appendChild($inst);
            if(!array_key_exists($matches[0],$instruction_set)){
                fprintf(STDERR,"wrong instruction\n");
                exit(22);
            }
            if( count($instruction_set[$matches[0]]) != count($matches)-1){
                fprintf(STDERR, "operand error\n");
                exit(23);
            }
            #zpracovani argumentu instrukce
            $arg_count=1;
            foreach($instruction_set[$matches[0]] as $operand){
                $arg = $doc->createElement("arg$arg_count");
                switch ($operand){
                    case 'var':
                        if(!preg_match('/^(?:LF|GF|TF)@[a-zA-Z_\-$&%*!?][a-zA-Z_\-$&%*!?\d]*$/',$matches[$arg_count])){
                            fprintf(STDERR,"lexical error - var\n");
                            exit(23);
                        }
                        $type='var';
                        $value = $matches[$arg_count];
                        break;
                    case 'symb':
                        $at_pos = strpos($matches[$arg_count],'@');
                        if($at_pos == false){
                            fprintf(STDERR,"lexical error - symb/@");
                            exit(23);
                        }
                        $type=substr($matches[$arg_count],0,$at_pos);
                        $value = substr($matches[$arg_count],$at_pos+1,strlen($matches[$arg_count]));
                        switch ($type){
                            case 'int':
                                if(!preg_match('/^[+-]?[\d]+$/',$value)){
                                    fprintf(STDERR,"lexical error - int\n");
                                    exit(23);
                                }
                                break;
                            case 'bool':
                                if(!preg_match('/^true|false$/',$value)){
                                    fprintf(STDERR,"lexical error - bool\n");
                                    exit(23);
                                }
                                break;
                            case 'string':
                                if(!preg_match('/^\S*$/',$value) or !escaped($value) ){
                                    fprintf(STDERR,"lexical error - string\n");
                                    exit(23);
                                }
                                break;
                            case 'nil':
                                if(!preg_match('/^nil$/',$value)){
                                    fprintf(STDERR,"lexical error - nil\n");
                                    exit(23);
                                }
                                break;
                            default:
                                #symb muze byt promena
                                $type='var';
                                $value = $matches[$arg_count];
                                if(!preg_match('/^(?:LF|GF|TF)@[a-zA-Z_\-$&%*!?][a-zA-Z_\-$&%*!?\d]*$/',$value)){
                                    fprintf(STDERR,"lexical error - symb>var\n");
                                    exit(23);
                                }
                                break;
                        }
                        break;
                    case 'label':
                        if(!preg_match('/^[a-zA-Z_\-$&%*!?][a-zA-Z_\-$&%*!?\d]*$/',$matches[$arg_count])){
                            fprintf(STDERR,"lexical error - label\n");
                            exit(23);
                        }
                        $type='label';
                        $value = $matches[$arg_count];
                        break;
                    case 'type':
                        if(!preg_match('/^int|bool|string|nil$/',$matches[$arg_count])){
                            fprintf(STDERR,"lexical error - type\n");
                            exit(23);
                        }
                        $type='type';
                        $value = $matches[$arg_count];
                        break;
                    default: exit(99);
                }

                $value = sanitize($value);
                $arg->setAttribute('type',$type);
                $arg->nodeValue = $value;
                $inst->appendChild($arg);
                $arg_count++;
            }
            $ins_count++;
        }

        return $doc;
    }

    #main
    ini_set('display_errors', 'stderr');
    if($argc >= 2) {
        if ( ($argv[1] == '-h' or $argv[1] == '--help') and $argc == 2) {
            printf("this is help\n");
            exit(0);
        }
        else{
            printf("unrecognized command-line option\n");
            exit(10);
        }
    }
    $doc = parseInput();
    echo $doc->saveXML();

?>