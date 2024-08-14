use std::rc::Rc;

use super::{
    exception::JMCError,
    lexer::Lexer,
    tokenizer::{Token, Tokenizer},
};

#[derive(Debug)]
pub struct FuncContent<'header, 'config, 'lexer> {
    lexer: &'lexer mut Lexer<'header, 'config, 'lexer>,
}

impl<'header, 'config, 'lexer> FuncContent<'header, 'config, 'lexer> {
    pub fn new(
        tokenizer: Rc<Tokenizer>,
        programs: Vec<Vec<Token>>,
        is_load: bool,
        lexer: &'lexer mut Lexer<'header, 'config, 'lexer>,
        prefix: &str,
    ) -> Self {
        #![allow(unused_variables)]
        todo!()
    }

    pub fn parse(&mut self) -> Result<Vec<String>, JMCError> {
        todo!()
    }
}