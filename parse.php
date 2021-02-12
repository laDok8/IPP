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
    "NOT" => array("var","symb", "symb", ),
    "INT2CHAR" => array("var","symb", ),
    "STR2INT" => array("var","symb", "symb", ),
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

    function parseInput(){
        global $instruction_set;

        #debug purposes - prepsat $stdin na STDIN
        $stdin = fopen("ippcode","r");
        $line = fgets($stdin);
        if($line != ".IPPcode21\n"){
            fprintf(STDERR,"wrong header");
            exit(21);
        }

        $ins_count = 1;
        $doc = new DOMDocument();
        $doc->encoding = "UTF-8";
        $doc->formatOutput = true;
        $root = $doc->createElement('program');
        $root->setAttribute('language', "IPPcode21");
        $root = $doc->appendChild($root);

        while( $line = fgets($stdin)) {
            preg_match_all("/\S+/",$line, $matches);
            //regex returns weird 2d array
            $matches = $matches[0];
            if( $matches[0][0] == '#')
                continue;

            $inst = $doc->createElement('instruction');
            $inst->setAttribute('order',$ins_count);
            $inst->setAttribute('opcode',$matches[0]);
            $root->appendChild($inst);

            if(!array_key_exists($matches[0],$instruction_set)){
                fprintf(STDERR,"wrong instruction");
                exit(22);
            }
            $arg_count=1;
            foreach($instruction_set[$matches[0]] as $operand){
                $arg = $doc->createElement("arg$arg_count");
                #TODO validovat regex a vyresit string zameny ???
                switch ($operand){
                    case 'var':
                        if(!preg_match('/^(?:LF|GF|TF)@[a-zA-Z_$%][a-zA-Z_$0-9%]*$/',$matches[$arg_count])){
                            fprintf(STDERR,"lexical error - var");
                            exit(23);
                        }
                        $type='var';
                        $value = $matches[$arg_count];
                        break;
                    case 'symb':
                        $type=explode("@",$matches[$arg_count])[0];
                        $value = explode("@",$matches[$arg_count])[1];
                        switch ($type){
                            case 'int':
                                if(!preg_match('/^[0-9]+$/',$value)){
                                    fprintf(STDERR,"lexical error - int");
                                    exit(23);
                                }
                                break;
                            case 'bool':
                                if(!preg_match('/^true|false$/',$value)){
                                    fprintf(STDERR,"lexical error - bool");
                                    exit(23);
                                }
                                break;
                            case 'string':
                                if(!preg_match('/^\S*$/',$value)){
                                    fprintf(STDERR,"lexical error - string");
                                    exit(23);
                                }
                                break;
                            case 'nil':
                                if(!preg_match('/^nil$/',$value)){
                                    fprintf(STDERR,"lexical error - nil");
                                    exit(23);
                                }
                                break;
                            default:
                                #symb can also by variable
                                $type='var';
                                $value = $matches[$arg_count];
                                if(!preg_match('/^(?:LF|GF|TF)@[a-zA-Z_$%][a-zA-Z_$0-9%]*$/',$value)){
                                    fprintf(STDERR,"lexical error - symb>var");
                                    exit(23);
                                }
                                break;
                        }
                        break;
                    case 'label':
                        if(!preg_match('/^[a-zA-Z_$%][a-zA-Z_$0-9%]*$/',$matches[$arg_count])){
                            fprintf(STDERR,"lexical error - label");
                            exit(23);
                        }
                        $type='label';
                        $value = $matches[$arg_count];
                        break;
                    case 'type':
                        if(!preg_match('/^string@(?:int|bool|string|nil)$/',$matches[$arg_count])){
                            fprintf(STDERR,"lexical error - type");
                            exit(23);
                        }
                        $type='type';
                        $value = explode("@",$matches[$arg_count])[1];
                        break;
                    default: exit(99);
                }

                $arg->setAttribute('type',$type);
                $arg->nodeValue = $value;
                $inst->appendChild($arg);
                if( !array_key_exists($arg_count, $matches) or $matches[$arg_count][0] == '#'){
                    fprintf(STDERR,"operand missing");
                    exit(23);
                }
                $arg_count++;
            }
            if(array_key_exists($arg_count, $matches) and $matches[$arg_count][0] != '#' ){
                fprintf(STDERR, "operand error");
                exit(23);
            }
            $ins_count++;
        }







        printf($doc->saveXML());
    }

    #main
    ini_set('display_errors', 'stderr');
    if($argc > 2) {
        if ($argv[1] == '-h' or $argv[1] == '--help') {
            printf("this is help");
            exit(0);
        }
        else{
            printf("unrecognized command-line option");
            exit(10);
        }
    }
    parseInput();


?>