use phf::phf_map;

use super::{
    datapack::{Datapack, PreMcFunction},
    tokenizer::{Token, Tokenizer},
};

pub static DECORATORS: phf::Map<&'static str, JMCDecorator> = phf_map! {
    "test" => TEST,
};

pub enum ModifyMcFunction {
    Save(fn(JMCDecorator, pre_mcfunction: &PreMcFunction, datapack: &Datapack)),
    NoSave(fn(JMCDecorator, pre_mcfunction: PreMcFunction, datapack: &Datapack)),
}

impl ModifyMcFunction {
    pub fn is_save(&self) -> bool {
        match self {
            ModifyMcFunction::Save(_) => true,
            ModifyMcFunction::NoSave(_) => false,
        }
    }
}

pub struct JMCDecorator {
    pub modify_mcfunction: ModifyMcFunction,
}

impl JMCDecorator {
    pub fn call(&self, tokenizer: &Tokenizer, prefix: &str, arg_token: Option<Token>) -> Self {
        #![allow(unused_variables)]
        todo!()
    }
    pub fn is_save_to_datapack(&self) -> bool {
        self.modify_mcfunction.is_save()
    }
}

const TEST: JMCDecorator = JMCDecorator {
    modify_mcfunction: ModifyMcFunction::NoSave(|_, _, _| {}),
};
