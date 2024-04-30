use std::collections::VecDeque;
use std::rc::Rc;

use jmc::compile::header::Header;
use jmc::compile::tokenizer::Token;
use jmc::compile::tokenizer::TokenType;
use jmc::compile::tokenizer::Tokenizer;

mod jmc;

fn main() {
    match Tokenizer::parse_raw_string(
        &Rc::new(Header::default()),
        Rc::new(r#""\n\t\r TEST \"\"'''""#.to_owned()),
        String::new(),
        None,
        false,
        false,
    ) {
        Ok(a) => {
            println!("{:?}", a.programs)
        }
        Err(error) => println!("{}", error.msg),
    }
}
