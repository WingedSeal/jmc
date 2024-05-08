use std::fs;
use std::rc::Rc;
use std::{collections::HashSet, path::PathBuf};

use phf::{phf_map, phf_set};

use super::super::terminal::configuration::Configuration;

use super::datapack::Datapack;
use super::exception::JMCError;
use super::header::Header;
use super::tokenizer::{Token, Tokenizer};
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
    if_else_box: Vec<(Option<ConditionToken>, Vec<CodeBlockToken>)>,
    do_while_box: Option<CodeBlockToken>,
    /// Tokenizer for load function
    load_tokenizer: Option<Tokenizer<'header>>,
    /// Set of path that's already imported
    imports: HashSet<PathBuf>,
    config: &'config Configuration,
    datapack: Datapack<'header, 'config, 'lexer>,
    /// Header shared between compilation
    header: &'header Header,
    load_function: Vec<Vec<Token>>,
}

impl<'header, 'config, 'lexer> Lexer<'header, 'config, 'lexer> {
    pub fn new(config: &'config Configuration, header: &'header Header) -> Self {
        let datapack = Datapack::new();
        Self {
            if_else_box: vec![],
            do_while_box: None,
            load_tokenizer: None,
            imports: HashSet::new(),
            config,
            datapack,
            header,
            load_function: vec![],
        }
    }

    /// Parse a jmc file
    pub fn parse_file(
        config: &'config Configuration,
        file_path: &PathBuf,
        is_load: bool,
        header: &'header Header,
    ) -> Result<Self, JMCError> {
        let mut lexer = Self::new(config, header);
        if lexer.imports.contains(file_path) {
            return Ok(lexer);
        }
        let file_path_str = file_path
            .to_str()
            .expect("file_path is read from jmc file which is valid UTF-8")
            .to_owned();
        let raw_string = match fs::read_to_string(file_path) {
            Ok(raw_string) => raw_string,
            Err(_) => {
                return Err(JMCError::jmc_file_not_found(format!(
                    "JMC file not found: {file_path_str}"
                )))
            }
        };
        lexer.parse(Rc::new(raw_string), file_path_str, is_load)?;
        Ok(lexer)
    }

    /// Parse string read from JMC file
    ///
    /// * `is_load` - Whether the file is for load function, defaults to False
    pub fn parse(
        &mut self,
        file_string: Rc<String>,
        file_path_str: String,
        is_load: bool,
    ) -> Result<(), JMCError> {
        let mut tokenizer = Tokenizer::parse_raw_string(
            self.header,
            file_string,
            file_path_str,
            None,
            true,
            false,
        )?;

        if is_load {
            self.load_tokenizer = Some(tokenizer.clone()); // FIXME: avoid cloning this
        }

        // FIXME: I have no idea what the `__update_load` is actually doing, so I'm omitting it for now.
        // python version line 162: self.__update_load(file_path_str, raw_string)
        let programs = std::mem::take(&mut tokenizer.programs);
        for command in programs {
            match command[0].string.as_str() {
                "function" if !self.is_vanilla_func(&command) => {
                    self.parse_current_load()?;
                    self.parse_func(&tokenizer, &command, tokenizer.file_path_str.as_str())?;
                }
                "new" => {
                    self.parse_current_load()?;
                    self.parse_new(&tokenizer, &command)?;
                }
                "class" => {
                    self.parse_current_load()?;
                    self.parse_class(&tokenizer, &command, tokenizer.file_path_str.as_str())?;
                }
                "import" => {
                    self.parse_current_load()?;
                    self.parse_import(&tokenizer, &command, tokenizer.file_path_str.as_str())?;
                }
                decorator if is_decorator(decorator) => {
                    self.parse_current_load()?;
                    self.parse_decorated_func(
                        &tokenizer,
                        &command,
                        tokenizer.file_path_str.as_str(),
                    )?;
                }
                _ => self.load_function.push(command),
            }
            self.parse_current_load()?;
        }
        Ok(())
    }

    fn is_vanilla_func(&self, command: &Vec<Token>) -> bool {
        todo!()
    }

    /// Parse current load function that's in self.load_function and clear it
    fn parse_current_load(&self) -> Result<(), JMCError> {
        if self.load_function.is_empty() {
            return Ok(());
        }
        todo!()
    }

    fn parse_func(
        &self,
        tokenizer: &Tokenizer,
        command: &Vec<Token>,
        file_path_str: &str,
    ) -> Result<(), JMCError> {
        todo!()
    }

    fn parse_decorated_func(
        &self,
        tokenizer: &Tokenizer,
        command: &Vec<Token>,
        file_path_str: &str,
    ) -> Result<(), JMCError> {
        todo!()
    }

    fn parse_new(&self, tokenizer: &Tokenizer, command: &Vec<Token>) -> Result<(), JMCError> {
        todo!()
    }

    fn parse_class(
        &self,
        tokenizer: &Tokenizer,
        command: &Vec<Token>,
        file_path_str: &str,
    ) -> Result<(), JMCError> {
        todo!()
    }

    fn parse_import(
        &self,
        tokenizer: &Tokenizer,
        command: &Vec<Token>,
        file_path_str: &str,
    ) -> Result<(), JMCError> {
        todo!()
    }
}
