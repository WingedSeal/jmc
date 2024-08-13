use std::error::Error;
use std::fs;
use std::path::Path;
use std::rc::Rc;
use std::{collections::HashSet, path::PathBuf};

use phf::{phf_map, phf_set};

use crate::jmc::compile::decorator_parse::ModifyMcFunction;

use super::super::terminal::configuration::Configuration;
use super::datapack::{Datapack, PreMcFunction};
use super::decorator_parse::DECORATORS;
use super::exception::{relative_file_name, JMCError};
use super::header::Header;
use super::lexer_func_content::FuncContent;
use super::tokenizer::{Token, TokenType, Tokenizer};
use super::utils::{convention_jmc_to_mc, is_decorator, unsafe_share};

/// List of all possible vanilla json file types
static JSON_FILE_TYPES: phf::Set<&'static str> = phf_set! {
    "advancements",
    "dimension",
    "dimension_type",
    "loot_tables",
    "predicates",
    "recipes",
    "item_modifiers",
    "structures",
    "worldgen/biome",
    "worldgen/configured_carver",
    "worldgen/configured_feature",
    "worldgen/configured_surface_builder",
    "worldgen/density_function",
    "worldgen/flat_level_generator_preset",
    "worldgen/noise",
    "worldgen/noise_settings",
    "worldgen/placed_feature",
    "worldgen/processor_list",
    "worldgen/structure",
    "worldgen/structure_set",
    "worldgen/template_pool",
    "worldgen/world_preset",
    "trim_material",
    "trim_pattern",
    "chat_type",
    "damage_type",
};

/// Dictionary of JMC's custom file type that'll be automatically converted to vanilla ones
static JMC_JSON_FILE_TYPES: phf::Map<&'static str, &'static str> = phf_map! {
    "advancement" => "advancements",
    "loot_table" => "loot_tables",
    "structure" => "structures",
    "recipe" => "recipes",
};

type ConditionToken = Token;
/// Curly Parenthesis Token
type CodeBlockToken = Token;

#[derive(Debug)]
pub struct Lexer<'header, 'config, 'lexer> {
    if_else_box: Vec<(Option<ConditionToken>, Vec<CodeBlockToken>)>,
    do_while_box: Option<CodeBlockToken>,
    /// Tokenizer for load function
    load_tokenizer: Option<Rc<Tokenizer<'header>>>,
    /// Set of path that's already imported
    imports: HashSet<PathBuf>,
    config: &'config Configuration,
    datapack: Datapack<'header, 'config, 'lexer>,
    /// Header shared between compilation
    pub header: &'header mut Header,
    load_function: Vec<Vec<Token>>,
}

impl<'header, 'config, 'lexer> Lexer<'header, 'config, 'lexer> {
    pub fn new(config: &'config Configuration, header: &'header mut Header) -> Self {
        let datapack = Datapack::new(config);
        let mut lexer = Self {
            if_else_box: vec![],
            do_while_box: None,
            load_tokenizer: None,
            imports: HashSet::new(),
            config,
            datapack,
            header,
            load_function: vec![],
        };
        // datapack.lexer must be set right after the initialization
        // of lexer, otherwise there'd be a dangling reference
        lexer.datapack.lexer = Some(unsafe_share!(&mut lexer, Lexer));
        lexer
    }

    /// Parse a jmc file
    pub fn parse_file(
        config: &'config Configuration,
        file_path: &PathBuf,
        is_load: bool,
        header: &'header mut Header,
    ) -> Result<Self, JMCError> {
        let mut lexer = Self::new(config, header);
        if lexer.imports.contains(file_path) {
            return Ok(lexer);
        }
        let raw_string = match fs::read_to_string(file_path) {
            Ok(raw_string) => raw_string,
            Err(_) => {
                let file_path_str = file_path
                    .to_str()
                    .expect("file_path is read from jmc file which is valid UTF-8")
                    .to_owned();
                return Err(JMCError::jmc_file_not_found(format!(
                    "JMC file not found: {file_path_str}"
                )));
            }
        };
        lexer.parse(Rc::new(raw_string), file_path, is_load)?;
        Ok(lexer)
    }
    /// Parse string read from JMC file
    ///
    /// * `is_load` - Whether the file is for load function, defaults to False
    pub fn parse(
        &mut self,
        file_string: Rc<String>,
        file_path: &PathBuf,
        is_load: bool,
    ) -> Result<(), JMCError> {
        let file_path_str = file_path
            .to_str()
            .expect("file_path is read from jmc file which is valid UTF-8")
            .to_owned();

        let header = unsafe { &mut *(self.header as *mut Header) };
        let mut tokenizer =
            Tokenizer::parse_raw_string(header, file_string, file_path_str, None, true, false)?;
        let programs = std::mem::take(&mut tokenizer.programs);

        let tokenizer = Rc::new(tokenizer);
        if is_load {
            self.load_tokenizer = Some(Rc::clone(&tokenizer)); // FIXME: avoid cloning this
        }

        // FIXME: I have no idea what the `__update_load` is actually doing, so I'm omitting it for now.
        // python version line 162: self.__update_load(file_path_str, raw_string)
        for command in programs {
            let tokenizer = Rc::clone(&tokenizer);
            match command[0].string.as_str() {
                "function" if !self.is_vanilla_func(&command) => {
                    self.parse_current_load()?;
                    let file_path_str = tokenizer.file_path_str.clone();
                    self.parse_func(tokenizer, command, &file_path_str, "")?;
                }
                "new" => {
                    self.parse_current_load()?;
                    self.parse_new(tokenizer, command)?;
                }
                "class" => {
                    self.parse_current_load()?;
                    let file_path_str = tokenizer.file_path_str.clone();
                    self.parse_class(tokenizer, command, &file_path_str, "")?;
                }
                "import" => {
                    self.parse_current_load()?;
                    self.parse_import(tokenizer, command, &file_path)?;
                }
                decorator if is_decorator(decorator) => {
                    self.parse_current_load()?;
                    let file_path_str = tokenizer.file_path_str.clone();
                    self.parse_decorated_func(tokenizer, command, &file_path_str, "")?;
                }
                _ => self.load_function.push(command),
            }
            self.parse_current_load()?;
        }
        Ok(())
    }

    /// Whether command is in vanilla function syntax
    fn is_vanilla_func(&self, command: &Vec<Token>) -> bool {
        let length = command.len();
        if length == 2 && command[1].token_type == TokenType::String {
            return true;
        }
        if !(length == 4
            && command[1].token_type == TokenType::Keyword
            && command[2].token_type == TokenType::Operator
            && command[2].string == ":"
            && command[3].token_type == TokenType::Keyword)
        {
            return false;
        }
        // Amount of tokens that is ignored
        let mut ignored_count = 0;
        // Clear paths
        if length > 4 {
            for token_pair in command[4..].windows(2).step_by(2) {
                if token_pair[0].string == "/" {
                    ignored_count += 1;
                }
            }
        }
        let length = length - ignored_count;
        if length == 4 {
            return true;
        }
        if length == 5 && command[command.len() - 1].token_type == TokenType::ParenCurly {
            return true;
        }
        if length >= 5 && command[4].string == "with" {
            // FIXME: make sure this works
            return true;
        }
        return false;
    }

    /// Parse current load function that's in self.load_function and clear it
    fn parse_current_load(&mut self) -> Result<(), JMCError> {
        if self.load_function.is_empty() {
            return Ok(());
        }
        let commands = self.parse_load_func_content()?;
        self.datapack.functions[&self.datapack.config.load_name].extend(commands);
        Ok(())
    }

    /// Parse content inside load function
    fn parse_load_func_content(&mut self) -> Result<Vec<String>, JMCError> {
        let programs: Vec<Vec<Token>> = std::mem::take(&mut self.load_function);
        let load_tokenizer = Rc::clone(&self.load_tokenizer.as_ref().expect("load_tokenizer"));
        self.parse_func_content(load_tokenizer, programs, "", true)
    }

    /// Parse a content inside function
    ///
    /// * `is_load` - Whether the function is a load function
    /// * return - List of commands(string)
    pub fn parse_func_content(
        &mut self,
        tokenizer: Rc<Tokenizer>,
        programs: Vec<Vec<Token>>,
        prefix: &str,
        is_load: bool,
    ) -> Result<Vec<String>, JMCError> {
        let lexer = unsafe_share!(self, Self);
        FuncContent::new(tokenizer, programs, is_load, lexer, prefix).parse()
    }

    /// Parse a function definition in form of list of token
    ///
    /// * `tokenizer` - Tokenizer
    /// * `command` - List of token inside a function definition
    /// * `file_path_str` - File path to current JMC function as string
    /// * `prefix` - Prefix of function(for Class feature), defaults to `''`
    /// * `is_save_to_datapack` - Whether to save the result function into the datapack, defaults to `true`
    fn parse_func(
        &mut self,
        tokenizer: Rc<Tokenizer<'header>>,
        command: Vec<Token>,
        file_path_str: &str,
        prefix: &str,
    ) -> Result<(), JMCError> {
        let pre_function =
            self.parse_func_tokens(tokenizer, command, file_path_str, prefix, true)?;
        let (mcfunction, func_path) = pre_function.parse()?;
        self.datapack
            .functions
            .insert(func_path.clone(), mcfunction);
        Ok(())
    }

    /// Parse a function definition in form of list of token
    ///
    /// * `tokenizer` - Tokenizer
    /// * `command` - List of token inside a function definition
    /// * `file_path_str` - File path to current JMC function as string
    /// * `prefix` Prefix of function(for Class feature), defaults to `''``
    /// * `is_save_to_datapack` - Whether to save the result function into the datapack, defaults to `true`
    /// * return - PreMcFunction
    fn parse_func_tokens(
        &mut self,
        tokenizer: Rc<Tokenizer<'header>>,
        command: Vec<Token>,
        file_path_str: &str,
        prefix: &str,
        is_save_to_datapack: bool,
    ) -> Result<PreMcFunction<'header, 'config, 'lexer>, JMCError> {
        if command.len() < 2 {
            return Err(JMCError::jmc_syntax_exception(
                "Expected keyword(function's name)".to_owned(),
                Some(&command[0]),
                &tokenizer,
                true,
                true,
                false,
                None,
            ));
        }
        if command[1].token_type != TokenType::Keyword {
            return Err(JMCError::jmc_syntax_exception(
                "Expected keyword(function's name)".to_owned(),
                Some(&command[1]),
                &tokenizer,
                false,
                true,
                false,
                None,
            ));
        }
        if command.len() < 3 {
            return Err(JMCError::jmc_syntax_exception(
                "Expected round bracket, `()`".to_owned(),
                Some(&command[1]),
                &tokenizer,
                true,
                true,
                false,
                None,
            ));
        }
        if is_save_to_datapack && command[2].string != "()" {
            return Err(JMCError::jmc_syntax_exception(
                "Expected empty round bracket, `()`".to_owned(),
                Some(&command[2]),
                &tokenizer,
                false,
                true,
                false,
                None,
            ));
        }
        if command.len() < 4 {
            return Err(JMCError::jmc_syntax_exception(
                "Expected {".to_owned(),
                Some(&command[1]),
                &tokenizer,
                true,
                true,
                false,
                None,
            ));
        }
        if command[3].token_type != TokenType::ParenCurly {
            return Err(JMCError::jmc_syntax_exception(
                "Expected {".to_owned(),
                Some(&command[3]),
                &tokenizer,
                false,
                false,
                false,
                None,
            ));
        }
        if command.len() > 4 {
            return Err(JMCError::jmc_syntax_exception(
                "Unexpected token".to_owned(),
                Some(&command[4]),
                &tokenizer,
                false,
                true,
                false,
                None,
            ));
        }
        let func_path = prefix.to_owned()
            + &convention_jmc_to_mc(&command[1].string, &command[1], &tokenizer, "", true)?;
        if func_path.starts_with(&format!("{0}/", self.datapack.config.private_name)) {
            // FIXME: find a better way to do this
            return Err(JMCError::jmc_syntax_warning(
                format!("Function({func_path}) may override private function of JMC"),
                Some(&command[1]),
                &tokenizer,
                false,
                true,
                false,
                Some(format!(
                    "Please avoid starting function's path with {0}",
                    self.datapack.config.private_name
                )),
            ));
        }
        let mut command_iter = command.into_iter();
        command_iter.next();
        let mcfunction_name_token = command_iter
            .next()
            .expect("command should have a length of 3 or more");
        let params_token = command_iter
            .next()
            .expect("command should have a length of 3 or more");
        let mcfunction_content_token = command_iter
            .next()
            .expect("command should have a length of 3 or more");
        let line = mcfunction_content_token.line;
        let col = mcfunction_content_token.col;
        let mut func_content = mcfunction_content_token.string;
        func_content.remove(0);
        func_content.pop();
        if func_path == self.datapack.config.load_name {
            return Err(JMCError::jmc_syntax_warning(
                "Load function is defined".to_owned(),
                Some(&mcfunction_name_token),
                &tokenizer,
                false,
                true,
                false,
                Some(format!(
                    "JMC needs to reserve '{0}' name for load function.",
                    self.datapack.config.load_name
                )),
            ));
        }
        if self.datapack.functions.contains_key(&func_path) {
            let (old_function_token, old_function_tokenizer) =
                &self.datapack.defined_file_pos[&func_path];
            return Err(JMCError::jmc_syntax_warning(
                format!("Duplicate function declaration({func_path})"),
                Some(&mcfunction_name_token),
                &tokenizer,
                false,
                true,
                false,
                Some(format!(
                    "This function was already defined at line {0} col {1} in {2}",
                    old_function_token.line,
                    old_function_token.col,
                    relative_file_name(
                        &old_function_tokenizer.file_path_str,
                        Some(old_function_token.line),
                        Some(old_function_token.col)
                    )
                )),
            ));
        }
        if func_path == self.datapack.config.private_name {
            return Err(JMCError::jmc_syntax_warning(
                "Private function is defined".to_owned(),
                Some(&mcfunction_name_token),
                &tokenizer,
                false,
                false,
                false,
                Some(format!(
                    "JMC needs to reserve '{0}' name for private function.",
                    self.datapack.config.private_name
                )),
            ));
        }

        self.datapack.defined_file_pos.insert(
            func_path.clone(),
            (mcfunction_name_token.clone(), Rc::clone(&tokenizer)),
        );
        Ok(PreMcFunction::new(
            func_content.to_owned(),
            file_path_str.to_owned(),
            line,
            col,
            func_path,
            mcfunction_name_token,
            params_token,
            unsafe_share!(self, Self),
            tokenizer,
            prefix.to_owned(),
        ))
    }

    fn parse_decorated_func(
        &mut self,
        tokenizer: Rc<Tokenizer<'header>>,
        command: Vec<Token>,
        file_path_str: &str,
        prefix: &str,
    ) -> Result<(), JMCError> {
        let decorator_name = &command[0].string[1..];
        let decorator = DECORATORS.get(decorator_name);
        if decorator.is_none() {
            return Err(JMCError::jmc_syntax_exception(
                format!("Unrecognized decorator '{decorator_name}'"),
                Some(&command[0]),
                &tokenizer,
                false,
                true,
                false,
                if decorator_name == "import" {
                    Some("Did you mean to use 'import' (without @) instead?".to_owned())
                } else {
                    None
                },
            ));
        }
        let decorator = decorator.expect("decorator can't be None due to guard clause");
        if command.len() < 5 {
            return Err(JMCError::jmc_syntax_exception(
                "Function decorator syntax usage is '@decorator_name function name() {}' or '@decorator_name() function name() {}'".to_owned(),
                Some(&command[0]),
                &tokenizer,
                false,
                true,
                false,
                None
            ));
        }
        let token_type = command[1].token_type;
        let mut function_commands = command;
        let args: Option<Token>;
        if token_type == TokenType::ParenRound {
            args = function_commands.drain(..1).nth(1);
        } else {
            function_commands.remove(0);
            args = None;
        }
        let pre_mcfunction = self.parse_func_tokens(
            Rc::clone(&tokenizer),
            function_commands,
            file_path_str,
            prefix,
            decorator.is_save_to_datapack(),
        )?;
        match decorator.modify_mcfunction {
            ModifyMcFunction::Save(modify) => {
                modify(
                    decorator.call(&tokenizer, prefix, args),
                    &pre_mcfunction,
                    &self.datapack,
                );
                let (_mcfunction, func_path) = pre_mcfunction.parse()?;
                self.datapack.functions.insert(func_path, _mcfunction);
            }
            ModifyMcFunction::NoSave(modify) => {
                modify(
                    decorator.call(&tokenizer, prefix, args),
                    pre_mcfunction,
                    &self.datapack,
                );
            }
        }
        Ok(())
    }

    fn parse_new(&self, tokenizer: Rc<Tokenizer>, command: Vec<Token>) -> Result<(), JMCError> {
        #![allow(unused_variables)]
        let mut has_extends = false;
        if command.len() < 2 {
            return Err(JMCError::jmc_syntax_exception(
                "Expected keyword(JSON file's type)".to_owned(),
                Some(&command[0]),
                &tokenizer,
                true,
                true,
                false,
                None,
            ));
        }
        if command[1].token_type != TokenType::Keyword {
            return Err(JMCError::jmc_syntax_exception(
                "Expected keyword(JSON file's type)".to_owned(),
                Some(&command[1]),
                &tokenizer,
                false,
                true,
                false,
                None,
            ));
        }
        if command.len() < 3 {
            return Err(JMCError::jmc_syntax_exception(
                "Expected round bracket(JSON file's path)".to_owned(),
                Some(&command[1]),
                &tokenizer,
                true,
                true,
                false,
                None,
            ));
        }
        if command[2].string == "()" {
            return Err(JMCError::jmc_syntax_exception(
                "Expected JSON file's path in the bracket".to_owned(),
                Some(&command[2]),
                &tokenizer,
                false,
                true,
                false,
                None,
            ));
        }
        todo!()
    }

    fn parse_class(
        &mut self,
        tokenizer: Rc<Tokenizer>,
        command: Vec<Token>,
        file_path_str: &str,
        prefix: &str,
    ) -> Result<(), JMCError> {
        if command.len() < 2 {
            return Err(JMCError::jmc_syntax_exception(
                "Expected class name after keyword 'class'".to_owned(),
                Some(&command[0]),
                &tokenizer,
                false,
                true,
                false,
                None,
            ));
        }
        if command[1].token_type != TokenType::Keyword {
            return Err(JMCError::jmc_syntax_exception(
                format!(
                    "Expected class name after keyword 'class' (got {0})",
                    command[1].token_type
                ),
                Some(&command[1]),
                &tokenizer,
                false,
                true,
                false,
                None,
            ));
        }

        if command.len() < 3 {
            return Err(JMCError::jmc_syntax_exception(
                "Expected '{' after class name".to_owned(),
                Some(&command[1]),
                &tokenizer,
                false,
                true,
                false,
                None,
            ));
        }

        let class_path = format!(
            "{prefix}{0}/",
            convention_jmc_to_mc(&command[1].string, &command[1], &tokenizer, "", true)?
        );
        let line = command[2].line;
        let col = command[2].col;
        let mut class_content = command
            .into_iter()
            .nth(2)
            .expect("command should have length of 3 or more")
            .string;
        class_content.remove(0);
        class_content.pop();
        self.parse_class_content(
            &class_path,
            Rc::new(class_content),
            file_path_str,
            line,
            col,
            tokenizer.file_string.clone(),
        )?;
        return Ok(());
    }

    fn parse_class_content(
        &mut self,
        prefix: &str,
        class_content: Rc<String>,
        file_path_str: &str,
        line: u32,
        col: u32,
        file_string: Option<Rc<String>>,
    ) -> Result<(), JMCError> {
        let mut tokenizer = Tokenizer::parse_raw_string_col_line(
            unsafe_share!(self.header, Header),
            class_content,
            file_path_str.to_owned(),
            file_string,
            true,
            false,
            line,
            col,
        )?;
        let programs = std::mem::take(&mut tokenizer.programs);
        let tokenizer = Rc::new(tokenizer);
        for command in programs {
            let tokenizer = Rc::clone(&tokenizer);
            match command[0].string.as_str() {
                "function" => self.parse_func(tokenizer, command, file_path_str, prefix)?,
                "new" => self.parse_new(tokenizer, command)?,
                "class" => self.parse_class(tokenizer, command, file_path_str, prefix)?,
                "import" => {
                    return Err(JMCError::jmc_syntax_exception(
                        "Importing is not supported in class".to_owned(),
                        Some(&command[0]),
                        &tokenizer,
                        false,
                        true,
                        false,
                        None,
                    ))
                }
                decorator if is_decorator(decorator) => {
                    self.parse_decorated_func(tokenizer, command, file_path_str, "")?
                }
                string => {
                    return Err(JMCError::jmc_syntax_exception(
                        format!("Expected 'function' or 'new' or 'class' (got {})", string),
                        Some(&command[0]),
                        &tokenizer,
                        false,
                        true,
                        false,
                        None,
                    ))
                }
            }
        }
        Ok(())
    }

    fn parse_import(
        &mut self,
        tokenizer: Rc<Tokenizer>,
        command: Vec<Token>,
        file_path: &PathBuf,
    ) -> Result<(), JMCError> {
        if command.len() < 2 {
            return Err(JMCError::jmc_syntax_exception(
                "Expected string after 'import'".to_owned(),
                Some(&command[0]),
                &tokenizer,
                true,
                true,
                false,
                None,
            ));
        }
        if command[1].token_type != TokenType::String {
            return Err(JMCError::jmc_syntax_exception(
                format!(
                    "Expected string after 'import' (got {0})",
                    command[1].token_type
                ),
                Some(&command[1]),
                &tokenizer,
                false,
                false,
                false,
                None,
            ));
        }
        if command.len() > 2 {
            return Err(JMCError::jmc_syntax_exception(
                "Unexpected token".to_owned(),
                Some(&command[2]),
                &tokenizer,
                false,
                true,
                false,
                None,
            ));
        }

        if command[1].string.starts_with("/*") || command[1].string.ends_with("\\*") {
            let path_string = command[1].string.as_str();
            let path_string = &path_string[..path_string.len() - 2];
            let directory = Path::new(path_string);
            if !directory.is_dir() {
                return Err(JMCError::jmc_file_not_found(format!(
                    "Directory(folder) not found: {0}",
                    directory.to_string_lossy()
                )));
            }
            let pattern: PathBuf = [&directory.to_string_lossy(), "**", "*.jmc"]
                .iter()
                .collect();
            let paths =
                glob::glob(&pattern.to_string_lossy()).expect("glob should have valid pattern");
            for path in paths {
                let path = path.expect("glob should have valid pattern");
                Lexer::parse_file(
                    self.config,
                    &path,
                    false,
                    unsafe_share!(self.header, Header),
                )?;
            }
            return Ok(());
        }
        let mut path = file_path.clone();
        let mut path_string = command[1].string.clone();
        if !path_string.ends_with(".jmc") {
            path_string.push_str(".jmc");
        }
        path.push(path_string);
        Lexer::parse_file(self.config, &path, false, self.header)?;
        Ok(())
    }
}
