use crate::cli::{Cli, HttpMethod};
use anyhow::Result;
use reqwest::Client;
use std::time::Duration;

pub struct Response {
    pub status: u16,
    pub headers: Vec<(String, String)>,
    pub body: Vec<u8>,
}

pub async fn execute(cli: &Cli) -> Result<Response> {
    let method = cli.infer_method();

    let mut builder = Client::builder();

    if let Some(seconds) = cli.timeout {
        builder = builder.timeout(Duration::from_secs(seconds));
    }

    if cli.follow_redirects {
        builder = builder.redirect(reqwest::redirect::Policy::limited(20));
    } else {
        builder = builder.redirect(reqwest::redirect::Policy::none());
    }

    let client = builder.build()?;

    let mut request = match method {
        HttpMethod::Get => client.get(&cli.url),
        HttpMethod::Post => client.post(&cli.url),
        HttpMethod::Put => client.put(&cli.url),
        HttpMethod::Delete => client.delete(&cli.url),
        HttpMethod::Head => client.head(&cli.url),
        HttpMethod::Patch => client.patch(&cli.url),
    };

    // Add custom headers
    let headers = cli.parse_headers()?;
    for (key, value) in &headers {
        request = request.header(key.as_str(), value.as_str());
    }

    // Add body data
    if let Some(ref data) = cli.data {
        request = request.body(data.clone());
    }

    if cli.verbose {
        eprintln!("> {} {}", method.as_str(), cli.url);
        for (key, value) in &headers {
            eprintln!("> {key}: {value}");
        }
        eprintln!(">");
    }

    let response = request.send().await?;
    let status = response.status().as_u16();

    let resp_headers: Vec<(String, String)> = response
        .headers()
        .iter()
        .map(|(k, v)| (k.to_string(), v.to_str().unwrap_or("").to_string()))
        .collect();

    let body = response.bytes().await?.to_vec();

    Ok(Response {
        status,
        headers: resp_headers,
        body,
    })
}
