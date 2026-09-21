mod cli;
mod client;
mod output;

use anyhow::Result;
use clap::Parser;

#[tokio::main]
async fn main() -> Result<()> {
    let cli = cli::Cli::parse();

    if cli.verbose {
        eprintln!("> method:     {}", cli.infer_method());
        eprintln!("> url:        {}", cli.url);
        eprintln!("> headers:    {:?}", cli.headers);
        eprintln!("> data:       {:?}", cli.data);
        eprintln!("> follow:     {}", cli.follow_redirects);
        eprintln!("> timeout:    {:?}", cli.timeout);
    }

    let response = client::execute(&cli).await?;

    match &cli.output {
        Some(path) => {
            output::write_to_file(&response, path)?;
            if cli.verbose {
                eprintln!("< saved body to '{path}' ({} bytes)", response.body.len());
            }
        }
        None => {
            output::print_response(&response, cli.include_headers)?;
        }
    }

    Ok(())
}
