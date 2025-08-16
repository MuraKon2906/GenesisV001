use pyo3::prelude::*;
use regex::Regex;
use translators::{GoogleTranslator, Translator};

#[pyfunction]
fn hello_from_bin() -> String {
    "Hello I am CASY. What can I do for you Buddy \n 1. Translation \n 2. AI Productivity \n 3. Teleprompter!".to_string()
}
#[pyfunction]
fn genesis_translate(input: &str) -> String {
    let google_trans = GoogleTranslator::default();
    let res = google_trans.translate_sync(input, "", "en").unwrap();
    res
}
#[pyfunction]
fn remove_gen_waste(gen_input: &str) -> String {
    let reg = Regex::new(r"\*").unwrap();
    let cleaned = reg.replace_all(gen_input, "").to_string();
    cleaned
}
/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello_from_bin, m)?)?;
    m.add_function(wrap_pyfunction!(genesis_translate, m)?)?;

    m.add_function(wrap_pyfunction!(remove_gen_waste, m)?)?;

    Ok(())
}
