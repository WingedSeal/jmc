use std::cell::UnsafeCell;
use std::fs;
use std::path::Path;
use std::rc::Rc;
use std::{collections::HashSet, path::PathBuf};

use phf::{phf_map, phf_set};

use super::super::terminal::configuration::Configuration;

use super::datapack::Datapack;
use super::exception::JMCError;
use super::header::Header;
use super::lexer_func_content::FuncContent;
use super::tokenizer::{Token, TokenType, Tokenizer};
use super::utils::is_decorator;

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
    inner: UnsafeCell<LexerInner<'header, 'config, 'lexer>>,
}

impl<'header, 'config, 'lexer> Lexer<'header, 'config, 'lexer> {
    pub fn get(&self) -> &mut LexerInner<'header, 'config, 'lexer> {
        unsafe { &mut *self.inner.get() }
    }
    pub fn into_inner(self) -> LexerInner<'header, 'config, 'lexer> {
        self.inner.into_inner()
    }

    pub fn new(config: &'config Configuration, header: &'header Header) -> Self {
        let datapack = Datapack::new(config);
        let inner = UnsafeCell::new(LexerInner {
            if_else_box: vec![],
            do_while_box: None,
            load_tokenizer: None,
            imports: HashSet::new(),
            config,
            datapack,
            header,
            load_function: vec![],
            lexer_outer: None,
        });
        unsafe {
            // datapack.lexer must be set right after the initialization
            // of LexerInner, otherwise there'd be a dangling reference
            (*inner.get()).datapack.lexer = Some(&mut *inner.get());
        }
        let lexer = Self { inner };
        unsafe {
            (*lexer.inner.get()).lexer_outer = Some(&lexer as *const Lexer);
        }
        lexer
    }
    /// Parse a jmc file
    pub fn parse_file(
        config: &'config Configuration,
        file_path: &PathBuf,
        is_load: bool,
        header: &'header Header,
    ) -> Result<Self, JMCError> {
        let lexer = Self::new(config, header);
        if lexer.get().imports.contains(file_path) {
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
        lexer.get().parse(Rc::new(raw_string), file_path, is_load)?;
        Ok(lexer)
    }
}

#[derive(Debug)]
pub struct LexerInner<'header, 'config, 'lexer> {
    if_else_box: Vec<(Option<ConditionToken>, Vec<CodeBlockToken>)>,
    do_while_box: Option<CodeBlockToken>,
    /// Tokenizer for load function
    load_tokenizer: Option<Rc<Tokenizer<'header>>>,
    /// Set of path that's already imported
    imports: HashSet<PathBuf>,
    config: &'config Configuration,
    datapack: Datapack<'header, 'config, 'lexer>,
    /// Header shared between compilation
    header: &'header Header,
    load_function: Vec<Vec<Token>>,
    lexer_outer: Option<*const Lexer<'header, 'config, 'lexer>>,
}

impl<'header, 'config, 'lexer> LexerInner<'header, 'config, 'lexer> {
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
        let mut tokenizer = Tokenizer::parse_raw_string(
            self.header,
            file_string,
            file_path_str,
            None,
            true,
            false,
        )?;
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
                    self.parse_func(tokenizer, &command, file_path_str)?;
                }
                "new" => {
                    self.parse_current_load()?;
                    self.parse_new(tokenizer, &command)?;
                }
                "class" => {
                    self.parse_current_load()?;
                    let file_path_str = tokenizer.file_path_str.clone();
                    self.parse_class(tokenizer, &command, file_path_str)?;
                }
                "import" => {
                    self.parse_current_load()?;
                    self.parse_import(tokenizer, &command, file_path)?;
                }
                decorator if is_decorator(decorator) => {
                    self.parse_current_load()?;
                    let file_path_str = tokenizer.file_path_str.clone();
                    self.parse_decorated_func(tokenizer, &command, file_path_str)?;
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
        self.parse_func_content(load_tokenizer, programs, "".to_owned(), true)
    }

    /// Parse a content inside function
    ///
    /// * `is_load` - Whether the function is a load function
    /// * return - List of commands(string)
    fn parse_func_content(
        &mut self,
        tokenizer: Rc<Tokenizer>,
        programs: Vec<Vec<Token>>,
        prefix: String,
        is_load: bool,
    ) -> Result<Vec<String>, JMCError> {
        let lexer: &mut LexerInner;
        unsafe {
            lexer = &mut *(self as *mut LexerInner);
        }
        FuncContent::new(tokenizer, programs, is_load, lexer, prefix).parse()
    }

    fn parse_func(
        &self,
        tokenizer: Rc<Tokenizer>,
        command: &Vec<Token>,
        file_path_str: String,
    ) -> Result<(), JMCError> {
        todo!()
    }

    fn parse_decorated_func(
        &self,
        tokenizer: Rc<Tokenizer>,
        command: &Vec<Token>,
        file_path_str: String,
    ) -> Result<(), JMCError> {
        todo!()
    }

    fn parse_new(&self, tokenizer: Rc<Tokenizer>, command: &Vec<Token>) -> Result<(), JMCError> {
        todo!()
    }

    fn parse_class(
        &self,
        tokenizer: Rc<Tokenizer>,
        command: &Vec<Token>,
        file_path_str: String,
    ) -> Result<(), JMCError> {
        todo!()
    }

    fn parse_import(
        &self,
        tokenizer: Rc<Tokenizer>,
        command: &Vec<Token>,
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
                Lexer::parse_file(self.config, &path, false, self.header)?;
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
