use phf::phf_map;

const TEST: JMCDecorator = JMCDecorator {};

pub static DECORATORS: phf::Map<&'static str, JMCDecorator> = phf_map! {
    "test" => TEST,
};

pub struct JMCDecorator {}
