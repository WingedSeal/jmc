#![allow(dead_code)]

use std::fmt::Write;
use std::path::PathBuf;

use super::tokenizer::Token;
use super::tokenizer::Tokenizer;
use JMCErrorType::*;

fn create_error_msg(
    message: String,
    token: Option<Token>,
    tokenizer: Tokenizer,
    is_length_include_col: bool,
    is_display_col_length: bool,
    is_entire_line: bool,
    suggestion: Option<String>,
    overide_file_str: Option<fn(&str) -> String>,
) -> String {
    let string: String;
    let length: usize;
    let mut col: usize;
    let mut line: usize;
    match token {
        Some(token) => {
            string = token.get_full_string();
            length = token.length();
            col = token.col as usize;
            line = token.line as usize;
        }
        None => {
            string = "".to_string();
            length = 1;
            col = tokenizer.col as usize;
            line = tokenizer.line as usize;
        }
    }
    let mut display_line = line;
    let mut display_col = col;
    let newline_count = string.matches('\n').count();
    let right_newline_count = length - string.rfind('\n').unwrap();

    if is_length_include_col {
        if string.contains('\n') {
            line += newline_count;
            col = right_newline_count;
        } else {
            col += length;
        }
        display_col += 1;
    }

    if is_display_col_length {
        if string.contains('\n') {
            display_line += newline_count;
            display_col = right_newline_count + 1;
        } else {
            display_col += length;
        }
    } else {
        display_col += 1;
    }

    let msgs: Vec<&str> = tokenizer.get_file_string().split('\n').collect();
    let max_space = (display_line + 1).to_string().len();
    let line_;
    match overide_file_str {
        Some(overide_file_str) => {
            line_ = overide_file_str(msgs[display_line - 1]);
        }
        None => line_ = msgs[display_line - 1].to_string(),
    }
    let mut final_msg;
    if is_entire_line {
        let tab_count = line_.matches('\t').count();
        final_msg = format!(
            "In {0}
{message} at line {line}.
{1}{2} |{3}
{4}{5} |{6}
{7}{8}
{9} |{10}
",
            relative_file_name(&tokenizer.file_path_str, Some(line as u32), None),
            display_line - 1,
            " ".repeat(max_space - (display_line - 1).to_string().len()),
            if display_line > 1 {
                msgs[display_line - 2].replace('\t', "    ")
            } else {
                "".to_string()
            },
            display_line,
            " ".repeat(max_space - (display_line).to_string().len()),
            line_.replace('\t', "    "),
            " ".repeat(col + max_space + 3 * tab_count + 1),
            "^".repeat(line_.len() - col + 1),
            display_line + 1,
            if display_line < msgs.len() {
                msgs[display_line].replace('\t', "    ")
            } else {
                "".to_string()
            }
        )
    } else {
        let tab_count = line_[0..col - 1].matches('\t').count();
        final_msg = format!(
            "In {0}
{message} at line {line} col {col}.
{1}{2} |{3}
{4}{5} |{6}
{7}{8}
{9} |{10}
",
            relative_file_name(
                &tokenizer.file_path_str,
                Some(line as u32),
                Some(col as u32)
            ),
            display_line - 1,
            " ".repeat(max_space - (display_line - 1).to_string().len()),
            if display_line > 1 {
                msgs[display_line - 2].replace('\t', "    ")
            } else {
                "".to_string()
            },
            display_line,
            " ".repeat(max_space - (display_line).to_string().len()),
            line_.replace('\t', "    "),
            " ".repeat(col + max_space + 3 * tab_count + 1),
            "^".repeat(display_col),
            display_line + 1,
            if display_line < msgs.len() {
                msgs[display_line].replace('\t', "    ")
            } else {
                "".to_string()
            }
        )
    }
    if let Some(suggestion) = suggestion {
        final_msg.write_str(&suggestion).unwrap();
    }
    final_msg
}

fn relative_file_name(file_name: &str, line: Option<u32>, col: Option<u32>) -> String {
    let file_path = PathBuf::from(file_name);
    let cwd = std::env::current_dir().expect("Current directory should not fail");
    if file_path.starts_with(&cwd) {
        return file_name.to_string();
    }
    let mut file_name = file_path
        .strip_prefix(&cwd)
        .unwrap()
        .to_str()
        .unwrap()
        .to_string();
    if let Some(line) = line {
        file_name.write_fmt(format_args!(":{line}")).unwrap();
    }
    if let Some(col) = col {
        file_name.write_fmt(format_args!(":{col}")).unwrap();
    }
    file_name
}

enum JMCErrorType {
    EvaluationException,
    HeaderFileNotFoundError,
    HeaderDuplicatedMacro,
    HeaderSyntaxException,
    JMCSyntaxException,
}

pub struct JMCError {
    error_type: JMCErrorType,
    msg: String,
}
impl JMCError {
    fn evaluation_exception(string: String) -> Self {
        let msg = format!("Unable to evaluate expression '{string}'");
        Self {
            error_type: EvaluationException,
            msg,
        }
    }
    fn header_file_not_found_error(path: PathBuf) -> Self {
        let msg = format!("Header file not found: {0}", path.to_str().unwrap());
        Self {
            error_type: HeaderFileNotFoundError,
            msg,
        }
    }
    fn header_duplicated_macro(
        message: String,
        file_name: String,
        line: u32,
        line_str: String,
    ) -> Self {
        let msg = format!(
            "In {0}\n{message} at line {line}\n{line_str}",
            relative_file_name(&file_name, Some(line), None)
        );
        Self {
            error_type: HeaderDuplicatedMacro,
            msg,
        }
    }

    fn header_syntax_exception(
        message: String,
        file_name: String,
        line: u32,
        line_str: String,
        suggestion: Option<String>,
    ) -> Self {
        let mut msg = format!(
            "In {0}\n{message} at line {line}\n{line_str}",
            relative_file_name(&file_name, Some(line), None)
        );
        if let Some(suggestion) = suggestion {
            msg.write_str(suggestion.as_str()).unwrap();
        }
        Self {
            error_type: HeaderSyntaxException,
            msg,
        }
    }

    fn jmc_syntax_exception(
        message: String,
        token: Option<Token>,
        tokenizer: Tokenizer,
        is_length_include_col: bool,
        is_display_col_length: bool,
        is_entire_line: bool,
        suggestion: Option<String>,
    ) -> Self {
        let msg = create_error_msg(
            message,
            token,
            tokenizer,
            is_length_include_col,
            is_display_col_length,
            is_entire_line,
            suggestion,
            None,
        );
        Self {
            error_type: JMCSyntaxException,
            msg,
        }
    }
}
