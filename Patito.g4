grammar Patito;

// Reglas de sintaxis
programa: p v f inicio cuerpo 'fin';
inicio: 'inicio';
p: 'programa' ID END_STM;
v: vars?;
f: funcs*;

cuerpo: '{' (e*)? '}' | e*;
e: estatuto;

asigna: ID '=' expresion END_STM;

expresion: exp (bo exp)?;
bo: OP_MAYOR | OP_MENOR | OP_MAYOR_IGUAL | OP_MENOR_IGUAL | OP_DIFERENTE | OP_IGUAL_IGUAL;

cte: NUMERO | 'cte_ent' | 'cte_float';

estatuto: asigna
        | condicion
        | ciclo
        | llamada
        | imprime
        | funcs;

exp: termino (op termino)*;
op: OP_SUMA | OP_RESTA;

termino: factor (of factor)*;
of: OP_DIV | OP_MUL;

funcs: 'nula' ID '(' param ')' '{' d_v? cuerpo '}' END_STM;
param: (ID ':' tipo (',' ID ':' tipo)*)?;
d_v: vars?;

tipo: 'entero' | 'flotante';

vars: 'vars' d;
d: ID (',' ID)* ':' tipo END_STM (d)?;

imprime: 'escribe' '(' param_imp ')' END_STM;
param_imp: expresion | LETRERO (',' param_imp)?;

ciclo: 'mientras' '(' expresion ')' 'haz' cuerpo END_STM;

condicion: 'si' '(' expresion ')' cuerpo e_c END_STM;
e_c: ('sino' cuerpo)?;

llamada: ID '(' e_l ')' END_STM;
e_l: (expresion (',' expresion)*)?;

factor: '(' expresion ')'
      | sign cte
      | ID
      | NUMERO;
sign: OP_SUMA | OP_RESTA;

// Definición de Tokens
ID : [a-zA-Z_][a-zA-Z_0-9]* ;
OP_SUMA: '+' ;
OP_RESTA: '-' ;
OP_MUL: '*' ;
OP_DIV: '/' ;
OP_MAYOR: '>' ;
OP_MENOR: '<' ;
OP_MAYOR_IGUAL: '>=' ;
OP_MENOR_IGUAL: '<=' ;
OP_IGUAL_IGUAL: '==' ;
OP_DIFERENTE: '!=' ;
END_STM: ';' ;
LETRERO : '"' ~["\r\n]* '"' ;
NUMERO: [0-9]+ ('.' [0-9]+)?;
WS: [ \t\r\n]+ -> skip ;
COMMENT: '//' ~[\r\n]* -> skip;