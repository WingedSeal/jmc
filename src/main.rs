#![allow(dead_code)]
use jmc::compile::header::Header;
use jmc::compile::tokenizer::Tokenizer;
use std::rc::Rc;

mod jmc;

fn main() {
    match Tokenizer::parse_raw_string(
        &Header::default(),
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
