#![allow(dead_code)]

use super::exception::JMCError;
use std::fmt::Debug;
use std::iter::Peekable;
use std::rc::Rc;

/// Array of string that, if a line starts with, should automatically terminate line on `{}` without semicolons
const TERMINATE_LINE: [&'static str; 10] = [
    "function", "class", "new", "schedule", "if", "else", "do", "while", "for", "switch",
];

const OPERATORS: [char; 13] = [
    '+', '-', '*', '/', '>', '<', '=', '%', ':', '!', '|', '&', '?',
];

#[derive(Eq, PartialEq, Debug)]
pub enum TokenType {
    Keyword,
    Operator,
    ParenRound,
    ParenSquare,
    ParenCurly,
    String,
    Comma,
    Func,
}

#[derive(Eq, PartialEq, Debug)]
enum StateType {
    Keyword,
    Operator,
    Paren,
    ParenRound,
    ParenSquare,
    ParenCurly,
    String,
    Comment,
    Comma,
    None,
}

impl TokenType {
    fn value(&self) -> &'static str {
        match self {
            TokenType::Keyword => "Keyword",
            TokenType::Operator => "Operator",
            // TokenType::Paren => "PAREN",
            TokenType::ParenRound => "RoundParentheses",
            TokenType::ParenSquare => "SquareParentheses",
            TokenType::ParenCurly => "CurlyParentheses",
            TokenType::String => "StringLiteral",
            // TokenType::Comment => "Comment",
            TokenType::Comma => "Comma",
            TokenType::Func => "Function",
        }
    }
}

#[derive(Debug)]
pub struct Token {
    pub token_type: TokenType,
    pub line: u32,
    pub col: u32,
    pub string: String,
    pub _macro_length: u32,
    pub quote: char,
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
        debug_assert!(
            token.token_type != TokenType::ParenCurly
                || (token.string.starts_with("{") && token.string.ends_with("}"))
        );
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
        debug_assert!(
            token.token_type != TokenType::ParenCurly
                || (token.string.starts_with("{") && token.string.ends_with("}"))
        );
        token
    }

    /// Getting the length of the string in token(including quotation mark)
    pub fn length(&self) -> usize {
        match self.token_type {
            TokenType::String => {
                Tokenizer::unescape_str_force_quote(&self.string, self.quote).len()
            }
            _ => self.string.len(),
        }
    }

    /// Get self.string including quotation mark
    pub fn get_full_string(&self) -> String {
        if self.token_type != TokenType::String {
            return self.string.to_owned();
        }
        Tokenizer::unescape_str(&self.string, quote::SINGLE)
    }

    /// Get original self.string including quotation mark
    pub fn get_original_string(&self) -> String {
        assert_eq!(self.token_type, TokenType::String);
        let string: String = Tokenizer::unescape_str(&self.string, self.quote);
        if self.quote == quote::BACKTICK {
            return format!("`\n{0}\n`", &string[1..string.len() - 1]);
        }
        string
    }
}
#[derive(Debug)]
struct Pos {
    pub line: u32,
    pub col: u32,
}

mod re {
    use once_cell::sync::Lazy;
    use regex::Regex;
    pub const NEW_LINE: char = '\n';

    pub const BACKSLASH: char = '\\';
    pub static WHITESPACE: Lazy<Regex> =
        Lazy::new(|| Regex::new(r"\s+").expect("the regex should not fail to compile"));
    pub static KEYWORD: Lazy<Regex> = Lazy::new(|| {
        Regex::new(r"[a-zA-Z0-9_\.\/\^\~]").expect("the regex should not fail to compile")
    });
    pub const SEMICOLON: char = ';';
    pub const COMMA: char = ',';
    pub const HASH: char = '#';
    pub const SLASH: char = '/';
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

fn get_paren_pair(left_paren: char) -> Result<char, ()> {
    match left_paren {
        paren::L_ROUND => Ok(paren::R_ROUND),
        paren::L_SQUARE => Ok(paren::R_SQUARE),
        paren::L_CURLY => Ok(paren::R_CURLY),
        _ => Err(()),
    }
}
#[derive(Debug)]
struct MacroFactoryInfo {
    name: String,
    macro_factory: String, // TODO: Change to MacroFactory
    /// Argument count
    arg_count: u32,
    pos: Pos,
}
#[derive(Debug)]
/// A class for converting string into tokens
pub struct Tokenizer {
    /// List of lines(list of tokens)
    pub programs: Vec<Vec<Token>>,
    /// Starts at 1
    pub line: u32,
    /// Starts at 1
    pub col: u32,
    /// Current TokenType
    state: StateType,
    /// Current string for token
    token_str: String,
    /// Position for creating token
    token_pos: Option<Pos>,
    /// Current list of tokens
    keywords: Vec<Token>,
    /// List of keywords(list_of_tokens)
    list_of_keywords: Vec<Vec<Token>>,

    /// Raw string read from file/given from another tokenizer
    raw_string: Rc<String>,
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
    /// * `expect_semicolon` - Whether to expect a semicolon at the end, defaults to `true`
    /// * `allow_semicolon` - Whether to allow last missing last semicolon, defaults to `false`
    pub fn new(
        raw_string: String,
        file_path_str: String,
        file_string: Option<String>,
        expect_semicolon: bool,
        allow_semicolon: bool,
    ) -> Result<Self, JMCError> {
        let mut tokenizer = Self {
            programs: vec![],
            line: 0,
            col: 0,
            state: StateType::None,
            token_str: String::new(),
            token_pos: None,
            keywords: vec![],
            list_of_keywords: vec![],
            raw_string: Rc::new(raw_string),
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
        tokenizer.parse(expect_semicolon, false)?;
        Ok(tokenizer)
    }

    pub fn get_file_string(&self) -> &str {
        match &self.file_string {
            Some(file_string) => &file_string,
            None => &self.raw_string,
        }
    }

    /// Parse string
    ///
    /// * `string` - String to parse
    /// * `listne` - Current line
    /// * `costl` - Current column
    /// * `expect_semicolon` - Whether to expect a semicolon at the end
    /// * `allow_last_missing_semicolon` - Whether to allow last missing last semicolon, defaults to False
    /// * return - List of keywords(list of tokens)
    fn parse(
        &mut self,
        expect_semicolon: bool,
        allow_last_missing_semicolon: bool,
    ) -> Result<&Vec<Vec<Token>>, JMCError> {
        self.parse_chars(expect_semicolon)?;

        match self.state {
            StateType::String => {
                return Err(JMCError::jmc_syntax_exception(
                    "String literal contains an unescaped linebreak".to_owned(),
                    None,
                    self,
                    true,
                    false,
                    true,
                    Some(
                        "If you intended to use multiple line, try multiline string '`'".to_owned(),
                    ),
                ));
            }
            StateType::Paren => {
                let token_pos = match &self.token_pos {
                    Some(token_pos) => token_pos,
                    None => panic!("token_pos is None"),
                };
                debug_assert!(!self.token_pos.is_none());
                let paren: String = match &self.left_paren {
                    Some(left_paren) => left_paren.to_string(),
                    None => "".to_owned(),
                };
                return Err(JMCError::jmc_syntax_exception(
                    "Bracket was never closed".to_owned(),
                    Some(&Token::new(
                        TokenType::Keyword,
                        token_pos.line,
                        token_pos.col,
                        paren,
                        None,
                        None,
                    )),
                    self,
                    false,
                    true,
                    false,
                    Some("This can be the result of unclosed string as well".to_owned()),
                ));
            }
            _ => {}
        }
        if expect_semicolon && (!self.keywords.is_empty() || !self.token_str.is_empty()) {
            if !self.token_str.is_empty() {
                self.append_token();
            }
            if allow_last_missing_semicolon {
                self.append_keywords();
            }
            return Err(JMCError::jmc_syntax_exception(
                "Expected semicolon(;)".to_owned(),
                Some(&self.keywords[self.keywords.len() - 1]),
                &self,
                true,
                true,
                false,
                None,
            ));
        }

        if !expect_semicolon {
            if !self.token_str.is_empty() {
                self.append_token();
            }
            if !self.keywords.is_empty() {
                self.append_keywords();
            }
        }
        Ok(&self.list_of_keywords)
    }

    fn parse_chars(&mut self, expect_semicolon: bool) -> Result<(), JMCError> {
        let raw_string_rc = Rc::clone(&self.raw_string);
        let mut raw_string_iter = raw_string_rc.chars().peekable();
        while let Some(ch) = raw_string_iter.next() {
            self.col += 1;
            if ch == re::SEMICOLON && self.state == StateType::None && !expect_semicolon {
                return Err(JMCError::jmc_syntax_exception(
                    "Unexpected semicolon(;)".to_owned(),
                    None,
                    &self,
                    false,
                    true,
                    false,
                    None,
                ));
            }

            if ch == re::NEW_LINE {
                self.parse_newline(ch)?;
                continue;
            }

            if ch == re::SLASH
                && raw_string_iter.peek() == Some(&re::SLASH)
                && self.state != StateType::Paren
                && self.state != StateType::String
            {
                raw_string_iter.next();
                if !self.token_str.is_empty() {
                    self.append_token();
                }
                self.state = StateType::Comment;
                continue;
            }
            if let StateType::Keyword | StateType::Operator = self.state {
                if self.parse_keyword_and_operator(ch, expect_semicolon)? {
                    continue;
                }
            }
            match self.state {
                StateType::Paren => self.parse_paren(&mut raw_string_iter, ch, expect_semicolon)?,
                StateType::String => self.parse_string(&mut raw_string_iter, ch)?,
                StateType::Comment => continue,
                StateType::None => self.parse_none(ch)?,
                _ => panic!("invalid state"),
            }
        }
        Ok(())
    }

    fn parse_newline(&mut self, ch: char) -> Result<(), JMCError> {
        self.is_comment = false;
        match self.state {
            StateType::String => {
                if self.quote == Some(quote::BACKTICK) {
                    self.token_str.push(ch);
                } else {
                    return Err(JMCError::jmc_syntax_exception(
                        "String literal contains unescaped line break".to_owned(),
                        None,
                        self,
                        false,
                        false,
                        true,
                        None,
                    ));
                }
            }
            StateType::Comment => self.state = StateType::None,
            StateType::Keyword | StateType::Operator => {
                self.append_token();
            }
            StateType::Paren => {
                self.token_str.push(ch);
            }
            _ => {}
        }
        self.line += 1;
        self.col = 0;
        Ok(())
    }

    fn escape(ch: char) -> Result<char, ()> {
        match ch {
            'n' => Ok('\n'),
            'r' => Ok('\r'),
            't' => Ok('\t'),
            '\\' => Ok('\\'),
            '0' => Ok('\0'),
            '\'' => Ok('\''),
            '"' => Ok('"'),
            _ => Err(()),
        }
    }

    /// Unescape string and surround it by the most suited quote, prefering `prefered_quote` then return that with the prefered quote
    pub fn unescape_str(string: &str, prefered_quote: char) -> String {
        let choosen_quote;
        let single_quote_count = string.matches('\'').count();
        let double_quote_count = string.matches('\"').count();
        if single_quote_count > double_quote_count {
            choosen_quote = '"';
        } else if single_quote_count < double_quote_count {
            choosen_quote = '\'';
        } else {
            choosen_quote = prefered_quote
        }
        Self::unescape_str_force_quote(string, choosen_quote)
    }

    /// Unescape string and surround it by the chosen `forced_quote`
    fn unescape_str_force_quote(string: &str, mut forced_quote: char) -> String {
        const QUOTES: [char; 2] = ['\'', '"'];
        if !QUOTES.contains(&forced_quote) {
            forced_quote = '"'
        }
        let mut unescaped_string = forced_quote.to_string();
        for ch in string.chars().into_iter() {
            match Self::unescape(ch, forced_quote) {
                Some(unescaped_str) => unescaped_string.push_str(unescaped_str),
                None => unescaped_string.push(ch),
            }
        }
        unescaped_string.push(forced_quote);
        unescaped_string
    }

    fn unescape(ch: char, prefered_quote: char) -> Option<&'static str> {
        match ch {
            '\n' => Some("\\n"),
            '\r' => Some("\\r"),
            '\t' => Some("\\t"),
            '\\' => Some("\\\\"),
            '\0' => Some("\\0"),
            '\'' => {
                if prefered_quote == quote::SINGLE {
                    Some("\\'")
                } else {
                    Some("'")
                }
            }
            '"' => {
                if prefered_quote == quote::DOUBLE {
                    Some("\\\"")
                } else {
                    Some("\"")
                }
            }
            _ => None,
        }
    }

    fn parse_string(
        &mut self,
        raw_string_iter: &mut Peekable<impl Iterator<Item = char>>,
        ch: char,
    ) -> Result<(), JMCError> {
        if ch == re::BACKSLASH {
            let next_char: char = match raw_string_iter.peek() {
                Some(next_char) => *next_char,
                None => {
                    return Err(JMCError::jmc_syntax_exception(
                        "String literal contains unescaped line break".to_owned(),
                        None,
                        self,
                        false,
                        false,
                        true,
                        Some("You are currently trying to escape(\\) nothing.".to_owned()),
                    ));
                }
            };
            raw_string_iter.next();
            match Self::escape(next_char) {
                Ok(unescaped) => self.token_str.push(unescaped),
                Err(_) => {
                    self.token_str.push('\\');
                    self.token_str.push(ch)
                }
            }
            return Ok(());
        }
        if Some(ch) != self.quote {
            self.token_str.push(ch);
            return Ok(());
        }
        if ch == quote::BACKTICK {
            self.validate_multiline_string()?;
        }
        Ok(())
    }

    fn validate_multiline_string(&mut self) -> Result<(), JMCError> {
        let first_newline = self.raw_string.find('\n');
        let last_newline = self.raw_string.rfind('\n');
        let first_line: &str;
        let last_line: &str;
        match (first_newline, last_newline) {
            (None, None) => Err(JMCError::jmc_syntax_exception(
                "Expected newline after open backtick(`) for multiline string".to_owned(),
                None,
                self,
                false,
                false,
                false,
                None,
            )),
            (Some(first_newline), Some(last_newline)) => {
                if first_newline == last_newline {
                    return Err(JMCError::jmc_syntax_exception(
                        "Expected newline before close backtick(`) for multiline string".to_owned(),
                        None,
                        self,
                        false,
                        true,
                        false,
                        None,
                    ));
                }
                first_line = &self.raw_string[..first_newline];
                last_line = &self.raw_string[last_newline + 1..];
                if !first_line.is_empty() && !re::WHITESPACE.is_match(first_line) {
                    return Err(JMCError::jmc_syntax_exception(
                        format!(
                            "Expected whitespaces line after open backtick(`) (got {first_line:?})"
                        ),
                        None,
                        self,
                        false,
                        true,
                        false,
                        None,
                    ));
                }
                if !last_line.is_empty() && !re::WHITESPACE.is_match(last_line) {
                    return Err(JMCError::jmc_syntax_exception(
                        format!(
                            "Expected whitespaces line before open backtick(`) (got {last_line:?})"
                        ),
                        None,
                        self,
                        false,
                        true,
                        false,
                        None,
                    ));
                }
                Ok(())
            }
            _ => panic!("first_newline and last_line have to be both None or Some"),
        }
    }

    /// Return `false` if it's not a keyword/operator anymore and the current char should be checked further
    fn parse_keyword_and_operator(
        &mut self,
        ch: char,
        expect_semicolon: bool,
    ) -> Result<bool, JMCError> {
        const NON_KEYWORD: [char; 7] = [
            quote::SINGLE,
            quote::DOUBLE,
            quote::BACKTICK,
            paren::L_CURLY,
            paren::L_ROUND,
            paren::L_SQUARE,
            re::COMMA,
        ];
        if ch.is_whitespace() || NON_KEYWORD.contains(&ch) {
            self.append_keywords();
            return Ok(false);
        }
        let is_operator = OPERATORS.contains(&ch);
        if self.state == StateType::Keyword && is_operator {
            self.append_token();
            self.token_pos = Some(self.get_pos());
            self.state = StateType::Operator;
        } else if self.state == StateType::Operator && !is_operator && ch != re::SEMICOLON {
            self.append_token();
            self.token_pos = Some(self.get_pos());
            self.state = StateType::Keyword;
        }

        if ch != re::SEMICOLON {
            self.token_str.push(ch);
            return Ok(true);
        }
        if expect_semicolon {
            self.append_token();
            return Ok(false);
        }
        if !self.allow_semicolon {
            return Err(JMCError::jmc_syntax_exception(
                "Unexpected semicolon(;)".to_owned(),
                None,
                self,
                false,
                true,
                false,
                None,
            ));
        }
        self.allow_semicolon = false;

        const MINECRAFT_ARRAY_TYPE: [&'static str; 3] = ["I", "B", "L"];
        if MINECRAFT_ARRAY_TYPE.contains(&self.token_str.as_str()) {
            self.token_str.push(ch);
            return Ok(true);
        }
        Err(JMCError::jmc_syntax_exception(
            "Unexpected semicolon(;)".to_owned(),
            None,
            self,
            false,
            true,
            false,
            None,
        ))
    }

    fn parse_paren(
        &mut self,
        raw_string_iter: &mut Peekable<impl Iterator<Item = char>>,
        ch: char,
        expect_semicolon: bool,
    ) -> Result<(), JMCError> {
        self.token_str.push(ch);
        if self.is_string {
            match ch {
                re::BACKSLASH => {
                    match raw_string_iter.next() {
                        Some(next) => self.token_str.push(next),
                        None => return Err(JMCError::jmc_syntax_exception(
                            "String literal contains an unescaped linebreak".to_owned(),
                            None,
                            self,
                            true,
                            false,
                            true,
                            Some(
                                "If you intended to use multiple line, try multiline string '`'"
                                    .to_owned(),
                            ),
                        )),
                    }
                }
                re::NEW_LINE => {
                    return Err(JMCError::jmc_syntax_exception(
                        "String literal contains an unescaped linebreak".to_owned(),
                        None,
                        self,
                        true,
                        false,
                        true,
                        Some(
                            "If you intended to use multiple line, try multiline string '`'"
                                .to_owned(),
                        ),
                    ));
                }
                _ if Some(ch) == self.quote => {
                    self.is_string = false;
                }
                _ => {}
            }
            return Ok(());
        }
        if self.is_comment {
            return Ok(());
        }

        match ch {
            _ if Some(ch) == self.left_paren => self.paren_count += 1,
            _ if Some(ch) == self.right_paren => {
                if self.paren_count != 0 {
                    self.paren_count -= 1;
                    return Ok(());
                }
                let mut is_paren_curly = false;
                match self.left_paren {
                    Some(paren::L_CURLY) => {
                        self.state = StateType::ParenCurly;
                        is_paren_curly = true;
                    }
                    Some(paren::L_ROUND) => self.state = StateType::ParenRound,
                    Some(paren::L_SQUARE) => self.state = StateType::ParenRound,
                    _ => panic!("self.left_paren shouldn't be None at this point"),
                }
                if is_paren_curly
                    && expect_semicolon
                    && self.should_terminate_line(0)
                    && (!self.is_shorten_if() || self.should_terminate_line(2))
                {
                    self.append_keywords()
                }
            }
            quote::SINGLE | quote::DOUBLE | quote::BACKTICK => {
                self.is_string = true;
                self.quote = Some(ch);
            }
            re::SLASH if raw_string_iter.peek() == Some(&re::SLASH) => self.is_comment = true,
            re::HASH if self.keywords.is_empty() => self.is_comment = true,
            _ => {}
        }
        todo!()
    }

    fn parse_none(&mut self, ch: char) -> Result<(), JMCError> {
        match ch {
            quote::SINGLE | quote::DOUBLE | quote::BACKTICK => {
                self.token_str.push(ch);
                self.token_pos = Some(self.get_pos());
                self.state = StateType::String;
                self.quote = Some(ch);
            }
            re::SEMICOLON => match &self.macro_factory {
                Some(macro_factory) => {
                    return Err(JMCError::jmc_syntax_exception(
                        format!(
                            "Expected a round bracket after macro factory({0})",
                            macro_factory.name
                        ),
                        None,
                        self,
                        false,
                        true,
                        false,
                        Some("Macro factory is a macro that acts like a function (requires parameter(s))".to_owned()),
                    ));
                }
                None => self.append_keywords(),
            },
            paren::L_CURLY | paren::L_ROUND | paren::L_SQUARE => {
                self.token_str.push(ch);
                self.token_pos = Some(self.get_pos());
                self.state = StateType::Paren;
                self.left_paren = Some(ch);
                self.right_paren =
                    Some(get_paren_pair(ch).expect("should only pair when it's paren"))
            }
            paren::R_CURLY | paren::R_ROUND | paren::R_SQUARE => {
                return Err(JMCError::jmc_syntax_exception(
                    format!("Unexpected closing bracket ({ch})"),
                    None,
                    self,
                    false,
                    false,
                    false,
                    None,
                ));
            }
            re::HASH if self.keywords.is_empty() => self.state = StateType::Comment,
            re::COMMA => {
                self.token_str.push(ch);
                self.token_pos = Some(self.get_pos());
                self.state = StateType::Comma;
                self.append_token();
            }
            _ if OPERATORS.contains(&ch) => {
                self.token_str.push(ch);
                self.token_pos = Some(self.get_pos());
                self.state = StateType::Operator;
            }
            // _ if ch.is_whitespace() => return Ok(()),
            _ => {
                self.token_str.push(ch);
                self.token_pos = Some(self.get_pos());
                self.state = StateType::Keyword;
            }
        }
        Ok(())
    }

    fn append_token(&mut self) {
        todo!()
    }

    fn append_keywords(&mut self) {
        todo!()
    }

    fn should_terminate_line(&self, start_at: u32) -> bool {
        todo!()
    }

    fn is_shorten_if(&self) -> bool {
        todo!()
    }

    #[inline]
    fn get_pos(&self) -> Pos {
        Pos {
            line: self.line,
            col: self.col,
        }
    }
}

#[cfg(test)]
mod token_tests {
    use super::*;

    #[test]
    fn test_get_full_string() {
        assert_eq!(
            Token::new(
                TokenType::Keyword,
                1,
                1,
                "KEYWORD_TOKEN".to_owned(),
                None,
                None,
            )
            .get_full_string(),
            "KEYWORD_TOKEN"
        );
        assert_eq!(
            Token::new(
                TokenType::String,
                1,
                1,
                "STRING_TOKEN".to_owned(),
                None,
                Some('"'),
            )
            .get_full_string(),
            "'STRING_TOKEN'"
        );
        assert_eq!(
            Token::new(
                TokenType::String,
                1,
                1,
                "'STRING_TOKEN'".to_owned(),
                None,
                Some('"'),
            )
            .get_full_string(),
            "\"'STRING_TOKEN'\""
        );
        assert_eq!(
            Token::empty(TokenType::Keyword, "KEYWORD_TOKEN".to_owned()).get_full_string(),
            "KEYWORD_TOKEN"
        );
    }
}

#[cfg(test)]
mod tokenizer_tests {
    use super::*;

    #[test]
    fn test_unescape_string() {
        assert_eq!(
            Tokenizer::unescape_str("\n\t\r TEST \"\"'''", '\''),
            r#""\n\t\r TEST \"\"'''""#
        )
    }

    #[test]
    #[ignore = "waiting for tokenizer"]
    fn test_escape() {
        assert_eq!(
            Tokenizer::new(
                r#""\n\t\r TEST \"\"'''""#.to_owned(),
                String::new(),
                None,
                true,
                false
            )
            .unwrap()
            .programs[0][0]
                .string,
            "\n\t\r TEST \"\"'''"
        )
    }
}
