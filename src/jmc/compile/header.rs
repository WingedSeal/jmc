use std::{collections::HashMap, rc::Rc};

use super::tokenizer::Token;

#[derive(Debug)]
/// Store information about how to convert
pub struct MacroFactory {}

impl MacroFactory {
    pub fn call(&self, tokens: &[Token], line: u32, col: u32) -> Vec<Token> {
        todo!()
    }
}

#[derive(Debug, Default)]
/// Struct containing all information shared in a compilation
pub struct Header {
    pub macros: HashMap<String, (Rc<MacroFactory>, usize)>,
}
