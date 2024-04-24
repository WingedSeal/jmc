#![allow(dead_code)]

use super::exception::JMCError;
use std::fmt::Debug;

/// Array of string that, if a line starts with, should automatically terminate line on `{}` without semicolons
const TERMINATE_LINE: [&'static str; 10] = [
    "function", "class", "new", "schedule", "if", "else", "do", "while", "for", "switch",
];

const OPERATORS: &[&'static str] = &[
    "+", "-", "*", "/", ">", "<", "=", "%", ":", "!", "|", "&", "?",
];

#[derive(Eq, PartialEq)]
pub enum TokenType {
    Keyword,
    Operator,
    Paren,
    ParenRound,
    ParenSquare,
    ParenCurly,
    String,
    Comment,
    Comma,
    Func,
}

impl TokenType {
    fn value(&self) -> &'static str {
        match self {
            TokenType::Keyword => "Keyword",
            TokenType::Operator => "Operator",
            TokenType::Paren => "PAREN",
            TokenType::ParenRound => "RoundParentheses",
            TokenType::ParenSquare => "SquareParentheses",
            TokenType::ParenCurly => "CurlyParentheses",
            TokenType::String => "StringLiteral",
            TokenType::Comment => "Comment",
            TokenType::Comma => "Comma",
            TokenType::Func => "Function",
        }
    }
}

pub struct Token {
    pub token_type: TokenType,
    pub line: u32,
    pub col: u32,
    pub string: String,
    pub _macro_length: u32,
    pub quote: char,
}

fn repr(value: impl Debug) -> String {
    format!("{0:?}", value)
}

impl Token {
    /// A dataclass containing information for Token for Lexical Analysis
    ///
    /// * `token_type` - Type of the token
    /// * `line` - Which line it's found in
    /// * `col` - Which column it's found in
    /// * `string` - The string representation (including parentheses, excluding quotation mark)
    pub fn new(
        token_type: TokenType,
        line: u32,
        col: u32,
        string: String,
        _macro_length: Option<u32>,
        quote: Option<char>,
    ) -> Self {
        let _macro_length: u32 = match _macro_length {
            Some(value) => value,
            None => 0,
        };
        let quote: char = match quote {
            Some(value) => value,
            None => '"',
        };
        let token = Self {
            token_type,
            line,
            col,
            string,
            _macro_length,
            quote,
        };
        token.post_init();
        token
    }

    /// Create an empty token
    ///
    /// * `token_type` - New token's TokenType
    /// * `string` - New token's string
    /// * return - New token
    pub fn empty(token_type: TokenType, string: String) -> Self {
        let token = Self {
            token_type,
            line: 0,
            col: 0,
            string,
            _macro_length: 0,
            quote: '"',
        };
        token.post_init();
        token
    }

    /// Edit string and _length according to macros(`#define something`) defined
    fn post_init(&self) {
        if self.token_type != TokenType::ParenCurly {
            return;
        };
        if !self.string.starts_with("{") || !self.string.ends_with("}") {
            panic!("ParenCurly Token created but string doesn't start and end with the parenthesis")
        }
    }

    /// Getting the length of the string in token(including quotation mark)
    pub fn length(&self) -> usize {
        match self.token_type {
            TokenType::String => repr(&self.string).len(),
            _ => self.string.len(),
        }
    }

    /// Get self.string including quotation mark
    pub fn get_full_string(&self) -> String {
        if self.token_type != TokenType::String {
            return self.string.to_string();
        }
        if self.quote != '`' {
            let string: String = repr(&self.string);
            return format!("`\n{0}\n`", &string[1..string.len() - 1]);
        }
        repr(&self.string)
    }

    /// Get self.string including quotation mark (Raise error when the token_type is not TokenType.STRING)
    pub fn add_quotation(&self) -> String {
        assert!(self.token_type == TokenType::String);
        repr(&self.string)
    }
}

struct Pos {
    pub line: u32,
    pub col: u32,
}

mod re {
    pub const NEW_LINE: &str = "\n";
    pub const BACKSLASH: &str = "\\";
    pub const WHITESPACE: &str = r"\s+";
    pub const KEYWORD: &str = r"[a-zA-Z0-9_\.\/\^\~]";
    pub const SEMICOLON: &str = ";";
    pub const COMMA: &str = ",";
    pub const HASH: &str = "#";
    pub const SLASH: &str = "/";
}

mod quote {
    pub const SINGLE: char = '\'';
    pub const DOUBLE: char = '"';
    pub const BACKTICK: char = '`';
}

mod paren {
    pub const L_ROUND: char = '(';
    pub const R_ROUND: char = ')';
    pub const L_SQUARE: char = '[';
    pub const R_SQUARE: char = ']';
    pub const L_CURLY: char = '{';
    pub const R_CURLY: char = '}';
}

pub fn get_paren_pair(left_paren: char) -> Result<char, ()> {
    match left_paren {
        paren::L_ROUND => Ok(paren::R_ROUND),
        paren::L_SQUARE => Ok(paren::R_SQUARE),
        paren::L_CURLY => Ok(paren::R_CURLY),
        _ => Err(()),
    }
}

struct MacroFactoryInfo {
    name: String,
    macro_factory: String, // TODO: Change to MacroFactory
    /// Argument count
    arg_count: u32,
    pos: Pos,
}

/// A class for converting string into tokens
pub struct Tokenizer {
    /// List of lines(list of tokens)
    programs: Vec<Vec<Token>>,
    /// Starts at 1
    pub line: u32,
    /// Starts at 1
    pub col: u32,
    /// Current TokenType
    state: Option<TokenType>,
    /// Current string for token
    token_str: String,
    /// Position for creating token
    token_pos: Option<Pos>,
    /// Current list of tokens
    keywords: Vec<Token>,
    /// List of keywords(list_of_tokens)
    list_of_keywords: Vec<Vec<Token>>,

    /// Raw string read from file/given from another tokenizer
    raw_string: String,
    /// Entire string read from current file
    file_string: Option<String>,
    /// File path to current JMC function as string
    pub file_path_str: String,

    // String
    /// Type of quote
    quote: Option<char>,
    /// Whether it is an escaped character (Backslashed)
    is_escaped: bool,

    // Parenthesis
    /// Type of left parenthesis
    left_paren: Option<char>,
    /// Type of right parenthesis
    right_paren: Option<char>,
    /// Count of left parenthesis / Count of current layer
    paren_count: u32,
    /// Whether the current character is in string (For paren TokenType)
    is_string: bool,
    /// Whether the current character is in comment (For paren TokenType)
    is_comment: bool,

    /// Whether to allow semicolon at the next char(For minecraft array `[I;int, ...]`)
    allow_semicolon: bool,
    /// JMC macro factory
    macro_factory: Option<MacroFactoryInfo>,
}

impl Tokenizer {
    /// * `raw_string` - Raw string read from file/given from another tokenizer
    /// * `file_path_str` - Entire string read from current file
    /// * `expect_semicolon` - Whether to expect a semicolon at the end
    /// * `allow_semicolon` - Whether to allow last missing last semicolon, defaults to False
    pub fn new(
        raw_string: String,
        file_path_str: String,
        file_string: Option<String>,
        expect_semicolon: bool,
        allow_semicolon: bool,
    ) -> Self {
        let mut tokenizer = Self {
            programs: vec![],
            line: 0,
            col: 0,
            state: None,
            token_str: String::new(),
            token_pos: None,
            keywords: vec![],
            list_of_keywords: vec![],
            raw_string,
            file_string,
            file_path_str,
            quote: None,
            is_escaped: false,
            left_paren: None,
            right_paren: None,
            paren_count: 0,
            is_string: false,
            is_comment: false,
            allow_semicolon,
            macro_factory: None,
        };
        tokenizer.parse(expect_semicolon);
        tokenizer
    }

    fn parse(&mut self, expect_semicolon: bool) -> Result<Vec<Vec<Token>>, JMCError> {
        self.parse_chars(expect_semicolon)?;
        if let Some(TokenType::String) = self.state {
            todo!()
        }
        todo!()
    }

    fn parse_chars(&self, expect_semicolon: bool) -> Result<(), JMCError> {
        todo!()
    }

    pub fn get_file_string(&self) -> &String {
        match &self.file_string {
            Some(file_string) => &file_string,
            None => &self.raw_string,
        }
    }
}
