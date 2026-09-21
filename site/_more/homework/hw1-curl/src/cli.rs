use clap::Parser;
use std::collections::HashMap;
use std::str::FromStr;

#[derive(Debug, Clone, PartialEq)]
pub enum HttpMethod {
    Get,
    Post,
    Put,
    Delete,
    Head,
    Patch,
}

impl FromStr for HttpMethod {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_uppercase().as_str() {
            "GET" => Ok(Self::Get),
            "POST" => Ok(Self::Post),
            "PUT" => Ok(Self::Put),
            "DELETE" => Ok(Self::Delete),
            "HEAD" => Ok(Self::Head),
            "PATCH" => Ok(Self::Patch),
            _ => Err(format!("unknown HTTP method: '{s}'")),
        }
    }
}

impl HttpMethod {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Get => "GET",
            Self::Post => "POST",
            Self::Put => "PUT",
            Self::Delete => "DELETE",
            Self::Head => "HEAD",
            Self::Patch => "PATCH",
        }
    }
}

impl std::fmt::Display for HttpMethod {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

#[derive(Parser, Debug)]
#[command(
    name = "rurl",
    version,
    about = "A curl-like HTTP client written in Rust"
)]
pub struct Cli {
    /// The URL to send the request to
    pub url: String,

    /// HTTP method to use
    #[arg(short = 'X', long = "request", default_value_t = HttpMethod::Get)]
    pub method: HttpMethod,

    /// Pass custom header(s) to the server (-H "Name: Value")
    #[arg(short = 'H', long = "header", action = clap::ArgAction::Append)]
    pub headers: Vec<String>,

    /// Send data in the request body
    #[arg(short = 'd', long = "data")]
    pub data: Option<String>,

    /// Follow redirects
    #[arg(short = 'L', long = "location")]
    pub follow_redirects: bool,

    /// Maximum time allowed for the request (in seconds)
    #[arg(short = 'm', long = "max-time")]
    pub timeout: Option<u64>,

    /// Include response headers in the output
    #[arg(short = 'i', long = "include")]
    pub include_headers: bool,

    /// Verbose output
    #[arg(short = 'v', long = "verbose")]
    pub verbose: bool,

    /// Write output to a file
    #[arg(short = 'o', long = "output")]
    pub output: Option<String>,
}

impl Cli {
    pub fn parse_headers(&self) -> anyhow::Result<HashMap<String, String>> {
        let mut map = HashMap::new();
        for h in &self.headers {
            let (key, value) = h.split_once(':').ok_or_else(|| {
                anyhow::anyhow!("Invalid header format: '{h}'. Expected 'Name: Value'")
            })?;
            map.insert(key.trim().to_string(), value.trim().to_string());
        }
        Ok(map)
    }

    pub fn infer_method(&self) -> &HttpMethod {
        // If data is provided but method is GET, upgrade to POST
        if self.data.is_some() && matches!(self.method, HttpMethod::Get) {
            &HttpMethod::Post
        } else {
            &self.method
        }
    }
}
