use super::super::compile::pack_version::PackVersion;

#[derive(Debug)]
pub struct Configuration {
    pub namespace: String,
    pub pack_version: PackVersion,
    pub load_name: String,
}
