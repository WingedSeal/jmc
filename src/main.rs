#![allow(dead_code)]
use jmc::compile::header::Header;
use jmc::compile::lexer::Lexer;
use jmc::compile::pack_version::PackVersion;
use jmc::compile::tokenizer::Tokenizer;
use jmc::terminal::configuration::Configuration;
use std::path::PathBuf;
use std::rc::Rc;

mod jmc;

fn main() {
    let config = Configuration {
        namespace: "namespace".to_owned(),
        load_name: "__load__".to_owned(),
        pack_version: PackVersion::new(20),
    };
    let mut header = Header::default();
    let lexer = Lexer::new(&config, &mut header);
    println!(
        "{0}",
        lexer
            .get()
            .parse(
                Rc::new(r#"say "Hello World";"#.to_owned()),
                &PathBuf::from("~/Desktop/main.jmc"),
                true,
            )
            .err()
            .unwrap()
            .msg
    );
}
