use std::rc::Rc;

use super::{
    exception::JMCError,
    lexer::LexerInner,
    tokenizer::{Token, Tokenizer},
};

#[derive(Debug)]
pub struct FuncContent<'header, 'config, 'lexer> {
    lexer: &'lexer mut LexerInner<'header, 'config, 'lexer>,
}

impl<'header, 'config, 'lexer> FuncContent<'header, 'config, 'lexer> {
    pub fn new(
        tokenizer: Rc<Tokenizer>,
        programs: Vec<Vec<Token>>,
        is_load: bool,
        lexer: &'lexer mut LexerInner<'header, 'config, 'lexer>,
        prefix: String,
    ) -> Self {
        todo!()
    }

    pub fn parse(&mut self) -> Result<Vec<String>, JMCError> {
        todo!()
    }
}
