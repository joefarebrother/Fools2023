use clap::Parser;
use std::io::prelude::*;
use std::net::TcpStream;
use std::time::{Duration, Instant};

#[derive(Parser)]
struct Args {
    password: String,
    username: Option<String>,
    #[arg(short, long)]
    upfront: bool,
}

struct Out {
    header_time: Duration,
    un_time: Duration,
    pw_time: Duration,
    correct: bool,
}

// Expected header:
// ======================================================================
// Welcome to Glitch Research Laboratory Network: Test Server 2 (GRLTS02)
// ======================================================================
// This machine requires authentication.
// Username:
// length: 265 (there are crlfs for some reason)

// Expected response:
// >> Please wait...
// >> Username OK. Password required
// Password:
// length: 62

// Expected response 2:
// >> Please wait...
// >> Password is incorrect.
// Username:
// length: 54

fn try_pass(username: &str, password: &str, upfront: bool) -> std::io::Result<Out> {
    let mut to_send = format!("{}\n{}", username, password);
    if upfront {
        to_send += "\n";
    }

    let start = Instant::now();

    let mut stream = TcpStream::connect("fools2023.online:13338")?;

    const EXPECTED_INTRO_LEN: usize = 265;
    const EXPECTED_UN_RESP_LEN: usize = 62;
    const EXPECTED_PW_RESP_LEN: usize = 54;

    stream.read_exact(&mut [0; EXPECTED_INTRO_LEN])?;

    let rec_header = Instant::now();

    stream.write_all(to_send.as_bytes())?;
    stream.read_exact(&mut [0; EXPECTED_UN_RESP_LEN])?;

    let un_end = Instant::now();

    if !upfront {
        stream.write_all("\n".as_bytes())?;
    }
    let mut buf = [0_u8; EXPECTED_PW_RESP_LEN];
    stream.read_exact(&mut buf)?;

    let end = Instant::now();

    let header_dur = rec_header - start;
    let un_dur = un_end - rec_header;
    let pw_dur = end - un_end;

    let buf_str: String = String::from_utf8_lossy(&buf).to_string();
    let incorrect = buf_str.contains("incorrect");

    Ok(Out {
        header_time: header_dur,
        un_time: un_dur,
        pw_time: pw_dur,
        correct: !incorrect,
    })
}

fn main() -> std::io::Result<()> {
    let args = Args::parse();

    let username = args.username.unwrap_or("ax.arwen".to_owned());

    let res = try_pass(&username, &args.password, args.upfront)?;

    println!(
        "{}, {}, {}, {}, {}",
        args.password,
        res.header_time.as_nanos(),
        res.un_time.as_nanos(),
        res.pw_time.as_nanos(),
        res.correct
    );

    Ok(())
}
