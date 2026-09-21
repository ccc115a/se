use crate::client::Response;
use anyhow::{Context, Result};
use std::io::Write;

pub fn print_response(resp: &Response, include_headers: bool) -> Result<()> {
    let mut stdout = std::io::stdout().lock();

    if include_headers {
        writeln!(stdout, "HTTP/1.1 {}", resp.status)?;
        for (key, value) in &resp.headers {
            writeln!(stdout, "{key}: {value}")?;
        }
        writeln!(stdout)?;
    }

    stdout
        .write_all(&resp.body)
        .context("failed to write response body")?;
    stdout.flush()?;

    Ok(())
}

pub fn write_to_file(resp: &Response, path: &str) -> Result<()> {
    std::fs::write(path, &resp.body).with_context(|| format!("failed to write to '{path}'"))
}
